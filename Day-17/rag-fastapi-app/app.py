"""
RAG FastAPI Application – Day 17
Endpoints: upload, query, list documents, delete document, history
Run: uvicorn app:app --reload
Docs: http://127.0.0.1:8000/docs
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from document_processor import extract_text, chunk_text, SUPPORTED_EXTENSIONS
from rag import RAGEngine

# ── App Setup ─────────────────────────────────────────────────────────────────

app    = FastAPI(
    title="RAG API",
    description="Upload documents and ask questions. Answers are grounded in your documents.",
    version="1.0.0"
)
engine = RAGEngine()

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# In-memory conversation history (list of dicts)
history: list[dict] = []


# ── Pydantic Models ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict]
    timestamp: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "RAG API is running. Visit /docs for the interactive API docs."}


@app.post("/upload", summary="Upload a PDF, TXT, or DOCX document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document. It will be chunked, embedded, and stored in the vector database.
    Supported formats: .pdf, .txt, .docx
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Supported: {list(SUPPORTED_EXTENSIONS)}"
        )

    # Save file to disk
    save_path = UPLOAD_DIR / file.filename
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text and chunk
    try:
        text   = extract_text(str(save_path), ext)
        chunks = chunk_text(text)
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Failed to process document: {str(e)}")

    if not chunks:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Document appears to be empty or unreadable.")

    # Embed and store
    doc_info = engine.add_document(chunks, file.filename)

    return {
        "message":     "Document uploaded and indexed successfully.",
        "doc_id":      doc_info["doc_id"],
        "filename":    doc_info["filename"],
        "chunks":      doc_info["chunks"],
        "upload_time": doc_info["upload_time"]
    }


@app.post("/query", response_model=QueryResponse, summary="Ask a question about your documents")
def query_documents(body: QueryRequest):
    """
    Ask a question. The system retrieves relevant chunks from uploaded documents
    and generates a grounded answer. The question and answer are saved to history.
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result    = engine.query(body.question)
    timestamp = datetime.utcnow().isoformat() + "Z"

    entry = {
        "question":  body.question,
        "answer":    result["answer"],
        "sources":   result["sources"],
        "timestamp": timestamp
    }
    history.append(entry)

    return entry


@app.get("/documents", summary="List all uploaded documents")
def list_documents():
    """Return all documents currently stored in the vector database."""
    docs = engine.list_documents()
    return {"total": len(docs), "documents": docs}


@app.delete("/document/{doc_id}", summary="Remove a document from the vector database")
def delete_document(doc_id: str):
    """
    Delete a document by its doc_id (returned when uploading).
    All chunks belonging to that document are removed from the vector store.
    """
    removed = engine.delete_document(doc_id)
    if removed == 0:
        raise HTTPException(status_code=404, detail=f"No document found with doc_id '{doc_id}'.")
    return {"message": f"Document '{doc_id}' deleted.", "chunks_removed": removed}


@app.get("/history", summary="Get conversation history")
def get_history():
    """Return all questions asked and answers given in this session."""
    return {"total": len(history), "history": history}


@app.delete("/history", summary="Clear conversation history")
def clear_history():
    """Clear all conversation history for this session."""
    history.clear()
    return {"message": "Conversation history cleared."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
