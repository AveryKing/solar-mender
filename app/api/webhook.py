import logging
import json
from urllib.parse import unquote
from fastapi import APIRouter, Depends, Request, status, HTTPException
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
    db: AsyncSession = Depends(get_db),
    _signature: None = Depends(verify_github_signature)
):
    """
    Endpoint for GitHub webhooks.
    Validates signature and filters for failed workflow runs.
    Dispatches to Cloud Tasks for reliable execution.
    """
    # Read raw body BEFORE Pydantic validation
    event_type = request.headers.get("X-GitHub-Event")
    logger.info(f"Received GitHub event: {event_type}")
    
    try:
        raw_body = await request.body()
        logger.debug(f"Raw webhook body (first 500 chars): {raw_body.decode()[:500]}")
        
        # GitHub can send webhooks as either JSON or form-encoded
        # Check content type
        content_type = request.headers.get("Content-Type", "")
        
        if "application/x-www-form-urlencoded" in content_type:
            # Parse form-encoded: payload=URL_ENCODED_JSON
            body_str = raw_body.decode()
            if body_str.startswith("payload="):
                # Extract and URL-decode the payload
                payload_json = unquote(body_str[8:])  # Skip "payload=" prefix
                logger.debug(f"Extracted URL-decoded payload: {payload_json[:500]}")
                body_dict = json.loads(payload_json)
            else:
                raise HTTPException(status_code=400, detail="Invalid form-encoded payload format")
        else:
            # Direct JSON
            body_dict = json.loads(raw_body)
        
        logger.debug(f"Parsed JSON keys: {list(body_dict.keys())}")
        
        # Now validate with Pydantic
        payload = GitHubWebhookPayload(**body_dict)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook body: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    except Exception as e:
        logger.error(f"Pydantic validation failed: {e}")
        logger.error(f"Body was: {raw_body.decode()[:500] if 'raw_body' in locals() else 'N/A'}")
        raise HTTPException(status_code=422, detail=f"Validation error: {e}")

    if event_type == "ping":
        return {"message": "Pong"}

    # Only process 'workflow_run' events that have failed
    if not payload.workflow_run or payload.workflow_run.conclusion != "failure":
        logger.info(f"Ignoring event: workflow_run={payload.workflow_run is not None}, conclusion={payload.workflow_run.conclusion if payload.workflow_run else 'N/A'}")
        return {"message": "Ignored: Not a failed workflow run"}

    # Create a new repair job record
    repo_name = payload.repository.full_name if payload.repository else "unknown"
    run_id = str(payload.workflow_run.id)

    logger.info(f"Creating repair job for repo={repo_name}, run_id={run_id}")

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
        return {"message": "Repair job created but failed to dispatch", "job_id": new_job.id}

    return {
        "message": "Repair job scheduled via Cloud Tasks",
        "job_id": new_job.id,
        "run_id": run_id
    }
