"""Application service for deterministic Truth Layer operations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.exceptions import ValidationError
from core.validators import validate_required_text

from .claim_validator import ClaimValidator
from .evidence import EvidenceStore, InMemoryEvidenceStore
from .models import Claim, ClaimValidation, Evidence


class TruthLayerService:
    """Coordinate evidence storage, claim validation, and approval."""

    def __init__(
        self,
        evidence_store: EvidenceStore | None = None,
        claim_validator: ClaimValidator | None = None,
    ) -> None:
        self._evidence_store = evidence_store or InMemoryEvidenceStore()
        self._claim_validator = claim_validator or ClaimValidator()

    def add_evidence(self, evidence: Evidence) -> Evidence:
        """Add an immutable evidence record to the configured store."""
        return self._evidence_store.add(evidence)

    def get_evidence(self, evidence_id: str) -> Evidence | None:
        """Retrieve one evidence record by ID."""
        return self._evidence_store.get(validate_required_text(evidence_id, "evidence_id"))

    def validate_claim(self, claim: Claim) -> ClaimValidation:
        """Validate a claim against all currently stored evidence."""
        evidence = {
            item.evidence_id: item for item in self._evidence_store.list_all()
        }
        return self._claim_validator.validate(claim, evidence)

    def approve_claim(self, claim: Claim) -> Claim:
        """Return an approved copy only when the claim is supported."""
        validation = self.validate_claim(claim)
        if validation.status != "supported":
            raise ValidationError(
                f"Only supported claims can be approved; status is {validation.status}."
            )
        return Claim(
            claim_id=claim.claim_id,
            text=claim.text,
            evidence_ids=claim.evidence_ids,
            approved=True,
        )
