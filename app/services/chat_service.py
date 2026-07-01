import logging
from typing import List

from app.models.schemas import ChatRequest, ChatResponse, AssessmentRecommendation
from app.services.llm import LLMService
from app.services.intent import IntentClassifier
from app.services.retriever import CatalogRetriever
from app.core.prompts import (
    CLARIFY_PROMPT,
    RECOMMEND_PROMPT,
    COMPARE_PROMPT,
    REFINE_PROMPT,
    REFUSE_PROMPT
)

logger = logging.getLogger(__name__)

class ChatService:
    """
    Orchestrates the conversation state machine.
    Routes the request based on intent and coordinates between LLM and Retriever.
    """
    
    def __init__(self, llm_service: LLMService, intent_classifier: IntentClassifier, retriever: CatalogRetriever):
        self.llm = llm_service
        self.intent_classifier = intent_classifier
        self.retriever = retriever

    def process_chat(self, request: ChatRequest) -> ChatResponse:
        classification = self.intent_classifier.classify(request.conversation)
        intent = classification.intent
        
        logger.info(f"Routing request to state: {intent.upper()}")
        
        if intent == "clarify": return self._handle_clarify(request)
        elif intent == "recommend": return self._handle_recommend(request)
        elif intent == "compare": return self._handle_compare(request)
        elif intent == "refine": return self._handle_refine(request)
        elif intent == "refuse": return self._handle_refuse(request)
        else: return ChatResponse(message="I am sorry, I am having trouble understanding. Could you rephrase?")

    def _extract_latest_query(self, request: ChatRequest) -> str:
        return request.conversation[-1].content

    def _handle_clarify(self, request: ChatRequest) -> ChatResponse:
        history = self.intent_classifier.format_history(request.conversation)
        query = self._extract_latest_query(request)
        prompt = CLARIFY_PROMPT.format(history=history, query=query)
        
        response_text = self.llm.generate_text(prompt)
        return ChatResponse(message=response_text)

    def _handle_recommend(self, request: ChatRequest) -> ChatResponse:
        query = self._extract_latest_query(request)
        docs = self.retriever.search_assessments(query, k=4)
        
        if not docs:
            return ChatResponse(message="I couldn't find any specific assessments matching your criteria in our catalog. Could you try broadening your search?")
            
        recommendations = [
            AssessmentRecommendation(
                name=doc.metadata.get("name", "Unknown"),
                url=doc.metadata.get("url", "#"),
                test_type=doc.metadata.get("test_type", "General")
            ) for doc in docs
        ]
            
        context = "\n\n".join([d.page_content for d in docs])
        prompt = RECOMMEND_PROMPT.format(query=query, context=context)
        response_text = self.llm.generate_text(prompt)
        
        return ChatResponse(message=response_text, recommendations=recommendations)

    def _handle_compare(self, request: ChatRequest) -> ChatResponse:
        query = self._extract_latest_query(request)
        docs = self.retriever.search_assessments(query, k=3)
        
        context = "\n\n".join([d.page_content for d in docs])
        prompt = COMPARE_PROMPT.format(query=query, context=context)
        response_text = self.llm.generate_text(prompt)
        
        return ChatResponse(message=response_text)

    def _handle_refine(self, request: ChatRequest) -> ChatResponse:
        history = self.intent_classifier.format_history(request.conversation)
        query = self._extract_latest_query(request)
        search_query = f"Previous context: {history}\nRefinement: {query}"
        
        docs = self.retriever.search_assessments(search_query, k=4)
        
        recommendations = [
            AssessmentRecommendation(
                name=doc.metadata.get("name", "Unknown"),
                url=doc.metadata.get("url", "#"),
                test_type=doc.metadata.get("test_type", "General")
            ) for doc in docs
        ]
            
        context = "\n\n".join([d.page_content for d in docs])
        prompt = REFINE_PROMPT.format(query=query, context=context)
        response_text = self.llm.generate_text(prompt)
        
        return ChatResponse(message=response_text, recommendations=recommendations)

    def _handle_refuse(self, request: ChatRequest) -> ChatResponse:
        query = self._extract_latest_query(request)
        prompt = REFUSE_PROMPT.format(query=query)
        response_text = self.llm.generate_text(prompt)
        return ChatResponse(message=response_text)
