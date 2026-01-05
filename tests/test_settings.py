from __future__ import annotations

import json
from pathlib import Path

from ai_assistant.settings import load_settings, save_settings, Settings


def test_settings_load_save(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_ASSISTANT_DATA_DIR", str(tmp_path))
    settings = load_settings()
    assert settings.allow_screenshots is False
    assert settings.allow_browsing is True

    settings.allow_screenshots = True
    settings.allow_browsing = False
    save_settings(settings)

    data = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
    assert data["allow_screenshots"] is True
    assert data["allow_browsing"] is False

    loaded = load_settings()
    assert loaded.allow_screenshots is True
    assert loaded.allow_browsing is False
