"""Unit tests for the Storage foundation."""

import unittest

from core.exceptions import ValidationError
from storage import InMemoryStorage, Storage, StorageService


class RecordingStorage:
    """Minimal injected storage implementation for delegation tests."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, object | None]] = []
        self.values: dict[str, object] = {}

    def save(self, key: str, value: object) -> None:
        self.calls.append(("save", key, value))
        self.values[key] = value

    def get(self, key: str) -> object | None:
        self.calls.append(("get", key, None))
        return self.values.get(key)

    def delete(self, key: str) -> None:
        self.calls.append(("delete", key, None))
        self.values.pop(key, None)

    def exists(self, key: str) -> bool:
        self.calls.append(("exists", key, None))
        return key in self.values


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = InMemoryStorage[object]()

    def test_storage_protocol_usage(self) -> None:
        storage: Storage[object] = self.storage
        storage.save("profile", {"name": "Ada"})
        self.assertEqual(storage.get("profile"), {"name": "Ada"})

    def test_save_and_get(self) -> None:
        self.storage.save("profile", {"name": "Ada"})
        self.assertEqual(self.storage.get("profile"), {"name": "Ada"})

    def test_get_missing_key_returns_none(self) -> None:
        self.assertIsNone(self.storage.get("missing-key"))

    def test_exists_reports_true_for_present_key(self) -> None:
        self.storage.save("profile", {"name": "Ada"})
        self.assertTrue(self.storage.exists("profile"))

    def test_exists_reports_false_for_missing_key(self) -> None:
        self.assertFalse(self.storage.exists("missing-key"))

    def test_delete_existing_key(self) -> None:
        self.storage.save("profile", {"name": "Ada"})
        self.storage.delete("profile")
        self.assertFalse(self.storage.exists("profile"))
        self.assertIsNone(self.storage.get("profile"))

    def test_delete_missing_key_is_idempotent(self) -> None:
        self.storage.save("other", {"name": "Grace"})
        self.storage.delete("missing")
        self.assertEqual(self.storage.get("other"), {"name": "Grace"})

    def test_save_replaces_existing_value_deterministically(self) -> None:
        self.storage.save("profile", "first")
        self.storage.save("profile", "second")
        self.assertEqual(self.storage.get("profile"), "second")

    def test_delete_one_key_does_not_delete_another(self) -> None:
        self.storage.save("first", 1)
        self.storage.save("second", 2)
        self.storage.delete("first")
        self.assertIsNone(self.storage.get("first"))
        self.assertEqual(self.storage.get("second"), 2)

    def test_storage_instances_do_not_share_state(self) -> None:
        first = InMemoryStorage[str]()
        second = InMemoryStorage[str]()
        first.save("profile", "first-value")
        self.assertEqual(first.get("profile"), "first-value")
        self.assertIsNone(second.get("profile"))

    def test_empty_key_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.storage.save("", "value")

    def test_whitespace_key_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.storage.save("   ", "value")

    def test_invalid_key_rejected_across_all_operations(self) -> None:
        operations = (
            lambda: self.storage.save("", "value"),
            lambda: self.storage.get(""),
            lambda: self.storage.delete(""),
            lambda: self.storage.exists(""),
        )
        for operation in operations:
            with self.subTest(operation=operation), self.assertRaises(ValidationError):
                operation()

    def test_deterministic_operations(self) -> None:
        self.storage.save("alpha", "A")
        self.storage.save("beta", "B")
        self.storage.save("alpha", "updated-A")
        self.storage.delete("beta")
        self.assertEqual(self.storage.get("alpha"), "updated-A")
        self.assertIsNone(self.storage.get("beta"))
        self.assertTrue(self.storage.exists("alpha"))
        self.assertFalse(self.storage.exists("beta"))

    def test_service_saves_and_retrieves_data(self) -> None:
        service = StorageService[object]()
        service.save("profile", {"name": "Ada"})
        self.assertEqual(service.get("profile"), {"name": "Ada"})

    def test_service_checks_existence(self) -> None:
        service = StorageService[str]()
        self.assertFalse(service.exists("key"))
        service.save("key", "value")
        self.assertTrue(service.exists("key"))

    def test_service_deletes_data(self) -> None:
        service = StorageService[str]()
        service.save("key", "value")
        service.delete("key")
        self.assertFalse(service.exists("key"))
        self.assertIsNone(service.get("key"))

    def test_service_delegates_to_injected_storage(self) -> None:
        storage = RecordingStorage()
        service = StorageService[object](storage)

        service.save("key", "value")
        self.assertEqual(service.get("key"), "value")
        self.assertTrue(service.exists("key"))
        service.delete("key")

        self.assertEqual(
            [call[0] for call in storage.calls],
            ["save", "get", "exists", "delete"],
        )
        self.assertEqual(storage.calls[0], ("save", "key", "value"))

    def test_service_validates_key_before_delegation(self) -> None:
        storage = RecordingStorage()
        service = StorageService[object](storage)

        with self.assertRaises(ValidationError):
            service.save(" ", "value")

        self.assertEqual(storage.calls, [])

    def test_injected_storage_is_used_by_service(self) -> None:
        storage = InMemoryStorage[str]()
        service = StorageService[str](storage)
        service.save("key", "value")
        self.assertEqual(storage.get("key"), "value")
        self.assertEqual(service.get("key"), "value")


if __name__ == "__main__":
    unittest.main()
