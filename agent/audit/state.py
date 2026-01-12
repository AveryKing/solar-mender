from typing import TypedDict, List, Optional, Any
from agent.state import AgentState

class AuditAgentState(AgentState):
    """
    State for the AuditAgent.
    
    Attributes:
        audit_results: The findings from the system audit.
        technical_debt: Identified technical debt items.
        recommendations: Suggested improvements.
    """
    audit_results: Optional[str]
    technical_debt: List[dict]
    recommendations: List[str]
