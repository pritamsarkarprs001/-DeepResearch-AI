# agents/synthesizer.py
# SYNTHESIZER AGENT: Combines all research into one final polished Markdown report.

from agents.llm_config import get_llm


def synthesizer_agent(topic: str, research_notes: list, critic_feedback: str = "") -> str:
    """
    Input: topic, research notes from Researcher, optional critic feedback
    Output: a full Markdown-formatted research report (string)
    """
    llm = get_llm(temperature=0.4)

    # Build the research content block for the AI to read
    notes_text = ""
    all_sources = []
    for i, note in enumerate(research_notes, start=1):
        notes_text += f"\nSection {i} - {note['question']}\n{note['summary']}\n"
        all_sources.extend(note.get("sources", []))

    # Build a unique source list for the references section
    seen = set()
    references = []
    for s in all_sources:
        ref = s.get("ref", "")
        if ref and ref not in seen:
            seen.add(ref)
            references.append(ref)

    prompt = f"""You are a professional research report writer.

Write a complete, well-structured research report in Markdown format on this topic:
"{topic}"

Use the research findings below as your factual basis. Organize into:
- A title (# heading)
- An introduction paragraph
- 2-4 clear sections with ## headings, based on the research findings
- A short conclusion paragraph

Research findings to base the report on:
{notes_text}

Quality notes to address: {critic_feedback if critic_feedback else "None"}

Write the full report now in clean Markdown. Do not include a references section
(we will add that separately).
"""

    try:
        response = llm.invoke(prompt)
        report_body = response.content.strip()
    except Exception as e:
        print(f"❌ Synthesizer agent error: {e}")
        report_body = f"# {topic}\n\n⚠️ Report generation failed: {e}"

    # Append a references section ourselves (reliable, not AI-generated)
    references_md = "\n\n## References\n"
    if references:
        for ref in references:
            references_md += f"- {ref}\n"
    else:
        references_md += "- No sources recorded.\n"

    full_report = report_body + references_md
    return full_report