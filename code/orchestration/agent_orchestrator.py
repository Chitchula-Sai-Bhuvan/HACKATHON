
"""
AGENT ORCHESTRATOR:
The "Brain" of the system.
Sequence:
1. Locate Agent -> Finding potential bug spots (Consolidated & Ranked)
2. Explainer Agent -> Grounding bug in knowledge base
3. Memory Agent -> Checking for duplicates in output.csv
4. Writer Agent -> Saving the final report
"""

from abh.agents.bug_locator_agent import BugLocatorAgent
from abh.agents.bug_explainer_agent import BugExplainerAgent
from abh.agents.bug_memory_agent import BugMemoryAgent
from abh.agents.csv_writer_agent import CSVWriterAgent
from abh.configs.paths_config import OUTPUT_CSV

class AgentOrchestrator:
    """Orchestrates the workflow between different agents."""
    
    def __init__(self):
        self.locator = BugLocatorAgent()
        self.explainer = BugExplainerAgent()
        self.memory = BugMemoryAgent()
        self.writer = CSVWriterAgent()

    async def run_pipeline(self, target_file_path: str):
        print(f"\n🚀 --- Starting Agentic Analysis for: {target_file_path} ---")
        
        # 1. Read input
        if not target_file_path.endswith(('.cpp', '.c', '.h', '.py')):
            print(f"⚠️ Warning: {target_file_path} has an unusual extension, detection might be less accurate.")
            
        with open(target_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 2. LOCATE: Identify where the bug is
        print("\n[Step 1/4] Locating potential bug sites...")
        # (Input validation optional for raw content)
        bugs = await self.locator.locate_bug(target_file_path, content)
        # BUG: Output of locator is List[BugObject], validate if needed
        # We assume locator internal consolidation returned high quality BugObjects
        
        if not bugs:
            print("✅ No known bug patterns localized. Your code seems clean against our DB!")
            return []

        # 3. EXPLAIN & CHECK MEMORY
        memory_decisions = []
        
        for i, bug in enumerate(bugs):
            print(f"\n--- Processing Detection {i+1}/{len(bugs)} ---")
            
            # 3a. EXPLAIN: Ground the bug in knowledge
            print("[Step 2/4] Grounding bug in Knowledge Base...")
            # Input Validation (BugObject)
            from abh.schemas.bug_object_schema import BugObject
            self.explainer.validate_input(bug, BugObject)
            
            bug = await self.explainer.explain_bug(bug)
            # Output Validation
            self.explainer.validate_output(bug, BugObject)
            
            # 3b. MEMORY: Check if we've already reported this
            print("[Step 3/4] Checking Short-Term Memory (Identity Management)...")
            self.memory.validate_input(bug, BugObject)
            
            decision = await self.memory.check_short_term_memory(bug)
            # decision is a dict, we could define a DecisionSchema if we wanted
            memory_decisions.append(decision)

        # 4. REPORT: Write to CSV
        print("\n[Step 4/4] Finalizing report...")
        await self.writer.finalize_report(memory_decisions)
        
        print(f"\n✨ --- Analysis Complete! Results saved in {OUTPUT_CSV} --- ✨")
        return [d['record'] for d in memory_decisions]
