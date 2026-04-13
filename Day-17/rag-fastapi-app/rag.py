"""
RAG Engine – handles embeddings, ChromaDB storage, retrieval, and LLM answer generation.
"""

import os
import uuid
from datetime import datetime
from openai import OpenAI
import chromadb

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL  = "gpt-4o-mini"
DB_PATH     = "./chroma_db"

RAG_PROMPT = """\
Answer the question using only the context below.
If the answer is not in the context, say "I don't have information about that in the uploaded documents."

Context:
{context}

Question: {question}
Answer:"""


class RAGEngine:
    def __init__(self):
        self.openai     = OpenAI()
        self.chroma     = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.chroma.get_or_create_collection(name="documents")

    # ── Embeddings ────────────────────────────────────────────────────────────

    def _embed(self, text: str) -> list[float]:
        """Get OpenAI embedding for a single text string."""
        response = self.openai.embeddings.create(model=EMBED_MODEL, input=text)
        return response.data[0].embedding

    # ── Document Management ───────────────────────────────────────────────────

    def add_document(self, chunks: list[str], filename: str) -> dict:
        """Embed all chunks and store them in ChromaDB. Returns document metadata."""
        doc_id      = str(uuid.uuid4())[:8]
        upload_time = datetime.utcnow().isoformat() + "Z"

        embeddings = [self._embed(chunk) for chunk in chunks]
        ids        = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas  = [
            {"doc_id": doc_id, "filename": filename,
             "chunk_index": i, "upload_time": upload_time}
            for i in range(len(chunks))
        ]

        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

        return {"doc_id": doc_id, "filename": filename,
                "chunks": len(chunks), "upload_time": upload_time}

    def list_documents(self) -> list[dict]:
        """Return one entry per unique document (deduplicated from chunk metadata)."""
        if self.collection.count() == 0:
            return []

        all_meta = self.collection.get(include=["metadatas"])["metadatas"]
        seen     = {}
        for m in all_meta:
            doc_id = m["doc_id"]
            if doc_id not in seen:
                seen[doc_id] = {
                    "doc_id":      doc_id,
                    "filename":    m["filename"],
                    "upload_time": m["upload_time"],
                }
        return list(seen.values())

    def delete_document(self, doc_id: str) -> int:
        """Delete all chunks belonging to a document. Returns number of chunks removed."""
        all_data = self.collection.get(include=["metadatas"])
        ids_to_delete = [
            chunk_id
            for chunk_id, meta in zip(all_data["ids"], all_data["metadatas"])
            if meta["doc_id"] == doc_id
        ]

        if not ids_to_delete:
            return 0

        self.collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)

    # ── Query ─────────────────────────────────────────────────────────────────

    def query(self, question: str, n_results: int = 3) -> dict:
        """Retrieve relevant chunks and generate an answer from the LLM."""
        if self.collection.count() == 0:
            return {
                "answer":  "No documents uploaded yet. Please upload a document first.",
                "sources": []
            }

        query_embedding = self._embed(question)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count())
        )

        chunks    = results["documents"][0]
        metadatas = results["metadatas"][0]

        # Build context from retrieved chunks
        context = "\n\n---\n\n".join(chunks)

        # Call LLM
        response = self.openai.chat.completions.create(
            model=CHAT_MODEL,
            temperature=0,
            messages=[
                {"role": "user", "content": RAG_PROMPT.format(
                    context=context, question=question
                )}
            ]
        )

        answer = response.choices[0].message.content.strip()

        # Deduplicate sources
        seen_sources = set()
        sources = []
        for m in metadatas:
            key = (m["doc_id"], m["filename"])
            if key not in seen_sources:
                seen_sources.add(key)
                sources.append({"doc_id": m["doc_id"], "filename": m["filename"]})

        return {"answer": answer, "sources": sources}
