import asyncio
from typing import List, Dict
from abh.agents.base_agent import BaseAgent
from abh.schemas.bug_object_schema import BugObject
from abh.tools.code_parser_tool import detect_language, split_to_numbered_lines
from abh.tools.mcp_tools import search_knowledge_base

class BugLocatorAgent(BaseAgent):
    """
    The Bug Locator Agent determines WHERE a bug exists in the user's code.
    Identifies exact line numbers by matching local code patterns against vector memory.
    """

    def __init__(self):
        super().__init__("BugLocatorAgent")

    # --- Agent Spec (Framework Definitions) ---
    ROLE = "Identify exact line numbers of potential bugs by matching code patterns against vector memory."
    SYSTEM_PROMPT = """
    You are the Bug Locator Agent.
    Your responsibility is to identify WHERE a bug might exist.
    Rules:
    - Focus ONLY on localization (line numbers).
    - Do NOT explain why it is a bug.
    - Use 'search_documents' to find similar historical patterns.
    - Consolidate detections by semantic signature.
    - Return only the most relevant Primary Bug.
    """
    ALLOWED_TOOLS = ["search_documents"]
    # ------------------------------------------

    # Stage 1: Suspect Indicators
    SUSPICIOUS_KEYWORDS = [
        "smartVec", "vecEditMode", "copyLabel", "execute", 
        "RDI_BEGIN", "RDI_END", "protocol", "pin", "burst",
        "iClamp", "vForce", "vMeas", "iMeas", "emap", "pmux", "cogo"
    ]

    SIMILARITY_THRESHOLD = 0.65

    async def locate_bug(self, file_path: str, code_content: str) -> List[BugObject]:
        self.initialize_reasoning()
        print(f"🔍 [BugLocatorAgent] Analyzing {file_path}...")
        
        language = detect_language(file_path)
        numbered_lines = split_to_numbered_lines(code_content)
        
        # Phase A: Detection
        candidates = []
        for line_no, content in numbered_lines:
            stripped = content.strip()
            if not stripped or stripped.startswith(("//", "/*", "#")):
                continue
            if any(kw in stripped for kw in self.SUSPICIOUS_KEYWORDS):
                candidates.append({"line_no": line_no, "content": stripped})
        
        print(f"Found {len(candidates)} candidate lines for verification.")

        raw_detections = []
        import json
        import re

        for cand in candidates:
            query = f"{language} bug related to: {cand['content']}"
            try:
                # Tool Enforcement
                self.enforce_tool("search_documents")
                results = await search_knowledge_base(query)
                for item in results.content:
                    try:
                        data = json.loads(item.text)
                        matches = data if isinstance(data, list) else [data]
                        for res in matches:
                            score = res.get("score", 0.0)
                            if score >= self.SIMILARITY_THRESHOLD:
                                k_text = res.get("text", "")
                                
                                # Extract Bug Signature and Type from [BUG_KNOWLEDGE]
                                b_type = "Potential Bug"
                                b_sig = "Unknown Signature"
                                
                                type_match = re.search(r"Bug Type:\s*(.*)", k_text)
                                if type_match:
                                    b_type = type_match.group(1).strip()
                                
                                sig_match = re.search(r"Bug Signature:\s*(.*)", k_text)
                                if sig_match:
                                    b_sig = sig_match.group(1).strip()
                                
                                raw_detections.append({
                                    "line_no": cand['line_no'],
                                    "score": score,
                                    "bug_type": b_type,
                                    "bug_signature": b_sig,
                                    "knowledge_text": k_text
                                })
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                print(f"Error searching for line {cand['line_no']}: {e}")

        # Phase B: Consolidation (Bug Identity Resolution)
        # Group by signature
        grouped_data: Dict[str, List[Dict]] = {}
        for det in raw_detections:
            sig = det['bug_signature']
            grouped_data.setdefault(sig, []).append(det)

        final_bugs = []
        for sig, items in grouped_data.items():
            # Pick representative detection (highest confidence)
            best = max(items, key=lambda x: x["score"])
            
            # Merge line numbers
            lines = sorted(list(set(d["line_no"] for d in items)))
            
            # Compute Relevance Score
            # relevance = confidence + 0.05 * number_of_lines
            relevance = best['score'] + (0.05 * len(lines))
            
            bug = BugObject(
                bug_id="LOCATED",
                language=language,
                bug_type=best['bug_type'],
                bug_line_numbers=lines,
                buggy_code_snippet=best['knowledge_text'][:200] + "...", 
                source="vector_db",
                similarity_score=relevance, # Using combined relevance for ranking
                context=best['knowledge_text'], 
                bug_signature=sig
            )
            final_bugs.append(bug)

        # Sort by relevance and pick TOP 1
        final_bugs.sort(key=lambda b: b.similarity_score or 0.0, reverse=True)
        
        primary_bug = final_bugs[:1] # Returning only primary for now
        
        print(f"Consolidation complete. Identified {len(final_bugs)} potential, selecting {len(primary_bug)} Primary Bug.")
        return primary_bug
