# 🤖 RAG Website Chatbot

>  Chat with any website using AI-powered Retrieval-Augmented Generation

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react)](https://reactjs.org)
[![Groq](https://img.shields.io/badge/LLM-Groq_LLaMA_3.3_70B-F55036)](https://groq.com)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange)](https://trychroma.com)

---

## 📌 Project Description

A production-ready AI chatbot that crawls any website, indexes all its content into a vector database, and lets users ask natural language questions — answered instantly using LLaMA 3.3 70B via Groq.

**What makes this different from existing RAG chatbots:**

| Feature | This Project | ChatPDF | Perplexity |
|---|:---:|:---:|:---:|
| 🔴 Prompt Injection Detection | ✅ | ❌ | ❌ |
| 📊 Confidence Badges (HIGH/MEDIUM/LOW) | ✅ | ❌ | ❌ |
| 📡 Live Crawl Progress (SSE) | ✅ | ❌ | ❌ |
| 💡 Auto-generated Suggested Questions | ✅ | ❌ | ❌ |
| 🌐 Full Website Recursive Crawl | ✅ | ❌ | ✅ |
| ⚡ Token-by-token Streaming | ✅ | ❌ | ✅ |
| 📎 Source Citations per Answer | ✅ | ✅ | ✅ |

---

## 🏗 System Architecture

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
    │       └── Recursive same-domain crawl
    │
    ├── TextChunker (sliding window, configurable)
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

| Layer | Technology | Why |
|---|---|---|
| LLM | Groq LLaMA 3.3 70B | Fastest inference, free tier, excellent reasoning |
| Embeddings | HuggingFace all-MiniLM-L6-v2 | Local, fast, no API cost, 384-dim |
| Vector DB | ChromaDB | Persistent, local, simple API, cosine similarity |
| Backend | FastAPI + SSE | Async, fast, auto-docs, native streaming |
| Frontend | React 18 + Tailwind CSS | Component-based, utility-first dark UI |
| Crawler | httpx + BeautifulSoup4 | Async HTTP, robust HTML parsing |
| Containerization | Docker + Docker Compose | One-command deployment |

---

## 📁 Project Structure

```
rag-website-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── ingest.py        # Crawl & index endpoints + SSE progress
│   │   │   └── chat.py          # Q&A endpoints + streaming
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic settings
│   │   │   └── logging.py       # Loguru setup
│   │   ├── models/
│   │   │   └── schemas.py       # All Pydantic models
│   │   ├── services/
│   │   │   ├── crawler.py       # Async web crawler
│   │   │   ├── vector_store.py  # ChromaDB + embeddings
│   │   │   ├── llm_service.py   # Groq LLM + suggested questions
│   │   │   └── site_manager.py  # Site metadata persistence
│   │   ├── utils/
│   │   │   ├── chunker.py       # Sliding-window text chunker
│   │   │   └── injection_detector.py  # 15-pattern injection guard
│   │   └── main.py              # FastAPI app + CORS + lifespan
│   ├── tests/
│   │   ├── test_injection_detector.py  # 15 tests
│   │   ├── test_chunker.py             # 12 tests
│   │   ├── test_crawler.py             # 14 tests
│   │   └── test_api.py                 # 14 tests (mocked)
│   ├── requirements.txt
│   ├── pytest.ini
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.jsx       # Main chat area
│   │   │   │   ├── ChatMessage.jsx      # User/assistant bubbles
│   │   │   │   ├── ChatInput.jsx        # Textarea + send/stop
│   │   │   │   └── SuggestedQuestions.jsx
│   │   │   ├── sidebar/
│   │   │   │   └── Sidebar.jsx          # URL input, site list, progress
│   │   │   └── ui/
│   │   │       ├── ConfidenceBadge.jsx  # HIGH/MEDIUM/LOW/FALLBACK
│   │   │       └── SourceCitations.jsx  # Expandable source links
│   │   ├── hooks/
│   │   │   ├── useChat.js              # SSE streaming chat state
│   │   │   └── useIngest.js            # Crawl progress state
│   │   ├── services/
│   │   │   └── api.js                  # Axios API layer
│   │   ├── App.jsx
│   │   └── index.js
│   ├── public/index.html
│   ├── tailwind.config.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Groq API key](https://console.groq.com) (free)
- Git

---

### 🚀 Option 1: Local Development (Recommended for demo)

#### Backend

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/rag-website-chatbot.git
cd rag-website-chatbot/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at: http://localhost:8000
API Docs at: http://localhost:8000/docs

#### Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# REACT_APP_API_URL=http://localhost:8000/api/v1 (default)

# Start development server
npm start
```

Frontend runs at: http://localhost:3000

---

### 🐳 Option 2: Docker (One-command)

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/rag-website-chatbot.git
cd rag-website-chatbot

# Add your Groq API key to backend/.env
cp backend/.env.example backend/.env
echo "GROQ_API_KEY=your_key_here" >> backend/.env

# Build and start
docker compose up --build

# App: http://localhost:3000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

### 🧪 Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --tb=short
```

Expected: **55 tests** across 4 test files.

---

## 🔑 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | required | Your Groq API key |
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

---

## 📡 API Reference

### Ingest

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/ingest/start` | Start crawling a website |
| GET | `/api/v1/ingest/stream/{site_id}` | SSE: live crawl progress |
| GET | `/api/v1/ingest/status/{site_id}` | Get site status |
| GET | `/api/v1/ingest/sites` | List all indexed sites |
| DELETE | `/api/v1/ingest/sites/{site_id}` | Delete a site |

### Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/chat/ask` | Ask a question (non-streaming) |
| POST | `/api/v1/chat/stream` | Ask a question (SSE streaming) |
| GET | `/api/v1/chat/suggested/{site_id}` | Get suggested questions |

Full interactive docs: **http://localhost:8000/docs**

---

## 🔒 Security Features

- **Prompt Injection Detection**: 15 regex patterns guard against jailbreaks, instruction overrides, system prompt extraction, and script injection
- **Input length limits**: Questions capped at 1000 characters
- **Domain-scoped crawling**: Crawler never leaves the target domain
- **CORS configuration**: Strict origin whitelisting
- **Rate limiting**: Crawl delay between requests (300ms) to be a good citizen

---

## 💡 Solution Approach

1. **Crawling**: An async BFS crawler using `httpx` visits all pages of a given domain, extracts clean text (removing nav, scripts, footers), and follows internal links recursively.

2. **Chunking**: Text is split into overlapping windows (500 words, 50-word overlap) to ensure context is not lost at boundaries.

3. **Indexing**: Each chunk is embedded locally using `all-MiniLM-L6-v2` (384 dimensions) and stored in ChromaDB with cosine similarity space.

4. **Retrieval**: At query time, the question is embedded and top-K most similar chunks are retrieved using cosine similarity.

5. **Generation**: Retrieved chunks are injected as context into LLaMA 3.3 70B via Groq's ultra-fast inference API, which streams the response back token by token via SSE.

6. **Confidence**: The cosine similarity score of the top retrieved chunk determines the confidence level — transparent to the user via color-coded badges.

---

## 🎥 Video Demo

📹 [Watch on YouTube (Unlisted)](https://youtube.com/YOUR_LINK_HERE)

---

## 👤 Author

**Razi** — [GitHub](https://github.com/razi-ekp)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
