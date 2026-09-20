"""Deterministic document generation without external services."""

from __future__ import annotations

from core.exceptions import ValidationError

from .models import DocumentRequest, GeneratedDocument


class DeterministicDocumentGenerator:
    """Package supplied document content without adding or changing facts."""

    def generate(self, request: DocumentRequest) -> GeneratedDocument:
        """Return the request content as an immutable generated document."""
        if not isinstance(request, DocumentRequest):
            raise ValidationError("request must be a DocumentRequest instance.")
        return GeneratedDocument(request.document_type, request.content)
