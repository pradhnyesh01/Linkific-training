"""
Project 4 – Data Extractor
Extracts structured JSON from free-form text.
Supports: invoice, resume, news article
"""

import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv(dotenv_path="../../../.env")

llm= ChatOpenAI(model="gpt-4o-mini", temperature=0)
json_parser = JsonOutputParser()

SCHEMAS = {
    "invoice": "invoice_number, date, client_name, client_email, items (list of {name, amount}), total, due_date",
    "resume":  "name, email, phone, skills (list), education (list of {degree, institution, year}), experience (list of {role, company, years})",
    "news":    "headline, date, author, location, key_facts (list of 3), sentiment (positive/negative/neutral)",
}

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a data extraction assistant. Extract information accurately. Return only valid JSON."),
    ("human",
     "Extract the following fields from the text: {schema}\n\n"
     "If a field is not found, use null.\n\n"
     "Text:\n{text}\n\n"
     "Return only valid JSON.")
])

chain = prompt | llm | json_parser


def extract(text: str, doc_type: str) -> dict:
    if doc_type not in SCHEMAS:
        raise ValueError(f"doc_type must be one of: {list(SCHEMAS.keys())}")
    return chain.invoke({"schema": SCHEMAS[doc_type], "text": text})


# ── Sample texts ─────────────────────────────────────────────────────────────

INVOICE = """
INVOICE #INV-2024-042  |  Date: 5 March 2024
Bill To: Priya Mehta (priya@startup.in)

Services:
- Logo Design: Rs 15,000
- Website Mockup (3 pages): Rs 30,000
- Brand Guidelines Document: Rs 10,000

Total Due: Rs 55,000
Due by: 20 March 2024
"""

RESUME = """
John Doe
doejohn@email.com | +91-9876543210

Skills: Python, Machine Learning, Flask, SQL, LangChain

Education:
  B.Tech Computer Science – Pune University, 2024

Experience:
  ML Intern – Linkific, 2026 (ongoing)
  Data Analyst Intern – InfoCorp, 2023 (6 months)
"""

NEWS = """
ISRO successfully soft-landed Chandrayaan-3 near the lunar south pole on August 23, 2023,
making India the first country to achieve this feat. Reported by Ananya Sharma from Bengaluru,
the lander Vikram deployed rover Pragyan which confirmed sulphur presence on the moon surface.
Scientists called it a historic milestone achieved at a fraction of global mission costs.
"""

SAMPLES = {"invoice": INVOICE, "resume": RESUME, "news": NEWS}


if __name__ == "__main__":
    for doc_type, text in SAMPLES.items():
        print(f"\n{'='*60}")
        print(f"Extracting: {doc_type.upper()}")
        print("-" * 60)
        result = extract(text, doc_type)
        print(json.dumps(result, indent=2))
