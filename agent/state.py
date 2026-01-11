from typing import TypedDict, List, Optional, Annotated
import operator

class AgentState(TypedDict):
    """
    State representation for the LangGraph agent.
    """
    # Core IDs
    job_id: int
    run_id: str
    repo_name: str
    
    # Context
    error_logs: Optional[str]
    root_cause: Optional[str]
    target_file_path: Optional[str]
    original_content: Optional[str]
    fixed_content: Optional[str]
    context_files: Optional[dict]  # Dict[str, str] - file paths to contents
    
    # Confidence scoring
    diagnosis_confidence: Optional[float]
    fix_confidence: Optional[float]
    failure_category: Optional[str]
    
    # Metadata
    commit_author: Optional[str]
    total_cost: Annotated[float, operator.add]
    status: str
    error: Optional[str]
    pr_url: Optional[str]
    pr_draft: bool
