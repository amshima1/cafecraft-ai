"""Parser boundary for resume text and structured resume input."""

from __future__ import annotations

from typing import Any

from core.exceptions import ValidationError

from .models import Resume
from .schemas import validate_resume


class ResumeParser:
    """Normalize raw resume input into a validated Resume model."""

    def parse(self, data: Resume | dict[str, Any] | str) -> Resume:
        if isinstance(data, Resume):
            return data
        if isinstance(data, str):
            if not data.strip():
                raise ValidationError("resume text must not be empty.")
            return Resume(
                resume_id="resume-from-text",
                full_name="Unknown",
                email="unknown@example.com",
                summary=data.strip(),
            )
        return validate_resume(data)
