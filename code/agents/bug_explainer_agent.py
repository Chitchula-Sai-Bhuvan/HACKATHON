import json
import re
from abh.agents.base_agent import BaseAgent
from typing import Optional, Dict
from abh.schemas.bug_object_schema import BugObject
from abh.tools.mcp_tools import search_knowledge_base

class BugExplainerAgent(BaseAgent):
    """
    Agent responsible for explaining why a piece of code is buggy by grounding
    the explanation in previously ingested bug knowledge.
    """
    
    def __init__(self):
        super().__init__("BugExplainerAgent")

    # --- Agent Spec (Framework Definitions) ---
    ROLE = "Explain why the already-located bug is wrong using grounded knowledge."
    SYSTEM_PROMPT = """
    You are the Bug Explainer Agent.
    Your responsibility is to explain why a bug is incorrect.
    Rules:
    - You MUST NOT locate bugs or modify line numbers.
    - You MUST NOT invent explanations.
    - Ground explanations strictly in retrieved [BUG_KNOWLEDGE].
    - Use 'search_documents' to find the specific knowledge block.
    - If no relevant knowledge is found, explicitly say so.
    """
    ALLOWED_TOOLS = ["search_documents"]
    # ------------------------------------------

    SIMILARITY_THRESHOLD = 0.65

    async def explain_bug(self, bug_obj: BugObject) -> BugObject:
        self.initialize_reasoning()
        """
        Takes a localized BugObject and enriches it with a grounded explanation.
        """
        print(f"[BugExplainerAgent] Explaining bug: {bug_obj.bug_signature}...")
        
        # Phase 1: Query Construction
        # Use signature, type, and snippet to build a focused query
        query = f"[BUG_KNOWLEDGE] {bug_obj.language} {bug_obj.bug_type} {bug_obj.bug_signature}"
        
        try:
            # Tool Enforcement
            self.enforce_tool("search_documents")
            # Phase 2: Knowledge Retrieval
            results = await search_knowledge_base(query)
            
            # Phase 3: Evidence Selection
            best_knowledge = None
            max_score = 0.0
            relevant_knowledge_items = []
            
            for item in results.content:
                try:
                    data = json.loads(item.text)
                    matches = data if isinstance(data, list) else [data]
                    for res in matches:
                        score = res.get("score", 0.0)
                        k_text = res.get("text", "")
                        
                        # Verify it's actually bug knowledge and relevant
                        if "[BUG_KNOWLEDGE]" in k_text and score >= self.SIMILARITY_THRESHOLD:
                            if bug_obj.bug_signature in k_text:
                                score += 0.2 # Boost for exact signature match
                            relevant_knowledge_items.append({"text": k_text, "score": score})
                except json.JSONDecodeError:
                    continue
            
            # Sort by score and take top N for LLM context
            relevant_knowledge_items.sort(key=lambda x: x["score"], reverse=True)
            
            # Prepare default retrieval-based results as fallback
            fallback_explanation = "No specific explanation found in knowledge base."
            fallback_summary = "Potential bug detected."
            
            if relevant_knowledge_items:
                fallback_explanation = relevant_knowledge_items[0]["text"]
                fallback_explanation = re.sub(r"^\[BUG_KNOWLEDGE\].*?Content:\s*", "", fallback_explanation, flags=re.DOTALL)
                fallback_summary = fallback_explanation.split('.')[0] + "."
                if len(fallback_summary) > 100:
                    fallback_summary = fallback_summary[:97] + "..."

            # Phase 4: Generative Synthesis
            print(f"🧠 [BugExplainerAgent] Synthesizing explanation using generative brain...")
            
            # Prepare context for the LLM
            context_blocks = "\n---\n".join([f"Source: knowledge_base\nContent: {item['text']}" for item in relevant_knowledge_items[:3]])
            
            if not context_blocks:
                bug_obj.explanation = fallback_explanation
                bug_obj.summary = fallback_summary
                bug_obj.source = "vector_db"
                return bug_obj

            llm_prompt = f"""
            Analyze the following bug in {bug_obj.language} code.
            
            RETRIEVED KNOWLEDGE:
            {context_blocks}
            
            BUG SIGNATURE: {bug_obj.bug_signature}
            BUG TYPE: {bug_obj.bug_type}
            AFFECTED LINES: {bug_obj.bug_line_numbers}
            
            TASK:
            1. Provide a detailed 2-3 sentence explanation of WHY this code is incorrect based on the retrieved knowledge.
            2. Provide a concise 1-line summary of the bug.
            
            OUTPUT FORMAT:
            SUMMARY: <1-line-summary>
            EXPLANATION: <detailed-explanation>
            """
            
            try:
                llm_response = await self.call_llm(llm_prompt)
                
                # Parse LLM response
                summary = None
                explanation = None
                
                summary_match = re.search(r"SUMMARY:\s*(.*)", llm_response, re.IGNORECASE)
                if summary_match:
                    summary = summary_match.group(1).strip()
                
                explanation_match = re.search(r"EXPLANATION:\s*(.*)", llm_response, re.IGNORECASE | re.DOTALL)
                if explanation_match:
                    explanation = explanation_match.group(1).strip()

                if summary and explanation and "Error" not in llm_response:
                    bug_obj.explanation = explanation
                    bug_obj.summary = summary
                    bug_obj.source = "generative_ai"
                    print(f"Successfully synthesized explanation using generative brain.")
                else:
                    raise ValueError("LLM returned malformed or error response.")
                    
            except Exception as e:
                print(f"⚠️ [BugExplainerAgent] Generative synthesis failed, falling back to retrieval: {e}")
                bug_obj.explanation = fallback_explanation
                bug_obj.summary = fallback_summary
                bug_obj.source = "vector_db"
            
            return bug_obj
            
        except Exception as e:
            print(f"❌ [BugExplainerAgent] Critical Error: {e}")
            bug_obj.explanation = f"Error during processing: {str(e)}"
            bug_obj.summary = "Error during reasoning."
            return bug_obj

    def _extract_field(self, text: str, field_name: str) -> str:
        """Helper to extract named fields from [BUG_KNOWLEDGE] block."""
        pattern = rf"{field_name}:\n(.*?)(?=\n\n|\n[A-Z][a-z ]+:|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
