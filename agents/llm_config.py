# agents/llm_config.py
# Shared helper: connects to Groq's free AI model.
# All 4 agents import this instead of repeating connection code.

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load the .env file so we can read our secret GROQ_API_KEY
load_dotenv()


def get_llm(temperature: float = 0.3):
    """
    Returns a connected Groq LLM.
    temperature: 0 = very factual/strict, 1 = more creative. We use low values for research accuracy.
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("❌ GROQ_API_KEY not found! Check your .env file.")

    llm = ChatGroq(
        api_key=api_key,
        model="llama-3.1-8b-instant",  # free, fast Groq model
        temperature=temperature
    )
    return llm