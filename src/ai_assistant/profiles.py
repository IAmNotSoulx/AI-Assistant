from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ai_assistant.storage import get_repo_root


@dataclass
class QuickAction:
    label: str
    prompt: str


@dataclass
class AppTarget:
    label: str
    type: str
    value: str


@dataclass
class GameProfile:
    profile_id: str
    name: str
    keywords: list[str]
    system_prefix: str
    quick_actions: list[QuickAction]
    app_targets: list[AppTarget]
    default_urls: list[dict[str, str]]


DEFAULT_PROFILES_FILE = "GAME_PROFILES.json"


def load_profiles(file_path: Path | None = None) -> list[GameProfile]:
    path = file_path or get_repo_root() / DEFAULT_PROFILES_FILE
    raw = json.loads(path.read_text(encoding="utf-8"))
    profiles = []
    for entry in raw.get("profiles", []):
        profiles.append(
            GameProfile(
                profile_id=entry["id"],
                name=entry["name"],
                keywords=entry.get("keywords", []),
                system_prefix=entry.get("system_prefix", ""),
                quick_actions=[
                    QuickAction(label=item["label"], prompt=item["prompt"])
                    for item in entry.get("quick_actions", [])
                ],
                app_targets=[
                    AppTarget(label=item["label"], type=item["type"], value=item["value"])
                    for item in entry.get("app_targets", [])
                ],
                default_urls=entry.get("default_urls", []),
            )
        )
    return profiles
