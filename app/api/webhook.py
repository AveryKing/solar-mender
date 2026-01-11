import logging
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_github_signature
from app.db.base import get_db
from app.db.models import JobStatus, RepairJob
from app.schemas.webhook import GitHubWebhookPayload
from app.core.cloud_tasks import create_cloud_task

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/github", status_code=status.HTTP_202_ACCEPTED)
async def github_webhook(
    request: Request,
    payload: GitHubWebhookPayload,
    db: AsyncSession = Depends(get_db),
    _signature: None = Depends(verify_github_signature)
):
    """
    Endpoint for GitHub webhooks.
    Validates signature and filters for failed workflow runs.
    Dispatches to Cloud Tasks for reliable execution.
    """
    # Only process 'workflow_run' events that have failed
    if not payload.workflow_run or payload.workflow_run.conclusion != "failure":
        return {"message": "Ignored: Not a failed workflow run"}

    # Create a new repair job record
    repo_name = payload.repository.full_name if payload.repository else "unknown"
    run_id = str(payload.workflow_run.id)

    new_job = RepairJob(
        repo_name=repo_name,
        run_id=run_id,
        status=JobStatus.PENDING
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # Prepare payload for Cloud Task (includes job_id)
    task_payload = payload.model_dump()
    task_payload["job_id"] = new_job.id

    # Dispatch to Google Cloud Tasks
    try:
        task_name = create_cloud_task(task_payload)
        logger.info(f"Created Cloud Task {task_name} for job {new_job.id}")
    except Exception as e:
        logger.error(f"Failed to create Cloud Task for job {new_job.id}: {e}")
        # Optionally update job status to FAILED here
        return {"message": "Repair job created but failed to dispatch", "job_id": new_job.id}

    return {
        "message": "Repair job scheduled via Cloud Tasks",
        "job_id": new_job.id,
        "run_id": run_id
    }
