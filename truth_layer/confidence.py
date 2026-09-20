"""Bounded, non-probabilistic confidence levels."""

from core.exceptions import ValidationError


CONFIDENCE_LEVELS = ("high", "medium", "low", "unknown")


def confidence_level(status: str) -> str:
    """Map a claim validation status to a bounded confidence level."""
    mapping = {
        "supported": "high",
        "uncertain": "medium",
        "unsupported": "low",
    }
    if status in mapping:
        return mapping[status]
    if status in (None, "") or not isinstance(status, str):
        return "unknown"
    return "unknown"
