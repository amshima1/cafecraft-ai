"""Immutable domain models for verified career information."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class WorkExperience:
    employer: str
    job_title: str
    start_date: date
    end_date: date | None = None
    description: str = ""
    skills: tuple[str, ...] = ()


@dataclass(frozen=True)
class Education:
    institution: str
    degree: str
    field_of_study: str = ""
    start_date: date | None = None
    end_date: date | None = None
    details: str = ""


@dataclass(frozen=True)
class Certification:
    name: str
    issuer: str
    issue_date: date | None = None
    expiration_date: date | None = None
    credential_id: str = ""


@dataclass(frozen=True)
class Project:
    name: str
    description: str
    technologies: tuple[str, ...] = ()
    url: str = ""


@dataclass(frozen=True)
class Achievement:
    title: str
    description: str
    date: date | None = None


@dataclass(frozen=True)
class CareerProfile:
    profile_id: str
    full_name: str
    email: str
    phone: str = ""
    location: str = ""
    professional_summary: str = ""
    work_experience: tuple[WorkExperience, ...] = ()
    education: tuple[Education, ...] = ()
    skills: tuple[str, ...] = ()
    certifications: tuple[Certification, ...] = ()
    projects: tuple[Project, ...] = ()
    achievements: tuple[Achievement, ...] = ()
    languages: tuple[str, ...] = ()
    portfolio_links: tuple[str, ...] = ()
