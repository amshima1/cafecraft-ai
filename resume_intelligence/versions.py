"""Version tracking for resume snapshots."""

from __future__ import annotations

from datetime import datetime

from core.exceptions import ValidationError

from .models import Resume, ResumeVersion


class ResumeVersionManager:
    """In-memory manager for immutable resume snapshots."""

    def __init__(self) -> None:
        self._versions: dict[str, dict[int, ResumeVersion]] = {}

    def create_version(self, resume: Resume, *, version_id: str | None = None, version_number: int | None = None) -> ResumeVersion:
        if not isinstance(resume, Resume):
            raise ValidationError("resume must be a Resume instance.")
        if version_number is not None and (
            not isinstance(version_number, int) or version_number <= 0
        ):
            raise ValidationError("version_number must be a positive integer.")

        now = datetime.utcnow()
        version_bucket = self._versions.setdefault(resume.resume_id, {})
        next_number = version_number if version_number is not None else max(version_bucket, default=0) + 1
        if next_number in version_bucket:
            raise ValidationError(f"version {next_number} already exists for resume {resume.resume_id}.")

        resolved_version_id = version_id or f"{resume.resume_id}-v{next_number}"
        if any(existing.version_id == resolved_version_id for existing in version_bucket.values()):
            raise ValidationError(f"version_id {resolved_version_id} already exists.")

        version = ResumeVersion(
            version_id=resolved_version_id,
            resume_id=resume.resume_id,
            version_number=next_number,
            created_at=now,
            updated_at=now,
            snapshot=resume,
        )
        version_bucket[next_number] = version
        return version

    def get_version(self, version_id: str) -> ResumeVersion | None:
        for resume_versions in self._versions.values():
            for version in resume_versions.values():
                if version.version_id == version_id:
                    return version
        return None

    def get_versions(self, resume_id: str) -> tuple[ResumeVersion, ...]:
        return tuple(self._versions.get(resume_id, {}).values())

    def get_latest_version(self, resume_id: str) -> ResumeVersion | None:
        versions = self.get_versions(resume_id)
        if not versions:
            return None
        return max(versions, key=lambda item: item.version_number)
