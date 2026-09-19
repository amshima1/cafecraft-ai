"""Utilities for parsing structured responses from AI services."""

from __future__ import annotations

import json
from typing import TypeAlias

from core.exceptions import AIServiceError


JSONPrimitive: TypeAlias = None | bool | int | float | str
JSONValue: TypeAlias = JSONPrimitive | list["JSONValue"] | dict[str, "JSONValue"]


def parse_ai_response(response_text: str) -> JSONValue:
    """Parse a non-empty AI response containing a JSON value.

    Leading and trailing whitespace is ignored.  JSON objects, arrays, scalar
    values, and ``null`` are returned using their normal Python equivalents.

    Args:
        response_text: The raw text returned by an AI service.

    Returns:
        The decoded JSON value.

    Raises:
        AIServiceError: If the response is not non-empty text or is not valid
            JSON.  The original parsing exception is chained for diagnostics
            without exposing it to callers as the primary error.
    """
    if not isinstance(response_text, str) or not response_text.strip():
        raise AIServiceError("AI service returned an empty response.")

    try:
        value = json.loads(response_text)
    except (json.JSONDecodeError, RecursionError) as error:
        raise AIServiceError("AI service returned invalid JSON.") from error

    return value


def parse_response(response_text: str) -> JSONValue:
    """Parse an AI response as JSON.

    This is a concise alias for :func:`parse_ai_response` for callers that
    already work with a response parser abstraction.
    """
    return parse_ai_response(response_text)
