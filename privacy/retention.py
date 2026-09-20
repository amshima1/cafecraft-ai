"""Deterministic, caller-controlled retention policies."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from core.exceptions import ValidationError
from core.validators import validate_required_text


@dataclass(frozen=True)
class RetentionPolicy:
    """Define the number of days data may be retained for a purpose."""

    purpose: str
    retention_days: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "purpose", validate_required_text(self.purpose, "purpose"))
        if isinstance(self.retention_days, bool) or not isinstance(self.retention_days, int):
            raise ValidationError("retention_days must be a positive integer.")
        if self.retention_days <= 0:
            raise ValidationError("retention_days must be a positive integer.")

    def is_expired(self, created_date: date, current_date: date) -> bool:
        """Return whether the retention deadline is on or before ``current_date``."""
        if not isinstance(created_date, date) or not isinstance(current_date, date):
            raise ValidationError("created_date and current_date must be dates.")
        return current_date >= created_date + timedelta(days=self.retention_days)
