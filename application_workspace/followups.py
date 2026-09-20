"""Deterministic follow-up decisions."""

from __future__ import annotations

from datetime import date

from .models import Application


class FollowUpService:
    """Determine follow-up due state from explicit application dates only."""

    def is_due(self, application: Application, *, on_date: date | None = None) -> bool:
        if application.follow_up_date is None:
            return False
        return application.follow_up_date <= (on_date or date.today())

    def due_applications(self, applications: tuple[Application, ...], *, on_date: date | None = None) -> tuple[Application, ...]:
        return tuple(application for application in applications if self.is_due(application, on_date=on_date))
