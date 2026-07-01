# agents/critic.py
# CRITIC AGENT: Reviews research notes for quality, gaps, and missing info.

import json
from agents.llm_config import get_llm


def critic_agent(topic: str, research_notes: list) -> dict:
    """
    Input: original topic + research notes from Researcher agent
    Output: dict with 'approved' (bool), 'feedback' (str), 'follow_up_questions' (list)
    """
    llm = get_llm(temperature=0.2)

    # Build a readable summary of all research so far for the AI to review
    notes_text = ""
    for note in research_notes:
        notes_text += f"Q: {note['question']}\nFindings: {note['summary']}\n\n"

    prompt = f"""You are a strict research quality reviewer.

Original research topic: "{topic}"

Research findings so far:
{notes_text}

Review these findings critically. Answer in EXACTLY this format (no extra text):
APPROVED: yes or no
FEEDBACK: one short sentence on overall quality
FOLLOW_UP: comma-separated list of 0-2 follow-up questions if anything important is missing, or "none"
"""

    try:
        response = llm.invoke(prompt)
        text = response.content.strip()

        # Default values in case parsing fails
        approved = True
        feedback = "Research looks sufficient."
        follow_ups = []

        for line in text.split("\n"):
            line = line.strip()
            if line.upper().startswith("APPROVED:"):
                approved = "yes" in line.lower()
            elif line.upper().startswith("FEEDBACK:"):
                feedback = line.split(":", 1)[-1].strip()
            elif line.upper().startswith("FOLLOW_UP:"):
                raw = line.split(":", 1)[-1].strip()
                if raw.lower() != "none" and raw:
                    follow_ups = [q.strip() for q in raw.split(",") if q.strip()]

        return {
            "approved": approved,
            "feedback": feedback,
            "follow_up_questions": follow_ups
        }

    except Exception as e:
        print(f"❌ Critic agent error: {e}")
        # If critic fails, approve by default so the pipeline doesn't get stuck
        return {"approved": True, "feedback": "Critic check skipped due to error.", "follow_up_questions": []}