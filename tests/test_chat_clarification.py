from app.models.schemas import IntentClassification

def test_clarification_intent(client, mock_dependencies):
    """
    Tests that if the LLM identifies the intent as 'clarify' 
    (or 'recommend' but with insufficient context), the State Machine routes to _handle_clarify.
    """
    mock_llm = mock_dependencies["llm"]
    
    # Mock the structured output to return a clarify intent
    mock_llm.generate_structured.return_value = IntentClassification(
        intent="clarify",
        context_sufficient=False
    )
    
    # Mock the text generation for the clarifying question
    mock_llm.generate_text.return_value = "Could you please specify which job role you are hiring for?"

    payload = {
        "conversation": [
            {"role": "user", "content": "I need a test."}
        ]
    }
    
    response = client.post("/chat", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "job role" in data["message"]
    # No recommendations should be given during clarification
    assert len(data["recommendations"]) == 0
    
    # Ensure retriever was NOT called (saves DB/API compute)
    mock_dependencies["retriever"].search_assessments.assert_not_called()
