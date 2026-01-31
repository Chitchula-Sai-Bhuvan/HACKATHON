
"""
COMMANDS TO IMPLEMENT:
1. Accept user code file as input
2. Parse code line-by-line
3. Compare against known correct patterns from vector DB (using BugExplainerAgent/MCP search)
4. Identify:
   - exact line number(s)
   - buggy snippet
   - language
   - bug type
5. Output a Bug Object (partial)
"""

from ..schemas.bug_object_schema import BugObject
from typing import List

class BugLocatorAgent:
    """Agent responsible for identifying potential bugs in code."""
    
    async def locate_bug(self, file_path: str, code_content: str) -> List[BugObject]:
        # TODO: Implement line-by-line parsing
        # TODO: Detect potential buggy snippets
        # TODO: Initialize BugObject with line numbers, snippet, etc.
        return []
