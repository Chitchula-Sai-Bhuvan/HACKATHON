
from pydantic import BaseModel, Field
from typing import List
from .bug_object_schema import BugObject

class CSVSchema(BaseModel):
    """Schema for the CSV output format."""
    # Matches output.csv columns: bug_id, language, bug_type, lines, explanation, context, source
    bugs: List[BugObject]
