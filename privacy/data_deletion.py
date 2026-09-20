"""Persistence-neutral user data deletion operations."""

from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import Any

from core.validators import validate_required_text


@dataclass(frozen=True)
class DeletionResult:
    """Describe whether a user's supplied data was deleted."""

    user_id: str
    data_existed: bool
    deleted: bool


class DataDeletionManager:
    """Delete one user from an explicitly supplied mutable data store."""

    def delete_user_data(
        self, data_store: MutableMapping[str, Any], user_id: str
    ) -> DeletionResult:
        """Delete only ``user_id`` and report the deterministic outcome."""
        user_id = validate_required_text(user_id, "user_id")
        if not isinstance(data_store, MutableMapping):
            from core.exceptions import ValidationError

            raise ValidationError("data_store must be a mutable mapping.")
        existed = user_id in data_store
        if existed:
            del data_store[user_id]
        return DeletionResult(user_id, existed, existed)

    def request_deletion(
        self, data_store: MutableMapping[str, Any], user_id: str
    ) -> DeletionResult:
        """Process a deletion request against the explicitly supplied store."""
        return self.delete_user_data(data_store, user_id)
