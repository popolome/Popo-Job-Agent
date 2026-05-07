"""
State schema for Popo-Job-Agent.
This is the shared memory object passed between all agents in the graph.
Every agent reads from and writes to this state.
"""

from typing import Optional
from pydantic import BaseModel, Field


class JobAgentState(BaseModel):
    """Shared state passed between all nodes in the LangGraph."""

    # --- User input ---
    job_title: str = Field(description="Target job title, e.g. 'Data Scientist'")
    company_name: str = Field(description="Target company, e.g. 'DBS Bank'")
    candidate_profile: str = Field(
        description="Brief summary of the candidate's skills and experience"
    )

    # --- Researcher agent outputs ---
    raw_search_results: Optional[str] = Field(
        default=None,
        description="Raw Tavily search results for the role"
    )
    scraped_jd_text: Optional[str] = Field(
        default=None,
        description="Cleaned job description text scraped from URL"
    )
    company_summary: Optional[str] = Field(
        default=None,
        description="Brief company background from web search"
    )
    sources: list[str] = Field(
        default_factory=list,
        description="URLs cited during research"
    )

    # --- Writer agent outputs ---
    cover_letter: Optional[str] = Field(
        default=None,
        description="Tailored cover letter draft"
    )
    skills_gap: Optional[str] = Field(
        default=None,
        description="Skills gap analysis against the JD"
    )
    interview_questions: Optional[list[str]] = Field(
        default=None,
        description="Top 5 predicted interview questions"
    )

    # --- Responsible AI layer outputs ---
    confidence_score: Optional[float] = Field(
        default=None,
        description="0.0–1.0 confidence in output quality based on source richness"
    )
    hallucination_flags: list[str] = Field(
        default_factory=list,
        description="Any claims flagged as potentially unverified"
    )

    # --- Control flow ---
    error: Optional[str] = Field(
        default=None,
        description="Error message if any step fails"
    )
    step_log: list[str] = Field(
        default_factory=list,
        description="Ordered log of completed steps for debugging"
    )
