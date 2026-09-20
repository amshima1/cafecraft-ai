"""Immutable models for document generation."""

from __future__ import annotations

from dataclasses import dataclass

from core.validators import validate_required_text


@dataclass(frozen=True)
class DocumentRequest:
    """Caller-supplied document type and content."""

    document_type: str
    content: str

    def __post_init__(self) -> None:
        """Validate required request fields without changing supplied values."""
        validate_required_text(self.document_type, "document_type")
        validate_required_text(self.content, "content")


@dataclass(frozen=True)
class GeneratedDocument:
    """Immutable document result produced by a generator."""

    document_type: str
    content: str

    def __post_init__(self) -> None:
        """Validate required generated-document fields."""
        validate_required_text(self.document_type, "document_type")
        validate_required_text(self.content, "content")
