"""Thin service facade for document generation."""

from __future__ import annotations

from .generator import DeterministicDocumentGenerator
from .interfaces import DocumentGenerator
from .models import DocumentRequest, GeneratedDocument


class DocumentService:
    """Coordinate document request validation and generator delegation."""

    def __init__(self, generator: DocumentGenerator | None = None) -> None:
        self._generator = generator or DeterministicDocumentGenerator()

    def generate(self, document_type: str, content: str) -> GeneratedDocument:
        """Generate a document from explicitly supplied type and content."""
        request = DocumentRequest(document_type=document_type, content=content)
        return self._generator.generate(request)
