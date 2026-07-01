from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.llm import LLMService
from app.services.intent import IntentClassifier
from app.services.retriever import CatalogRetriever

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency Injection logic for the FastAPI endpoints
# This ensures we don't recreate expensive objects (like LLMs or DB connections) on every single POST request.

_llm_service = None
_intent_classifier = None
_retriever = None

def get_chat_service() -> ChatService:
    """Dependency provider for ChatService."""
    global _llm_service, _intent_classifier, _retriever
    
    if _llm_service is None:
        _llm_service = LLMService()
    if _intent_classifier is None:
        _intent_classifier = IntentClassifier(llm_service=_llm_service)
    if _retriever is None:
        _retriever = CatalogRetriever()
        
    return ChatService(
        llm_service=_llm_service,
        intent_classifier=_intent_classifier,
        retriever=_retriever
    )

@router.post("/chat", response_model=ChatResponse, summary="Stateless Chat Endpoint")
async def chat_endpoint(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)):
    """
    Main endpoint for the Conversational Assessment Recommendation Agent.
    Requires a stateless conversation history array in the payload.
    """
    try:
        response = chat_service.process_chat(request)
        return response
    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Internal server error during chat processing: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
