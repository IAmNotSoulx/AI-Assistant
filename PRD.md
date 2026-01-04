# AI-Assistant (Desktop Gaming Helper)

## Summary
A Windows desktop assistant with a chat UI optimized for gaming support. It can:
- answer questions via LLM,
- browse the web (search + fetch pages) and answer with citations,
- capture the user’s screen and explain what it sees (errors, menus, settings screens),
- open common gaming apps and URLs.

## Target platform
- Windows 11 (v1)

## Primary use-cases
1) “What does this error mean?” (user clicks Capture Screen or asks “explain this”)
2) “Summarize the latest patch notes for X” (browse + cite sources)
3) “Best settings for my situation” (based on user info + browsing + reasoning)
4) “Open Discord / Steam / Ubisoft Connect / Siege / Rust / OBS / MSI Afterburner”
5) “Find me a guide for … and summarize it”

## Goals (v1)
- Desktop chat UI (PySide6) with:
  - chat history
  - buttons: Capture Screen, Open App, Browse (optional), Settings
- LLM provider abstraction:
  - OpenAI and Anthropic supported (keys via .env)
- Tools callable by the assistant:
  - open_app(name_or_path, args?)
  - open_url(url)
  - capture_screen() -> saves screenshot locally and returns path
  - describe_screen(question, screenshot_path) -> vision model call (gated by toggle)
  - web_search(query) -> list of results (title, url, snippet)
  - fetch_url(url) -> extracts readable text
- Browsing must produce answers with source links/citations.

## Non-goals (v1)
- Logging into apps.
- Automating in-game actions (no aim-assist, recoil macros, etc.).
- System-wide spying/stealth behavior.

## Privacy toggles
- “Allow sending screenshots to AI” default OFF
- “Allow browsing (network requests)” default ON (since you want browsing)
- “Redact sensitive info in screenshots” (basic: blur taskbar clock + notifications area) optional

## Architecture
- Language: Python 3.11+
- UI: PySide6
- Screen capture: mss (fast) + Pillow for preview
- Web:
  - search adapter (s
