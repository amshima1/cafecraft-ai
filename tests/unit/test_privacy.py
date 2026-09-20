"""Unit tests for the Privacy foundation."""

import unittest
from datetime import date

from core.exceptions import ValidationError
from privacy import (
    ConsentManager,
    ConsentRecord,
    DataDeletionManager,
    DataExporter,
    DeletionResult,
    PrivacyService,
    RetentionPolicy,
)


class PrivacyTests(unittest.TestCase):
    def test_valid_consent_and_immutability(self):
        record = ConsentRecord("user-1", "analytics", True, "2026-09-20T10:00:00Z")
        self.assertEqual(record.user_id, "user-1")
        with self.assertRaises((AttributeError, TypeError)):
            record.granted = False

    def test_invalid_consent_text(self):
        for values in (("", "purpose", "time"), ("user", "", "time"), ("user", "purpose", "")):
            with self.assertRaises(ValidationError):
                ConsentRecord(values[0], values[1], True, values[2])

    def test_grant_revoke_and_retrieval(self):
        manager = ConsentManager()
        granted = manager.grant("user-1", "analytics", "t1")
        self.assertIs(manager.get_consent("user-1", "analytics"), granted)
        self.assertTrue(manager.has_consent("user-1", "analytics"))
        manager.revoke("user-1", "analytics", "t2")
        self.assertFalse(manager.has_consent("user-1", "analytics"))

    def test_duplicate_consent_handling_is_latest_wins(self):
        manager = ConsentManager()
        first = manager.grant("user-1", "analytics", "t1")
        second = manager.revoke("user-1", "analytics", "t2")
        self.assertIsNot(manager.get_consent("user-1", "analytics"), first)
        self.assertEqual(manager.get_consent("user-1", "analytics"), second)

    def test_export_preserves_data_without_mutation_or_unrelated_data(self):
        data = {"profile": {"name": "Ada"}, "resume": ["Python"]}
        exported = DataExporter().export(data)
        self.assertEqual(exported, data)
        self.assertIsNot(exported, data)
        exported["profile"]["name"] = "Changed"
        self.assertEqual(data["profile"]["name"], "Ada")
        self.assertNotIn("system_data", exported)

    def test_deletion_results(self):
        store = {"user-1": {"name": "Ada"}, "user-2": {"name": "Grace"}}
        manager = DataDeletionManager()
        result = manager.delete_user_data(store, "user-1")
        self.assertEqual(result, DeletionResult("user-1", True, True))
        self.assertNotIn("user-1", store)
        self.assertIn("user-2", store)
        missing = manager.delete_user_data(store, "missing")
        self.assertEqual(missing, DeletionResult("missing", False, False))
        self.assertIn("user-2", store)

    def test_invalid_deletion_user_id(self):
        with self.assertRaises(ValidationError):
            DataDeletionManager().delete_user_data({}, " ")

    def test_retention_policy_and_deterministic_dates(self):
        policy = RetentionPolicy("resume", 30)
        created = date(2026, 1, 1)
        self.assertFalse(policy.is_expired(created, date(2026, 1, 30)))
        self.assertTrue(policy.is_expired(created, date(2026, 1, 31)))
        self.assertEqual(policy.is_expired(created, date(2026, 1, 31)), True)

    def test_invalid_retention_policy(self):
        for purpose, days in (("", 30), ("resume", 0), ("resume", -1)):
            with self.assertRaises(ValidationError):
                RetentionPolicy(purpose, days)

    def test_service_coordinates_all_operations(self):
        store = {"user-1": {"resume": "content"}}
        service = PrivacyService(retention_policy=RetentionPolicy("resume", 1))
        service.grant_consent("user-1", "export", "t1")
        self.assertTrue(service.has_consent("user-1", "export"))
        self.assertEqual(service.export_data(store["user-1"]), store["user-1"])
        result = service.delete_user_data(store, "user-1")
        self.assertTrue(result.deleted)
        self.assertTrue(service.is_data_expired(date(2026, 1, 1), date(2026, 1, 2)))
        service.revoke_consent("user-1", "export", "t2")
        self.assertFalse(service.has_consent("user-1", "export"))


if __name__ == "__main__":
    unittest.main()
