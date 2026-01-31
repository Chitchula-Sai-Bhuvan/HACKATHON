
import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from abh.tools.mcp_tools import search_knowledge_base

async def verify_retrieval():
    print("🔍 Verifying retrieval of structured [BUG_KNOWLEDGE]...")
    query = "rdi.smartVec label copyLabel"
    try:
        result = await search_knowledge_base(query)
        print("\n--- Search Results ---")
        for i, item in enumerate(result.content):
            print(f"Result {i+1}:")
            print(item.text[:1000])
            print("-" * 20)
        
        if any("[BUG_KNOWLEDGE]" in item.text for item in result.content):
            print("\n✅ Verification SUCCESS: Found structured bug knowledge.")
        else:
            print("\n⚠️ Verification WARNING: Found results but they don't seem to use the new [BUG_KNOWLEDGE] template.")
            print("Did you restart the mcp_server.py process?")
    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")
        print("Make sure server/mcp_server.py is running on port 8003.")

if __name__ == "__main__":
    asyncio.run(verify_retrieval())
