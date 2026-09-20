"""Claim validation against explicit evidence."""

from __future__ import annotations

from collections.abc import Mapping

from core.exceptions import ValidationError
from core.validators import validate_required_text

from .fact_checker import FactChecker
from .models import Claim, ClaimValidation, Evidence


class ClaimValidator:
    """Validate claims without generating or replacing factual content."""

    def __init__(self, fact_checker: FactChecker | None = None) -> None:
        self._fact_checker = fact_checker or FactChecker()

    def validate(
        self, claim: Claim, evidence_by_id: Mapping[str, Evidence]
    ) -> ClaimValidation:
        """Validate a claim against the supplied evidence mapping."""
        if not isinstance(claim, Claim):
            raise ValidationError("claim must be a Claim instance.")
        validate_required_text(claim.claim_id, "claim_id")
        validate_required_text(claim.text, "text")
        if not isinstance(claim.evidence_ids, tuple):
            raise ValidationError("evidence_ids must be a tuple.")
        for evidence_id in claim.evidence_ids:
            validate_required_text(evidence_id, "evidence_id")
        return self._fact_checker.check(claim, evidence_by_id)
