from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.db.models import JobStatus

class RepairJobBase(BaseModel):
    """Base schema for RepairJob."""
    repo_name: str
    run_id: str
    status: JobStatus = JobStatus.PENDING
    vertex_cost_est: float = 0.0

class RepairJobCreate(RepairJobBase):
    """Schema for creating a new RepairJob."""
    pass

class RepairJobUpdate(BaseModel):
    """Schema for updating a RepairJob."""
    status: Optional[JobStatus] = None
    error_log_summary: Optional[str] = None
    vertex_cost_est: Optional[float] = None
    pr_url: Optional[str] = None

class RepairJobRead(RepairJobBase):
    """Schema for reading a RepairJob."""
    id: int
    error_log_summary: Optional[str] = None
    pr_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
