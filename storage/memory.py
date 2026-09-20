"""Deterministic in-memory storage implementation."""

from __future__ import annotations

from typing import Generic, TypeVar

from .interfaces import Storage, _validate_key

_ValueT = TypeVar("_ValueT")


class InMemoryStorage(Storage[_ValueT], Generic[_ValueT]):
    """Simple instance-local in-memory storage."""

    def __init__(self) -> None:
        self._values: dict[str, _ValueT] = {}

    def save(self, key: str, value: _ValueT) -> None:
        """Create or replace a value for the validated key."""
        self._values[_validate_key(key)] = value

    def get(self, key: str) -> _ValueT | None:
        """Return the stored value or None when the key is absent."""
        return self._values.get(_validate_key(key))

    def delete(self, key: str) -> None:
        """Remove a value for the key without affecting other entries."""
        self._values.pop(_validate_key(key), None)

    def exists(self, key: str) -> bool:
        """Return whether the validated key is present."""
        return _validate_key(key) in self._values
