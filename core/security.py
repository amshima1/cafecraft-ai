"""Security helpers for safely handling sensitive values."""

from __future__ import annotations

from typing import Any


def has_sensitive_value(value: Any) -> bool:
    """Return whether a value appears to contain sensitive data."""
    if value is None:
        return False
    if isinstance(value, str):
        cleaned = value.strip()
        return bool(cleaned) and cleaned.lower() not in {"null", "none", "n/a", ""}
    return True


def mask_secret(value: Any, *, visible_chars: int = 4, placeholder: str = "***") -> str:
    """Mask a secret value while preserving a short preview for logs."""
    if value is None:
        return "None"

    text = str(value)
    if not text:
        return placeholder

    if len(text) <= visible_chars:
        return placeholder

    if visible_chars <= 0:
        return placeholder

    prefix = text[:visible_chars]
    suffix = text[-visible_chars:] if visible_chars < len(text) else ""
    return f"{prefix}{placeholder}{suffix}" if suffix else f"{prefix}{placeholder}"
