import logging
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.db.base import get_db
from app.db.models import JobStatus, RepairJob
from app.schemas.webhook import GitHubWebhookPayload
from agent.graph import repair_agent, get_langfuse_callback

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
    # ... (existing code) ...
        # Update status to FIXING
        await db.execute(
            update(RepairJob)
            .where(RepairJob.id == job_id)
            .values(status=JobStatus.FIXING)
        )
        await db.commit()

        # Run LangGraph Agent with Langfuse Tracing
        langfuse_handler = get_langfuse_callback()
        
        # We pass the callback in the config (LangChain/LangGraph convention)
        final_state = await repair_agent.ainvoke(
            initial_state,
            config={"callbacks": [langfuse_handler]}
        )
        
        # Flush traces to ensure they are sent before the worker exits
        langfuse_handler.flush()

        # Update database with results
        # ... (rest of code) ...
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
