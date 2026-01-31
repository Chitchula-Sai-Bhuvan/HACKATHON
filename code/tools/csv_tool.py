
"""
COMMANDS TO IMPLEMENT:
1. Read CSV safely
2. Update rows
3. Merge line numbers if needed
"""

import csv
import os
from ..configs.paths_config import OUTPUT_CSV
from ..schemas.bug_object_schema import BugObject
from typing import List

def read_existing_bugs() -> List[BugObject]:
    # TODO: Load from output.csv if it exists
    return []

def write_bug_to_file(bug: BugObject):
    # TODO: Implement append or update-existing logic
    pass
