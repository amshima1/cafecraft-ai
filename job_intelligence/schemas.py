"""Validation and conversion of structured AI responses."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from core.exceptions import ValidationError

from .models import ATSAnalysisResult, JobAnalysisResult, JobGapAnalysisResult, JobMatchingResult


def _payload(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError("AI response must be a JSON object.")
    return value


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValidationError(f"AI response field '{field_name}' must be an array of text.")
    return [item.strip() for item in value]


def _fields(payload: Any, names: Iterable[str]) -> dict[str, list[str]]:
    data = _payload(payload)
    return {name: _string_list(data.get(name, []), name) for name in names}


def validate_job_analysis(payload: Any) -> JobAnalysisResult:
    return JobAnalysisResult(**_fields(payload, JobAnalysisResult.__dataclass_fields__))


def validate_job_matching(payload: Any) -> JobMatchingResult:
    return JobMatchingResult(**_fields(payload, JobMatchingResult.__dataclass_fields__))


def validate_ats_analysis(payload: Any) -> ATSAnalysisResult:
    data = _payload(payload)
    values = _fields(data, ATSAnalysisResult.__dataclass_fields__ - {"ats_score_statement"})
    statement = data.get("ats_score_statement")
    if statement != "No exact ATS score is predicted.":
        raise ValidationError("ats_score_statement must state that no exact ATS score is predicted.")
    return ATSAnalysisResult(**values, ats_score_statement=statement)


def validate_gap_analysis(payload: Any) -> JobGapAnalysisResult:
    return JobGapAnalysisResult(**_fields(payload, JobGapAnalysisResult.__dataclass_fields__))
