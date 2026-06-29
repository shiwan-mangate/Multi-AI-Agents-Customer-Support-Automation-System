# layer_4_analytics/schemas/language_metrics.py

from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator

# Enforce strict system-level synchronization with Layer 3 Subsystems
SupportedISOLanguages = Literal["en", "hi", "es", "fr", "de", "ar"]

CANONICAL_LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ar": "Arabic"
}


class LanguageMetrics(BaseModel):
    """
    Data contract representing a specific language's platform adoption, 
    market volumetric growth vectors, and neural translation pipeline success rates.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "language_code": "hi",
                "language_name": "Hindi",
                "ticket_count": 1240,
                "satisfaction_rate": 89.40,
                "translation_success_rate": 98.70,
                "previous_period_count": 1080,
                "growth_rate": 14.81,
                "period_start": "2026-06-01T00:00:00Z",
                "period_end": "2026-06-30T23:59:59Z"
            }
        }
    )

    # Core Language Identifiers
    language_code: SupportedISOLanguages = Field(
        ...,
        description="The clean standard ISO language code matching the Layer 3 processing system identifiers"
    )
    language_name: str = Field(
        ...,
        description="The canonical human-readable language string name validated against the ISO code map"
    )

    # Volumetric Trailing Load Metrics
    ticket_count: int = Field(
        ...,
        ge=0,
        description="Total absolute number of incoming customer tickets processed using this language"
    )
    satisfaction_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="The rolling customer CSAT percentage derived explicitly from this language's feedback records"
    )
    translation_success_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Critical Layer 3 health KPI: (successful_translations / total_translations) * 100"
    )

    # Trend Analysis and Market Signals
    previous_period_count: int = Field(
        ...,
        ge=0,
        description="Absolute ticket volume recorded for this specific language inside the matching preceding window"
    )
    growth_rate: Optional[float] = Field(
        None,
        description="Period-over-period market growth delta percentage. Stored as None if mathematically undefined (0 historical baseline)"
    )

    # Timezone-Aware Temporal Tracking Context Bounds
    period_start: datetime = Field(
        ...,
        description="The timezone-aware UTC isolation timestamp lower-bound of the language auditing window"
    )
    period_end: datetime = Field(
        ...,
        description="The timezone-aware UTC isolation timestamp upper-bound of the language auditing window"
    )

    @model_validator(mode="after")
    def validate_language_mathematical_and_temporal_integrity(self) -> "LanguageMetrics":
        """
        Enforces algebraic consistency across processing totals, delta calculations, 
        canonical nomenclature rules, and strict timezone-aware UTC bounds.
        """
      
        expected_name = CANONICAL_LANGUAGE_NAMES.get(self.language_code)
        if self.language_name != expected_name:
            raise ValueError(
                f"Nomenclature fragmentation detected: Provided language_name='{self.language_name}' "
                f"does not match standard enterprise mapping for '{self.language_code}' (Expected: '{expected_name}')."
            )

        
        if self.previous_period_count == 0:
            if self.growth_rate is not None:
                raise ValueError(
                    f"Mathematical policy violation for language '{self.language_code}': "
                    f"growth_rate must be explicitly instantiated as None when previous_period_count is 0."
                )
        else:
            if self.growth_rate is not None:
                expected_growth = round(
                    ((self.ticket_count - self.previous_period_count) / self.previous_period_count) * 100.0,
                    2
                )
                
                if abs(self.growth_rate - expected_growth) > 0.1:
                    raise ValueError(
                        f"Market growth rate divergence for language '{self.language_code}': "
                        f"Stated growth_rate={self.growth_rate}% does not match computed value ({expected_growth}%)."
                    )

       
        for dt_field, dt_val in [("period_start", self.period_start), ("period_end", self.period_end)]:
            if dt_val.tzinfo is None:
                raise ValueError(
                    f"Timezone constraint violation for language '{self.language_code}': "
                    f"'{dt_field}' must be explicitly instantiated as a timezone-aware datetime object."
                )
            if dt_val.utcoffset() != timezone.utc.utcoffset(dt_val):
                raise ValueError(
                    f"Data isolation violation for language '{self.language_code}': "
                    f"'{dt_field}' uses a non-UTC offset ({dt_val.tzinfo}). All Layer 4 metrics must be strictly UTC normalized."
                )

        
        if self.period_end < self.period_start:
            raise ValueError(
                f"Temporal chronological inversion for language '{self.language_code}': "
                f"period_end ({self.period_end}) cannot occur prior to period_start ({self.period_start})."
            )

        return self