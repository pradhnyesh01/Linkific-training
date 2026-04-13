# Day 16 – Embeddings, Vector DB & RAG

## Setup
```bash
pip install chromadb faiss-cpu sentence-transformers langchain langchain-openai langchain-community python-dotenv
```
Uses `OPENAI_API_KEY` from Day-14 `.env`.

## Deliverables

| File | Description |
|---|---|
| `embeddings-basics.ipynb` | Embeddings, cosine/euclidean similarity, ChromaDB, FAISS |
| `rag-pipeline.ipynb` | Full RAG: load → split → embed → store → retrieve → generate |
| `query.py` | Terminal query interface for the built vector store |
| `compare.py` | Direct LLM vs RAG comparison on 5 test questions |
| `documents/` | 3 knowledge base files (ml_concepts, python_tips, india_space) |
| `README.md` | RAG architecture + concept reference |

## Concepts Covered

### Embeddings
- Text → fixed-size vector of floats representing meaning
- Similar meaning → similar vectors (close in vector space)
- Model used: `text-embedding-3-small` (OpenAI) for RAG, `all-MiniLM-L6-v2` (sentence-transformers) for basics

### Vector Similarity
- **Cosine similarity**: angle between vectors, range -1 to 1. Preferred for text.
- **Euclidean distance**: straight-line distance. Lower = more similar.

### ChromaDB
- Vector database that stores both text and embeddings
- `chromadb.Client()` for in-memory, `PersistentClient(path=...)` for disk
- `collection.add()` to insert, `collection.query()` to search

### FAISS
- Meta's fast nearest-neighbour library — stores vectors only
- `IndexFlatL2` for exact search, scalable to millions of vectors

### RAG Pipeline
1. **Load** documents with `DirectoryLoader`
2. **Split** into chunks with `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)`
3. **Embed** chunks with `OpenAIEmbeddings`
4. **Store** in `Chroma.from_documents()`
5. **Retrieve** with `vectorstore.as_retriever(search_kwargs={"k": 3})`
6. **Generate** with `RetrievalQA` — injects retrieved chunks into prompt as context
