from langchain_core.documents import Document
from app.models.schemas import IntentClassification

def test_refinement_intent(client, mock_dependencies):
    mock_llm = mock_dependencies["llm"]
    mock_retriever = mock_dependencies["retriever"]
    
    mock_llm.generate_structured.return_value = IntentClassification(
        intent="refine",
        context_sufficient=True
    )
    
    mock_retriever.search_assessments.return_value = [
        Document(
            page_content="Mock Remote Test", 
            metadata={"name": "Remote Java", "url": "http://shl.com/remote", "test_type": "Skills"}
        )
    ]
    
    mock_llm.generate_text.return_value = "Here are the remote options."

    payload = {
        "conversation": [
            {"role": "user", "content": "I need a test for java developers."},
            {"role": "assistant", "content": "Here are tests for java developers..."},
            {"role": "user", "content": "Actually, make sure they support remote testing."}
        ]
    }
    
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["recommendations"][0]["name"] == "Remote Java"
    # Ensure retriever search query included previous context
    search_call_args = mock_retriever.search_assessments.call_args[0][0]
    assert "java developers" in search_call_args.lower()
    assert "remote" in search_call_args.lower()
