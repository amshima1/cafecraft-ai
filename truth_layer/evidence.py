"""Evidence storage boundaries for the Truth Layer."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.exceptions import ValidationError
from core.validators import validate_required_text

from .models import Evidence


class EvidenceStore(ABC):
    """Persistence-neutral interface for immutable evidence records."""

    @abstractmethod
    def add(self, evidence: Evidence) -> Evidence:
        """Store evidence and return the stored immutable object."""
        raise NotImplementedError

    @abstractmethod
    def get(self, evidence_id: str) -> Evidence | None:
        """Return evidence by ID, or None when it is unknown."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> tuple[Evidence, ...]:
        """Return all evidence in insertion order."""
        raise NotImplementedError


class InMemoryEvidenceStore(EvidenceStore):
    """Deterministic in-memory evidence store for this foundation."""

    def __init__(self) -> None:
        self._evidence: dict[str, Evidence] = {}

    def add(self, evidence: Evidence) -> Evidence:
        if not isinstance(evidence, Evidence):
            raise ValidationError("evidence must be an Evidence instance.")
        evidence_id = validate_required_text(evidence.evidence_id, "evidence_id")
        if evidence_id in self._evidence:
            raise ValidationError("An evidence record with this evidence_id already exists.")
        self._evidence[evidence_id] = evidence
        return evidence

    def get(self, evidence_id: str) -> Evidence | None:
        return self._evidence.get(validate_required_text(evidence_id, "evidence_id"))

    def list_all(self) -> tuple[Evidence, ...]:
        return tuple(self._evidence.values())
