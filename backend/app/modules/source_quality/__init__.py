"""Source Quality Pipeline - domain scoring, freshness, dedup, diversity."""
from app.modules.source_quality.service import SourceQualityService

__all__ = ["SourceQualityService"]
