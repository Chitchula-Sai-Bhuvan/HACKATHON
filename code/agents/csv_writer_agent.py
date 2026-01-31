
"""
COMMANDS TO IMPLEMENT:
1. Create output.csv if missing
2. Follow CSV schema strictly
3. Write:
   - new bug rows
   - or update existing rows
4. Ensure no duplication of bug entries
"""

from ..schemas.bug_object_schema import BugObject
from ..tools.csv_tool import write_bug_to_file
from typing import List

class CSVWriterAgent:
    """Agent responsible for formatting and writing findings to CSV."""
    
    async def finalize_report(self, bugs: List[BugObject]):
        # TODO: Iterate through bugs and write via csv_tool
        pass
