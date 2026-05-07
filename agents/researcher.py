"""
Researcher Agent
Searches the web, scrapes the JD, and gathers company background.
Writes results into shared JobAgentState.
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from utils.state import JobAgentState
from tools.researcher_tools import web_search, scrape_jd, get_company_summary


RESEARCHER_SYSTEM_PROMPT = """You are a job research specialist.
Given a job title and company name, your job is to:
1. Search for the job posting and extract the key requirements
2. Scrape the actual JD if a direct URL is found
3. Gather company background (industry, culture, recent news)

Be thorough. The Writer agent depends entirely on your research.
Always return structured findings with sources cited."""


def researcher_agent(state: JobAgentState) -> JobAgentState:
    """
    LangGraph node: Researcher Agent
    Runs web search, JD scrape, and company summary.
    Updates state with research findings.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    step_log = state.step_log.copy()
    sources = state.sources.copy()

    try:
        # --- Step 1: Web search for the JD ---
        step_log.append("Researcher: running web search")
        search_query = f"{state.job_title} {state.company_name} job description Singapore"
        search_results = web_search.invoke({"query": search_query})
        sources += _extract_urls(search_results)

        # --- Step 2: Try to scrape top JD URL ---
        scraped_text = ""
        top_url = _extract_top_url(search_results)
        if top_url:
            step_log.append(f"Researcher: scraping JD from {top_url}")
            scraped_text = scrape_jd.invoke({"url": top_url})

        # --- Step 3: Company background ---
        step_log.append("Researcher: fetching company summary")
        company_info = get_company_summary.invoke(
            {"company_name": state.company_name}
        )

        # --- Step 4: LLM summarises findings into structured research ---
        step_log.append("Researcher: summarising findings with LLM")
        summary_prompt = f"""
Summarise the following research into a structured job brief:

JD SEARCH RESULTS:
{search_results[:3000]}

SCRAPED JD:
{scraped_text[:3000]}

COMPANY INFO:
{company_info[:2000]}

Return a structured brief with:
- Role summary (3–4 sentences)
- Key technical requirements (bullet list)
- Key soft skills / culture signals (bullet list)
- Company overview (2–3 sentences)
"""
        messages = [
            SystemMessage(content=RESEARCHER_SYSTEM_PROMPT),
            HumanMessage(content=summary_prompt)
        ]
        response = llm.invoke(messages)
        structured_research = response.content

        return state.model_copy(update={
            "raw_search_results": structured_research,
            "scraped_jd_text": scraped_text[:3000],
            "company_summary": company_info[:1500],
            "sources": list(set(sources)),
            "step_log": step_log + ["Researcher: complete"]
        })

    except Exception as e:
        return state.model_copy(update={
            "error": f"Researcher agent failed: {str(e)}",
            "step_log": step_log + [f"Researcher: ERROR — {str(e)}"]
        })


def _extract_urls(search_text: str) -> list[str]:
    """Pull [SOURCE] URLs out of Tavily output."""
    urls = []
    for line in search_text.splitlines():
        if line.startswith("[SOURCE]"):
            url = line.replace("[SOURCE]", "").strip()
            if url:
                urls.append(url)
    return urls


def _extract_top_url(search_text: str) -> str:
    """Return the first URL found in search results."""
    urls = _extract_urls(search_text)
    return urls[0] if urls else ""
