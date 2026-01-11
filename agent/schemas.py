from typing import List, Optional
from pydantic import BaseModel, Field

class DiagnoseResponse(BaseModel):
    """Schema for the diagnosis of the CI/CD failure."""
    root_cause: str = Field(description="A concise summary of the root cause of the failure.")
    confidence: float = Field(description="Confidence score (0.0-1.0) indicating certainty about the diagnosis.")

class LocateResponse(BaseModel):
    """Schema for identifying the file to fix."""
    file_path: str = Field(description="The absolute file path that needs to be fixed. e.g. 'app/api/main.py'")

class FixResponse(BaseModel):
    """Schema for the fix implementation."""
    fixed_content: str = Field(description="The complete, corrected content of the file.")
    confidence: float = Field(description="Confidence score (0.0-1.0) indicating certainty that this fix works.")
    explanation: str = Field(description="A brief explanation of what was fixed and why.")

class ContextAnalysisResponse(BaseModel):
    """Schema for identifying related context files."""
    related_files: List[str] = Field(description="List of file paths that are related to the target file and root cause.")
