import os
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "CRITICAL: GROQ_API_KEY is missing. "
        "Please ensure your .env file is present and contains the key."
    )

logger.info("Environment variables loaded successfully.")