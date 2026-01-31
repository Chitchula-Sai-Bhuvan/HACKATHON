
import os
import csv
import sys
from pathlib import Path

try:
    from llama_index.core import Document, VectorStoreIndex, Settings, StorageContext
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
except ImportError:
    print("Error: llama-index not installed. Please install requirements.txt")
    sys.exit(1)

# Import paths from config
# Given the structure: code/tools/ingest_v2.py
# We need to import from code.configs.paths_config
# Since we are running from project root, we can use absolute imports
try:
    from abh.configs.paths_config import SAMPLES_CSV, STORAGE_DIR, EMBEDDING_MODEL_DIR
except ImportError:
    # Fallback for local execution if sys.path is not setup
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    SAMPLES_CSV = BASE_DIR / "samples.csv"
    STORAGE_DIR = BASE_DIR / "server" / "storage"
    EMBEDDING_MODEL_DIR = BASE_DIR / "server" / "embedding_model"

def format_bug_knowledge(row):
    """
    Formats a CSV row into the [BUG_KNOWLEDGE] template.
    """
    bug_id = row.get('ID', 'UNKNOWN')
    explanation = row.get('Explanation', '').strip()
    context = row.get('Context', '').strip()
    buggy_code = row.get('Code', '').strip()
    correct_code = row.get('Correct Code', '').strip()
    
    # Inferred fields
    language = "C++"  # Default for Infineon RDI
    
    # Simple bug type inference
    bug_type = "API Misuse"
    if "mode" in explanation.lower() or "mode" in context.lower():
        bug_type = "Mode Configuration Mismatch"
    elif "order" in explanation.lower() or "sequence" in explanation.lower():
        bug_type = "Order Violation"
    elif "mismatch" in explanation.lower():
        bug_type = "Interface Mismatch"

    # Simple signature creation
    # Extract first few words or key symbols
    signature = f"Bug in {context[:30]}..." if context else "General RDI Bug"
    if "rdi." in buggy_code:
        # Try to find the method call
        import re
        matches = re.findall(r"rdi\.(\w+)\(\)", buggy_code)
        if matches:
            signature = " + ".join(list(dict.fromkeys(matches))) # unique methods

    template = f"""[BUG_KNOWLEDGE]

Language:
{language}

Bug Type:
{bug_type}

Context:
{context}

Buggy Code:
{buggy_code}

Correct Code:
{correct_code}

Explanation:
{explanation}

Bug Signature:
{signature}
"""
    return template, {"bug_id": bug_id, "type": "bug_knowledge"}

def main():
    print("🚀 Starting structured Knowledge Ingestion (Phase 1)...")
    
    if not os.path.exists(EMBEDDING_MODEL_DIR):
        print(f"Error: Embedding model directory {EMBEDDING_MODEL_DIR} not found.")
        return

    print(f"Loading embedding model from {EMBEDDING_MODEL_DIR}...")
    embed_model = HuggingFaceEmbedding(model_name=str(EMBEDDING_MODEL_DIR))
    Settings.embed_model = embed_model
    Settings.llm = None

    print(f"Reading samples from {SAMPLES_CSV}...")
    documents = []
    with open(SAMPLES_CSV, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            text, metadata = format_bug_knowledge(row)
            doc = Document(text=text, metadata=metadata)
            documents.append(doc)
    
    print(f"Loaded {len(documents)} structured documents.")

    print("Creating vector index...")
    index = VectorStoreIndex.from_documents(documents)

    print(f"Persisting index to {STORAGE_DIR}...")
    os.makedirs(STORAGE_DIR, exist_ok=True)
    index.storage_context.persist(persist_dir=str(STORAGE_DIR))
    
    print("✅ Ingestion Phase 1 COMPLETED.")

if __name__ == "__main__":
    main()
