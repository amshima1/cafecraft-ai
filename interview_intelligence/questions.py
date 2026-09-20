"""Deterministic interview-question generation from supplied job requirements."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from core.exceptions import ValidationError
from core.validators import validate_required_text

from .models import InterviewQuestion
from .schemas import validate_question


class InterviewQuestionGenerator:
    """Generate practice questions without using candidate facts or AI."""

    def generate(self, job_information: Mapping[str, Any]) -> tuple[InterviewQuestion, ...]:
        if not isinstance(job_information, Mapping):
            raise ValidationError("job information must be a mapping.")
        questions: list[InterviewQuestion] = []
        groups = (
            ("responsibilities", "responsibility", "Describe how you would approach this responsibility: ", "medium"),
            ("required_skills", "skill", "Describe a verified example of using this skill: ", "medium"),
            ("qualifications", "qualification", "How does your verified background address this qualification: ", "hard"),
            ("experience_requirements", "experience", "Describe relevant verified experience for this requirement: ", "medium"),
        )
        for field, category, prefix, difficulty in groups:
            values = job_information.get(field, ())
            if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
                raise ValidationError(f"{field} must be a collection.")
            for value in values:
                fact = validate_required_text(value, f"{field} item")
                questions.append(InterviewQuestion(
                    question_id=f"question-{len(questions) + 1}",
                    question=prefix + fact,
                    category=category,
                    difficulty=difficulty,
                    source="generated_practice_from_job_requirement",
                    evidence_needed=("specific example", "your role", "result or outcome"),
                ))
        return tuple(questions)

    def validate(self, question: InterviewQuestion | Mapping[str, Any]) -> InterviewQuestion:
        return validate_question(question)
