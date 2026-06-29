import json
import re
import logging
from typing import Any, Dict, Optional


logger = logging.getLogger("parser")

def extract_json(raw_response: str) -> str:
    """
    Isolates and extracts a JSON string from messy LLM output.
    Handles markdown wrappers, conversational filler, and trailing text.
    """
   
    if not isinstance(raw_response, str):
        logger.error(f"Expected string for extraction, got {type(raw_response)}")
        return ""

    
    markdown_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(markdown_pattern, raw_response, re.IGNORECASE)
    
    if match:
        logger.debug("Extracted JSON from markdown block.")
        return match.group(1).strip()
    
    
    try:
        start_index = raw_response.find("{")
        end_index = raw_response.rfind("}") + 1

        if start_index != -1 and end_index > start_index:
            json_str = raw_response[start_index:end_index]
            logger.debug("Extracted JSON via curly brace anchoring.")
            return json_str
    except Exception as e:
        logger.warning(f"JSON extraction fallback failed: {str(e)}")

    
    return raw_response.strip()


def load_json(json_str: str) -> Optional[Dict[str, Any]]:
    """
    Parses a JSON string into a dictionary with robust error handling.
    Returns None if parsing fails to trigger explicit retry logic.
    """
    if not json_str or not isinstance(json_str, str):
        logger.warning("Invalid or empty input provided for JSON parsing.")
        return None
        
    try:
        clean_str = extract_json(json_str)
        
        data = json.loads(clean_str)
        logger.info("Successfully parsed LLM JSON response.")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)} | Snippet: {json_str[:50]}...")
        return None
    except Exception as e:
        logger.critical(f"Unexpected error during JSON parsing: {str(e)}")
        return None