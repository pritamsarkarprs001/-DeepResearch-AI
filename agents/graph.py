# agents/graph.py
# This file wires our 4 agents together into one automatic workflow using LangGraph.

from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END

from agents.planner import planner_agent
from agents.researcher import researcher_agent
from agents.critic import critic_agent
from agents.synthesizer import synthesizer_agent


# ---- 1. Define the "State" that flows between agents ----
# Think of this as a shared clipboard all agents read from and write to.
class ResearchState(TypedDict):
    topic: str
    sub_questions: List[str]
    research_notes: List[Dict]
    critique: Dict
    iteration: int
    final_report: str
    status: str  # human-readable progress message for the UI


MAX_ITERATIONS = 2  # safety limit: max 2 research loops, so it never runs forever


# ---- 2. Define each node (a node = one agent doing its job) ----

def planner_node(state: ResearchState) -> ResearchState:
    state["status"] = "🧠 Planner: breaking topic into sub-questions..."
    state["sub_questions"] = planner_agent(state["topic"])
    state["research_notes"] = []
    state["iteration"] = 0
    return state


def researcher_node(state: ResearchState) -> ResearchState:
    state["status"] = "🔎 Researcher: gathering information..."
    new_notes = researcher_agent(state["sub_questions"])
    state["research_notes"].extend(new_notes)
    state["iteration"] += 1
    return state


def critic_node(state: ResearchState) -> ResearchState:
    state["status"] = "🧐 Critic: reviewing research quality..."
    critique = critic_agent(state["topic"], state["research_notes"])
    state["critique"] = critique
    return state


def synthesizer_node(state: ResearchState) -> ResearchState:
    state["status"] = "✍️ Synthesizer: writing final report..."
    feedback = state["critique"].get("feedback", "")
    state["final_report"] = synthesizer_agent(state["topic"], state["research_notes"], feedback)
    state["status"] = "✅ Report complete!"
    return state


# ---- 3. Decide: after Critic, do we loop back or move to Synthesizer? ----
def should_continue(state: ResearchState) -> str:
    approved = state["critique"].get("approved", True)
    follow_ups = state["critique"].get("follow_up_questions", [])
    reached_limit = state["iteration"] >= MAX_ITERATIONS

    if approved or not follow_ups or reached_limit:
        return "synthesizer"
    else:
        # Set the new follow-up questions as the next thing to research
        state["sub_questions"] = follow_ups
        return "researcher"


# ---- 4. Build the graph (the flowchart) ----
def build_research_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("critic", critic_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "critic")

    # Conditional branch: critic decides next step
    graph.add_conditional_edges(
        "critic",
        should_continue,
        {"researcher": "researcher", "synthesizer": "synthesizer"}
    )

    graph.add_edge("synthesizer", END)

    return graph.compile()


# ---- 5. Simple function the Streamlit app will call ----
def run_research_pipeline(topic: str) -> dict:
    """
    Runs the full multi-agent pipeline for a given topic.
    Returns the final state dict containing the report + all intermediate data.
    """
    app_graph = build_research_graph()
    initial_state: ResearchState = {
        "topic": topic,
        "sub_questions": [],
        "research_notes": [],
        "critique": {},
        "iteration": 0,
        "final_report": "",
        "status": "Starting..."
    }
    final_state = app_graph.invoke(initial_state)
    return final_state