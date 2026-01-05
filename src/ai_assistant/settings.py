from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from ai_assistant.storage import get_data_dir, ensure_data_dirs


SETTINGS_FILE_NAME = "settings.json"


@dataclass
class Settings:
    allow_screenshots: bool = False
    allow_browsing: bool = True


def settings_path() -> Path:
    data_dir = ensure_data_dirs()["data"]
    return data_dir / SETTINGS_FILE_NAME


def load_settings() -> Settings:
    path = settings_path()
    if not path.exists():
        settings = Settings()
        save_settings(settings)
        return settings
    data = json.loads(path.read_text(encoding="utf-8"))
    return Settings(
        allow_screenshots=bool(data.get("allow_screenshots", False)),
        allow_browsing=bool(data.get("allow_browsing", True)),
    )


def save_settings(settings: Settings) -> None:
    path = settings_path()
    path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
