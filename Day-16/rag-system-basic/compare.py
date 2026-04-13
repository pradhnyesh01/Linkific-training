"""
Direct LLM vs RAG Comparison
Shows how RAG gives more accurate, document-grounded answers.

Run after building the vector store via rag-pipeline.ipynb.
"""

import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv(dotenv_path="../../.env")

DB_PATH = "./chroma_rag_db"

# ── Setup ─────────────────────────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Direct LLM chain (no retrieval)
direct_chain = (
    ChatPromptTemplate.from_messages([("human", "{question}")])
    | llm
    | StrOutputParser()
)

# RAG chain
if not os.path.exists(DB_PATH):
    print(f"ERROR: Vector store not found at '{DB_PATH}'.")
    print("Run rag-pipeline.ipynb first.")
    sys.exit(1)

embeddings  = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
retriever   = vectorstore.as_retriever(search_kwargs={"k": 3})

rag_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "Answer the question using only the context below. "
        "If the answer is not in the context, say 'I don't have information about that.'\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\nAnswer:"
    )
)

rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": rag_prompt},
    return_source_documents=True
)

# ── Test Questions ────────────────────────────────────────────────────────────

QUESTIONS = [
    "What is the exact cost of the Chandrayaan-3 mission in rupees?",
    "What record did PSLV-C37 set in 2017?",
    "What are the solutions for overfitting listed in the ML document?",
    "What is Aditya-L1 and what does it study?",
    "How do Python generators save memory?",
]

# ── Run Comparison ────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("  COMPARISON: Direct LLM  vs  RAG")
print("=" * 70)

for q in QUESTIONS:
    print(f"\nQUESTION: {q}")
    print("-" * 70)

    direct_answer = direct_chain.invoke({"question": q})
    print(f"DIRECT LLM:\n{direct_answer.strip()}")

    rag_result = rag_chain.invoke({"query": q})
    sources = {os.path.basename(d.metadata["source"]) for d in rag_result["source_documents"]}
    print(f"\nRAG (sources: {', '.join(sources)}):\n{rag_result['result'].strip()}")
    print()
