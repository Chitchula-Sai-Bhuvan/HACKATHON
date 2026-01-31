
"""
REUSABLE TOOL: Code Parser
1. Detect programming language
2. Split code into numbered lines
3. Extract function / block context
"""

import os
from typing import List, Tuple

def detect_language(file_path: str) -> str:
    """Detect based on extension."""
    suffix = os.path.splitext(file_path)[1].lower()
    mapping = {
        ".py": "Python",
        ".cpp": "C++",
        ".h": "C++",
        ".c": "C",
        ".java": "Java",
        ".js": "JavaScript"
    }
    return mapping.get(suffix, "Unknown")

def split_to_numbered_lines(code: str) -> List[Tuple[int, str]]:
    """Return list of (line_number, content) tuples."""
    lines = code.splitlines()
    return [(i + 1, line) for i, line in enumerate(lines)]

def get_block_context(code: str, target_line: int, window: int = 5) -> str:
    """Extract block around a line for context."""
    lines = code.splitlines()
    start = max(0, target_line - window - 1)
    end = min(len(lines), target_line + window)
    return "\n".join(lines[start:end])
