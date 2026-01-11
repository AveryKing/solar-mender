import hmac
import hashlib
from fastapi import Request, HTTPException, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.base import get_db

async def verify_github_signature(
    request: Request,
    x_hub_signature_256: str = Header(None)
) -> None:
    """
    Validates the GitHub HMAC signature.
    
    Args:
        request: The incoming FastAPI request.
        x_hub_signature_256: The signature from the X-Hub-Signature-256 header.
        
    Raises:
        HTTPException: If the signature is missing or invalid.
    """
    if not x_hub_signature_256:
        raise HTTPException(status_code=403, detail="X-Hub-Signature-256 header is missing")

    if not settings.GITHUB_SECRET:
        # In development, if secret is not set, we might skip validation or fail
        # For security, we should fail if expected but missing
        raise HTTPException(status_code=500, detail="GITHUB_SECRET is not configured")

    body = await request.body()
    # Cache body in request state so it can be reused in the route handler
    request.state.body = body
    
    signature = "sha256=" + hmac.new(
        settings.GITHUB_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid GitHub signature")
