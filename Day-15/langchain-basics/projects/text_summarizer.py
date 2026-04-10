"""
Project 2 – Text Summarizer with Custom Instructions
Supports different summary styles: bullet, tldr, executive, eli5
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv(dotenv_path="../../../.env")

llm    = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
parser = StrOutputParser()

# Style instructions injected as a variable
STYLES = {
    "bullet":    "Summarize as 5 concise bullet points. Each bullet max 15 words.",
    "tldr":      "Write a single TL;DR sentence of max 25 words.",
    "executive": "Write an executive summary: Context (1 line), Key Points (3 bullets), Action (1 line).",
    "eli5":      "Explain this like I am 10 years old. Use simple words, max 3 sentences.",
}

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a precise text summarizer. Follow the instruction exactly."),
    ("human",
     "Instruction: {instruction}\n\n"
     "Text to summarize:\n{text}")
])

chain = prompt | llm | parser


def summarize(text: str, style: str = "bullet") -> str:
    if style not in STYLES:
        raise ValueError(f"Style must be one of: {list(STYLES.keys())}")
    return chain.invoke({
        "instruction": STYLES[style],
        "text":        text
    })


SAMPLE_TEXT = """
India's space agency ISRO successfully launched the Chandrayaan-3 mission on July 14, 2023.
The spacecraft consisted of a lander named Vikram and a rover named Pragyan.
After a journey of about 40 days, Chandrayaan-3 made a historic soft landing near the lunar
south pole on August 23, 2023. India became the fourth country to land on the Moon and the
first to land near the south pole. The Pragyan rover deployed from Vikram and collected data
on soil composition and temperature. ISRO scientists confirmed the presence of sulphur on
the lunar surface for the first time. The mission cost approximately Rs 615 crore.
"""

if __name__ == "__main__":
    for style in STYLES:
        print(f"\n{'='*60}")
        print(f"Style: {style.upper()}")
        print("-" * 60)
        print(summarize(SAMPLE_TEXT, style=style))
