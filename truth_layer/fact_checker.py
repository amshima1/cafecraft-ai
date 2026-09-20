"""Deterministic evidence-reference fact checking."""

from __future__ import annotations

from collections.abc import Mapping

from core.exceptions import ValidationError

from .models import Claim, ClaimValidation, Evidence


class FactChecker:
    """Check claims using only explicitly referenced evidence records."""

    def check(
        self, claim: Claim, evidence_by_id: Mapping[str, Evidence]
    ) -> ClaimValidation:
        """Return a validation result without inferring whether text is true."""
        if not isinstance(claim, Claim):
            raise ValidationError("claim must be a Claim instance.")
        missing = tuple(
            evidence_id
            for evidence_id in claim.evidence_ids
            if evidence_id not in evidence_by_id
        )
        if not claim.evidence_ids:
            return ClaimValidation(
                claim_id=claim.claim_id,
                status="unsupported",
                notes=("The claim does not reference evidence.",),
            )
        if missing:
            return ClaimValidation(
                claim_id=claim.claim_id,
                status="unsupported",
                missing_evidence=missing,
                notes=("One or more referenced evidence records are missing.",),
            )

        referenced = tuple(evidence_by_id[evidence_id] for evidence_id in claim.evidence_ids)
        if all(evidence.verified for evidence in referenced):
            return ClaimValidation(
                claim_id=claim.claim_id,
                status="supported",
                supported_by=claim.evidence_ids,
                notes=("All referenced evidence is verified.",),
            )
        return ClaimValidation(
            claim_id=claim.claim_id,
            status="uncertain",
            supported_by=claim.evidence_ids,
            notes=("Referenced evidence exists but is not fully verified.",),
        )
