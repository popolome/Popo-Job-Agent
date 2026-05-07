"""
Popo-Job-Agent — Main LangGraph Graph
Orchestrates: Researcher → Writer → Responsible AI

Usage:
    from graph import run_agent
    result = run_agent("Data Scientist", "DBS Bank", "your profile here")
"""

from dotenv import load_dotenv
load_dotenv()

import os
from langgraph.graph import StateGraph, END

from utils.state import JobAgentState
from agents.researcher import researcher_agent
from agents.writer import writer_agent
from agents.responsible_ai import responsible_ai_layer



def should_continue(state: JobAgentState) -> str:
    """
    Routing function: if an error occurred at any point, skip to END.
    Otherwise continue to the next node.
    """
    if state.error:
        return "end"
    return "continue"


def build_graph() -> StateGraph:
    """
    Build and compile the LangGraph StateGraph.

    Graph structure:
        researcher_agent
              ↓
        writer_agent
              ↓
        responsible_ai_layer
              ↓
             END
    """
    # Initialise graph with our shared state schema
    graph = StateGraph(JobAgentState)

    # --- Register nodes ---
    graph.add_node("researcher", researcher_agent)
    graph.add_node("writer", writer_agent)
    graph.add_node("responsible_ai", responsible_ai_layer)

    # --- Entry point ---
    graph.set_entry_point("researcher")

    # --- Edges with error routing ---
    graph.add_conditional_edges(
        "researcher",
        should_continue,
        {
            "continue": "writer",
            "end": END
        }
    )
    graph.add_conditional_edges(
        "writer",
        should_continue,
        {
            "continue": "responsible_ai",
            "end": END
        }
    )
    graph.add_edge("responsible_ai", END)

    return graph.compile()


def run_agent(
    job_title: str,
    company_name: str,
    candidate_profile: str
) -> JobAgentState:
    """
    Run the full Popo-Job-Agent pipeline.

    Args:
        job_title: e.g. "Data Scientist"
        company_name: e.g. "DBS Bank"
        candidate_profile: brief text summary of the candidate's background

    Returns:
        Final JobAgentState with all outputs populated
    """
    app = build_graph()

    initial_state = JobAgentState(
        job_title=job_title,
        company_name=company_name,
        candidate_profile=candidate_profile
    )

    # LangSmith traces this automatically via LANGCHAIN_TRACING_V2=true
    result = app.invoke(initial_state)
    return result


# --- Quick CLI test ---
if __name__ == "__main__":
    SAMPLE_PROFILE = """
    BSc Data Science & Analytics (Distinction), University of Portsmouth.
    3 years experience in IT and automation at Isetan Singapore.
    Projects: YOLOv8 CV systems, RAG chatbot, MLOps on AWS ECS Fargate,
    Power Automate, UiPath, Random Forest models served via FastAPI.
    Skills: Python, LangChain, Docker, GitHub Actions, SQL, Streamlit.
    """

    print("Running Popo-Job-Agent...\n")
    state = run_agent(
        job_title="Data Scientist",
        company_name="DBS Bank",
        candidate_profile=SAMPLE_PROFILE
    )

    if state.get("error"):
        print(f"ERROR: {state['error']}")
    else:
        print("=== COVER LETTER ===")
        print(state["cover_letter"])
        print("\n=== SKILLS GAP ===")
        print(state["skills_gap"])
        print("\n=== INTERVIEW QUESTIONS ===")
        for q in state["interview_questions"]:
            print(q)
        print(f"\n=== CONFIDENCE SCORE: {state['confidence_score']} ===")
        if state["hallucination_flags"]:
            print("FLAGS:")
            for f in state["hallucination_flags"]:
                print(f"  - {f}")
        print(f"\nSources used: {len(state['sources'])}")
        print("\nStep log:")
        for step in state["step_log"]:
            print(f"  {step}")
