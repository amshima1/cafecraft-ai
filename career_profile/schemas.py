"""Validation and construction for Career Profile data."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

from core.exceptions import ValidationError
from core.validators import validate_email, validate_required_text

from .models import Achievement, CareerProfile, Certification, Education, Project, WorkExperience


def _text(value: Any, field_name: str, *, required: bool = True) -> str:
    if value is None and not required:
        return ""
    if not required and value == "":
        return ""
    return validate_required_text(value, field_name)


def _date(value: Any, field_name: str, *, required: bool = False) -> date | None:
    if value is None or (value == "" and not required):
        if required:
            raise ValidationError(f"{field_name} is required.")
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError as error:
            raise ValidationError(f"{field_name} must be a valid ISO date.") from error
    raise ValidationError(f"{field_name} must be a valid date.")


def _list(value: Any, field_name: str) -> tuple[Any, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValidationError(f"{field_name} must be a collection.")
    return tuple(value)


def _text_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    return tuple(_text(item, f"{field_name}[{index}]") for index, item in enumerate(_list(value, field_name)))


def _mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationError(f"{field_name} must be an object.")
    return value


def _work(value: Any, index: int) -> WorkExperience:
    data = _mapping(value, f"work_experience[{index}]")
    return WorkExperience(
        employer=_text(data.get("employer"), f"work_experience[{index}].employer"),
        job_title=_text(data.get("job_title"), f"work_experience[{index}].job_title"),
        start_date=_date(data.get("start_date"), f"work_experience[{index}].start_date", required=True),
        end_date=_date(data.get("end_date"), f"work_experience[{index}].end_date"),
        description=_text(data.get("description"), f"work_experience[{index}].description", required=False),
        skills=_text_tuple(data.get("skills", ()), f"work_experience[{index}].skills"),
    )


def _education(value: Any, index: int) -> Education:
    data = _mapping(value, f"education[{index}]")
    start = _date(data.get("start_date"), f"education[{index}].start_date")
    end = _date(data.get("end_date"), f"education[{index}].end_date")
    if start and end and end < start:
        raise ValidationError(f"education[{index}].end_date cannot precede start_date.")
    return Education(
        institution=_text(data.get("institution"), f"education[{index}].institution"),
        degree=_text(data.get("degree"), f"education[{index}].degree"),
        field_of_study=_text(data.get("field_of_study"), f"education[{index}].field_of_study", required=False),
        start_date=start,
        end_date=end,
        details=_text(data.get("details"), f"education[{index}].details", required=False),
    )


def _certification(value: Any, index: int) -> Certification:
    data = _mapping(value, f"certifications[{index}]")
    issue = _date(data.get("issue_date"), f"certifications[{index}].issue_date")
    expiration = _date(data.get("expiration_date"), f"certifications[{index}].expiration_date")
    if issue and expiration and expiration < issue:
        raise ValidationError(f"certifications[{index}].expiration_date cannot precede issue_date.")
    return Certification(
        name=_text(data.get("name"), f"certifications[{index}].name"),
        issuer=_text(data.get("issuer"), f"certifications[{index}].issuer"),
        issue_date=issue,
        expiration_date=expiration,
        credential_id=_text(data.get("credential_id"), f"certifications[{index}].credential_id", required=False),
    )


def _project(value: Any, index: int) -> Project:
    data = _mapping(value, f"projects[{index}]")
    return Project(
        name=_text(data.get("name"), f"projects[{index}].name"),
        description=_text(data.get("description"), f"projects[{index}].description"),
        technologies=_text_tuple(data.get("technologies", ()), f"projects[{index}].technologies"),
        url=_text(data.get("url"), f"projects[{index}].url", required=False),
    )


def _achievement(value: Any, index: int) -> Achievement:
    data = _mapping(value, f"achievements[{index}]")
    return Achievement(
        title=_text(data.get("title"), f"achievements[{index}].title"),
        description=_text(data.get("description"), f"achievements[{index}].description"),
        date=_date(data.get("date"), f"achievements[{index}].date"),
    )


def validate_profile(data: CareerProfile | Mapping[str, Any]) -> CareerProfile:
    """Validate raw profile data and return an immutable domain model."""
    if isinstance(data, CareerProfile):
        return data
    values = _mapping(data, "profile")
    work = tuple(_work(item, index) for index, item in enumerate(_list(values.get("work_experience", ()), "work_experience")))
    education = tuple(_education(item, index) for index, item in enumerate(_list(values.get("education", ()), "education")))
    certifications = tuple(_certification(item, index) for index, item in enumerate(_list(values.get("certifications", ()), "certifications")))
    projects = tuple(_project(item, index) for index, item in enumerate(_list(values.get("projects", ()), "projects")))
    achievements = tuple(_achievement(item, index) for index, item in enumerate(_list(values.get("achievements", ()), "achievements")))
    return CareerProfile(
        profile_id=_text(values.get("profile_id"), "profile_id"),
        full_name=_text(values.get("full_name"), "full_name"),
        email=validate_email(values.get("email"), "email"),
        phone=_text(values.get("phone"), "phone", required=False),
        location=_text(values.get("location"), "location", required=False),
        professional_summary=_text(values.get("professional_summary"), "professional_summary", required=False),
        work_experience=work,
        education=education,
        skills=_text_tuple(values.get("skills", ()), "skills"),
        certifications=certifications,
        projects=projects,
        achievements=achievements,
        languages=_text_tuple(values.get("languages", ()), "languages"),
        portfolio_links=_text_tuple(values.get("portfolio_links", ()), "portfolio_links"),
    )
