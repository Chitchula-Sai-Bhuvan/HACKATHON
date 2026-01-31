
"""
BUG MEMORY AGENT:
Responsibility: Prevents reporting the SAME bug twice (Short-term memory).
Action: Checks output.csv against current detection.
"""

import hashlib
from typing import Optional, Dict, List
from abh.schemas.bug_object_schema import BugObject
from abh.tools.csv_tool import read_existing_bugs
from abh.tools.similarity_checker_tool import calculate_similarity, compute_bug_signature

from abh.agents.base_agent import BaseAgent

class BugMemoryAgent(BaseAgent):
    """Agent responsible for deciding how a bug should be remembered."""
    
    def __init__(self):
        super().__init__("BugMemoryAgent")

    # --- Agent Spec (Framework Definitions) ---
    ROLE = "Prevent duplicate bug reporting by checking against short-term memory (output.csv)."
    SYSTEM_PROMPT = """
    You are the Bug Memory Agent.
    Your responsibility is to detect if a bug has already been reported.
    Rules:
    - Compare incoming bug signature against existing signatures in output.csv.
    - Use 'calculate_similarity' to decide if it's a duplicate.
    - Flag duplicates for the orchestrator.
    """
    ALLOWED_TOOLS = ["read_csv_snapshot", "compute_bug_signature", "compare_signatures"]
    # ------------------------------------------

    SIMILARITY_MATCH_THRESHOLD = 0.85

    async def check_short_term_memory(self, bug_obj: BugObject) -> Dict:
        self.initialize_reasoning()
        """
        Decides how the bug should be remembered.
        Returns a decision object with action: 'create' or 'update'.
        """
        print(f"🧠 [BugMemoryAgent] Decision phase for: {bug_obj.bug_signature}...")
        
        # Phase 1: Normalize (Identity)
        self.enforce_tool("compute_bug_signature")
        stable_signature = compute_bug_signature(bug_obj)
        bug_obj.bug_signature = stable_signature
        
        # Phase 2: Load Memory Snapshot
        self.enforce_tool("read_csv_snapshot")
        existing_rows = read_existing_bugs()
        
        # Phase 3 & 4: Duplicate Detection & Decision
        for row in existing_rows:
            # Reconstruct for similarity check
            existing_bug = BugObject(
                bug_id=row.get('bug_id', 'EXISTING'),
                language=row.get('language', 'Unknown'),
                bug_type=row.get('bug_type', 'Unknown'),
                bug_line_numbers=[int(x) for x in row.get('lines', '').split(',') if x.strip()],
                buggy_code_snippet="",
                bug_signature=row.get('bug_signature', '')
            )
            
            similarity = calculate_similarity(bug_obj, existing_bug)
            
            if similarity >= self.SIMILARITY_MATCH_THRESHOLD:
                # Case A: Same bug exists
                merged = sorted(list(set(existing_bug.bug_line_numbers) | set(bug_obj.bug_line_numbers)))
                print(f"Detected DUPLICATE. Action: UPDATE (Similarity: {similarity:.2f})")
                return {
                    "action": "update",
                    "bug_id": existing_bug.bug_id,
                    "merged_lines": merged,
                    "record": bug_obj
                }

        # Case B: New bug
        # Generate new bug_id (hash of signature)
        new_id = hashlib.md5(stable_signature.encode()).hexdigest()[:8]
        bug_obj.bug_id = new_id
        print(f"New bug pattern. Action: CREATE (ID: {new_id})")
        return {
            "action": "create",
            "bug_id": new_id,
            "merged_lines": bug_obj.bug_line_numbers,
            "record": bug_obj
        }
