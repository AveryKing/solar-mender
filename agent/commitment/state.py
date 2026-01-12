from typing import TypedDict, List, Optional, Any
from agent.state import AgentState

class CommitmentState(AgentState):
    """
    State for the CommitmentAgent.
    
    Attributes:
        diff: The git diff to analyze.
        context: Additional context about why the change was made.
        commit_message: The generated human-grade commit message.
        logical_groups: Changes grouped into logical units.
    """
    diff: str
    context: Optional[str]
    commit_message: Optional[str]
    logical_groups: List[dict]
