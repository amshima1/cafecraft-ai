"""Persistence-neutral document generation contracts."""

from __future__ import annotations

from typing import Protocol

from .models import DocumentRequest, GeneratedDocument


class DocumentGenerator(Protocol):
    """Protocol for deterministic or format-specific document generators."""

    def generate(self, request: DocumentRequest) -> GeneratedDocument:
        """Generate a document from a validated request."""
        ...
