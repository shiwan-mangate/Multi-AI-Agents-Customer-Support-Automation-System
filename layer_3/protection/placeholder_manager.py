import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class PlaceholderManager:
    """
    Manages the transformation between sensitive entities and safe placeholders.
    Creates a registry for translation and provides the logic to restore original data.
    """

    def create_placeholders(self, text: str, entities: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
        """
        Converts extracted entities into placeholders and returns the protected text
        and a restoration map.
        
        Args:
            text: Original raw text.
            entities: Dict of {entity_value: entity_type} from EntityExtractor.
            
        Returns:
            Tuple: 
                1. protected_text
                2. restoration_map: e.g., {"__EMAIL_1__": "john@gmail.com"}
        """
        protected_text = text
        restoration_map: Dict[str, str] = {}
        
        counters: Dict[str, int] = {}
        
       
        sorted_entities = sorted(entities.keys(), key=len, reverse=True)
        
        for entity_value in sorted_entities:
            entity_type = entities[entity_value]
            
          
            if entity_type not in counters:
                counters[entity_type] = 1
            
            
            placeholder = f"__{entity_type}_{counters[entity_type]}__"
            
        
            restoration_map[placeholder] = entity_value
            
           
            protected_text = re.sub(re.escape(entity_value), placeholder, protected_text)
            
     
            counters[entity_type] += 1
            
        logger.info(f"Placeholder Manager | Created {len(restoration_map)} placeholders.")
        return protected_text, restoration_map

    def restore_placeholders(self, text: str, restoration_map: Dict[str, str]) -> str:
        """
        Takes the translated text and the restoration map, and swaps the 
        placeholders back to their original values.
        """
        if not text or not restoration_map:
            return text

        restored_text = text
        
   
        sorted_placeholders = sorted(restoration_map.keys(), key=len, reverse=True)
        
        for placeholder in sorted_placeholders:
            original_value = restoration_map[placeholder]
            
            
            if placeholder not in restored_text:
                logger.warning(f"Translation anomaly: Placeholder {placeholder} dropped by LLM.")
                continue
                
      
            restored_text = re.sub(re.escape(placeholder), original_value, restored_text)

        return restored_text