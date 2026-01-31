
"""
COMMANDS TO IMPLEMENT:
1. Take Bug Object from Bug Locator Agent
2. Call MCP tool: search_documents(query)
3. Retrieve similar historical bugs + documentation
4. Generate:
   - explanation
   - context
   - corrected code reference
5. Update Bug Object
"""

from ..schemas.bug_object_schema import BugObject
from ..tools.mcp_tools import search_knowledge_base

class BugExplainerAgent:
    """Agent responsible for explaining why a piece of code is buggy."""
    
    async def explain_bug(self, bug_obj: BugObject) -> BugObject:
        # TODO: Generate a search query from the buggy snippet
        # TODO: Call search_knowledge_base via MCP
        # TODO: Synthesize results into explanation and corrected code
        return bug_obj
