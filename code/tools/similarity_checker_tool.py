
"""
REUSABLE TOOL: Similarity Checker
Uses bug signatures and types to determine if two BugObjects represent the same issue.
"""

from abh.schemas.bug_object_schema import BugObject

def calculate_similarity(bug_a: BugObject, bug_b: BugObject) -> float:
    """
    Returns a score from 0.0 to 1.0 representing how likely two bugs are identical.
    Primary identity is based on bug_signature.
    """
    if not bug_a.bug_signature or not bug_b.bug_signature:
        return 0.0
    
    # Exact signature match is 1.0
    if bug_a.bug_signature.lower() == bug_b.bug_signature.lower():
        return 1.0
    
    # Partial overlap in signature or same type
    score = 0.0
    if bug_a.bug_type == bug_b.bug_type:
        score += 0.3
    
    # Check for keyword overlap in signatures
    sig_a_words = set(bug_a.bug_signature.lower().split())
    sig_b_words = set(bug_b.bug_signature.lower().split())
    overlap = sig_a_words.intersection(sig_b_words)
    
    if overlap:
        score += 0.5 * (len(overlap) / max(len(sig_a_words), len(sig_b_words)))
        
    return min(1.0, score)

def compute_bug_signature(bug: BugObject) -> str:
    """
    Computes a deterministic string signature for a bug.
    Focuses on bug_type, correct_pattern, and key API tokens.
    """
    tokens = []
    if bug.bug_type:
        tokens.append(bug.bug_type.lower())
    
    if bug.correct_code_snippet:
        # Extract alphanumeric tokens from snippet
        import re
        snippet_tokens = re.findall(r'\w+', bug.correct_code_snippet.lower())
        tokens.extend(snippet_tokens[:10]) # Use first 10 tokens
        
    return "+".join(sorted(list(set(tokens))))
