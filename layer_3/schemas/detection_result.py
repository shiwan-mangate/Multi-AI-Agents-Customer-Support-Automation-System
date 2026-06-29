from typing import Optional

from pydantic import BaseModel


class DetectionResult(BaseModel):
    detected_language: str
    confidence: float

    detection_method: str

    script_detected: Optional[str] = None

    mixed_language_detected: bool = False

    raw_detector_results: dict | None = None