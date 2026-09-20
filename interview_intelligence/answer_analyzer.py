"""Deterministic answer observations for interview practice."""

from __future__ import annotations

import re

from core.validators import validate_required_text

from .models import AnswerAnalysis, InterviewQuestion


class AnswerAnalyzer:
    """Analyze only the supplied question, answer, and optional verified context."""

    _evidence_pattern = re.compile(r"\b\d+(?:%|\+)?\b|\b(increased|reduced|built|implemented|delivered|achieved|led)\b", re.I)

    def analyze(
        self,
        question: InterviewQuestion,
        answer: str,
        *,
        supplied_context: tuple[str, ...] = (),
    ) -> AnswerAnalysis:
        answer = "" if answer is None else answer
        if not isinstance(answer, str) or not answer.strip():
            return AnswerAnalysis(
                improvement_areas=("Provide an answer to the question.",),
                missing_evidence=("No answer was supplied.",),
                recommendations=("Use a specific situation, action, and result.",),
                notes=(f"Question analyzed: {question.question_id}",),
            )
        text = answer.strip()
        has_evidence = bool(self._evidence_pattern.search(text))
        claims = ()
        if supplied_context:
            claims = tuple(
                phrase for phrase in supplied_context
                if phrase and phrase.lower() not in text.lower()
            )
        return AnswerAnalysis(
            strengths=("A response was supplied.",) + (("The answer includes a concrete result or action.",) if has_evidence else ()),
            improvement_areas=() if has_evidence else ("Add a concrete action and result.",),
            missing_evidence=() if has_evidence else ("Specific evidence or measurable outcome.",),
            unsupported_claims=claims,
            recommendations=() if has_evidence else ("Use a specific example and explain the outcome.",),
            notes=(f"Question analyzed: {question.question_id}",),
        )
