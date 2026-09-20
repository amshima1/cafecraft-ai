"""Validation and construction for application data."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from typing import Any

from core.constants import APPLICATION_STATUSES
from core.exceptions import ValidationError
from core.validators import validate_required_text

from .models import Application


def _optional_text(value: Any, field_name: str) -> str:
    if value is None or value == "":
        return ""
    return validate_required_text(value, field_name)


def _date(value: Any, field_name: str) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError as error:
            raise ValidationError(f"{field_name} must be a valid ISO date.") from error
    raise ValidationError(f"{field_name} must be a valid date.")


def validate_application(data: Application | Mapping[str, Any]) -> Application:
    """Validate raw application data and return an immutable Application."""
    if isinstance(data, Application):
        if data.status not in APPLICATION_STATUSES:
            raise ValidationError("status must be a valid application status.")
        return data
    if not isinstance(data, Mapping):
        raise ValidationError("application data must be a mapping.")
    status = validate_required_text(data.get("status", "saved"), "status")
    if status not in APPLICATION_STATUSES:
        raise ValidationError("status must be a valid application status.")
    return Application(
        application_id=validate_required_text(data.get("application_id"), "application_id"),
        company=validate_required_text(data.get("company"), "company"),
        job_title=validate_required_text(data.get("job_title"), "job_title"),
        job_url=_optional_text(data.get("job_url"), "job_url"),
        location=_optional_text(data.get("location"), "location"),
        status=status,
        date_applied=_date(data.get("date_applied"), "date_applied"),
        resume_version_id=_optional_text(data.get("resume_version_id"), "resume_version_id"),
        cover_letter_id=_optional_text(data.get("cover_letter_id"), "cover_letter_id"),
        notes=_optional_text(data.get("notes"), "notes"),
        follow_up_date=_date(data.get("follow_up_date"), "follow_up_date"),
    )
