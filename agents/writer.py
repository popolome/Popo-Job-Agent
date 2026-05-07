"""
Writer Agent
Takes research from the Researcher agent and produces:
- Tailored cover letter
- Skills gap analysis
- Top 5 interview questions
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from utils.state import JobAgentState


WRITER_SYSTEM_PROMPT = """You are an expert career coach and technical writer
specialising in Singapore's data science job market.

You write cover letters that are:
- Concise (max 350 words), confident, and specific
- Grounded in the actual JD requirements
- Free of generic filler ("I am a passionate team player...")
- Singapore-appropriate in tone (professional but direct)

For skills gap analysis, be honest — highlight genuine gaps, not just
reassuring fluff. Candidates need actionable insight."""


def writer_agent(state: JobAgentState) -> JobAgentState:
    """
    LangGraph node: Writer Agent
    Generates cover letter, skills gap, and interview questions.
    Depends on Researcher agent having run first.
    """
    if state.error:
        return state  # Propagate error, skip writing

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.4
    )

    step_log = state.step_log.copy()

    try:
        context = f"""
JOB TITLE: {state.job_title}
COMPANY: {state.company_name}

RESEARCH FINDINGS:
{state.raw_search_results or 'No research available'}

CANDIDATE PROFILE:
{state.candidate_profile}
"""

        # --- Cover letter ---
        step_log.append("Writer: drafting cover letter")
        cover_letter = _generate_cover_letter(llm, context)

        # --- Skills gap ---
        step_log.append("Writer: analysing skills gap")
        skills_gap = _generate_skills_gap(llm, context)

        # --- Interview questions ---
        step_log.append("Writer: generating interview questions")
        interview_qs = _generate_interview_questions(llm, context)

        return state.model_copy(update={
            "cover_letter": cover_letter,
            "skills_gap": skills_gap,
            "interview_questions": interview_qs,
            "step_log": step_log + ["Writer: complete"]
        })

    except Exception as e:
        return state.model_copy(update={
            "error": f"Writer agent failed: {str(e)}",
            "step_log": step_log + [f"Writer: ERROR — {str(e)}"]
        })


def _generate_cover_letter(llm, context: str) -> str:
    messages = [
        SystemMessage(content=WRITER_SYSTEM_PROMPT),
        HumanMessage(content=f"""
Write a tailored cover letter for this application.
Do not include placeholders — write the actual letter.
Max 350 words.

{context}
""")
    ]
    return llm.invoke(messages).content


def _generate_skills_gap(llm, context: str) -> str:
    messages = [
        SystemMessage(content=WRITER_SYSTEM_PROMPT),
        HumanMessage(content=f"""
Analyse the skills gap between the candidate profile and the job requirements.

Structure your response as:
**Strong matches** (skills candidate clearly has)
**Partial matches** (candidate has adjacent experience, needs strengthening)
**Gaps** (skills missing entirely — be direct)
**Recommended actions** (specific steps to close the gaps)

{context}
""")
    ]
    return llm.invoke(messages).content


def _generate_interview_questions(llm, context: str) -> list[str]:
    messages = [
        SystemMessage(content=WRITER_SYSTEM_PROMPT),
        HumanMessage(content=f"""
Based on the JD and company background, predict the top 5 technical or
behavioural interview questions this candidate is likely to face.

Return ONLY a numbered list (1. ... 2. ... etc), no preamble.

{context}
""")
    ]
    raw = llm.invoke(messages).content
    lines = [
        line.strip() for line in raw.splitlines()
        if line.strip() and line.strip()[0].isdigit()
    ]
    return lines[:5]
