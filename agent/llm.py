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
    """
    def __init__(self):
        init_vertex_ai()
        # Gemini 1.5 Flash for fast analysis and summarization
        self.flash_model = GenerativeModel("gemini-1.5-flash")
        # Gemini 1.5 Pro for complex reasoning and coding
        self.pro_model = GenerativeModel("gemini-1.5-pro")

    async def get_model(self, model_type: str = "flash") -> GenerativeModel:
        """Returns the requested model instance."""
        if model_type == "pro":
            return self.pro_model
        return self.flash_model

vertex_client = VertexAIClient()
