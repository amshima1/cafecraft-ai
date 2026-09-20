"""Deterministic application metrics."""

from __future__ import annotations

from collections import Counter

from core.constants import APPLICATION_STATUSES

from .models import Application, ApplicationMetrics


class ApplicationAnalytics:
    """Calculate descriptive metrics without predictions."""

    def summarize(self, applications: tuple[Application, ...]) -> ApplicationMetrics:
        counts = Counter(application.status for application in applications)
        by_status = tuple((status, counts.get(status, 0)) for status in APPLICATION_STATUSES)
        return ApplicationMetrics(
            total_applications=len(applications),
            applications_by_status=by_status,
            interviews=counts.get("interview", 0),
            offers=counts.get("offer", 0),
            rejections=counts.get("rejected", 0),
        )
