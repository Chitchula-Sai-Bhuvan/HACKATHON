
"""
REUSABLE TOOL: CSV Operations
1. Read CSV safely
2. Update rows
3. Merge line numbers if needed
"""

import csv
import os
from abh.configs.paths_config import OUTPUT_CSV
from abh.schemas.bug_object_schema import BugObject
from typing import List

def read_existing_bugs() -> List[dict]:
    """Load existing bug rows as dicts from output.csv."""
    if not os.path.exists(OUTPUT_CSV):
        return []
    
    bugs = []
    with open(OUTPUT_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bugs.append(row)
    return bugs

def write_bugs_to_file(bugs: List[BugObject], overwrite: bool = False):
    """Write or append bugs to output.csv."""
    fieldnames = [
        "bug_id", "language", "bug_type", "lines", "bug_signature",
        "explanation", "context", "source", "timestamp"
    ]
    
    file_exists = os.path.isfile(OUTPUT_CSV)
    mode = 'w' if overwrite or not file_exists else 'a'
    
    with open(OUTPUT_CSV, mode=mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if mode == 'w' or not file_exists:
            writer.writeheader()
        
        for bug in bugs:
            # Flatten bug_line_numbers to comma-separated string
            line_str = ",".join(map(str, bug.bug_line_numbers))
            
            writer.writerow({
                "bug_id": bug.bug_id,
                "language": bug.language,
                "bug_type": bug.bug_type,
                "lines": line_str,
                "bug_signature": bug.bug_signature,
                "explanation": bug.explanation,
                "context": bug.context,
                "source": bug.source,
                "timestamp": bug.timestamp
            })

def update_bug_in_file(bug_id: str, merged_lines: List[int]):
    """Update an existing bug's lines in output.csv."""
    rows = read_existing_bugs()
    updated = False
    
    for row in rows:
        if row['bug_id'] == bug_id:
            row['lines'] = ",".join(map(str, merged_lines))
            updated = True
            break
    
    if updated:
        fieldnames = [
            "bug_id", "language", "bug_type", "lines", "bug_signature",
            "explanation", "context", "source", "timestamp"
        ]
        with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return True
    return False
