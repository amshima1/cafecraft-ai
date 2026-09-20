"""Immutable domain models for resumed career information."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ResumeEntry:
    """A single resume entry within a section."""

    title: str
    content: str = ""
    details: tuple[str, ...] = ()
    dates: tuple[str, ...] = ()
    metadata: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResumeSection:
    """A named grouping within a resume."""

    name: str
    entries: tuple[ResumeEntry, ...] = ()


@dataclass(frozen=True)
class Resume:
    """A structured resume seen as a verified source-of-truth snapshot."""

    resume_id: str
    full_name: str
    email: str
    summary: str = ""
    skills: tuple[str, ...] = ()
    sections: tuple[ResumeSection, ...] = ()


@dataclass(frozen=True)
class ResumeVersion:
    """An immutable snapshot of a resume at a specific version."""

    version_id: str
    resume_id: str
    version_number: int
    created_at: datetime
    updated_at: datetime
    snapshot: Resume
