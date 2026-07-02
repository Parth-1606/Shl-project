from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.llm import LLMService
from app.services.intent import IntentClassifier
from app.services.retriever import CatalogRetriever

logger = logging.getLogger(__name__)

router = APIRouter()

# Singleton services — initialized eagerly at module load so the heavy
# HuggingFace model download + ChromaDB connection happen at startup,
# not on the first user request (which would cause a timeout on Render).
_llm_service = LLMService()
_intent_classifier = IntentClassifier(llm_service=_llm_service)
_retriever = CatalogRetriever()
_chat_service = ChatService(
    llm_service=_llm_service,
    intent_classifier=_intent_classifier,
    retriever=_retriever
)

def get_chat_service() -> ChatService:
    """Dependency provider for ChatService."""
    return _chat_service

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
