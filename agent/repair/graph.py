import logging
from langgraph.graph import StateGraph, END
from agent.repair.state import RepairAgentState
from agent.repair.nodes.diagnose import diagnose_node
from agent.repair.nodes.classify import classify_node
from agent.repair.nodes.locate import locate_node
from agent.repair.nodes.fix import fix_node
from agent.repair.nodes.github_pr import pr_node
from agent.repair.nodes.monitor import monitor_deployment_node

logger = logging.getLogger(__name__)


def create_repair_graph():
    """
    Assembles the LangGraph repair workflow with reliability features.
    
    Returns:
        Compiled LangGraph workflow for the repair agent.
    """
    workflow = StateGraph(RepairAgentState)

    # Add Nodes
    workflow.add_node("diagnose", diagnose_node)
    workflow.add_node("classify", classify_node)
    workflow.add_node("locate", locate_node)
    workflow.add_node("fix", fix_node)
    workflow.add_node("pr", pr_node)
    workflow.add_node("monitor", monitor_deployment_node)

    # Entry point depends on the initial status
    def route_start(state: RepairAgentState) -> str:
        if state.get("status") == "MONITORING":
            return "monitor"
        return "diagnose"

    workflow.set_conditional_entry_point(
        route_start,
        {
            "monitor": "monitor",
            "diagnose": "diagnose"
        }
    )

    # Add Edges
    workflow.add_edge("monitor", END)

    # Add Edges with conditional routing
    workflow.add_edge("diagnose", "classify")
    
    def route_after_classify(state: RepairAgentState) -> str:
        """Routes after classification based on status."""
        if state.get("status") == "FAILED":
            return "end"
        return "locate"
    
    workflow.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "locate": "locate",
            "end": END
        }
    )
    workflow.add_edge("locate", "fix")
    workflow.add_edge("fix", "pr")
    workflow.add_edge("pr", END)

    return workflow.compile()
