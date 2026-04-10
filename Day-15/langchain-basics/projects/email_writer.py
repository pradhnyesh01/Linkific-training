"""
Project 1 – Email Writer
Takes: topic, tone, recipient
Returns: a complete ready-to-send email
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv(dotenv_path="../../../.env")

llm    = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
parser = StrOutputParser()

# Step 1: Write a draft
draft_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a professional email writer."),
    ("human",
     "Write an email to {recipient} about: {topic}\n"
     "Tone: {tone}\n"
     "Keep it under 100 words. Include subject line.")
])

# Step 2: Check and clean up
review_prompt = ChatPromptTemplate.from_messages([
    ("human",
     "Review this email and fix any grammar issues. "
     "Return only the corrected email, nothing else.\n\n{draft}")
])

# Two-step sequential chain
draft_chain  = draft_prompt  | llm | parser
review_chain = review_prompt | llm | parser

email_chain = draft_chain | (lambda d: {"draft": d}) | review_chain


def write_email(topic: str, tone: str, recipient: str) -> str:
    return email_chain.invoke({
        "topic":     topic,
        "tone":      tone,
        "recipient": recipient
    })


if __name__ == "__main__":
    examples = [
        {
            "topic":     "requesting a one-week deadline extension for the ML project",
            "tone":      "polite and professional",
            "recipient": "manager"
        },
        {
            "topic":     "thanking the team for their help on the internship",
            "tone":      "warm and friendly",
            "recipient": "team members"
        },
    ]

    for ex in examples:
        print(f"\n{'='*60}")
        print(f"Topic    : {ex['topic']}")
        print(f"Tone     : {ex['tone']}")
        print(f"Recipient: {ex['recipient']}")
        print("-" * 60)
        print(write_email(**ex))
