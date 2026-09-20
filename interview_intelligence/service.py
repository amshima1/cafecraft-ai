"""Application service for Interview Intelligence."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.validators import validate_required_text

from .answer_analyzer import AnswerAnalyzer
from .models import AnswerAnalysis, InterviewQuestion, PracticeSession
from .practice import InMemoryPracticeSessionStore, PracticeSessionStore, complete_session, record_answer
from .questions import InterviewQuestionGenerator
from .schemas import validate_question, validate_session


class InterviewIntelligenceService:
    def __init__(self, store: PracticeSessionStore | None = None) -> None:
        self._questions = InterviewQuestionGenerator()
        self._analyzer = AnswerAnalyzer()
        self._store = store or InMemoryPracticeSessionStore()

    def generate_questions(self, job_information: Mapping[str, Any]) -> tuple[InterviewQuestion, ...]:
        return self._questions.generate(job_information)

    def analyze_answer(self, question: InterviewQuestion, answer: str, *, supplied_context: tuple[str, ...] = ()) -> AnswerAnalysis:
        return self._analyzer.analyze(validate_question(question), answer, supplied_context=supplied_context)

    def create_session(self, data: PracticeSession | Mapping[str, Any]) -> PracticeSession:
        return self._store.create(validate_session(data))

    def get_session(self, session_id: str) -> PracticeSession | None:
        return self._store.get(validate_required_text(session_id, "session_id"))

    def record_answer(self, session_id: str, answer: str, analysis: AnswerAnalysis) -> PracticeSession:
        return record_answer(self._store, session_id, validate_required_text(answer, "answer"), analysis)

    def complete_session(self, session_id: str) -> PracticeSession:
        return complete_session(self._store, validate_required_text(session_id, "session_id"))
