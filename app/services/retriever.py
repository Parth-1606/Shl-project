import os
import logging
from typing import List, Dict

import chromadb
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class CatalogRetriever:
    """
    Service layer for querying the ChromaDB vector store.
    Uses ChromaDB's native API with built-in ONNX embeddings (all-MiniLM-L6-v2)
    to keep memory usage low on Render's free tier.
    """
    
    def __init__(self):
        self.chroma_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
        self.collection_name = "shl_catalog"
        self._collection = None
        self._init_store()

    def _init_store(self):
        """Initializes the connection to ChromaDB."""
        if not os.path.exists(self.chroma_dir):
            logger.warning(f"ChromaDB directory not found at {self.chroma_dir}. Make sure to run build_embeddings.py first.")
            return

        try:
            client = chromadb.PersistentClient(path=self.chroma_dir)
            self._collection = client.get_collection(
                name=self.collection_name
            )
            logger.info(f"Successfully connected to ChromaDB collection '{self.collection_name}' with {self._collection.count()} documents.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")

    def search_assessments(self, query: str, k: int = 4) -> List[Dict]:
        """
        Retrieves the top-k most relevant assessments for a given query.
        
        Args:
            query: The user's query (e.g., "I need a test for software developers")
            k: Maximum number of documents to retrieve
            
        Returns:
            A list of result dicts with 'page_content' and 'metadata' keys,
            mimicking LangChain Document structure for compatibility.
        """
        if not self._collection:
            logger.error("Collection is not initialized. Cannot perform search.")
            return []

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=k
            )
            
            # Convert ChromaDB results to Document-like dicts
            docs = []
            if results and results["documents"] and results["metadatas"]:
                for doc_text, metadata in zip(results["documents"][0], results["metadatas"][0]):
                    docs.append({
                        "page_content": doc_text,
                        "metadata": metadata
                    })
            return docs
        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            return []
