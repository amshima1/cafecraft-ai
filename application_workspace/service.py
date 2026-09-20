"""Application Workspace service facade."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from typing import Any

from core.validators import validate_required_text

from .analytics import ApplicationAnalytics
from .followups import FollowUpService
from .messages import FollowUpMessageGenerator
from .models import Application, ApplicationMetrics
from .schemas import validate_application
from .tracker import ApplicationTracker, InMemoryApplicationTracker


class ApplicationWorkspaceService:
    """Coordinate validation, tracking, follow-ups, messaging, and metrics."""

    def __init__(self, tracker: ApplicationTracker | None = None) -> None:
        self._tracker = tracker or InMemoryApplicationTracker()
        self._followups = FollowUpService()
        self._messages = FollowUpMessageGenerator()
        self._analytics = ApplicationAnalytics()

    def create(self, data: Application | Mapping[str, Any]) -> Application:
        return self._tracker.create(validate_application(data))

    def get(self, application_id: str) -> Application | None:
        return self._tracker.get(validate_required_text(application_id, "application_id"))

    def update(self, data: Application | Mapping[str, Any]) -> Application:
        return self._tracker.update(validate_application(data))

    def delete(self, application_id: str) -> None:
        self._tracker.delete(validate_required_text(application_id, "application_id"))

    def update_status(self, application_id: str, status: str) -> Application:
        application = self.get(application_id)
        if application is None:
            from core.exceptions import ValidationError
            raise ValidationError("Application does not exist.")
        values = {**application.__dict__, "status": status}
        return self._tracker.update(validate_application(values))

    def is_follow_up_due(self, application_id: str, *, on_date: date | None = None) -> bool:
        application = self.get(application_id)
        return application is not None and self._followups.is_due(application, on_date=on_date)

    def follow_up_message(self, application_id: str) -> str:
        application = self.get(application_id)
        if application is None:
            from core.exceptions import ValidationError
            raise ValidationError("Application does not exist.")
        return self._messages.generate(application)

    def metrics(self) -> ApplicationMetrics:
        return self._analytics.summarize(self._tracker.list_all())
