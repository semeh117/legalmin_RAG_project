# ⚖️ LegalMind — AI Legal Document Assistant

> Stop drowning in legal documents. Ask questions, get answers — instantly.

LegalMind is a **Retrieval-Augmented Generation (RAG)** application that lets lawyers, law students, and businesses upload legal documents and get precise, cited answers from their own files — powered by semantic search and a Large Language Model.

No hallucinations. No guessing. Every answer references the exact page it came from.

---

## 🧠 How It Works

```
PDF Upload → Text Extraction → Chunking → Embedding → ChromaDB
                                                            ↓
                                          User Question → Embed Question
                                                            ↓
                                                    Semantic Search
                                                            ↓
                                              Groq LLaMA → Answer + Page Citation
```

1. **Ingest** — PDF is extracted page by page and split into semantic chunks
2. **Embed** — Each chunk is transformed into a 384-dimensional vector using `all-MiniLM-L6-v2`
3. **Store** — Vectors are stored in ChromaDB for fast semantic search
4. **Retrieve** — User question is embedded and top-K most similar chunks are retrieved
5. **Generate** — Groq LLaMA builds a precise answer from retrieved chunks only

---

## ✨ Features

- 📄 **PDF Upload** — Upload any legal document (NDA, contracts, terms of service)
- 🔍 **Semantic Search** — Finds relevant clauses by meaning, not just keywords
- 🤖 **AI-Powered Answers** — Precise answers generated from your document only
- 📍 **Page Citations** — Every answer includes the exact page number
- 🚫 **No Hallucinations** — LLM is instructed to say "I don't know" if answer isn't in the document
- 🐳 **Dockerized** — Runs anywhere with a single command

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Embedding Model | `all-MiniLM-L6-v2` (Sentence Transformers) |
| Vector Database | ChromaDB |
| LLM | LLaMA 3.3 70B via Groq API |
| PDF Processing | PyMuPDF (fitz) |
| Chunking | LangChain Text Splitters |
| Containerization | Docker + Docker Compose |

---

## 🚀 Getting Started

### Prerequisites
- Docker Desktop installed and running
- Groq API key (free at [console.groq.com](https://console.groq.com))

### 1. Clone the repository
```bash
git clone https://github.com/semah117/legalmind.git
cd legalmind
```

### 2. Set up environment variables
```bash
cp .env.example .env
```
Open `.env` and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run with Docker
```bash
docker-compose up --build
```

### 4. Open the app
| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| FastAPI Docs | http://localhost:8000/docs |

---

## 📖 Usage

1. Open `http://localhost:8501` in your browser
2. Upload a legal PDF document
3. Type your question in the input field
4. Click **"Ask LegalMind"**
5. Get a precise answer with page citations

---

## 📁 Project Structure

```
legalmind/
├── backend/
│   ├── main.py          # FastAPI endpoints (/upload, /ask, /health)
│   ├── ingestion.py     # PDF extraction and chunking
│   ├── embeddings.py    # Sentence Transformer embeddings
│   ├── retrieval.py     # ChromaDB store and search
│   ├── llm.py           # Groq LLM prompt and generation
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app.py           # Streamlit UI
│   ├── requirements.txt
│   └── Dockerfile
├── sample_docs/         # Test PDFs
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check server status |
| POST | `/upload` | Upload and process a PDF |
| POST | `/ask` | Ask a question about the document |

Full interactive documentation available at `http://localhost:8000/docs`

---

## 👤 Author

**Semah** — [@semah117](https://github.com/semah117)

Data Science & AI Engineering Student — École Polytechnique de Sousse

