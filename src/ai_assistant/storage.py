from __future__ import annotations

import os
from pathlib import Path


DEFAULT_DATA_DIR_NAME = "data"


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_data_dir() -> Path:
    override = os.getenv("AI_ASSISTANT_DATA_DIR")
    if override:
        return Path(override)
    return Path.cwd().joinpath(DEFAULT_DATA_DIR_NAME)


def ensure_data_dirs() -> dict[str, Path]:
    data_dir = get_data_dir()
    screens_dir = data_dir / "screens"
    browser_dir = data_dir / "browser"
    logs_dir = data_dir / "logs"
    for path in (data_dir, screens_dir, browser_dir, logs_dir):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "data": data_dir,
        "screens": screens_dir,
        "browser": browser_dir,
        "logs": logs_dir,
    }
