"""Reusable retry support for transient AI service failures."""

from __future__ import annotations

from functools import wraps
import time
from typing import Callable, ParamSpec, TypeVar

from core.exceptions import AIServiceError


_P = ParamSpec("_P")
_R = TypeVar("_R")


def retry(
    *,
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """Retry a callable when it raises :class:`AIServiceError`.

    ``max_attempts`` is the total number of times the callable may run,
    including the initial attempt.  ``delay_seconds`` is applied between
    failed attempts and is not applied after the final attempt.

    Other exceptions are propagated immediately.  In particular,
    ``ValidationError`` and ``ConfigurationError`` are not retried because
    only ``AIServiceError`` is caught.

    Args:
        max_attempts: Positive total number of attempts to make.
        delay_seconds: Non-negative delay, in seconds, between attempts.

    Raises:
        ValueError: If ``max_attempts`` or ``delay_seconds`` is invalid.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    if delay_seconds < 0:
        raise ValueError("delay_seconds must be non-negative")

    def decorator(operation: Callable[_P, _R]) -> Callable[_P, _R]:
        @wraps(operation)
        def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            for attempt in range(max_attempts):
                try:
                    return operation(*args, **kwargs)
                except AIServiceError:
                    if attempt == max_attempts - 1:
                        raise
                    if delay_seconds:
                        time.sleep(delay_seconds)

            # The loop either returns or re-raises on every iteration.
            raise RuntimeError("retry loop exited unexpectedly")

        return wrapped

    return decorator
