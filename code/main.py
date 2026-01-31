
"""
COMMANDS TO IMPLEMENT:
1. Accept code file path from user
2. Trigger agent orchestrator
3. Print final summary
"""

import sys
import asyncio
import os
from abh.orchestration.agent_orchestrator import AgentOrchestrator

async def main():
    if len(sys.argv) < 2:
        print("\n🤖 Agentic Bug Hunter - Home of Automated Code Safety")
        print("Usage: python abh/main.py <path_to_code_file>")
        print("Example: python abh/main.py test_file.cpp\n")
        return

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"❌ Error: File {file_path} not found.")
        return

    orchestrator = AgentOrchestrator()
    try:
        await orchestrator.run_pipeline(file_path)
    except Exception as e:
        print(f"💥 Critical Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
