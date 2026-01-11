from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class Repository(BaseModel):
    """Schema for repository info in webhook payload."""
    full_name: str
    name: str
    owner: Dict[str, Any]

class WorkflowRun(BaseModel):
    """Schema for workflow_run info in webhook payload."""
    id: int
    name: str
    status: str
    conclusion: Optional[str] = None
    head_branch: str
    head_sha: str
    html_url: str
    run_number: int

class GitHubWebhookPayload(BaseModel):
    """
    Schema for the GitHub 'workflow_run' webhook payload.
    We strictly validate only what we need.
    """
    action: Optional[str] = None
    workflow_run: Optional[WorkflowRun] = None
    repository: Optional[Repository] = None
    sender: Optional[Dict[str, Any]] = None

    model_config = {
        "extra": "ignore"
    }
