"""Coordination service for the privacy foundation."""

from __future__ import annotations

from datetime import date
from typing import Any
from collections.abc import MutableMapping

from .consent import ConsentManager, ConsentRecord
from .data_deletion import DataDeletionManager, DeletionResult
from .data_export import DataExporter
from .retention import RetentionPolicy


class PrivacyService:
    """Coordinate privacy components without owning persistence."""

    def __init__(
        self,
        consent_manager: ConsentManager | None = None,
        data_exporter: DataExporter | None = None,
        data_deletion_manager: DataDeletionManager | None = None,
        retention_policy: RetentionPolicy | None = None,
    ) -> None:
        self._consent_manager = consent_manager or ConsentManager()
        self._data_exporter = data_exporter or DataExporter()
        self._data_deletion_manager = data_deletion_manager or DataDeletionManager()
        self._retention_policy = retention_policy

    def grant_consent(self, user_id: str, purpose: str, timestamp: str) -> ConsentRecord:
        """Grant consent through the configured consent manager."""
        return self._consent_manager.grant(user_id, purpose, timestamp)

    def revoke_consent(self, user_id: str, purpose: str, timestamp: str) -> ConsentRecord:
        """Revoke consent through the configured consent manager."""
        return self._consent_manager.revoke(user_id, purpose, timestamp)

    def has_consent(self, user_id: str, purpose: str) -> bool:
        """Check the latest consent decision."""
        return self._consent_manager.has_consent(user_id, purpose)

    def export_data(self, data: Any) -> Any:
        """Export supplied user data through the configured exporter."""
        return self._data_exporter.export(data)

    def delete_user_data(
        self, data_store: MutableMapping[str, Any], user_id: str
    ) -> DeletionResult:
        """Delete supplied user data through the configured deletion manager."""
        return self._data_deletion_manager.delete_user_data(data_store, user_id)

    def is_data_expired(self, created_date: date, current_date: date) -> bool:
        """Evaluate dates using the configured retention policy."""
        if self._retention_policy is None:
            from core.exceptions import ValidationError

            raise ValidationError("A retention policy is required for expiration checks.")
        return self._retention_policy.is_expired(created_date, current_date)
