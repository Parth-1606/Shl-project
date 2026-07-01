# SHL Assessment Recommendation Agent: Architectural Approach & Design Document

## 1. Executive Summary
This document outlines the design, architecture, and tradeoffs of the SHL Conversational Assessment Recommendation Agent. The objective was to build a robust, production-grade conversational AI that assists recruiters in discovering appropriate SHL Individual Test Solutions. By prioritizing a stateless architecture, strict hallucination guardrails, and modular service-oriented design, the resulting application is highly scalable, deterministic, and cost-efficient.

## 2. System Architecture
The application is built using a **Service-Oriented Architecture (SOA)** pattern utilizing **FastAPI** to expose a stateless backend. The core workflow is orchestrated by a state-machine that routes user interactions based on explicit intent detection.

### 2.1 Core Components
* **Stateless API (FastAPI):** Exposes `POST /chat` and `GET /health` endpoints. It holds no memory in the server; conversation history is passed by the client, allowing for infinite horizontal scalability via platforms like Render or AWS ECS.
* **Vector Database (ChromaDB):** Acts as the central Retrieval-Augmented Generation (RAG) store.
* **Local Embeddings (HuggingFace `sentence-transformers`):** Generates high-quality semantic vectors (`all-MiniLM-L6-v2`) locally, bypassing the latency, API constraints, and cost of external embedding models.
* **LLM Engine (Gemini 2.5 Flash):** Utilized strictly for *intent classification* and *conversational framing*.
* **State Machine (ChatService):** Routes requests into predefined logic paths: `RECOMMEND`, `CLARIFY`, `COMPARE`, `REFINE`, and `REFUSE`.

### 2.2 The RAG Pipeline
Instead of relying on the LLM to generate recommendations—which is highly prone to hallucinating non-existent tests or URLs—the RAG pipeline is constrained. 
1. The user's query is embedded and searched against ChromaDB.
2. The Top-K most relevant assessments are retrieved.
3. The LLM is provided the context and instructed to simply "introduce" the recommendations, while the actual structured assessment data (Name, URL, Type) is mapped directly from the database to the JSON response.

## 3. Key Architectural Decisions & Tradeoffs

### Tradeoff 1: Local Embeddings vs. API Embeddings
* **Decision:** Used `sentence-transformers` locally instead of Google/OpenAI embeddings.
* **Rationale:** Reduces network latency to 0ms for the retrieval phase, eliminates API token costs, and removes dependency on volatile external endpoints (avoiding 404 deprecation errors).
* **Tradeoff:** Increases the Docker/Deployment image size due to PyTorch dependencies and increases cold-start time slightly as the model loads into memory.

### Tradeoff 2: Stateless vs. Stateful Backend
* **Decision:** The FastAPI server is completely stateless. The frontend maintains the `conversationHistory` array and sends it with every request.
* **Rationale:** Essential for modern cloud deployment. A stateful backend requires Redis or sticky sessions, which dramatically increases infrastructure complexity and cost.
* **Tradeoff:** Increases the payload size of each HTTP request, as long conversations must be transmitted entirely.

### Tradeoff 3: Strict Schema Validation vs. Open Text
* **Decision:** Enforced strict Pydantic schemas on the LLM output via Langchain's `with_structured_output` (with a manual JSON parsing fallback for stability).
* **Rationale:** LLMs are non-deterministic. By enforcing a JSON schema, the application can programmatically route states (e.g., if `intent == "clarify"`) without relying on brittle regex parsing.
* **Tradeoff:** Requires more complex error handling if the LLM fails to adhere to the schema.

## 4. Evaluation & Hallucination Prevention
To ensure enterprise-grade reliability, the system implements a strict **Zero-Hallucination Policy** for catalog items:
1. **Direct Data Mapping:** The LLM is never allowed to generate URLs. The `retriever.py` extracts URLs directly from ChromaDB metadata and passes them strictly to the frontend via the `recommendations` JSON array.
2. **Intent Guardrails:** The system evaluates if the `context_sufficient` flag is true. If a user asks "I need a test", the system automatically triggers the `CLARIFY` state and prompts the user for a domain (e.g., Software Engineering or Finance) instead of blindly guessing.
3. **Automated Testing:** A full `pytest` suite uses Mock Dependency Injection to simulate LLM intent outputs. This validates the state machine's logic pathways (Recommend vs Refuse) in milliseconds without incurring real API costs.

## 5. Future Improvements
If this project were to be scaled for a global production release, the following enhancements would be prioritized:
1. **Migration to PostgreSQL + pgvector:** While ChromaDB is excellent for prototyping, migrating to a managed PostgreSQL instance with `pgvector` would allow for concurrent writes, automated backups, and ACID compliance.
2. **User Authentication & Session Management:** Implementing JWT tokens to allow recruiters to save their favorite assessments to a personal profile.
3. **Advanced RAG (Hybrid Search):** Combining the current dense vector search (semantic similarity) with BM25 sparse search (keyword matching) to improve retrieval accuracy for highly specific technical acronyms (e.g., "AWS DevOps").
