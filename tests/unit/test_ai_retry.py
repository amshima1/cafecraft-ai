import unittest
from unittest.mock import patch

from ai.retry import retry
from core.exceptions import AIServiceError, ConfigurationError, ValidationError


class RetryDecoratorTests(unittest.TestCase):
    """Focused tests for the ai.retry retry decorator."""

    def test_ai_service_error_is_retried_until_success(self):
        calls = {"count": 0}

        @retry(max_attempts=3, delay_seconds=0)
        def flaky():
            calls["count"] += 1
            if calls["count"] < 3:
                raise AIServiceError("temporary failure")
            return "success"

        with patch("ai.retry.time.sleep") as sleep_mock:
            result = flaky()

        self.assertEqual(result, "success")
        self.assertEqual(calls["count"], 3)
        self.assertEqual(sleep_mock.call_count, 2)

    def test_ai_service_error_stops_after_max_attempts(self):
        calls = {"count": 0}

        @retry(max_attempts=2, delay_seconds=0)
        def always_fails():
            calls["count"] += 1
            raise AIServiceError("still failing")

        with patch("ai.retry.time.sleep") as sleep_mock:
            with self.assertRaises(AIServiceError):
                always_fails()

        self.assertEqual(calls["count"], 2)
        self.assertEqual(sleep_mock.call_count, 1)

    def test_validation_error_is_not_retried(self):
        calls = {"count": 0}

        @retry(max_attempts=3, delay_seconds=0)
        def invalid_input():
            calls["count"] += 1
            raise ValidationError("invalid payload")

        with patch("ai.retry.time.sleep") as sleep_mock:
            with self.assertRaises(ValidationError):
                invalid_input()

        self.assertEqual(calls["count"], 1)
        self.assertEqual(sleep_mock.call_count, 0)

    def test_configuration_error_is_not_retried(self):
        calls = {"count": 0}

        @retry(max_attempts=3, delay_seconds=0)
        def bad_config():
            calls["count"] += 1
            raise ConfigurationError("missing setting")

        with patch("ai.retry.time.sleep") as sleep_mock:
            with self.assertRaises(ConfigurationError):
                bad_config()

        self.assertEqual(calls["count"], 1)
        self.assertEqual(sleep_mock.call_count, 0)

    def test_unexpected_exception_is_not_retried(self):
        calls = {"count": 0}

        @retry(max_attempts=3, delay_seconds=0)
        def unexpected():
            calls["count"] += 1
            raise RuntimeError("something unexpected")

        with patch("ai.retry.time.sleep") as sleep_mock:
            with self.assertRaises(RuntimeError):
                unexpected()

        self.assertEqual(calls["count"], 1)
        self.assertEqual(sleep_mock.call_count, 0)

    def test_invalid_retry_configuration_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "max_attempts must be at least 1"):
            retry(max_attempts=0)

        with self.assertRaisesRegex(ValueError, "delay_seconds must be non-negative"):
            retry(delay_seconds=-0.01)


if __name__ == "__main__":
    unittest.main()
