# SHL Conversational Assessment Recommendation Agent

A production-grade, stateful-acting (stateless API) RAG Chatbot designed to help recruiters navigate the SHL Individual Test Solutions catalog. 

Built with **FastAPI**, **LangChain**, **Gemini 2.5 Flash**, and **ChromaDB**.

---

## 🏗 Architecture
1. **Catalog Scraper**: Parses SHL HTML/data into a structured `catalog.json` file.
2. **Offline Embedding**: Converts the JSON catalog into semantic vectors stored locally in ChromaDB.
3. **Intent State Machine**: Dynamically routes conversational flow (`recommend`, `clarify`, `compare`, `refine`, `refuse`).
4. **Retrieval-Augmented Generation (RAG)**: Secures data integrity by mapping recommendations strictly from the database, preventing LLM hallucinations.

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- Python 3.11+
- Gemini API Key

### 2. Environment Variables
Copy `.env.example` to `.env` and fill in your Gemini API key:
```bash
cp .env.example .env
```
Ensure your `.env` contains:
```env
GOOGLE_API_KEY=your_actual_api_key
CHROMA_DB_DIR=./chroma_db
CATALOG_JSON_PATH=./app/catalog/data/catalog.json
```

### 3. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Build Vector Store (Run Once)
Before starting the server, you must initialize the ChromaDB vector database:
```bash
python -m app.catalog.build_embeddings
```

### 5. Start FastAPI Server
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

---

## 🧪 Testing

The project uses `pytest` with extensive Mock Dependency Injection to evaluate the State Machine without incurring API costs.

Run the test suite:
```bash
pytest tests/
```

---

## 🚢 Deployment (Render)

This project is configured for one-click deployment on [Render](https://render.com) using the included `render.yaml`.

**Deployment Steps:**
1. Push this repository to GitHub.
2. In the Render Dashboard, click **New > Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically detect `render.yaml`.
5. Go to the service **Environment Variables** in Render and manually set your `GOOGLE_API_KEY`.
6. Click **Deploy**.

Render will automatically install dependencies, build the embeddings during the `buildCommand`, and launch the ASGI server using `uvicorn`.
