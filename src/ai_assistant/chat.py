from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from ai_assistant.profiles import GameProfile
from ai_assistant.settings import Settings
from ai_assistant.user_context import load_user_context


TOOL_CALL_PATTERN = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class ChatMessage:
    role: str
    content: str


def build_system_prompt(profile: GameProfile, settings: Settings) -> str:
    user_context = load_user_context()
    tool_instructions = (
        "You can call tools by responding with a JSON object: "
        "{\"tool\": \"tool_name\", \"args\": { ... }}. "
        "Available tools: open_app(name_or_path, args?), open_url(url), "
        "capture_screen(), describe_screen(question, screenshot_path), "
        "web_search(query), fetch_url(url). "
        "If you call a tool, respond with ONLY the JSON."
    )
    browsing_instruction = (
        "If browsing tools are used, include a 'Sources:' section listing the URLs."
    )
    base = (
        "You are a Windows desktop gaming helper. "
        "Be concise, practical, and provide step-by-step troubleshooting when needed."
    )
    prompt_parts = [base, profile.system_prefix, tool_instructions, browsing_instruction]
    if user_context:
        prompt_parts.append(f"User context:\n{user_context}")
    return "\n\n".join(part for part in prompt_parts if part)


def parse_tool_call(text: str) -> tuple[str, dict[str, Any]] | None:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            data = json.loads(stripped)
            if "tool" in data:
                return data["tool"], data.get("args", {})
        except json.JSONDecodeError:
            return None
    match = TOOL_CALL_PATTERN.search(text)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    if "tool" in data:
        return data["tool"], data.get("args", {})
    return None
