
import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from abh.agents.bug_locator_agent import BugLocatorAgent

async def test_locator():
    print("🚀 Testing BugLocatorAgent with known buggy code...")
    
    # Example code containing a known bug from sample.csv (ID 16)
    buggy_cpp_code = """
#include <iostream>
void test_rdi() {
    rdi.smartVec().vecEditMode(TA::VECD);
    RDI_BEGIN();
    rdi.smartVec()
        .label("sLabel").copyLabel(false).pin(A)
        .writeData("rt", 8, 0)
        .execute();
    RDI_END();
}
"""
    
    locator = BugLocatorAgent()
    bugs = await locator.locate_bug("test_file.cpp", buggy_cpp_code)
    
    print("\n--- Detection Summary ---")
    for i, bug in enumerate(bugs):
        print(f"Bug {i+1}:")
        print(f" - Type: {bug.bug_type}")
        print(f" - Lines: {bug.bug_line_numbers}")
        print(f" - Snippet: {bug.buggy_code_snippet}")
        print(f" - Confidence: {bug.similarity_score}")
        print("-" * 20)
    
    if len(bugs) > 0:
        print("\n✅ BugLocatorAgent test PASSED.")
    else:
        print("\n❌ BugLocatorAgent test FAILED (No bugs detected).")

if __name__ == "__main__":
    asyncio.run(test_locator())
