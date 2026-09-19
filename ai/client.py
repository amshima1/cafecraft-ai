"""Small standard-library client for the DeepSeek chat API."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config import settings
from core.exceptions import AIServiceError, ConfigurationError


class DeepSeekClient:
    """Send prompts to the configured DeepSeek model."""

    _CHAT_COMPLETIONS_PATH = "/chat/completions"
    _TIMEOUT_SECONDS = 30

    def __init__(self) -> None:
        """Create a client using the current application configuration."""
        self._api_key = settings.DEEPSEEK_API_KEY
        if not isinstance(self._api_key, str) or not self._api_key.strip():
            raise ConfigurationError("DEEPSEEK_API_KEY is not configured.")

        self._base_url = settings.DEEPSEEK_BASE_URL
        self._model = settings.DEEPSEEK_MODEL
        if not isinstance(self._base_url, str) or not self._base_url.strip():
            raise ConfigurationError("DEEPSEEK_BASE_URL is not configured.")
        if not isinstance(self._model, str) or not self._model.strip():
            raise ConfigurationError("DEEPSEEK_MODEL is not configured.")

    def send_prompt(self, prompt: str) -> str:
        """Send a prompt and return the model's response text."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise AIServiceError("Prompt must be non-empty text.")

        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
        }
        request = Request(
            self._endpoint_url(),
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._TIMEOUT_SECONDS) as response:
                response_data = response.read()
        except HTTPError as error:
            raise AIServiceError(
                f"DeepSeek API request failed with HTTP {error.code}."
            ) from error
        except (URLError, TimeoutError, OSError) as error:
            raise AIServiceError("Unable to reach the DeepSeek API.") from error

        try:
            result: Any = json.loads(response_data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise AIServiceError("DeepSeek API returned invalid JSON.") from error

        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise AIServiceError("DeepSeek API returned an unexpected response.") from error

    def _endpoint_url(self) -> str:
        """Build the chat-completions URL from the configured base URL."""
        return f"{self._base_url.rstrip('/')}{self._CHAT_COMPLETIONS_PATH}"
