# Day 17 – RAG FastAPI Application

## Setup
```bash
pip install fastapi uvicorn python-multipart PyPDF2 python-docx chromadb openai python-dotenv
```

## Run
```bash
cd Day-17/rag-fastapi-app
uvicorn app:app --reload
```
Swagger UI at http://127.0.0.1:8000/docs

## Deliverables

| File | Description |
|---|---|
| `app.py` | FastAPI app with 7 endpoints |
| `rag.py` | RAGEngine class: embed, store, retrieve, answer |
| `document_processor.py` | Text extraction (PDF/TXT/DOCX) + chunking |
| `postman_collection.json` | Pre-built Postman requests for all endpoints |
| `README.md` | Architecture, endpoints, curl examples |

## API Endpoints

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/` | Health check |
| POST | `/upload` | Upload PDF/TXT/DOCX → chunk → embed → store |
| POST | `/query` | Question → retrieve → LLM → answer + sources |
| GET | `/documents` | List all indexed documents |
| DELETE | `/document/{doc_id}` | Remove document and all its chunks |
| GET | `/history` | View all Q&A from this session |
| DELETE | `/history` | Clear session history |

## Key Concepts

### FastAPI vs Flask
| | FastAPI | Flask |
|---|---|---|
| Speed | Very fast (async) | Slower (sync by default) |
| Docs | Auto-generated (Swagger) | Manual |
| Validation | Built-in (Pydantic) | Manual |
| Best for | APIs, ML serving | Simple web apps |

### How Documents Are Stored
- Each chunk stored with metadata: `doc_id`, `filename`, `chunk_index`, `upload_time`
- `doc_id` is an 8-char UUID prefix — used to group and delete all chunks of one document
- ChromaDB persisted to `./chroma_db/` — survives app restarts

### Chunking Strategy
- `chunk_size=500` characters, `overlap=50` characters
- Tries to break at sentence boundaries (`.` or `\n`) for cleaner chunks
- Overlap preserves context at chunk boundaries
