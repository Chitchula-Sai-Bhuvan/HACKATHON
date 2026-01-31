
"""
COMMANDS TO IMPLEMENT:
1. Accept code file path from user
2. Trigger agent orchestrator
3. Print final summary
"""

import sys
import asyncio
import os
from code.orchestration.agent_orchestrator import AgentOrchestrator

async def main():
    if len(sys.argv) < 2:
        print("Usage: python code/main.py <path_to_code_file>")
        return

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    print("Agentic Bug Hunter Initializing...")
    orchestrator = AgentOrchestrator()
    try:
        await orchestrator.run_pipeline(file_path)
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
