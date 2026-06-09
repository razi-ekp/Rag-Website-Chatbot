# 🤖 RAG Website Chatbot

> An AI-powered chatbot that crawls any website and lets you chat with its content in real time.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=white)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange)
![Groq](https://img.shields.io/badge/LLM-LLaMA_3.3_70B-F55036)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📸 Demo

> Paste any website URL → Watch it crawl in real time → Ask questions → Get AI answers with source citations

---

## ✨ Features

| Feature | Details |
|---|---|
| **Recursive crawler** | Follows same-domain links up to configurable page limits |
| **Live crawl progress** | Real-time progress bar using Server-Sent Events (SSE) |
| **Semantic search** | ChromaDB + HuggingFace all-MiniLM-L6-v2 embeddings |
| **Streaming answers** | Token-by-token streaming like ChatGPT via SSE |
| **Confidence scoring** | Labels answers as HIGH, MEDIUM, LOW, or FALLBACK |
| **Source citations** | Returns exact source URLs with each answer |
| **Suggested questions** | Auto-generates relevant questions after indexing |
| **Prompt injection detection** | 15 regex patterns block jailbreaks and instruction overrides |
| **Multi-site support** | Index multiple websites and switch between them |
| **Parallel crawling** | Fetches 5 pages simultaneously — 5x faster than sequential |

---

## 🏗 Architecture

```
User Browser
    │
    ▼
React Frontend (Port 3000)
    │  ├── URL Input → POST /api/v1/ingest/start
    │  ├── SSE Progress ← GET /api/v1/ingest/stream/{site_id}
    │  ├── Chat Question → POST /api/v1/chat/stream
    │  └── SSE Answer Stream ← token by token
    │
    ▼
FastAPI Backend (Port 8000)
    │
    ├── WebCrawler (httpx + BeautifulSoup)
    │       └── Parallel async crawl (5 pages simultaneously)
    │
    ├── TextChunker (sliding window, 500 words, 50 overlap)
    │
    ├── VectorStore (ChromaDB + HuggingFace all-MiniLM-L6-v2)
    │       └── Cosine similarity retrieval
    │
    ├── InjectionDetector (15 regex patterns)
    │
    └── LLMService (Groq API → LLaMA 3.3 70B)
            └── Streaming SSE back to frontend
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI + Uvicorn |
| **Crawler** | httpx + BeautifulSoup4 |
| **Embeddings** | HuggingFace all-MiniLM-L6-v2 (local) |
| **LLM** | Groq LLaMA 3.3 70B (llama-3.3-70b-versatile) |
| **Vector Store** | ChromaDB (local persistent) |
| **Frontend** | React 18 + Tailwind CSS |
| **Security** | Custom prompt injection detector (15 patterns) |
| **Testing** | pytest (55 tests) |
| **Deployment** | Docker + Docker Compose |

---

## 🔒 Security

| Feature | Details |
|---|---|
| **Prompt injection detection** | Detects role override attempts (`ignore previous instructions`, `act as`, `jailbreak`), system prompt extraction (`reveal your prompt`), and known jailbreak phrases before the message reaches the LLM |
| **Domain-scoped crawling** | Crawler never leaves the target domain — prevents SSRF-style abuse |
| **Input length limits** | Questions capped at 1000 characters |
| **CORS configuration** | Strict origin whitelisting |

Prompt injection attempts return a red security alert in the UI. The message never reaches the LLM.

---

## 📊 Confidence Score

| Label | Score Range | Meaning |
|---|---|---|
| **HIGH** | >= 0.75 | Strong match in crawled website content |
| **MEDIUM** | 0.50 - 0.74 | Partial but useful match |
| **LOW** | 0.35 - 0.49 | Weak match |
| **FALLBACK** | < 0.35 | No reliable context found |

---

## 📁 Project Structure

```
Rag-Website-Chatbot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── ingest.py           # Crawl & index endpoints + SSE progress
│   │   │   └── chat.py             # Q&A endpoints + streaming
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic settings
│   │   │   └── logging.py          # Loguru setup
│   │   ├── models/
│   │   │   └── schemas.py          # All Pydantic models
│   │   ├── services/
│   │   │   ├── crawler.py          # Async parallel web crawler
│   │   │   ├── vector_store.py     # ChromaDB + embeddings
│   │   │   ├── llm_service.py      # Groq LLM + suggested questions
│   │   │   └── site_manager.py     # Site metadata persistence
│   │   ├── utils/
│   │   │   ├── chunker.py          # Sliding-window text chunker
│   │   │   └── injection_detector.py  # 15-pattern injection guard
│   │   └── main.py                 # FastAPI app + CORS + lifespan
│   ├── tests/
│   │   ├── test_injection_detector.py  # 15 tests
│   │   ├── test_chunker.py             # 12 tests
│   │   ├── test_crawler.py             # 14 tests
│   │   └── test_api.py                 # 14 tests
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.jsx
│   │   │   │   ├── ChatMessage.jsx
│   │   │   │   ├── ChatInput.jsx
│   │   │   │   └── SuggestedQuestions.jsx
│   │   │   ├── sidebar/
│   │   │   │   └── Sidebar.jsx
│   │   │   └── ui/
│   │   │       ├── ConfidenceBadge.jsx
│   │   │       └── SourceCitations.jsx
│   │   ├── hooks/
│   │   │   ├── useChat.js
│   │   │   └── useIngest.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── index.js
│   ├── public/index.html
│   ├── tailwind.config.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── start.bat
├── .gitignore
└── README.md
```

---

## ⚙️ Prerequisites

- Python 3.11+
- Node.js 18+
- [Groq API key](https://console.groq.com) — free tier available
- Git
- Windows 10/11 (for `start.bat`) or Linux/Mac

---

## 🚀 Setup & Installation

### Option 1: Windows One-Click (Easiest)

```bash
# 1. Clone the repository
git clone https://github.com/razi-ekp/Rag-Website-Chatbot.git
cd Rag-Website-Chatbot

# 2. Create backend/.env file
copy backend\.env.example backend\.env
# Open backend/.env and add your GROQ_API_KEY

# 3. Double-click start.bat (Run as administrator)
# It automatically creates venv, installs dependencies,
# starts backend on http://127.0.0.1:8000
# and frontend on http://localhost:3000
```

---

### Option 2: Manual Setup

#### Backend

```bash
git clone https://github.com/razi-ekp/Rag-Website-Chatbot.git
cd Rag-Website-Chatbot/backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend: http://127.0.0.1:8000  
API Docs: http://127.0.0.1:8000/docs

#### Frontend

```bash
cd ../frontend
npm install
npm start
```

Frontend: http://localhost:3000

---

### Option 3: Docker

```bash
git clone https://github.com/razi-ekp/Rag-Website-Chatbot.git
cd Rag-Website-Chatbot

copy backend\.env.example backend\.env
# Add GROQ_API_KEY to backend/.env

docker compose up --build
```

---

## 🧪 Run Tests

```bash
cd backend
venv\Scripts\activate
pytest tests/ -v --tb=short
```

Expected: **55 tests passed** across 4 test files.

---

## 📡 API Reference

### Ingest

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/ingest/start` | Start crawling a website |
| GET | `/api/v1/ingest/stream/{site_id}` | SSE: live crawl progress |
| GET | `/api/v1/ingest/status/{site_id}` | Get site indexing status |
| GET | `/api/v1/ingest/sites` | List all indexed sites |
| DELETE | `/api/v1/ingest/sites/{site_id}` | Delete a site |

### Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/chat/ask` | Ask a question (non-streaming) |
| POST | `/api/v1/chat/stream` | Ask a question (SSE streaming) |
| GET | `/api/v1/chat/suggested/{site_id}` | Get AI-generated suggested questions |

Full interactive docs: **http://127.0.0.1:8000/docs**

---

## 🔑 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | **required** | Your Groq API key from console.groq.com |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | LLM model |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage path |
| `MAX_CRAWL_PAGES` | `50` | Max pages to crawl per site |
| `CHUNK_SIZE` | `500` | Words per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K_RESULTS` | `5` | Number of retrieved chunks |
| `CONFIDENCE_HIGH_THRESHOLD` | `0.75` | Cosine similarity for HIGH |
| `CONFIDENCE_MEDIUM_THRESHOLD` | `0.50` | Cosine similarity for MEDIUM |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed frontend origin |
| `HF_HUB_OFFLINE` | `1` | Use cached embedding model offline |

---

## 💡 Solution Approach

1. **Crawling** — Async parallel BFS crawler using `httpx` fetches 5 pages simultaneously, extracts clean text by removing nav/scripts/footers, and follows internal links within the same domain.

2. **Chunking** — Text split into overlapping windows (500 words, 50-word overlap) to preserve context at chunk boundaries.

3. **Indexing** — Each chunk embedded locally using `all-MiniLM-L6-v2` (384 dimensions) and stored in ChromaDB with cosine similarity space. No external embedding API cost.

4. **Retrieval** — At query time, the question is embedded and top-K most similar chunks retrieved using cosine similarity.

5. **Generation** — Retrieved chunks injected as context into LLaMA 3.3 70B via Groq's ultra-fast inference API, streamed back token by token via SSE.

6. **Confidence Scoring** — Cosine similarity score of top retrieved chunk determines confidence level shown as color-coded badges.

7. **Security** — Every question passes through 15-pattern injection detector before reaching the LLM.

---


## 👤 Author

**Mohammed Razi** — [GitHub](https://github.com/razi-ekp) | [LinkedIn](https://linkedin.com/in/raziekp)

---

## 📄 License

MIT License