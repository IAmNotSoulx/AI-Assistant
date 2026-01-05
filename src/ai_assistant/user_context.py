from __future__ import annotations

from pathlib import Path

from ai_assistant.storage import get_repo_root


USER_CONTEXT_FILE = "USER_CONTEXT.md"


def user_context_path() -> Path:
    return get_repo_root() / USER_CONTEXT_FILE


def load_user_context() -> str:
    path = user_context_path()
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8").strip()
    return content
