
"""
COMMANDS TO IMPLEMENT:
1. Wrapper functions for:
   - search_documents
   - list_files_and_folders
2. Handle MCP server connection
3. Ensure retry + timeout handling
"""

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from ..configs.paths_config import MCP_SERVER_URL

async def search_knowledge_base(query: str):
    """MCP Wrapper: search_documents."""
    # TODO: Implement connection pooling or robust session handling
    # TODO: Add retry logic
    async with sse_client(MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool("search_documents", arguments={"query": query})

async def list_mcp_files():
    """MCP Wrapper: list_files_and_folders."""
    async with sse_client(MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool("list_files_and_folders", arguments={})
