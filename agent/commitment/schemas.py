from typing import List
from pydantic import BaseModel, Field

class CommitMessage(BaseModel):
    """Schema for high-fidelity commit message."""
    subject: str = Field(description="50-character imperative mood subject line")
    body: str = Field(description="Detailed body explaining the 'Why' vs 'What', wrapped at 72 chars")
    type: str = Field(description="One of: feat, fix, refactor, chore, docs")

class LogicalGroup(BaseModel):
    """Schema for a logical group of changes."""
    files: List[str]
    description: str
    rationale: str
