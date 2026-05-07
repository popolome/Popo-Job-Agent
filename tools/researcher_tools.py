"""
Tools for the Researcher agent.
- web_search: Tavily API search
- scrape_jd: BeautifulSoup JD page scraper
- get_company_summary: focused company background search
"""

import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from langchain_core.tools import tool


_tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query: str) -> str:
    """
    Search the web for job-related information using Tavily.
    Returns a concatenated string of the top result snippets and URLs.
    """
    try:
        results = _tavily.search(
            query=query,
            max_results=5,
            search_depth="advanced"
        )
        output_lines = []
        for r in results.get("results", []):
            output_lines.append(f"[SOURCE] {r['url']}")
            output_lines.append(r.get("content", ""))
            output_lines.append("")
        return "\n".join(output_lines) if output_lines else "No results found."
    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def scrape_jd(url: str) -> str:
    """
    Scrape and clean the job description text from a given URL.
    Returns plain text with boilerplate removed.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove nav, footer, scripts, styles
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Extract visible text
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned = "\n".join(lines)

        # Truncate to avoid token overflow (roughly 3000 words)
        return cleaned[:12000] if len(cleaned) > 12000 else cleaned

    except Exception as e:
        return f"Scrape failed: {str(e)}"


@tool
def get_company_summary(company_name: str) -> str:
    """
    Search for a brief background summary of the company.
    Returns key facts: industry, size, recent news, culture signals.
    """
    query = f"{company_name} company overview Singapore industry culture 2024 2025"
    try:
        results = _tavily.search(query=query, max_results=3)
        snippets = [
            r.get("content", "") for r in results.get("results", [])
        ]
        return "\n\n".join(snippets) if snippets else "No company info found."
    except Exception as e:
        return f"Company search failed: {str(e)}"


# Export all tools as a list for easy binding to agents
researcher_tools = [web_search, scrape_jd, get_company_summary]
