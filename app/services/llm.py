import logging
from typing import Any, Type, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """
    Wrapper for the Gemini LLM client.
    Handles standard generation and structured output generation.
    """
    
    def __init__(self):
        if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your_gemini_api_key_here":
            logger.warning("GOOGLE_API_KEY is not set. LLM calls will fail.")
            
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            temperature=0.0, # Low temperature for reliable intent classification and grounded generation
            google_api_key=settings.GOOGLE_API_KEY
        )
        logger.info(f"Initialized LLMService with model {settings.MODEL_NAME}")

    def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        """
        Generates structured JSON output strictly matching a Pydantic schema.
        Uses Gemini's built-in structured output capabilities via Langchain.
        Includes a fallback for older versions of langchain-google-genai.
        """
        try:
            structured_llm = self.llm.with_structured_output(schema)
            return structured_llm.invoke(prompt)
        except Exception as e:
            logger.error(f"Error during structured generation: {e}. Falling back to manual JSON.")
            # Fallback for 'any' KeyError bug in langchain-google-genai
            prompt += "\n\nReturn EXACTLY a JSON object matching this schema. Do not include markdown formatting or backticks. Only return raw JSON: \n"
            prompt += str(schema.model_json_schema())
            
            response = self.llm.invoke(prompt)
            import json
            text = response.content.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
                
            data = json.loads(text.strip())
            return schema(**data)

    def generate_text(self, prompt: str) -> str:
        """
        Generates a standard text response.
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error during text generation: {e}")
            raise
