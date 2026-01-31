
"""
ORCHESTRATION FLOW:
1. Receive user code file
2. Call Bug Locator Agent
3. Call Bug Explainer Agent
4. Call Bug Memory Agent
5. Call CSV Writer Agent
6. Return final bug report
"""

from ..agents.bug_locator_agent import BugLocatorAgent
from ..agents.bug_explainer_agent import BugExplainerAgent
from ..agents.bug_memory_agent import BugMemoryAgent
from ..agents.csv_writer_agent import CSVWriterAgent
from ..configs.paths_config import OUTPUT_CSV

class AgentOrchestrator:
    """Orchestrates the workflow between different agents."""
    
    def __init__(self):
        self.locator = BugLocatorAgent()
        self.explainer = BugExplainerAgent()
        self.memory = BugMemoryAgent()
        self.writer = CSVWriterAgent()

    async def run_pipeline(self, target_file_path: str):
        print(f"--- Starting Analysis for {target_file_path} ---")
        
        # 1. Read input
        with open(target_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 2. Locate
        bugs = await self.locator.locate_bug(target_file_path, content)
        
        # 3. Explain and Check Memory
        final_bugs = []
        for bug in bugs:
            # Enrich with knowledge
            bug = await self.explainer.explain_bug(bug)
            # Check short-term memory (duplicates)
            bug = await self.memory.check_short_term_memory(bug)
            final_bugs.append(bug)

        # 4. Report
        await self.writer.finalize_report(final_bugs)
        
        print(f"--- Analysis Complete. Results in {OUTPUT_CSV} ---")
        return final_bugs
