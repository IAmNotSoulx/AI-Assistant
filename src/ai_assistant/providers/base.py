from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProviderChoice:
    name: str
    provider: "BaseProvider"


class BaseProvider:
    def send_chat(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError

    def describe_screen(self, system_prompt: str, question: str, image_path: str) -> str:
        raise NotImplementedError
