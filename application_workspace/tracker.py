"""Application tracking boundary and in-memory implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.exceptions import ValidationError

from .models import Application


class ApplicationTracker(ABC):
    """Persistence-neutral interface for application records."""

    @abstractmethod
    def create(self, application: Application) -> Application:
        raise NotImplementedError

    @abstractmethod
    def get(self, application_id: str) -> Application | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, application: Application) -> Application:
        raise NotImplementedError

    @abstractmethod
    def delete(self, application_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> tuple[Application, ...]:
        raise NotImplementedError


class InMemoryApplicationTracker(ApplicationTracker):
    """Simple tracker for application use and unit tests."""

    def __init__(self) -> None:
        self._applications: dict[str, Application] = {}

    def create(self, application: Application) -> Application:
        if application.application_id in self._applications:
            raise ValidationError("An application with this application_id already exists.")
        self._applications[application.application_id] = application
        return application

    def get(self, application_id: str) -> Application | None:
        return self._applications.get(application_id)

    def update(self, application: Application) -> Application:
        if application.application_id not in self._applications:
            raise ValidationError("Application does not exist.")
        self._applications[application.application_id] = application
        return application

    def delete(self, application_id: str) -> None:
        self._applications.pop(application_id, None)

    def list_all(self) -> tuple[Application, ...]:
        return tuple(self._applications.values())
