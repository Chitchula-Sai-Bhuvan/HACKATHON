
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BugObject(BaseModel):
    """Schema for a detections/Bug Object (Core Unit)."""
    bug_id: str = Field(..., description="Hash or unique ID for the bug pattern")
    language: str = Field(..., description="python / cpp / c")
    bug_type: str = Field(..., description="API misuse / logic error / order violation")
    bug_line_numbers: List[int] = Field(..., description="Exact line numbers in the file")
    buggy_code_snippet: str = Field(..., description="The original buggy code chunk")
    correct_code_snippet: Optional[str] = Field(None, description="The corrected code reference")
    context: Optional[str] = Field(None, description="The code context / block")
    explanation: Optional[str] = Field(None, description="Detailed explanation of the bug")
    source: str = Field(default="llm", description="vector_db | llm")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    similarity_score: Optional[float] = Field(None, description="Score if retrieved from memory")
