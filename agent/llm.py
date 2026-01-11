from typing import Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession
from app.core.config import settings

def init_vertex_ai() -> None:
    """Initialize Vertex AI with project and location."""
    vertexai.init(
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.GOOGLE_CLOUD_LOCATION
    )

class VertexAIClient:
    """
    Client wrapper for Vertex AI Gemini models.
    Lazy initializes the models to prevent startup crashes.
    """
    def __init__(self):
        self._flash_model = None
        self._pro_model = None
        self._initialized = False

    def _init(self):
        if not self._initialized:
            try:
                init_vertex_ai()
                self._flash_model = GenerativeModel("gemini-1.5-flash")
                self._pro_model = GenerativeModel("gemini-1.5-pro")
                self._initialized = True
            except Exception as e:
                # Log error but don't crash the whole app on import
                print(f"Vertex AI initialization failed: {e}")

    async def get_model(self, model_type: str = "flash") -> GenerativeModel:
        """Returns the requested model instance."""
        self._init()
        if model_type == "pro":
            return self._pro_model
        return self._flash_model

vertex_client = VertexAIClient()
