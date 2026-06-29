import logging
from typing import Dict
from layer_3.protection.entity_extractor import EntityExtractor
from layer_3.protection.placeholder_manager import PlaceholderManager
from layer_3.protection.format_protector import FormatProtector
from layer_3.schemas.protected_content import ProtectedContent

logger = logging.getLogger(__name__)

class FormatAndEntityProtector:
    """
    Facade for the Protection Layer. 
    Orchestrates format protection and entity masking with strict namespace separation.
    """

    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.placeholder_manager = PlaceholderManager()
        self.format_protector = FormatProtector()

    def protect(self, text: str) -> ProtectedContent:
        if not text:
            return ProtectedContent(
                original_text="",
                protected_text="",
                entity_placeholders={},
                format_placeholders={},
                entity_count=0,
                format_count=0
            )

        try:
         
            extracted_entities = self.entity_extractor.extract_entities(text)
            text_with_entities, entity_map = self.placeholder_manager.create_placeholders(text, extracted_entities)
            
         
            final_protected_text, format_map = self.format_protector.protect_formats(text_with_entities)
            
            logger.info(f"Protection Complete | Entities={len(entity_map)} | Formats={len(format_map)}")
            
            return ProtectedContent(
                original_text=text,
                protected_text=final_protected_text,
                entity_placeholders=entity_map,
                format_placeholders=format_map,
                entity_count=len(entity_map),
                format_count=len(format_map)
            )

        except Exception as e:
            logger.error(
                f"CRITICAL: Protection failed | TextLength={len(text)} | Error={e}", 
                exc_info=True
            )
            return ProtectedContent(
                original_text=text,
                protected_text=text,
                entity_placeholders={},
                format_placeholders={},
                entity_count=0,
                format_count=0
            )

    def restore(self, translated_text: str, content: ProtectedContent) -> str:
        try:
           
            restored = self.format_protector.restore_formats(
                translated_text, 
                content.format_placeholders
            )
         
            restored = self.placeholder_manager.restore_placeholders(
                restored, 
                content.entity_placeholders
            )
            
            logger.info("Protection Restore Complete")
            return restored
        except Exception as e:
            logger.error(f"CRITICAL: Restoration failed | Error={e}", exc_info=True)
            return translated_text