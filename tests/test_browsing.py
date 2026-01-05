from __future__ import annotations

from ai_assistant.settings import Settings
from ai_assistant.tools import ToolRegistry


def test_browsing_pipeline(monkeypatch):
    settings = Settings(allow_screenshots=False, allow_browsing=True)
    registry = ToolRegistry(settings, None)

    class FakeResponse:
        def __init__(self, text: str):
            self.text = text

        def raise_for_status(self):
            return None

    def fake_get(url, params=None, timeout=20):
        if "duckduckgo" in url:
            html = """
            <div class='result'>
              <a class='result__a' href='https://example.com'>Example</a>
              <a class='result__snippet'>Snippet</a>
            </div>
            """
            return FakeResponse(html)
        return FakeResponse("<html><body><h1>Title</h1><p>Content</p></body></html>")

    monkeypatch.setattr("ai_assistant.tools.requests.get", fake_get)

    search_result = registry.web_search("test query")
    assert search_result.success is True
    assert "example.com" in search_result.message
    fetch_result = registry.fetch_url("https://example.com")
    assert fetch_result.success is True
    assert "Content" in fetch_result.message
