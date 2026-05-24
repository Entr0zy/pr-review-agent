"""Gemini backend (used for the Google Cloud Rapid Agent hackathon build).

Requires the optional dependency: ``pip install google-genai``. The import is
lazy so the rest of the package works without it installed.
"""
from __future__ import annotations

import os


class GeminiClient:
    def __init__(self, model: str = "gemini-2.5-pro", api_key: str | None = None):
        # NOTE: switch `model` to the Gemini 3 model id for the hackathon submission.
        try:
            from google import genai
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise ImportError(
                "google-genai is not installed. Run: pip install 'pr-review-agent[gemini]'"
            ) from exc
        self._genai = genai
        self._client = genai.Client(api_key=api_key or os.environ.get("GEMINI_API_KEY"))
        self._model = model

    def complete(self, system: str, user: str) -> str:  # pragma: no cover - needs network
        response = self._client.models.generate_content(
            model=self._model,
            contents=user,
            config={
                "system_instruction": system,
                "response_mime_type": "application/json",
                "temperature": 0.1,
            },
        )
        return response.text or "{}"
