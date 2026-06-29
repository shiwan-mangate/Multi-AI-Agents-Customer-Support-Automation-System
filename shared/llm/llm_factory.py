# shared/llm/llm_factory.py

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

@lru_cache(maxsize=1)
def build_llm() -> BaseChatModel:
    """
    Centralized LLM factory.

    Benefits:
    - Single reusable LLM instance
    - Easy model swapping
    - Centralized configuration
    - Cached (singleton-like behavior)

    Returns:
        BaseChatModel
    """

    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables."
        )

    return ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=groq_api_key,
        temperature=0,
        max_retries=2,
        timeout=30,
        max_tokens=None
    )


def get_llm() -> BaseChatModel:
    """
    Convenience wrapper.

    Usage:
        llm = get_llm()
    """
    return build_llm()