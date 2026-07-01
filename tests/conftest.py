import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app
from app.api.chat import get_chat_service
from app.services.chat_service import ChatService
from app.services.llm import LLMService
from app.services.intent import IntentClassifier
from app.services.retriever import CatalogRetriever
from langchain_core.documents import Document

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_dependencies():
    """
    Overrides the FastAPI dependencies with mocked LLM and Retriever services.
    This ensures tests run quickly, deterministically, and without API costs.
    """
    mock_llm = MagicMock(spec=LLMService)
    mock_retriever = MagicMock(spec=CatalogRetriever)
    
    intent_classifier = IntentClassifier(llm_service=mock_llm)
    
    chat_service = ChatService(
        llm_service=mock_llm, 
        intent_classifier=intent_classifier, 
        retriever=mock_retriever
    )
    
    app.dependency_overrides[get_chat_service] = lambda: chat_service
    
    yield {
        "llm": mock_llm,
        "retriever": mock_retriever,
        "chat_service": chat_service
    }
    
    app.dependency_overrides.clear()
