
"""
COMMANDS TO IMPLEMENT:
1. Check if output.csv exists
2. If exists:
   - Compare new bug with existing bugs
   - Use similarity checker tool
3. If same bug exists:
   - Append new line number to existing row
4. If not:
   - Mark bug as NEW
"""

from ..schemas.bug_object_schema import BugObject
from ..tools.similarity_checker_tool import calculate_similarity
from ..tools.csv_tool import read_existing_bugs
import os

class BugMemoryAgent:
    """Agent responsible for retrieving similar past bugs from short-term memory (shared output)."""
    
    async def check_short_term_memory(self, new_bug: BugObject) -> BugObject:
        # TODO: Load bugs from output.csv
        # TODO: Use similarity tool to find duplicates
        # TODO: Handle NEW vs EXISTING state
        return new_bug
