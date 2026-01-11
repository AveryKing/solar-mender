from datetime import datetime, timedelta
from typing import Optional
import logging
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import RepairJob

logger = logging.getLogger(__name__)

async def check_cost_budget(db: AsyncSession) -> tuple[bool, float, Optional[str]]:
    """
    Checks if the daily cost budget has been exceeded.
    
    Args:
        db: Database session.
        
    Returns:
        Tuple of (within_budget, current_cost, alert_message).
        within_budget: True if under budget, False if exceeded.
        current_cost: Current day's cost in USD.
        alert_message: Alert message if threshold exceeded, None otherwise.
    """
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    result = await db.execute(
        select(func.sum(RepairJob.vertex_cost_est))
        .where(RepairJob.created_at >= today_start)
    )
    current_cost = result.scalar() or 0.0
    
    within_budget = current_cost < settings.DAILY_COST_LIMIT
    alert_threshold = settings.DAILY_COST_LIMIT * settings.COST_ALERT_THRESHOLD
    
    alert_message = None
    if current_cost >= alert_threshold:
        alert_message = (
            f"Cost alert: ${current_cost:.2f} used today "
            f"({current_cost / settings.DAILY_COST_LIMIT * 100:.1f}% of ${settings.DAILY_COST_LIMIT:.2f} limit)"
        )
        logger.warning(alert_message)
    
    if not within_budget:
        logger.error(
            f"Daily cost budget exceeded: ${current_cost:.2f} >= ${settings.DAILY_COST_LIMIT:.2f}"
        )
    
    return (within_budget, current_cost, alert_message)

async def log_reasoning(db: AsyncSession, job_id: int, reasoning: str) -> None:
    """
    Logs reasoning and decisions for audit trail.
    
    Args:
        db: Database session.
        job_id: Job ID to update.
        reasoning: Reasoning text to log.
    """
    from sqlalchemy import update
    from app.db.models import RepairJob
    
    try:
        await db.execute(
            update(RepairJob)
            .where(RepairJob.id == job_id)
            .values(reasoning_log=reasoning)
        )
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to log reasoning for job {job_id}: {e}")
