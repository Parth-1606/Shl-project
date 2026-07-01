from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Message(BaseModel):
    role: Literal["user", "assistant"] = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The text content of the message")

class ChatRequest(BaseModel):
    conversation: List[Message] = Field(
        ..., 
        description="The full conversation history. Must contain at least one user message.",
        min_length=1
    )

class AssessmentRecommendation(BaseModel):
    name: str = Field(..., description="Name of the assessment from the catalog")
    url: str = Field(..., description="URL of the assessment")
    test_type: str = Field(..., description="The type of the test")

class ChatResponse(BaseModel):
    message: str = Field(..., description="The agent's text response")
    recommendations: Optional[List[AssessmentRecommendation]] = Field(
        default=[], 
        description="List of recommended assessments. Empty if no recommendations are made.",
        max_length=10
    )

class IntentClassification(BaseModel):
    """Internal schema for structured output from LLM during Intent Detection."""
    intent: str = Field(
        ..., 
        description="The classified intent. Must be EXACTLY one of: 'recommend', 'clarify', 'compare', 'refine', 'refuse'"
    )
    context_sufficient: bool = Field(
        ..., 
        description="Whether there is enough context to make a recommendation without asking clarification."
    )
