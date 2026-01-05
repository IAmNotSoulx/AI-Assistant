from __future__ import annotations

import json
import os
import subprocess
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from mss import mss
from PIL import Image

from ai_assistant.settings import Settings
from ai_assistant.storage import ensure_data_dirs


@dataclass
class ToolResult:
    success: bool
    message: str
    data: dict[str, Any] | None = None


class ToolRegistry:
    def __init__(self, settings: Settings, provider: Any | None) -> None:
        self.settings = settings
        self.provider = provider
        self._tools = {
            "open_app": self.open_app,
            "open_url": self.open_url,
            "capture_screen": self.capture_screen,
            "describe_screen": self.describe_screen,
            "web_search": self.web_search,
            "fetch_url": self.fetch_url,
        }

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def call(self, name: str, **kwargs: Any) -> ToolResult:
        if name not in self._tools:
            return ToolResult(False, f"Unknown tool: {name}")
        return self._tools[name](**kwargs)

    def open_app(self, name_or_path: str, args: list[str] | None = None) -> ToolResult:
        args = args or []
        if os.path.exists(name_or_path):
            try:
                subprocess.Popen([name_or_path, *args], shell=False)
                return ToolResult(True, f"Opened {name_or_path}.")
            except OSError as exc:
                return ToolResult(False, f"Failed to open {name_or_path}: {exc}")

        known = _resolve_known_app(name_or_path)
        if known:
            try:
                subprocess.Popen([*known, *args], shell=False)
                return ToolResult(True, f"Opened {name_or_path}.")
            except OSError as exc:
                return ToolResult(False, f"Failed to open {name_or_path}: {exc}")

        return ToolResult(False, f"Could not find app '{name_or_path}'.")

    def open_url(self, url: str) -> ToolResult:
        dirs = ensure_data_dirs()
        if find_spec("playwright") is not None:
            try:
                context = _get_playwright_context(str(dirs["browser"]))
                page = context.new_page()
                page.goto(url)
                return ToolResult(True, f"Opened {url} in Playwright browser.")
            except Exception as exc:  # pragma: no cover - safety net
                return ToolResult(False, f"Failed to open {url} in Playwright: {exc}")

        webbrowser.open(url)
        return ToolResult(True, f"Opened {url}.")

    def capture_screen(self) -> ToolResult:
        dirs = ensure_data_dirs()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = dirs["screens"] / f"screen_{timestamp}.png"
        with mss() as sct:
            monitor = sct.monitors[1]
            shot = sct.grab(monitor)
            img = Image.frombytes("RGB", shot.size, shot.rgb)
            img.save(filename)
        return ToolResult(True, f"Saved screenshot to {filename}", {"path": str(filename)})

    def describe_screen(
        self, question: str, screenshot_path: str, system_prompt: str | None = None
    ) -> ToolResult:
        if not self.settings.allow_screenshots:
            return ToolResult(False, "Screenshot sending is disabled in Settings.")
        if not self.provider:
            return ToolResult(False, "No provider configured.")
        prompt = system_prompt or ""
        response = self.provider.describe_screen(prompt, question, screenshot_path)
        return ToolResult(True, response)

    def web_search(self, query: str) -> ToolResult:
        if not self.settings.allow_browsing:
            return ToolResult(False, "Browsing is disabled in Settings.")
        response = requests.get(
            "https://duckduckgo.com/html/",
            params={"q": query},
            timeout=20,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.select("a.result__a"):
            title = item.get_text(strip=True)
            url = item.get("href")
            if not url:
                continue
            snippet_elem = item.find_parent("div", class_="result")
            snippet = ""
            if snippet_elem:
                snippet_text = snippet_elem.select_one("a.result__snippet")
                if snippet_text:
                    snippet = snippet_text.get_text(" ", strip=True)
            results.append({"title": title, "url": url, "snippet": snippet})
            if len(results) >= 5:
                break
        return ToolResult(True, json.dumps(results), {"results": results})

    def fetch_url(self, url: str) -> ToolResult:
        if not self.settings.allow_browsing:
            return ToolResult(False, "Browsing is disabled in Settings.")
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.stripped_strings)
        trimmed = text[:4000]
        return ToolResult(True, trimmed, {"url": url, "text": trimmed})


def _resolve_known_app(name: str) -> list[str] | None:
    app = name.lower()
    if app in {"notepad", "notepad.exe"}:
        return ["notepad.exe"]
    if app in {"calculator", "calc", "calc.exe"}:
        return ["calc.exe"]

    candidates = {
        "steam": [
            r"C:\Program Files (x86)\Steam\Steam.exe",
            r"C:\Program Files\Steam\Steam.exe",
        ],
        "discord": [
            os.path.expandvars(r"%LocalAppData%\Discord\Update.exe"),
        ],
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "riotclient": [
            r"C:\Riot Games\Riot Client\RiotClientServices.exe",
        ],
        "ubisoftconnect": [
            r"C:\Program Files (x86)\Ubisoft\Ubisoft Game Launcher\UbisoftConnect.exe",
            r"C:\Program Files\Ubisoft\Ubisoft Game Launcher\UbisoftConnect.exe",
        ],
    }

    for path in candidates.get(app, []):
        if os.path.exists(path):
            if app == "discord" and path.lower().endswith("update.exe"):
                return [path, "--processStart", "Discord.exe"]
            return [path]
    return None


_PLAYWRIGHT_CONTEXT = None
_PLAYWRIGHT_INSTANCE = None


def _get_playwright_context(user_data_dir: str):
    global _PLAYWRIGHT_CONTEXT
    global _PLAYWRIGHT_INSTANCE
    if _PLAYWRIGHT_CONTEXT is not None:
        return _PLAYWRIGHT_CONTEXT
    from playwright.sync_api import sync_playwright

    _PLAYWRIGHT_INSTANCE = sync_playwright().start()
    _PLAYWRIGHT_CONTEXT = _PLAYWRIGHT_INSTANCE.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
    )
    return _PLAYWRIGHT_CONTEXT
