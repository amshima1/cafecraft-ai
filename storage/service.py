"""Thin service layer for persistence-neutral storage operations."""

from __future__ import annotations

from typing import Generic, TypeVar

from .interfaces import Storage, _validate_key
from .memory import InMemoryStorage

_ValueT = TypeVar("_ValueT")


class StorageService(Generic[_ValueT]):
    """Coordinate storage operations through an injected implementation."""

    def __init__(self, storage: Storage[_ValueT] | None = None) -> None:
        self._storage = storage or InMemoryStorage[_ValueT]()

    def save(self, key: str, value: _ValueT) -> None:
        """Persist a value under a validated key."""
        self._storage.save(_validate_key(key), value)

    def get(self, key: str) -> _ValueT | None:
        """Retrieve a value for a validated key."""
        return self._storage.get(_validate_key(key))

    def delete(self, key: str) -> None:
        """Delete a value for a validated key if present."""
        self._storage.delete(_validate_key(key))

    def exists(self, key: str) -> bool:
        """Return whether a validated key currently exists."""
        return self._storage.exists(_validate_key(key))
