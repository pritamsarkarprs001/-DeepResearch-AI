# agents/planner.py
# PLANNER AGENT: Breaks a big research topic into smaller sub-questions.

from agents.llm_config import get_llm


def planner_agent(topic: str) -> list:
    """
    Input: a research topic (e.g. "Impact of AI on jobs")
    Output: a list of 3-5 specific sub-questions to research
    """
    llm = get_llm(temperature=0.3)

    prompt = f"""You are a research planning expert.
Break down this research topic into exactly 4 specific, focused sub-questions
that together would fully cover the topic.

Topic: "{topic}"

Respond ONLY with a numbered list, one sub-question per line. No extra text.
Example format:
1. First sub-question here
2. Second sub-question here
"""

    try:
        response = llm.invoke(prompt)
        text = response.content

        # Parse numbered lines into a clean list of sub-questions
        sub_questions = []
        for line in text.split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                # Remove "1. " or "1) " prefix
                question = line.split(".", 1)[-1].split(")", 1)[-1].strip()
                if question:
                    sub_questions.append(question)

        # Safety fallback: if parsing failed, just use the whole topic
        if not sub_questions:
            sub_questions = [topic]

        return sub_questions

    except Exception as e:
        print(f"❌ Planner agent error: {e}")
        return [topic]  # fallback: research the original topic directly