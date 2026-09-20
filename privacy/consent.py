"""Deterministic, in-memory consent management."""

from __future__ import annotations

from dataclasses import dataclass

from core.validators import validate_required_text


@dataclass(frozen=True)
class ConsentRecord:
    """An immutable consent decision for one user and purpose."""

    user_id: str
    purpose: str
    granted: bool
    timestamp: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "user_id", validate_required_text(self.user_id, "user_id"))
        object.__setattr__(self, "purpose", validate_required_text(self.purpose, "purpose"))
        object.__setattr__(self, "timestamp", validate_required_text(self.timestamp, "timestamp"))
        if not isinstance(self.granted, bool):
            from core.exceptions import ValidationError

            raise ValidationError("granted must be a boolean.")


class ConsentManager:
    """Store the latest consent decision for each user and purpose."""

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], ConsentRecord] = {}

    def record_consent(self, record: ConsentRecord) -> ConsentRecord:
        """Record or deterministically replace a consent decision."""
        if not isinstance(record, ConsentRecord):
            from core.exceptions import ValidationError

            raise ValidationError("record must be a ConsentRecord instance.")
        self._records[(record.user_id, record.purpose)] = record
        return record

    def grant(self, user_id: str, purpose: str, timestamp: str) -> ConsentRecord:
        """Grant consent and return the stored decision."""
        return self.record_consent(ConsentRecord(user_id, purpose, True, timestamp))

    def revoke(self, user_id: str, purpose: str, timestamp: str) -> ConsentRecord:
        """Revoke consent and return the stored decision."""
        return self.record_consent(ConsentRecord(user_id, purpose, False, timestamp))

    def get_consent(self, user_id: str, purpose: str) -> ConsentRecord | None:
        """Return the latest decision, or ``None`` when no decision exists."""
        key = (validate_required_text(user_id, "user_id"), validate_required_text(purpose, "purpose"))
        return self._records.get(key)

    def has_consent(self, user_id: str, purpose: str) -> bool:
        """Return whether the latest decision grants consent."""
        record = self.get_consent(user_id, purpose)
        return record is not None and record.granted
