from __future__ import annotations

import base64
import os
from pathlib import Path

import requests

from ai_assistant.providers.base import BaseProvider


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def send_chat(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {"role": msg["role"], "content": msg["content"]} for msg in messages
            ],
            "max_tokens": 800,
            "temperature": 0.2,
        }
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=self._headers(),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]

    def describe_screen(self, system_prompt: str, question: str, image_path: str) -> str:
        encoded = base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": encoded,
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 800,
            "temperature": 0.2,
        }
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=self._headers(),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]
