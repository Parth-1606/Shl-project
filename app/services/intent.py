import logging
from typing import List

from app.models.schemas import IntentClassification, Message
from app.services.llm import LLMService
from app.core.prompts import INTENT_CLASSIFICATION_PROMPT

logger = logging.getLogger(__name__)

class IntentClassifier:
    """Service to classify the user's intent based on their prompt and history."""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def format_history(self, conversation: List[Message]) -> str:
        """Formats the conversation history for the prompt."""
        if not conversation:
            return "No previous history."
        
        # Exclude the last message as it's the target for intent classification
        history = conversation[:-1]
        if not history:
            return "No previous history."
            
        formatted = ""
        for msg in history:
            formatted += f"[{msg.role.upper()}]: {msg.content}\n"
        return formatted.strip()

    def classify(self, conversation: List[Message]) -> IntentClassification:
        """
        Takes the conversation, extracts the latest message, and determines intent.
        Returns a structured IntentClassification object.
        """
        if not conversation:
            raise ValueError("Conversation cannot be empty.")
            
        latest_message = conversation[-1].content
        history_str = self.format_history(conversation)
        
        prompt = INTENT_CLASSIFICATION_PROMPT.format(
            history=history_str,
            message=latest_message
        )
        
        logger.info(f"Classifying intent for message: '{latest_message}'")
        
        # We rely on Gemini's structured output via our LLM service
        classification = self.llm.generate_structured(
            prompt=prompt, 
            schema=IntentClassification
        )
        
        logger.info(f"Detected Intent: {classification.intent}, Context Sufficient: {classification.context_sufficient}")
        
        # If user wants a recommendation but context is vague, downgrade to clarify
        if classification.intent == "recommend" and not classification.context_sufficient:
            logger.info("Downgrading intent to 'clarify' due to insufficient context.")
            classification.intent = "clarify"
            
        return classification
