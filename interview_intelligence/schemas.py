"""Validation and construction for Interview Intelligence data."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from core.exceptions import ValidationError
from core.validators import validate_required_text

from .models import AnswerAnalysis, InterviewQuestion, PracticeSession


def _texts(value: Any, field_name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValidationError(f"{field_name} must be a collection.")
    return tuple(
        validate_required_text(item, f"{field_name}[{index}]")
        for index, item in enumerate(value)
    )


def validate_question(data: InterviewQuestion | Mapping[str, Any]) -> InterviewQuestion:
    if isinstance(data, InterviewQuestion):
        return data
    if not isinstance(data, Mapping):
        raise ValidationError("question data must be a mapping.")
    return InterviewQuestion(
        question_id=validate_required_text(data.get("question_id"), "question_id"),
        question=validate_required_text(data.get("question"), "question"),
        category=validate_required_text(data.get("category"), "category"),
        difficulty=validate_required_text(data.get("difficulty"), "difficulty"),
        source=validate_required_text(data.get("source"), "source"),
        evidence_needed=_texts(data.get("evidence_needed", ()), "evidence_needed"),
    )


def validate_analysis(data: AnswerAnalysis | Mapping[str, Any]) -> AnswerAnalysis:
    if isinstance(data, AnswerAnalysis):
        return data
    if not isinstance(data, Mapping):
        raise ValidationError("analysis data must be a mapping.")
    return AnswerAnalysis(
        strengths=_texts(data.get("strengths", ()), "strengths"),
        improvement_areas=_texts(data.get("improvement_areas", ()), "improvement_areas"),
        missing_evidence=_texts(data.get("missing_evidence", ()), "missing_evidence"),
        unsupported_claims=_texts(data.get("unsupported_claims", ()), "unsupported_claims"),
        recommendations=_texts(data.get("recommendations", ()), "recommendations"),
        notes=_texts(data.get("notes", ()), "notes"),
    )


def validate_session(data: PracticeSession | Mapping[str, Any]) -> PracticeSession:
    if isinstance(data, PracticeSession):
        return data
    if not isinstance(data, Mapping):
        raise ValidationError("session data must be a mapping.")
    analysis = data.get("analysis")
    return PracticeSession(
        session_id=validate_required_text(data.get("session_id"), "session_id"),
        question_id=validate_required_text(data.get("question_id"), "question_id"),
        answer="" if analysis is None and data.get("answer") is None else (
            "" if data.get("answer") == "" else validate_required_text(data.get("answer"), "answer")
        ),
        analysis=None if analysis is None else validate_analysis(analysis),
        completed=data.get("completed", False) if isinstance(data.get("completed", False), bool) else (_ for _ in ()).throw(ValidationError("completed must be a boolean.")),
    )
