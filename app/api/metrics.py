from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.db.models import RepairJob, JobStatus

router = APIRouter()

@router.get("/metrics")
async def get_metrics(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns metrics about repair job performance.
    
    Args:
        days: Number of days to look back (default: 7).
        db: Database session.
        
    Returns:
        Dictionary with metrics including success rate, costs, and breakdowns.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Total jobs
    total_result = await db.execute(
        select(func.count(RepairJob.id))
        .where(RepairJob.created_at >= cutoff_date)
    )
    total_jobs = total_result.scalar() or 0
    
    # Success rate (PR_OPENED vs total)
    success_result = await db.execute(
        select(func.count(RepairJob.id))
        .where(
            RepairJob.created_at >= cutoff_date,
            RepairJob.status == JobStatus.PR_OPENED
        )
    )
    successful_jobs = success_result.scalar() or 0
    
    success_rate = (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0.0
    
    # Total cost
    cost_result = await db.execute(
        select(func.sum(RepairJob.vertex_cost_est))
        .where(RepairJob.created_at >= cutoff_date)
    )
    total_cost = cost_result.scalar() or 0.0
    
    # Average confidence scores
    avg_diag_confidence = await db.execute(
        select(func.avg(RepairJob.diagnosis_confidence))
        .where(
            RepairJob.created_at >= cutoff_date,
            RepairJob.diagnosis_confidence.isnot(None)
        )
    )
    avg_diag_conf = avg_diag_confidence.scalar() or 0.0
    
    avg_fix_confidence = await db.execute(
        select(func.avg(RepairJob.fix_confidence))
        .where(
            RepairJob.created_at >= cutoff_date,
            RepairJob.fix_confidence.isnot(None)
        )
    )
    avg_fix_conf = avg_fix_confidence.scalar() or 0.0
    
    # Status breakdown
    status_result = await db.execute(
        select(RepairJob.status, func.count(RepairJob.id))
        .where(RepairJob.created_at >= cutoff_date)
        .group_by(RepairJob.status)
    )
    status_breakdown = {status.value: count for status, count in status_result.all()}
    
    # Category breakdown
    category_result = await db.execute(
        select(RepairJob.failure_category, func.count(RepairJob.id))
        .where(
            RepairJob.created_at >= cutoff_date,
            RepairJob.failure_category.isnot(None)
        )
        .group_by(RepairJob.failure_category)
    )
    category_breakdown = {cat: count for cat, count in category_result.all()}
    
    # Cost per job
    avg_cost_per_job = (total_cost / total_jobs) if total_jobs > 0 else 0.0
    
    return {
        "period_days": days,
        "total_jobs": total_jobs,
        "successful_jobs": successful_jobs,
        "success_rate_percent": round(success_rate, 2),
        "total_cost_usd": round(total_cost, 4),
        "avg_cost_per_job_usd": round(avg_cost_per_job, 4),
        "avg_diagnosis_confidence": round(avg_diag_conf, 3),
        "avg_fix_confidence": round(avg_fix_conf, 3),
        "status_breakdown": status_breakdown,
        "category_breakdown": category_breakdown
    }
