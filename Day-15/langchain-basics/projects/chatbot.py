"""
Project 3 – Conversational Chatbot with Memory
Runs in the terminal. Type 'quit' to exit, 'reset' to clear memory.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts import PromptTemplate

load_dotenv(dotenv_path="../../../.env")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def make_conversation(persona: str = "helpful assistant") -> ConversationChain:
    """Create a fresh conversation chain with the given persona."""
    memory = ConversationBufferMemory(return_messages=False)

    # Custom prompt that includes persona + history
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=(
            f"You are a {persona}. Be concise — reply in 2-3 sentences max.\n\n"
            "Conversation so far:\n{history}\n"
            "Human: {input}\n"
            "Assistant:"
        )
    )

    return ConversationChain(llm=llm, memory=memory, prompt=prompt, verbose=False)


def run_chatbot():
    print("=" * 50)
    print("  LangChain Chatbot with Memory")
    print("  Commands: 'quit' to exit | 'reset' to clear memory | 'history' to view chat")
    print("=" * 50)

    persona = input("Enter chatbot persona (press Enter for 'helpful assistant'): ").strip()
    if not persona:
        persona = "helpful assistant"

    conversation = make_conversation(persona)
    print(f"\nChatbot ready as: {persona}\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "reset":
            conversation = make_conversation(persona)
            print("Memory cleared. Starting fresh.\n")
            continue
        if user_input.lower() == "history":
            print("\n--- Chat History ---")
            print(conversation.memory.buffer or "(empty)")
            print("--------------------\n")
            continue

        response = conversation.predict(input=user_input)
        print(f"Bot: {response}\n")


if __name__ == "__main__":
    run_chatbot()
