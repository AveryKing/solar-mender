from typing import TypedDict, Dict, Any, Optional, Annotated
import operator


class AgentState(TypedDict):
    """
    Generic state representation for all agents.
    
    This is the base state schema. Agent-specific implementations
    should extend this or use the 'data' field for agent-specific state.
    """
    # Core IDs
    job_id: int
    agent_name: str
    status: str
    
    # Flexible data storage (agent-specific state)
    data: Dict[str, Any]
    
    # Metadata
    metadata: Dict[str, Any]
    total_cost: Annotated[float, operator.add]
    error: Optional[str]
