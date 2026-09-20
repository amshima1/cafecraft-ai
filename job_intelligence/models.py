"""Typed domain models for job intelligence workflows."""

from __future__ import annotations

from dataclasses import dataclass, field


def _items() -> list[str]:
    return field(default_factory=list)


@dataclass(frozen=True)
class JobRequirement:
    """A requirement extracted from a job description."""

    text: str
    category: str
    required: bool = True


@dataclass(frozen=True)
class JobAnalysisResult:
    responsibilities: list[str] = field(default_factory=list)
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    qualifications: list[str] = field(default_factory=list)
    experience_requirements: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    other_requirements: list[str] = field(default_factory=list)
    missing_or_ambiguous_information: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class JobMatchingResult:
    matches: list[str] = field(default_factory=list)
    missing_requirements: list[str] = field(default_factory=list)
    uncertain_requirements: list[str] = field(default_factory=list)
    evidence_needed: list[str] = field(default_factory=list)
    candidate_strengths: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ATSAnalysisResult:
    relevant_keywords: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    unrepresented_keywords: list[str] = field(default_factory=list)
    alignment_issues: list[str] = field(default_factory=list)
    supported_improvements: list[str] = field(default_factory=list)
    verification_needed: list[str] = field(default_factory=list)
    ats_score_statement: str = "No exact ATS score is predicted."


@dataclass(frozen=True)
class JobGapAnalysisResult:
    confirmed_gaps: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    supported_requirements: list[str] = field(default_factory=list)
    evidence_needed: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
