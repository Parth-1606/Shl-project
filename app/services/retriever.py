import os
import logging
from typing import List
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()
logger = logging.getLogger(__name__)

class CatalogRetriever:
    """
    Service layer for querying the ChromaDB vector store.
    Uses Dependency Injection principles: it can be instantiated once
    and passed to the chat service.
    """
    
    def __init__(self):
        self.chroma_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
        self.collection_name = "shl_catalog"
        self._vector_store = None
        self._init_store()

    def _init_store(self):
        """Initializes the connection to ChromaDB."""
        if not os.path.exists(self.chroma_dir):
            logger.warning(f"ChromaDB directory not found at {self.chroma_dir}. Make sure to run build_embeddings.py first.")
            return

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            logger.error("GOOGLE_API_KEY is missing. Retriever cannot initialize embeddings.")
            return

        try:
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self._vector_store = Chroma(
                persist_directory=self.chroma_dir,
                embedding_function=embeddings,
                collection_name=self.collection_name
            )
            logger.info("Successfully connected to ChromaDB vector store.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")

    def search_assessments(self, query: str, k: int = 4) -> List[Document]:
        """
        Retrieves the top-k most relevant assessments for a given query.
        
        Args:
            query: The user's query (e.g., "I need a test for software developers")
            k: Maximum number of documents to retrieve
            
        Returns:
            A list of Langchain Document objects.
        """
        if not self._vector_store:
            logger.error("Vector store is not initialized. Cannot perform search.")
            return []

        try:
            # Using maximal marginal relevance (MMR) or similarity search.
            # Similarity search is standard, MMR helps if we want diversity.
            docs = self._vector_store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            return []
