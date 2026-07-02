import json
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

import chromadb

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def build_vector_store():
    """
    Reads the catalog.json file, creates embedding representations using 
    ChromaDB's built-in default embeddings (ONNX-based all-MiniLM-L6-v2),
    and stores them in a local ChromaDB instance.
    
    This approach avoids loading PyTorch (~400MB) and avoids Google API
    embedding issues, keeping memory well under Render's 512MB free tier.
    """
    catalog_path = os.getenv("CATALOG_JSON_PATH", "./app/catalog/data/catalog.json")
    chroma_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")

    if not os.path.exists(catalog_path):
        logger.error(f"Catalog file not found at {catalog_path}")
        return

    logger.info("Loading catalog data...")
    with open(catalog_path, "r", encoding="utf-8") as f:
        assessments = json.load(f)

    documents = []
    metadatas = []
    ids = []

    for i, item in enumerate(assessments):
        # Create a rich text representation for better semantic matching
        skills_str = ", ".join(item.get("skills_measured", []))
        roles_str = ", ".join(item.get("job_roles", []))
        
        content = (
            f"Assessment Name: {item['name']}\n"
            f"Type: {item['test_type']}\n"
            f"Description: {item['description']}\n"
            f"Skills Measured: {skills_str}\n"
            f"Target Roles: {roles_str}"
        )
        
        # Chroma expects metadata values to be strings, ints, floats, or bools
        metadata = {
            "name": item.get("name", "Unknown"),
            "url": item.get("url", "#"),
            "test_type": item.get("test_type", "General"),
            "duration": str(item.get("duration", "")),
            "remote_testing": str(item.get("remote_testing", "")),
            "adaptive": str(item.get("adaptive", ""))
        }
        
        documents.append(content)
        metadatas.append(metadata)
        ids.append(f"assessment_{i}")

    logger.info(f"Prepared {len(documents)} documents. Initializing ChromaDB with default embeddings...")
    
    # Use ChromaDB's built-in default embedding function (ONNX all-MiniLM-L6-v2)
    # This is lightweight (~80MB) compared to PyTorch sentence-transformers (~400MB)
    client = chromadb.PersistentClient(path=chroma_dir)
    
    # Delete existing collection if it exists, to rebuild fresh
    try:
        client.delete_collection("shl_catalog")
        logger.info("Deleted existing shl_catalog collection for rebuild.")
    except Exception:
        pass
    
    collection = client.get_or_create_collection(
        name="shl_catalog",
        metadata={"hnsw:space": "cosine"}
    )
    
    logger.info("Generating embeddings and writing to ChromaDB. This may take a moment...")
    
    # Add documents in batches
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    logger.info(f"Successfully built ChromaDB vector store at '{chroma_dir}' with {len(documents)} documents.")

if __name__ == "__main__":
    build_vector_store()
