from __future__ import annotations

import os

from ai_assistant.providers.anthropic_provider import AnthropicProvider
from ai_assistant.providers.base import ProviderChoice
from ai_assistant.providers.openai_provider import OpenAIProvider


def select_provider() -> ProviderChoice | None:
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if openai_key:
        return ProviderChoice(name="openai", provider=OpenAIProvider(openai_key))
    if anthropic_key:
        return ProviderChoice(name="anthropic", provider=AnthropicProvider(anthropic_key))
    return None
