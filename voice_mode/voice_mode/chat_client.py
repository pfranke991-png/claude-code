"""Provider-agnostische Chat-Anbindung über OpenAI-kompatible APIs."""

from __future__ import annotations

from typing import List

from openai import OpenAI

from .config import Settings


class ChatClient:
    """Minimale Chat-Session mit auswählbarem Provider."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        client_kwargs = {}
        base_url = settings.resolved_base_url()
        if base_url:
            client_kwargs["base_url"] = base_url
        if settings.api_key:
            client_kwargs["api_key"] = settings.api_key
        elif settings.provider == "lmstudio":
            client_kwargs["api_key"] = "lm-studio"
        self.client = OpenAI(**client_kwargs)
        self.history: List[dict] = [
            {
                "role": "system",
                "content": (
                    "Du bist ein prägnanter Assistent für Voice-Chat. Antworte kurz, klar "
                    "und vermeide lange Aufzählungen, damit Text-to-Speech schnell ist."
                ),
            }
        ]

    def list_models(self) -> list[str]:
        models = self.client.models.list()
        return sorted([entry.id for entry in models.data])

    def ask(self, user_text: str) -> str:
        self.history.append({"role": "user", "content": user_text})
        response = self.client.chat.completions.create(model=self.settings.model, messages=self.history)
        choice = response.choices[0].message.content or ""
        self.history.append({"role": "assistant", "content": choice})
        print(f"[assistant] {choice}")
        return choice
