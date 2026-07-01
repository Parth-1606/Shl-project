from app.models.schemas import IntentClassification

def test_comparison_intent(client, mock_dependencies):
    mock_llm = mock_dependencies["llm"]
    mock_retriever = mock_dependencies["retriever"]
    
    mock_llm.generate_structured.return_value = IntentClassification(
        intent="compare",
        context_sufficient=True
    )
    
    # Text gen mock
    mock_llm.generate_text.return_value = "Test A measures numerical skills, whereas Test B measures behavioral traits."

    payload = {
        "conversation": [
            {"role": "user", "content": "What is the difference between Verify G+ and OPQ32?"}
        ]
    }
    
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "numerical skills" in data["message"]
    # Comparison usually doesn't need to return the formal recommendation JSON block
    # depending on UX, but currently it returns an empty list
    assert len(data["recommendations"]) == 0
