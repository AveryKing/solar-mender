import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class JobStatus(str, enum.Enum):
    """Enum for RepairJob status."""
    PENDING = "PENDING"
    FIXING = "FIXING"
    PR_OPENED = "PR_OPENED"
    FAILED = "FAILED"

class RepairJob(Base):
    """
    Database model for tracking CI/CD repair jobs.
    """
    __tablename__ = "repair_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    repo_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    run_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    
    error_log_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vertex_cost_est: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # Metrics and reliability tracking
    diagnosis_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fix_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    failure_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Audit trail
    reasoning_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    pr_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pr_draft: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<RepairJob(id={self.id}, repo={self.repo_name}, status={self.status})>"
