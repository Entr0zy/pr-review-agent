"""LLM client protocol. Any backend (Gemini, mock, ...) implements `complete`."""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str:
        """Return the model's text response (expected to be JSON) for the prompts."""
        ...
