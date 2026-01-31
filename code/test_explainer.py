
import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from abh.agents.bug_explainer_agent import BugExplainerAgent
from abh.schemas.bug_object_schema import BugObject

async def test_explainer():
    print("🚀 Testing BugExplainerAgent with a localized bug...")
    
    # Simulate a bug object coming from BugLocatorAgent
    locator_output = BugObject(
        bug_id="LOCATED",
        language="C++",
        bug_type="Mode Configuration Mismatch",
        bug_signature="smartVec",
        bug_line_numbers=[4, 5, 10],
        buggy_code_snippet="rdi.smartVec().vecEditMode(TA::VECD);",
        similarity_score=0.85
    )
    
    explainer = BugExplainerAgent()
    enriched_bug = await explainer.explain_bug(locator_output)
    
    print("\n--- Explanation Summary ---")
    print(f"Bug Type: {enriched_bug.bug_type}")
    print(f"Signature: {enriched_bug.bug_signature}")
    print(f"Lines: {enriched_bug.bug_line_numbers}")
    print(f"Explanation: {enriched_bug.explanation}")
    print(f"Correct Pattern: {enriched_bug.correct_code_snippet}")
    print(f"Context: {enriched_bug.context}")
    print(f"Source: {enriched_bug.source}")
    print("-" * 20)
    
    if enriched_bug.explanation and enriched_bug.source == "vector_db":
        print("\n✅ BugExplainerAgent test PASSED (Grounded explanation retrieved).")
    else:
        print("\n❌ BugExplainerAgent test FAILED (No grounded explanation).")

if __name__ == "__main__":
    asyncio.run(test_explainer())
