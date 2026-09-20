"""Immutable domain models for the Truth Layer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    """A factual source that may support a claim."""

    evidence_id: str
    source_type: str
    source_reference: str
    fact: str
    verified: bool = False


@dataclass(frozen=True)
class Claim:
    """A statement whose support is explicitly referenced."""

    claim_id: str
    text: str
    evidence_ids: tuple[str, ...] = ()
    approved: bool = False


@dataclass(frozen=True)
class ClaimValidation:
    """The deterministic validation result for a claim."""

    claim_id: str
    status: str
    supported_by: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
