"""Unit tests for the AI response parser."""

import unittest

from ai.parser import parse_ai_response
from core.exceptions import AIServiceError


class ParseAIResponseTests(unittest.TestCase):
    """Verify the public behavior of :func:`parse_ai_response`."""

    def test_parses_json_object(self) -> None:
        """A valid JSON object is returned as the corresponding dictionary."""
        response = '{"name": "Ada", "skills": ["Python", "SQL"]}'

        result = parse_ai_response(response)

        self.assertEqual(
            result,
            {"name": "Ada", "skills": ["Python", "SQL"]},
        )

    def test_parses_json_array(self) -> None:
        """A valid JSON array is returned as the corresponding list."""
        response = '["resume", "cover letter", "interview"]'

        result = parse_ai_response(response)

        self.assertEqual(result, ["resume", "cover letter", "interview"])

    def test_rejects_empty_or_whitespace_only_response(self) -> None:
        """Empty responses do not produce a JSON value."""
        for response in ("", "   ", "\n\t"):
            with self.subTest(response=repr(response)):
                with self.assertRaises(AIServiceError):
                    parse_ai_response(response)

    def test_wraps_invalid_json_in_ai_service_error(self) -> None:
        """Malformed JSON is reported through the project exception type."""
        with self.assertRaises(AIServiceError) as raised:
            parse_ai_response('{"name": "Ada",}')

        self.assertNotIsInstance(raised.exception, ValueError)

    def test_does_not_expose_json_decode_error(self) -> None:
        """Callers never receive ``json.JSONDecodeError`` for invalid JSON."""
        try:
            parse_ai_response("not valid JSON")
        except AIServiceError:
            pass
        except ValueError as error:
            self.fail(f"raw JSON decoding error exposed: {error!r}")
        else:
            self.fail("invalid JSON was accepted")


if __name__ == "__main__":
    unittest.main()
