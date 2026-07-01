from langchain_core.documents import Document
from app.models.schemas import IntentClassification

def test_recommendation_intent(client, mock_dependencies):
    mock_llm = mock_dependencies["llm"]
    mock_retriever = mock_dependencies["retriever"]
    
    # Setup Mocks
    mock_llm.generate_structured.return_value = IntentClassification(
        intent="recommend",
        context_sufficient=True
    )
    
    mock_retriever.search_assessments.return_value = [
        Document(
            page_content="Mock Test 1", 
            metadata={"name": "Test A", "url": "http://shl.com/a", "test_type": "Cognitive"}
        )
    ]
    
    mock_llm.generate_text.return_value = "Here is a test for software engineers."

    payload = {
        "conversation": [
            {"role": "user", "content": "I need a cognitive test for software engineers."}
        ]
    }
    
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Assertions
    assert "Here is a test" in data["message"]
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["name"] == "Test A"
    assert data["recommendations"][0]["url"] == "http://shl.com/a"
    
    # Verify DB was queried
    mock_retriever.search_assessments.assert_called_once()
