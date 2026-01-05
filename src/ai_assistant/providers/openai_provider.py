from __future__ import annotations

import base64
import os
from pathlib import Path

import requests

from ai_assistant.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.vision_model = os.getenv("OPENAI_VISION_MODEL", self.model)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def send_chat(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": 0.2,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=self._headers(),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def describe_screen(self, system_prompt: str, question: str, image_path: str) -> str:
        encoded = base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")
        payload = {
            "model": self.vision_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded}"
                            },
                        },
                    ],
                },
            ],
            "temperature": 0.2,
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=self._headers(),
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
