import json
from google.cloud import tasks_v2
from app.core.config import settings

def create_cloud_task(payload: dict, endpoint: str = "/api/v1/worker/run") -> str:
    """
    Creates a Google Cloud Task to process a repair job.
    
    Args:
        payload: The data to send to the worker.
        endpoint: The worker endpoint to call.
        
    Returns:
        The name of the created task.
    """
    client = tasks_v2.CloudTasksClient()
    
    parent = client.queue_path(
        settings.GOOGLE_CLOUD_PROJECT, 
        settings.GOOGLE_CLOUD_LOCATION, 
        settings.CLOUD_TASKS_QUEUE
    )
    
    url = f"{settings.SERVICE_URL}{endpoint}"
    
    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(payload).encode(),
        }
    }
    
    # Note: In production, you'd add OIDC token for authentication between Cloud Tasks and Cloud Run
    # task["http_request"]["oidc_token"] = {"service_account_email": settings.SERVICE_ACCOUNT}

    response = client.create_task(request={"parent": parent, "task": task})
    return response.name
