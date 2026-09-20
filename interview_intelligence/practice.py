"""In-memory practice-session behavior."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.exceptions import ValidationError

from .models import AnswerAnalysis, PracticeSession


class PracticeSessionStore(ABC):
    @abstractmethod
    def create(self, session: PracticeSession) -> PracticeSession:
        raise NotImplementedError

    @abstractmethod
    def get(self, session_id: str) -> PracticeSession | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, session: PracticeSession) -> PracticeSession:
        raise NotImplementedError


class InMemoryPracticeSessionStore(PracticeSessionStore):
    def __init__(self) -> None:
        self._sessions: dict[str, PracticeSession] = {}

    def create(self, session: PracticeSession) -> PracticeSession:
        if session.session_id in self._sessions:
            raise ValidationError("A practice session with this session_id already exists.")
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> PracticeSession | None:
        return self._sessions.get(session_id)

    def update(self, session: PracticeSession) -> PracticeSession:
        if session.session_id not in self._sessions:
            raise ValidationError("Practice session does not exist.")
        self._sessions[session.session_id] = session
        return session


def record_answer(store: PracticeSessionStore, session_id: str, answer: str, analysis: AnswerAnalysis) -> PracticeSession:
    session = store.get(session_id)
    if session is None:
        raise ValidationError("Practice session does not exist.")
    return store.update(PracticeSession(session.session_id, session.question_id, answer, analysis, False))


def complete_session(store: PracticeSessionStore, session_id: str) -> PracticeSession:
    session = store.get(session_id)
    if session is None:
        raise ValidationError("Practice session does not exist.")
    if session.analysis is None:
        raise ValidationError("Practice session must have an analysis before completion.")
    return store.update(PracticeSession(session.session_id, session.question_id, session.answer, session.analysis, True))
