"""Public API for the persistence-neutral Storage foundation."""

from .interfaces import Storage
from .memory import InMemoryStorage
from .service import StorageService

__all__ = ["Storage", "InMemoryStorage", "StorageService"]
