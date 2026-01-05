from __future__ import annotations

import os

from ai_assistant.providers.factory import select_provider


def test_select_provider_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    choice = select_provider()
    assert choice is not None
    assert choice.name == "openai"


def test_select_provider_anthropic(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    choice = select_provider()
    assert choice is not None
    assert choice.name == "anthropic"


def test_select_provider_none(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    choice = select_provider()
    assert choice is None
