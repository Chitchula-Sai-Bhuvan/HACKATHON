
"""
CSV WRITER AGENT:
Responsibility: Finalizing the report and writing to disk.
Action: Uses csv_tool to save consolidated results.
"""

from typing import List, Dict
from abh.schemas.bug_object_schema import BugObject
from abh.tools.csv_tool import write_bugs_to_file, update_bug_in_file

from abh.agents.base_agent import BaseAgent

class CSVWriterAgent(BaseAgent):
    """Agent responsible for writing results to the output CSV."""
    
    def __init__(self):
        super().__init__("CSVWriterAgent")

    # --- Agent Spec (Framework Definitions) ---
    ROLE = "Finalize the bug report and persist it to disk."
    SYSTEM_PROMPT = """
    You are the CSV Writer Agent.
    Your responsibility is to format and save the final bug analysis.
    Rules:
    - Only write unique-non-duplicate bugs.
    - Ensure all required fields (lines, signatures, explanations) are present.
    - Never modify the content of the analysis.
    """
    ALLOWED_TOOLS = ["csv_tool"]
    # ------------------------------------------
    
    async def finalize_report(self, decisions: List[Dict]):
        self.initialize_reasoning()
        """
        Takes the final list of decisions from Memory Agent
        and applies them to the CSV.
        """
        print(f"[CSVWriterAgent] Finalizing report with {len(decisions)} decision(s)...")
        
        # Tool Enforcement
        self.enforce_tool("csv_tool")
        
        new_bugs = []
        for dec in decisions:
            action = dec.get("action")
            bug_id = dec.get("bug_id")
            merged_lines = dec.get("merged_lines", [])
            bug_obj = dec.get("record")
            
            if action == "update":
                print(f"Updating existing bug {bug_id} with merged lines...")
                update_bug_in_file(bug_id, merged_lines)
            elif action == "create":
                print(f"Creating new bug entry for {bug_id}...")
                new_bugs.append(bug_obj)
        
        if new_bugs:
            write_bugs_to_file(new_bugs)
            print(f"Successfully wrote {len(new_bugs)} new bug(s) to output.csv")
        
        print("Final report persistence complete.")
