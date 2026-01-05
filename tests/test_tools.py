from __future__ import annotations

import os

import pytest

from ai_assistant.settings import Settings
from ai_assistant.tools import ToolRegistry


class DummyProvider:
    def describe_screen(self, system_prompt: str, question: str, image_path: str) -> str:
        return f"desc:{question}"


def test_tool_registry_dispatch(monkeypatch):
    settings = Settings(allow_screenshots=True, allow_browsing=True)
    registry = ToolRegistry(settings, DummyProvider())

    monkeypatch.setattr("ai_assistant.tools.os.path.exists", lambda _: True)
    called = {}

    def fake_popen(args, shell=False):
        called["args"] = args
        return None

    monkeypatch.setattr("ai_assistant.tools.subprocess.Popen", fake_popen)
    result = registry.open_app("C:\\fake.exe")
    assert result.success is True
    assert called["args"][0] == "C:\\fake.exe"

    result = registry.call("unknown_tool")
    assert result.success is False


def test_describe_screen_blocked():
    settings = Settings(allow_screenshots=False, allow_browsing=True)
    registry = ToolRegistry(settings, DummyProvider())
    result = registry.describe_screen("What?", "path.png")
    assert result.success is False
    assert "disabled" in result.message


@pytest.mark.skipif(os.name != "nt" and not os.getenv("DISPLAY"), reason="No display")
def test_capture_screen(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_DATA_DIR", str(tmp_path))
    settings = Settings(allow_screenshots=False, allow_browsing=True)
    registry = ToolRegistry(settings, None)
    result = registry.capture_screen()
    assert result.success is True
    assert os.path.exists(result.data["path"])
