import os
from langchain_groq import ChatGroq


def get_llm_client():
    """
    Shared LLM dependency provider for escalation services.
    """

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
    )
        