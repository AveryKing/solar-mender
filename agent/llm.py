from typing import Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class VertexAIClient:
    """
    Client wrapper for Vertex AI Gemini models using LangChain.
    Lazy initializes the models to prevent startup crashes.
    """
    def __init__(self):
        self._flash_model: Optional[Any] = None
        self._pro_model: Optional[Any] = None
        self._initialized = False

    def _init(self):
        if not self._initialized:
            try:
                from langchain_google_vertexai import ChatVertexAI
                
                # ChatVertexAI automatically picks up credentials from environment
                # or we can pass project/location explicitly
                common_kwargs = {
                    "project": settings.GOOGLE_CLOUD_PROJECT,
                    "location": settings.GOOGLE_CLOUD_LOCATION,
                    "max_output_tokens": 8192,
                    "temperature": 0.0,  # Deterministic for code generation
                }
                
                self._flash_model = ChatVertexAI(
                    model_name="gemini-1.5-flash",
                    **common_kwargs
                )
                
                self._pro_model = ChatVertexAI(
                    model_name="gemini-1.5-pro",
                    **common_kwargs
                )
                
                self._initialized = True
                logger.info("Vertex AI (LangChain) initialized successfully")
            except Exception as e:
                # Log error but don't crash the whole app on import
                logger.error(f"Vertex AI initialization failed: {e}")
                print(f"Vertex AI initialization failed: {e}")

    def get_model(self, model_type: str = "flash") -> Any:
        """Returns the requested LangChain ChatVertexAI instance."""
        self._init()
        if model_type == "pro":
            if not self._pro_model:
                raise RuntimeError("Vertex AI Pro model not initialized")
            return self._pro_model
        
        if not self._flash_model:
             raise RuntimeError("Vertex AI Flash model not initialized")
        return self._flash_model

vertex_client = VertexAIClient()
