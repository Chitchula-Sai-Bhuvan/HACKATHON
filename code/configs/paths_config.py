
import os
from pathlib import Path

# Base project directory
# Since this file is in code/configs/paths_config.py, we need to go up 2 levels to get to project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Input/Output paths
SAMPLES_CSV = BASE_DIR / "samples.csv"
# The user wants output.csv in the root
OUTPUT_CSV = BASE_DIR / "output.csv"

# Server paths
SERVER_DIR = BASE_DIR / "server"
STORAGE_DIR = SERVER_DIR / "storage"
EMBEDDING_MODEL_DIR = SERVER_DIR / "embedding_model"

# MCP Config
MCP_SERVER_URL = "http://localhost:8003/sse"
