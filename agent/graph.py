import logging
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.diagnose import diagnose_node
from agent.nodes.locate import locate_node
from agent.nodes.fix import fix_node
from agent.nodes.github_pr import pr_node
from langfuse import Langfuse
from app.core.config import settings

def create_repair_graph():
    """
    Assembles the LangGraph repair workflow.
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("diagnose", diagnose_node)
    workflow.add_node("locate", locate_node)
    workflow.add_node("fix", fix_node)
    workflow.add_node("pr", pr_node)

    # Set Entry Point
    workflow.set_entry_point("diagnose")

    # Add Edges
    workflow.add_edge("diagnose", "locate")
    workflow.add_edge("locate", "fix")
    workflow.add_edge("fix", "pr")
    workflow.add_edge("pr", END)

    return workflow.compile()

# Singleton instance
repair_agent = create_repair_graph()

def get_langfuse_callback():
    """Returns a configured Langfuse callback handler."""
    langfuse = Langfuse(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST
    )
    return langfuse.callback_handler()
