"""Reusable orchestration for CaféCraft AI requests."""

from __future__ import annotations

from ai.client import DeepSeekClient
from core.exceptions import ValidationError


class AIEngine:
    """Validate prompts and delegate requests to a DeepSeek client."""

    def __init__(self, client: DeepSeekClient | None = None) -> None:
        """Create an engine with the supplied or configured client."""
        self._client = client or DeepSeekClient()

    def process_prompt(self, prompt: str) -> str:
        """Send a non-empty prompt and return the response text."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValidationError("Prompt must be non-empty text.")
        return self._client.send_prompt(prompt)
