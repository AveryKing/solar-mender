import logging
import os
from typing import Optional
from langfuse.callback import CallbackHandler
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_langfuse_callback() -> Optional[CallbackHandler]:
    """
    Returns a configured Langfuse callback handler.
    
    Returns:
        CallbackHandler instance if available, None otherwise.
    """
    if not CallbackHandler:
        logger.warning("Langfuse CallbackHandler not available, returning None")
        return None
        
    # Set environment variables for Langfuse to pick up
    os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
    os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
    os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST
    
    return CallbackHandler()
