import json
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def build_vector_store():
    """
    Reads the catalog.json file, creates embedding representations using HuggingFace, 
    and stores them in a local ChromaDB instance.
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
    for item in assessments:
        # Create a rich text representation for better semantic matching
        # We include name, description, test type, skills, and roles in the page_content
        skills_str = ", ".join(item.get("skills_measured", []))
        roles_str = ", ".join(item.get("job_roles", []))
        
        content = (
            f"Assessment Name: {item['name']}\n"
            f"Type: {item['test_type']}\n"
            f"Description: {item['description']}\n"
            f"Skills Measured: {skills_str}\n"
            f"Target Roles: {roles_str}"
        )
        
        # Keep the raw data in metadata so we can reconstruct exact recommendations later
        metadata = {
            "name": item.get("name"),
            "url": item.get("url"),
            "test_type": item.get("test_type"),
            "duration": item.get("duration"),
            "remote_testing": item.get("remote_testing"),
            "adaptive": item.get("adaptive")
        }
        
        # Chroma expects metadata values to be strings, ints, floats, or bools
        # Lists cannot be directly inserted into metadata in Chroma, so we flatten them if needed
        # or we just rely on stringification.
        
        doc = Document(page_content=content, metadata=metadata)
        documents.append(doc)

    logger.info(f"Prepared {len(documents)} documents. Initializing embeddings...")
    
    # We use sentence-transformers for robust local embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    logger.info("Generating embeddings and writing to ChromaDB. This may take a moment...")
    
    # Create and persist the vector store
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=chroma_dir,
        collection_name="shl_catalog"
    )
    
    logger.info(f"Successfully built ChromaDB vector store at '{chroma_dir}'")

if __name__ == "__main__":
    build_vector_store()
