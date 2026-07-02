# SHL Assessment Recommendation Agent — Approach Document

## 1. System Overview
A stateless, conversational AI agent that recommends SHL Individual Test Solutions via a RAG (Retrieval-Augmented Generation) pipeline. Built with **FastAPI**, **ChromaDB**, and **Gemini 2.5 Flash**.

**Live URL:** `https://shl-project-5116.onrender.com`  
**Endpoints:** `GET /health` · `POST /chat`

## 2. Architecture & Design Choices

### Retrieval Setup (RAG Pipeline)
- **Vector Store:** ChromaDB with built-in ONNX embeddings (`all-MiniLM-L6-v2`) — chosen over PyTorch-based sentence-transformers to stay under Render's 512MB free-tier memory limit.
- **Embedding Strategy:** Embeddings are generated at build time (`build_embeddings.py`) and persisted to disk. At runtime, queries are embedded using ChromaDB's native ONNX model (~80MB) and matched via cosine similarity against the catalog (Top-K=4).
- **Zero-Hallucination Policy:** The LLM never generates URLs or assessment names. These are mapped directly from ChromaDB metadata to the structured JSON response, eliminating fabricated catalog items entirely.

### Intent-Driven State Machine
A 5-state router classifies every user message via Gemini structured output:

| State | Trigger | Action |
|-------|---------|--------|
| `RECOMMEND` | Sufficient context for recommendation | Retrieve Top-K → LLM frames response |
| `CLARIFY` | Vague query (e.g., "I need a test") | LLM asks a clarifying question |
| `COMPARE` | User wants to compare tests | Retrieve relevant tests → LLM compares |
| `REFINE` | User modifies prior recommendations | New retrieval with refined context |
| `REFUSE` | Off-topic or prompt injection | Polite refusal, stays on-task |

### Prompt Design
- **Intent Classification Prompt:** Provides the LLM with all 5 intent definitions and the full conversation history. Returns structured JSON (`IntentClassification` Pydantic schema) for deterministic routing.
- **Generation Prompts:** Separated per intent. Each prompt constrains the LLM to only summarize/introduce retrieved context — never to invent information. A fallback JSON parser handles cases where `with_structured_output` fails.
- **Guardrail:** If intent is `recommend` but `context_sufficient=false`, the system automatically downgrades to `clarify`.

### Stateless Architecture
The backend stores no session state. The frontend maintains a `conversationHistory[]` array and sends the full history with every `POST /chat` request. This enables horizontal scaling without Redis or sticky sessions.

## 3. What Didn't Work & Iterations

| Attempt | Issue | Resolution |
|---------|-------|------------|
| HuggingFace `sentence-transformers` embeddings | PyTorch loaded ~400MB → OOM on Render's 512MB free tier | Switched to ChromaDB's built-in ONNX embeddings (~80MB) |
| Google `embedding-001` API | Model deprecated, returned 404 on `v1beta` API | Eliminated external embedding API dependency entirely |
| Lazy service initialization | First user request triggered model download + DB init → timeout | Moved to eager module-level initialization at startup |
| `StaticFiles` mounted at `/` | Catch-all intercepted `POST /chat` API route | Mounted static assets at `/static` prefix |

## 4. Evaluation Approach
- **Functional Testing:** `pytest` suite with mocked LLM dependencies validates all 5 state-machine paths without incurring API costs.
- **Retrieval Quality:** Manual evaluation across job-role queries (developer, sales, BPO) confirmed Top-4 similarity search returns contextually relevant assessments.
- **Hallucination Check:** Verified that all URLs and assessment names in API responses exist verbatim in `catalog.json` — no LLM-generated catalog data passes through.
- **Deployment Validation:** `/health` endpoint reports `google_api_key_set` and `chroma_db_exists` status for runtime diagnostics.

## 5. AI Tools Used
- **Antigravity (Agentic AI Coding Assistant):** Used for iterating on deployment configuration, debugging Render build failures, and resolving dependency/memory constraints. All code architecture, prompt design, and evaluation logic were designed collaboratively.
