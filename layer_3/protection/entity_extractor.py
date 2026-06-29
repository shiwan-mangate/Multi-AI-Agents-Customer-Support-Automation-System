import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class EntityExtractor:
    """
    Primary Extraction Engine.
    Identifies business-critical entities and normalizes IDs to ensure
    consistent masking across the pipeline.
    """

    SUPPORTED_ENTITY_TYPES = {
        "ORDER_ID", "TICKET_ID", "CUSTOMER_ID", "TRACKING_ID",
        "EMAIL", "PHONE", "URL", "AMOUNT"
    }


    ID_ENTITY_TYPES = {"ORDER_ID", "TICKET_ID", "CUSTOMER_ID", "TRACKING_ID"}

    PATTERNS = {
        "ORDER_ID": re.compile(r'\b(?:#?ORD(?:ER)?-[A-Z0-9]+)\b', re.IGNORECASE),
        "TICKET_ID": re.compile(r'\b(?:#?TKT(?:ICKET)?-[A-Z0-9]+)\b', re.IGNORECASE),
        "CUSTOMER_ID": re.compile(r'\b(?:#?CUS(?:T)?-[A-Z0-9]+)\b', re.IGNORECASE),
        "TRACKING_ID": re.compile(r'\b(?:TRK|SHIP)-[A-Z0-9]+\b', re.IGNORECASE),
        "EMAIL": re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'),
        "PHONE": re.compile(r'(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}'),
        "URL": re.compile(r'https?://[^\s]+|www\.[^\s]+', re.IGNORECASE),
        "AMOUNT": re.compile(r'[$₹€£]\s?\d+(?:\.\d{2})?')
    }

    def extract_entities(self, text: str) -> Dict[str, str]:
        """
        Scans text and returns a mapping of found entity string to its entity type.
        Normalizes IDs (Order/Ticket/Customer/Tracking) to uppercase.
        """
        if not text:
            return {}

        found_entities = {}
        
        for entity_type, pattern in self.PATTERNS.items():
            matches = pattern.finditer(text)
            for match in matches:
                entity_value = match.group(0)
                
                
                if entity_type in self.ID_ENTITY_TYPES:
                    entity_value = entity_value.upper()
                
               
                found_entities[entity_value] = entity_type

       
        logger.info(f"Entity Extraction | Count={len(found_entities)}")
            
        return found_entities