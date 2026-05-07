"""
Popo-Job-Agent — Streamlit UI
Run with: streamlit run ui/app.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from graph import run_agent

st.set_page_config(
    page_title="Popo-Job-Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Popo-Job-Agent")
st.caption(
    "Multi-agent AI for job application research · "
    "Powered by LangGraph + GPT-4o · Monitored via LangSmith"
)

# --- Sidebar: Candidate profile ---
with st.sidebar:
    st.header("Your profile")
    st.caption("Paste a brief summary of your skills and experience.")
    candidate_profile = st.text_area(
        label="Candidate profile",
        height=280,
        placeholder=(
            "BSc Data Science & Analytics...\n"
            "Skills: Python, LangChain, Docker...\n"
            "Projects: RAG chatbot, YOLOv8 pipeline..."
        )
    )
    st.divider()
    st.caption("Popo-Job-Agent by Jun Kit Mak · github.com/popolome")

# --- Main: Job input ---
col1, col2 = st.columns(2)
with col1:
    job_title = st.text_input("Job title", placeholder="Data Scientist")
with col2:
    company_name = st.text_input("Company", placeholder="DBS Bank")

run_btn = st.button("Run agent", type="primary", use_container_width=True)

# --- Run ---
if run_btn:
    if not job_title or not company_name or not candidate_profile:
        st.warning("Please fill in all three fields before running.")
    else:
        with st.spinner("Agent running — this takes 20–40 seconds..."):
            try:
                result = run_agent(job_title, company_name, candidate_profile)
            except Exception as e:
                st.error(f"Agent failed: {str(e)}")
                st.stop()

        if result.get("error"):
            st.error(f"Agent error: {result['error']}")
        else:
            # --- Confidence badge ---
            score = result.get("confidence_score", 0)
            color = "green" if score >= 0.8 else "orange" if score >= 0.5 else "red"
            st.markdown(
                f"**Confidence score:** :{color}[{score}]  "
                f"&nbsp;·&nbsp; Sources used: {len(result.get('sources', []))}"
            )

            # --- Flags ---
            flags = result.get("hallucination_flags", [])
            if flags:
                with st.expander(f"⚠️ {len(flags)} responsible AI flag(s)"):
                    for f in flags:
                        st.caption(f"• {f}")

            st.divider()

            # --- Tabs for outputs ---
            tab1, tab2, tab3, tab4 = st.tabs([
                "Cover letter", "Skills gap", "Interview Qs", "Debug log"
            ])

            with tab1:
                st.subheader("Cover letter")
                st.write(result.get("cover_letter", "Not generated."))
                if result.get("cover_letter"):
                    st.download_button(
                        "Download cover letter",
                        data=result["cover_letter"],
                        file_name=f"cover_letter_{company_name.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )

            with tab2:
                st.subheader("Skills gap analysis")
                st.write(result.get("skills_gap", "Not generated."))

            with tab3:
                st.subheader("Top 5 interview questions")
                questions = result.get("interview_questions", [])
                if questions:
                    for i, q in enumerate(questions, 1):
                        st.markdown(f"**{i}.** {q}")
                else:
                    st.write("Not generated.")

            with tab4:
                st.subheader("Step log")
                for step in result.get("step_log", []):
                    st.caption(step)
                st.subheader("Sources")
                for url in result.get("sources", []):
                    st.caption(url)
