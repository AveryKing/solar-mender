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
        # Langfuse reads from environment variables automatically
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
        os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
        os.environ["LANGFUSE_HOST"] = settings.LANGFUSE_HOST
        
        # Initialize CallbackHandler without arguments
        # It will read credentials from environment variables automatically
        return CallbackHandler()
    except ImportError as e:
        logger.warning(f"Langfuse CallbackHandler not available (ImportError): {e}")
        return None
    except Exception as e:
        logger.warning(f"Failed to initialize Langfuse callback: {type(e).__name__}: {e}", exc_info=True)
        return None
