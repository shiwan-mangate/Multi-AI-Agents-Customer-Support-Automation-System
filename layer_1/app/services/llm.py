from langchain_groq import ChatGroq
from app.utils.config import GROQ_API_KEY

# Master Level Configuration
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    groq_api_key=GROQ_API_KEY,
    temperature=0,
    max_retries=2,          
    timeout=30,             
    max_tokens=None,       
)
