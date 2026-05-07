"""
Responsible AI Layer
Runs after Writer agent. Adds:
- Confidence score based on source richness
- Hallucination flags for unverified claims
- Source citation summary
"""

from utils.state import JobAgentState


def responsible_ai_layer(state: JobAgentState) -> JobAgentState:
    """
    LangGraph node: Responsible AI Layer
    Scores output quality and flags potential issues.
    No LLM call needed — rule-based checks are sufficient and faster.
    """
    if state.error:
        return state

    step_log = state.step_log.copy()
    step_log.append("Responsible AI: running checks")

    flags = []
    score = 1.0

    # --- Check 1: Was research actually retrieved? ---
    if not state.raw_search_results:
        flags.append("No web search results found — cover letter may be generic")
        score -= 0.3

    # --- Check 2: Was JD actually scraped? ---
    if not state.scraped_jd_text or len(state.scraped_jd_text) < 200:
        flags.append(
            "JD text was short or missing — requirements may be incomplete"
        )
        score -= 0.2

    # --- Check 3: Sources present? ---
    if len(state.sources) == 0:
        flags.append("No sources cited — outputs are not grounded in retrieved data")
        score -= 0.2
    elif len(state.sources) < 2:
        flags.append("Only 1 source found — consider verifying JD on company website")
        score -= 0.1

    # --- Check 4: Cover letter sanity check ---
    if state.cover_letter:
        generic_phrases = [
            "i am passionate",
            "team player",
            "hard worker",
            "i am a quick learner"
        ]
        lower_cl = state.cover_letter.lower()
        for phrase in generic_phrases:
            if phrase in lower_cl:
                flags.append(
                    f"Cover letter contains generic phrase: '{phrase}' — consider revising"
                )
                score -= 0.05

    # --- Check 5: Interview questions generated? ---
    if not state.interview_questions or len(state.interview_questions) < 3:
        flags.append("Fewer than 3 interview questions generated — re-run may help")
        score -= 0.1

    # Clamp score between 0 and 1
    confidence = round(max(0.0, min(1.0, score)), 2)

    return state.model_copy(update={
        "confidence_score": confidence,
        "hallucination_flags": flags,
        "step_log": step_log + [
            f"Responsible AI: complete — confidence {confidence}, "
            f"{len(flags)} flag(s)"
        ]
    })
