"""Deterministic recruiter and follow-up message boundary."""

from __future__ import annotations

from .models import Application


class FollowUpMessageGenerator:
    """Generate a factual message without calling an AI provider."""

    def generate(self, application: Application) -> str:
        return (
            f"Subject: Follow-up on {application.job_title} application at {application.company}\n\n"
            f"Hello,\n\nI am following up on my application for the {application.job_title} role"
            f" at {application.company}. Please let me know if any additional information is needed.\n\n"
            "Thank you."
        )
