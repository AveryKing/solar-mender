import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.db.base import get_db
from app.db.models import JobStatus, RepairJob
from app.schemas.webhook import GitHubWebhookPayload
from agent.registry import get_registry

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/run", status_code=status.HTTP_200_OK)
async def run_repair_worker(
    payload: dict,  # Receive raw dict to handle custom fields like job_id
    db: AsyncSession = Depends(get_db)
):
    """
    Worker endpoint called by Google Cloud Tasks.
    Executes the appropriate agent for a specific job based on agent_name.
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

    # Get agent name from payload (default to 'repair' for backward compatibility)
    agent_name = payload.get("agent_name", "repair")
    registry = get_registry()
    agent = registry.get(agent_name)
    
    if not agent:
        logger.error(f"Agent '{agent_name}' not found in registry")
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    # Initialize state based on agent type
    # For repair agent, use repair-specific state structure
    if agent_name == "repair":
        initial_state: Dict[str, Any] = {
            "job_id": job_id,
            "run_id": str(gh_payload.workflow_run.id),
            "repo_name": gh_payload.repository.full_name,
            "total_cost": 0.0,
            "status": "FIXING",
            "pr_draft": False
        }
    else:
        # Generic state for other agents
        initial_state = {
            "job_id": job_id,
            "agent_name": agent_name,
            "status": "RUNNING",
            "data": payload.get("data", {}),
            "metadata": payload.get("metadata", {}),
            "total_cost": 0.0
        }

    try:
        # Update status to FIXING/RUNNING
        status_value = JobStatus.FIXING if agent_name == "repair" else JobStatus.FIXING
        await db.execute(
            update(RepairJob)
            .where(RepairJob.id == job_id)
            .values(status=status_value)
        )
        await db.commit()

        # Execute agent
        final_state = await agent.invoke(initial_state)

        # Build reasoning log for audit trail (repair-specific for now)
        if agent_name == "repair":
            reasoning_parts = [
                f"Diagnosis confidence: {final_state.get('diagnosis_confidence', 'N/A')}",
                f"Fix confidence: {final_state.get('fix_confidence', 'N/A')}",
                f"Failure category: {final_state.get('failure_category', 'N/A')}",
                f"Root cause: {final_state.get('root_cause', 'N/A')}",
                f"Target file: {final_state.get('target_file_path', 'N/A')}"
            ]
            reasoning_log = "\n".join(reasoning_parts)
            
            # Log reasoning
            from app.core.cost_control import log_reasoning
            await log_reasoning(db, job_id, reasoning_log)

            # Update database with results (repair-specific)
            await db.execute(
                update(RepairJob)
                .where(RepairJob.id == job_id)
                .values(
                    status=final_state.get("status", JobStatus.FAILED),
                    error_log_summary=final_state.get("root_cause"),
                    vertex_cost_est=final_state.get("total_cost", 0.0),
                    pr_url=final_state.get("pr_url"),
                    pr_draft=final_state.get("pr_draft", False),
                    diagnosis_confidence=final_state.get("diagnosis_confidence"),
                    fix_confidence=final_state.get("fix_confidence"),
                    failure_category=final_state.get("failure_category")
                )
            )
        else:
            # Generic update for other agents
            final_status = JobStatus.PR_OPENED if final_state.get("status") == "PR_OPENED" else JobStatus.FAILED
            await db.execute(
                update(RepairJob)
                .where(RepairJob.id == job_id)
                .values(
                    status=final_status,
                    vertex_cost_est=final_state.get("total_cost", 0.0)
                )
            )
        
        await db.commit()
        
        return {"status": "completed", "job_id": job_id, "agent": agent_name}

    except Exception as e:
        logger.error(f"Worker failed for job {job_id}: {e}")
        await db.execute(
            update(RepairJob)
            .where(RepairJob.id == job_id)
            .values(status=JobStatus.FAILED)
        )
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))
