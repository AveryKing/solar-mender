import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def get_langfuse_callback() -> Optional[object]:
    """
    Returns a configured Langfuse callback handler.
    
    Returns:
        CallbackHandler instance if available, None otherwise.
    """
    try:
        from langfuse.callback import CallbackHandler
        from app.core.config import settings
        
        # Set environment variables for Langfuse to pick up
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
        os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
        os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST
        
        return CallbackHandler()
    except ImportError:
        logger.warning("Langfuse CallbackHandler not available")
        return None
    except Exception as e:
        logger.warning(f"Failed to initialize Langfuse callback: {e}")
        return None
