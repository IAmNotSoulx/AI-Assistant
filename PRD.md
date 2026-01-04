# AI-Assistant (Desktop)

## Summary
A local-first Windows desktop assistant with a chat UI that can:
- answer questions using an LLM,
- open applications,
- capture the current screen and describe/comment on it using a vision-capable model,
- assist with web logins by launching a controlled browser profile (persistent session).

## Target platform
- Windows 11 (primary). Cross-platform is a stretch goal.

## Goals
1. Chat UI (desktop app) where user can ask questions.
2. “Tools” the assistant can call:
   - Open an app (e.g., Discord, Chrome, Steam) and optionally bring it to front.
   - Open a URL in a controlled browser.
   - Capture screen and send to vision model for description and Q&A about what’s visible.
3. Simple settings UI:
   - Choose provider: OpenAI or Anthropic (key in .env; provider can be disabled if no key).
   - Toggle: “Allow sending screenshots to provider” (default OFF).
   - Toggle: “Allow automation (mouse/keyboard)” (default OFF).
4. Safety/confirmation UX (even for personal use):
   - Any automation action (typing/clicking) must show a confirmation dialog with a preview of what will happen.

## Non-goals (v1)
- Universal “log into any native desktop app” automation.
- Running as a system-level keylogger or capturing passwords from other apps.
- Full self-updating, cloud sync, multi-device.

## Login approach (v1)
- Web logins only:
  - The assistant can launch a Playwright-controlled Chromium with a persistent profile directory.
  - User completes login manually the first time.
  - Subsequent sessions reuse cookies/session, so assistant can navigate authenticated pages.
- Native app logins:
  - Out of scope for v1 unless the user defines a per-app macro (future: macro runner).

## UX requirements
- Main window: chat transcript + input box + buttons:
  - “Capture Screen”
  - “Open App”
  - “Settings”
- Tray icon with “Show/Hide” and “Quit”.
- Optional hotkey for screen capture (nice-to-have).

## Architecture
- Python 3.11+
- UI: PySide6 (Qt)
- Core agent:
  - Maintains conversation history.
  - Uses “tool calling” style: model returns either a direct answer or a tool request.
  - Tool execution returns results back to the model for final response.
- Tools:
  - open_app(app_name, args?)
  - open_url(url)
  - capture_screen() -> image bytes saved locally + path
  - describe_screen(question?) -> calls vision model with screenshot (only if allowed)
  - (optional) automation: type_text(text), click(x,y) — behind confirmation + toggle

## Storage
- Local folder: ./data
- Logs: ./data/logs
- Screenshots: ./data/screens
- Settings: ./data/settings.json (never store API keys here)

## Configuration
- .env:
  - OPENAI_API_KEY=
  - ANTHROPIC_API_KEY=
  - DEFAULT_PROVIDER=openai|anthropic
