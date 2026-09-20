"""Immutable domain models for application tracking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Application:
    """A user's factual record of one job application."""

    application_id: str
    company: str
    job_title: str
    job_url: str = ""
    location: str = ""
    status: str = "saved"
    date_applied: date | None = None
    resume_version_id: str = ""
    cover_letter_id: str = ""
    notes: str = ""
    follow_up_date: date | None = None


@dataclass(frozen=True)
class ApplicationMetrics:
    """Deterministic counts derived from application records."""

    total_applications: int
    applications_by_status: tuple[tuple[str, int], ...]
    interviews: int
    offers: int
    rejections: int
