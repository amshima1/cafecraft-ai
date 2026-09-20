"""Unit tests for the Truth Layer foundation."""

import unittest

from core.exceptions import ValidationError
from truth_layer import (
    Claim,
    ClaimValidator,
    Evidence,
    InMemoryEvidenceStore,
    TruthLayerService,
    confidence_level,
)


class TruthLayerTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryEvidenceStore()
        self.service = TruthLayerService(self.store)
        self.verified = Evidence("e1", "career_profile", "profile-1", "Python skill", True)
        self.unverified = Evidence("e2", "note", "note-1", "Unverified statement", False)

    def test_valid_evidence_and_retrieval(self):
        self.assertIs(self.service.add_evidence(self.verified), self.verified)
        self.assertIs(self.service.get_evidence("e1"), self.verified)
        self.assertIsNone(self.service.get_evidence("missing"))

    def test_duplicate_evidence_rejected(self):
        self.service.add_evidence(self.verified)
        with self.assertRaises(ValidationError):
            self.service.add_evidence(self.verified)

    def test_evidence_results_are_deterministic(self):
        self.service.add_evidence(self.verified)
        self.service.add_evidence(self.unverified)
        self.assertEqual(self.store.list_all(), (self.verified, self.unverified))

    def test_claim_without_evidence_is_unsupported(self):
        result = self.service.validate_claim(Claim("c1", "I know Python"))
        self.assertEqual(result.status, "unsupported")

    def test_missing_evidence_is_unsupported(self):
        result = self.service.validate_claim(Claim("c1", "Claim", ("missing",)))
        self.assertEqual(result.status, "unsupported")
        self.assertEqual(result.missing_evidence, ("missing",))

    def test_unverified_evidence_is_uncertain(self):
        self.service.add_evidence(self.unverified)
        result = self.service.validate_claim(Claim("c1", "Claim", ("e2",)))
        self.assertEqual(result.status, "uncertain")
        self.assertEqual(result.supported_by, ("e2",))

    def test_verified_evidence_is_supported(self):
        self.service.add_evidence(self.verified)
        result = self.service.validate_claim(Claim("c1", "Claim", ("e1",)))
        self.assertEqual(result.status, "supported")
        self.assertEqual(result.supported_by, ("e1",))

    def test_confidence_mapping(self):
        self.assertEqual(confidence_level("supported"), "high")
        self.assertEqual(confidence_level("uncertain"), "medium")
        self.assertEqual(confidence_level("unsupported"), "low")
        self.assertEqual(confidence_level("invalid"), "unknown")

    def test_supported_claim_can_be_approved(self):
        self.service.add_evidence(self.verified)
        original = Claim("c1", "Claim", ("e1",))
        approved = self.service.approve_claim(original)
        self.assertTrue(approved.approved)
        self.assertFalse(original.approved)
        self.assertIsNot(approved, original)

    def test_uncertain_and_unsupported_claims_cannot_be_approved(self):
        self.service.add_evidence(self.unverified)
        with self.assertRaises(ValidationError):
            self.service.approve_claim(Claim("c1", "Claim", ("e2",)))
        with self.assertRaises(ValidationError):
            self.service.approve_claim(Claim("c2", "Claim"))

    def test_invalid_claim_input(self):
        with self.assertRaises(ValidationError):
            self.service.validate_claim(Claim("", "Claim"))
        with self.assertRaises(ValidationError):
            self.service.validate_claim(Claim("c1", ""))
        with self.assertRaises(ValidationError):
            ClaimValidator().validate(Claim("c1", "Claim", ["e1"]), {})

    def test_models_are_immutable(self):
        with self.assertRaises((AttributeError, TypeError)):
            self.verified.fact = "changed"


if __name__ == "__main__":
    unittest.main()
