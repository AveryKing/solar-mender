from langgraph.graph import StateGraph, END
from agent.commitment.state import CommitmentState
from agent.commitment.nodes.craft import craft_commit_node

def create_commitment_graph() -> StateGraph:
    """Creates the LangGraph workflow for the CommitmentAgent."""
    workflow = StateGraph(CommitmentState)
    
    workflow.add_node("craft_commit", craft_commit_node)
    
    workflow.set_entry_point("craft_commit")
    
    workflow.add_edge("craft_commit", END)
    
    return workflow.compile()
