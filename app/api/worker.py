import logging
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.db.base import get_db
from app.db.models import JobStatus, RepairJob
from app.schemas.webhook import GitHubWebhookPayload
from agent.graph import repair_agent

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run", status_code=status.HTTP_200_OK)
async def run_repair_worker(
    payload: dict,  # Receive raw dict to handle custom fields like job_id
    db: AsyncSession = Depends(get_db)
):
    """
    Worker endpoint called by Google Cloud Tasks.
    Executes the LangGraph repair agent for a specific job.
    """
    job_id = payload.get("job_id")
    if not job_id:
        logger.error("No job_id provided in worker payload")
        raise HTTPException(status_code=400, detail="job_id is required")

    # Re-validate the webhook part of the payload
    try:
        gh_payload = GitHubWebhookPayload(**payload)
    except Exception as e:
        logger.error(f"Invalid payload for job {job_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid GitHub payload")

    logger.info(f"Worker processing job {job_id}")

    # Initialize state
    initial_state = {
        "job_id": job_id,
        "run_id": str(gh_payload.workflow_run.id),
        "repo_name": gh_payload.repository.full_name,
        "total_cost": 0.0,
        "status": "FIXING"
    }

    try:
        # Update status to FIXING
        await db.execute(
            update(RepairJob)
            .where(RepairJob.id == job_id)
            .values(status=JobStatus.FIXING)
        )
        await db.commit()

        # Run LangGraph Agent
        final_state = await repair_agent.ainvoke(initial_state)

        # Update database with results
        await db.execute(
            update(RepairJob)
            .where(RepairJob.id == job_id)
            .values(
                status=final_state.get("status", JobStatus.FAILED),
                error_log_summary=final_state.get("root_cause"),
                vertex_cost_est=final_state.get("total_cost", 0.0),
                pr_url=final_state.get("pr_url")
            )
        )
        await db.commit()
        
        return {"status": "completed", "job_id": job_id}

    except Exception as e:
        logger.error(f"Worker failed for job {job_id}: {e}")
        await db.execute(
            update(RepairJob)
            .where(RepairJob.id == job_id)
            .values(status=JobStatus.FAILED)
        )
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))
