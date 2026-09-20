"""Immutable domain models for interview practice."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InterviewQuestion:
    """A question for interview practice and the evidence it requires."""

    question_id: str
    question: str
    category: str
    difficulty: str
    source: str
    evidence_needed: tuple[str, ...] = ()


@dataclass(frozen=True)
class AnswerAnalysis:
    """Deterministic observations about a supplied answer."""

    strengths: tuple[str, ...] = ()
    improvement_areas: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    unsupported_claims: tuple[str, ...] = ()
    recommendations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class PracticeSession:
    """An immutable snapshot of an interview practice session."""

    session_id: str
    question_id: str
    answer: str = ""
    analysis: AnswerAnalysis | None = None
    completed: bool = False
