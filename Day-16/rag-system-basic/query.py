"""
Query Interface – ask questions against the RAG vector store from the terminal.

Usage:
    python query.py                    # interactive mode
    python query.py "your question"    # single question mode

Build the vector store first by running all cells in rag-pipeline.ipynb.
"""

import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv(dotenv_path="../../.env")

DB_PATH = "./chroma_rag_db"

def build_rag_chain():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Vector store not found at '{DB_PATH}'.")
        print("Run rag-pipeline.ipynb first to build the index.")
        sys.exit(1)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    retriever   = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm         = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "Answer the question using only the context below. "
            "If the answer is not in the context, say 'I don't have information about that.'\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n"
            "Answer:"
        )
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )


def ask(chain, question: str):
    result  = chain.invoke({"query": question})
    sources = {os.path.basename(d.metadata["source"]) for d in result["source_documents"]}
    print(f"\nAnswer  : {result['result']}")
    print(f"Sources : {', '.join(sources)}\n")


def main():
    chain = build_rag_chain()
    print(f"RAG ready. Loaded from: {DB_PATH}")

    # Single question mode
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"\nQuestion: {question}")
        ask(chain, question)
        return

    # Interactive mode
    print("Type your question (or 'quit' to exit):\n")
    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() == "quit":
            break
        ask(chain, question)


if __name__ == "__main__":
    main()
