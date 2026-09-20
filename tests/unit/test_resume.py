"""Application service for resume validation, creation, and versioning."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from career_profile.models import CareerProfile
from core.exceptions import ValidationError
from core.validators import validate_required_text

from .builder import ResumeBuilder
from .models import Resume, ResumeVersion
from .parser import ResumeParser
from .schemas import validate_resume
from .versions import ResumeVersionManager


class ResumeService:
    """Coordinate resume validation, construction, and version management."""

    def __init__(self, version_manager: ResumeVersionManager | None = None) -> None:
        self._version_manager = version_manager or ResumeVersionManager()
        self._parser = ResumeParser()
        self._builder = ResumeBuilder()
        self._resumes: dict[str, Resume] = {}

    def create_resume(self, data: Resume | Mapping[str, Any]) -> Resume:
        resume = validate_resume(data)
        self._resumes[resume.resume_id] = resume
        return resume

    def get_resume(self, resume_id: str) -> Resume | None:
        return self._resumes.get(validate_required_text(resume_id, "resume_id"))

    def build_from_career_profile(self, profile: CareerProfile) -> Resume:
        if not isinstance(profile, CareerProfile):
            raise ValidationError("profile must be a CareerProfile instance.")
        resume = self._builder.build_from_profile(profile)
        self._resumes[resume.resume_id] = resume
        return resume

    def create_version(self, resume: Resume, *, version_id: str | None = None, version_number: int | None = None) -> ResumeVersion:
        if not isinstance(resume, Resume):
            resume = validate_resume(resume)
        if resume.resume_id not in self._resumes:
            self._resumes[resume.resume_id] = resume
        return self._version_manager.create_version(resume, version_id=version_id, version_number=version_number)

    def get_version(self, version_id: str) -> ResumeVersion | None:
        return self._version_manager.get_version(validate_required_text(version_id, "version_id"))

    def get_versions(self, resume_id: str) -> tuple[ResumeVersion, ...]:
        return self._version_manager.get_versions(validate_required_text(resume_id, "resume_id"))

    def get_latest_version(self, resume_id: str) -> ResumeVersion | None:
        return self._version_manager.get_latest_version(validate_required_text(resume_id, "resume_id"))

    def parse_resume(self, raw: Resume | Mapping[str, Any] | str) -> Resume:
        return self._parser.parse(raw)
