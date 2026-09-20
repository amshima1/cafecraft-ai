"""Persistence-neutral storage contracts."""

from __future__ import annotations

from typing import Protocol, TypeVar

from core.validators import validate_required_text

_ValueT = TypeVar("_ValueT")


def _validate_key(key: str) -> str:
    """Validate and normalize a storage key."""
    return validate_required_text(key, "key")


class Storage(Protocol[_ValueT]):
    """Generic persistence-neutral key-value storage contract."""

    def save(self, key: str, value: _ValueT) -> None:
        """Create or replace a value for the supplied key."""
        ...

    def get(self, key: str) -> _ValueT | None:
        """Return the value for the supplied key or None when absent."""
        ...

    def delete(self, key: str) -> None:
        """Delete the supplied key if present."""
        ...

    def exists(self, key: str) -> bool:
        """Return whether the supplied key has a stored value."""
        ...
