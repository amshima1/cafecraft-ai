"""Validation and construction helpers for resume data."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from core.exceptions import ValidationError
from core.validators import validate_email, validate_required_text

from .models import Resume, ResumeEntry, ResumeSection


def _text(value: Any, field_name: str, *, required: bool = True) -> str:
    if value is None and not required:
        return ""
    if value == "" and not required:
        return ""
    return validate_required_text(value, field_name)


def _sequence(value: Any, field_name: str) -> tuple[Any, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValidationError(f"{field_name} must be a collection.")
    return tuple(value)


def _text_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    values = _sequence(value, field_name)
    return tuple(_text(item, f"{field_name}[{index}]") for index, item in enumerate(values))


def _entry(value: Any, index: int) -> ResumeEntry:
    if not isinstance(value, Mapping):
        raise ValidationError(f"resume.sections[{index}].entries must be objects.")
    details = _sequence(value.get("details", ()), f"resume.sections[{index}].entries.details")
    dates = _sequence(value.get("dates", ()), f"resume.sections[{index}].entries.dates")
    metadata = _sequence(value.get("metadata", ()), f"resume.sections[{index}].entries.metadata")
    return ResumeEntry(
        title=_text(value.get("title"), f"resume.sections[{index}].entries[{index}].title"),
        content=_text(value.get("content"), f"resume.sections[{index}].entries[{index}].content", required=False),
        details=tuple(_text(item, f"resume.sections[{index}].entries[{index}].details[{offset}]") for offset, item in enumerate(details)),
        dates=tuple(_text(item, f"resume.sections[{index}].entries[{index}].dates[{offset}]") for offset, item in enumerate(dates)),
        metadata=tuple(_text(item, f"resume.sections[{index}].entries[{index}].metadata[{offset}]") for offset, item in enumerate(metadata)),
    )


def _section(value: Any, index: int) -> ResumeSection:
    if not isinstance(value, Mapping):
        raise ValidationError(f"resume.sections[{index}] must be an object.")
    entries = value.get("entries", ())
    if entries is None:
        entries = ()
    return ResumeSection(
        name=_text(value.get("name"), f"resume.sections[{index}].name"),
        entries=tuple(_entry(item, offset) for offset, item in enumerate(_sequence(entries, f"resume.sections[{index}].entries"))),
    )


def validate_resume(data: Resume | Mapping[str, Any]) -> Resume:
    """Validate and normalize raw resume data into an immutable Resume model."""
    if isinstance(data, Resume):
        return data
    if not isinstance(data, Mapping):
        raise ValidationError("resume data must be a mapping.")
    sections = data.get("sections", ())
    if sections is None:
        sections = ()
    return Resume(
        resume_id=_text(data.get("resume_id"), "resume_id"),
        full_name=_text(data.get("full_name"), "full_name"),
        email=validate_email(data.get("email"), "email"),
        summary=_text(data.get("summary"), "summary", required=False),
        skills=_text_tuple(data.get("skills", ()), "skills"),
        sections=tuple(_section(item, offset) for offset, item in enumerate(_sequence(sections, "sections"))),
    )


def validate_version(data: Mapping[str, Any]) -> dict[str, Any]:
    """Validate version metadata and return a normalized dictionary."""
    if not isinstance(data, Mapping):
        raise ValidationError("version data must be a mapping.")
    if "resume_id" not in data or "version_id" not in data or "version_number" not in data:
        raise ValidationError("version_id, resume_id, and version_number are required.")
    version_number = data["version_number"]
    if not isinstance(version_number, int) or version_number <= 0:
        raise ValidationError("version_number must be a positive integer.")
    return {
        "version_id": _text(data.get("version_id"), "version_id"),
        "resume_id": _text(data.get("resume_id"), "resume_id"),
        "version_number": version_number,
        "snapshot": validate_resume(data.get("snapshot")),
    }
