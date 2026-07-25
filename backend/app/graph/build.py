"""Assemble and compile the LangGraph agent.

A MemorySaver checkpointer keys state by thread_id (= session_id), which is what
gives the agent multi-turn memory: an "edit" turn loads the form produced by an
earlier "log" turn and merges the correction into it. Swap MemorySaver for a
Postgres checkpointer to persist sessions across restarts.
"""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from . import nodes
from .state import ComplaintState


def build_graph():
    g = StateGraph(ComplaintState)

    g.add_node("router", nodes.router_node)
    g.add_node("log_complaint", nodes.log_node)
    g.add_node("edit_complaint", nodes.edit_node)
    g.add_node("extract_document", nodes.document_node)
    g.add_node("assess_risk", nodes.assess_risk_node)
    g.add_node("summarize_complaint", nodes.summarize_node)
    g.add_node("check_completeness", nodes.check_completeness_node)
    g.add_node("answer_question", nodes.answer_node)
    g.add_node("respond", nodes.respond_node)

    g.add_edge(START, "router")
    g.add_conditional_edges(
        "router",
        nodes.route_by_intent,
        {
            "log": "log_complaint",
            "edit": "edit_complaint",
            "document": "extract_document",
            "question": "answer_question",
        },
    )
    g.add_edge("log_complaint", "assess_risk")
    g.add_edge("edit_complaint", "assess_risk")
    g.add_edge("extract_document", "assess_risk")
    g.add_edge("assess_risk", "summarize_complaint")
    g.add_edge("summarize_complaint", "check_completeness")
    g.add_edge("check_completeness", "respond")
    g.add_edge("respond", END)
    g.add_edge("answer_question", END)

    return g.compile(checkpointer=MemorySaver())


# Module-level singleton so the in-memory checkpointer persists across requests.
graph = build_graph()
