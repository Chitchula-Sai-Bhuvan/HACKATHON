
import asyncio
import sys
import os
import csv

# Add project root to sys.path
sys.path.append(os.getcwd())

from abh.agents.bug_memory_agent import BugMemoryAgent
from abh.schemas.bug_object_schema import BugObject
from abh.configs.paths_config import OUTPUT_CSV

async def test_memory():
    print("🚀 Testing BugMemoryAgent...")
    
    # 1. Ensure a dummy output.csv exists
    fieldnames = ["bug_id", "language", "bug_type", "lines", "explanation", "context", "source", "timestamp"]
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            "bug_id": "smartVec", # signature stored in bug_id for comparison
            "language": "C++",
            "bug_type": "Mode Configuration Mismatch",
            "lines": "5,6",
            "explanation": "Existing explanation",
            "context": "Existing context",
            "source": "vector_db",
            "timestamp": "2026-01-31T12:00:00"
        })
    
    # 2. Test duplicate detection
    new_bug = BugObject(
        bug_id="LOCATED",
        language="C++",
        bug_type="Mode Configuration Mismatch",
        bug_signature="smartVec",
        bug_line_numbers=[10, 11],
        buggy_code_snippet="rdi.smartVec()...",
        similarity_score=0.9
    )
    
    agent = BugMemoryAgent()
    checked_bug = await agent.check_short_term_memory(new_bug)
    
    if checked_bug.bug_id == "DUPLICATE":
        print("\n✅ BugMemoryAgent detected DUPLICATE successfully.")
    else:
        print("\n❌ BugMemoryAgent FAILED to detect duplicate.")

    # 3. Test new bug (no duplicate)
    unique_bug = BugObject(
        bug_id="LOCATED",
        language="C++",
        bug_type="API Misuse",
        bug_signature="iClamp mismatch",
        bug_line_numbers=[20],
        buggy_code_snippet="rdi.dc().iClamp()...",
        similarity_score=0.8
    )
    
    checked_bug_2 = await agent.check_short_term_memory(unique_bug)
    if checked_bug_2.bug_id == "LOCATED":
        print("\n✅ BugMemoryAgent confirmed UNIQUE bug successfully.")
    else:
        print("\n❌ BugMemoryAgent incorrectly flagged UNIQUE bug as duplicate.")

if __name__ == "__main__":
    asyncio.run(test_memory())
