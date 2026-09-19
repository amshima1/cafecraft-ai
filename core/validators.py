"""Reusable validation helpers for CaféCraft AI."""

import re
from numbers import Real

from .exceptions import ValidationError


_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_required_text(value: str, field_name: str = "value") -> str:
    """Return non-empty text or raise a validation error."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} is required and must be non-empty text.")
    return value.strip()


def validate_email(value: str, field_name: str = "email") -> str:
    """Return a normalized email address or raise a validation error."""
    email = validate_required_text(value, field_name)
    if not _EMAIL_PATTERN.fullmatch(email):
        raise ValidationError(f"{field_name} must be a valid email address.")
    return email


def validate_non_negative_number(
    value: Real, field_name: str = "value"
) -> Real:
    """Return a non-negative number or raise a validation error."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValidationError(f"{field_name} must be a number.")
    if value < 0:
        raise ValidationError(f"{field_name} must be non-negative.")
    return value
