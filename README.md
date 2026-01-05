# AI-Assistant (Desktop Gaming Helper)

A minimal Windows desktop assistant built with PySide6. It supports chat-based help, screen capture, profile-aware prompts, OpenAI/Anthropic providers, and a persistent Playwright browser opener.

## Features
- Chat UI with profile selector and quick actions.
- Screen capture saved to `./data/screens` with thumbnail preview.
- Tool calling: `open_app`, `open_url`, `capture_screen`, `describe_screen`, `web_search`, `fetch_url`.
- Provider abstraction: OpenAI + Anthropic (keys via environment variables).
- User context injection from `USER_CONTEXT.md` (editable via Settings).
- Screenshot upload is **OFF by default** and gated in Settings.

## Windows Setup (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install
```

## Run (PowerShell)
```powershell
$env:OPENAI_API_KEY="YOUR_KEY"  # or set $env:ANTHROPIC_API_KEY
$env:PYTHONPATH="src"
python -m ai_assistant.main
```

On first run, the app creates a `./data` directory with:
- `data/screens` (screenshots)
- `data/browser` (Playwright profile)
- `data/logs`

## Settings
- **Allow sending screenshots to AI** (default OFF).
- **Allow browsing (network requests)** (default ON).
- **Edit User Context** opens `USER_CONTEXT.md` in your default editor.

## Tests (PowerShell)
```powershell
$env:PYTHONPATH="src"
pytest
```

## Environment Variables
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`: provider keys.
- `OPENAI_MODEL`: OpenAI chat model (default `gpt-4o-mini`).
- `OPENAI_VISION_MODEL`: OpenAI vision model (defaults to `OPENAI_MODEL`).
- `ANTHROPIC_MODEL`: Anthropic model (default `claude-3-5-sonnet-20241022`).
- `AI_ASSISTANT_DATA_DIR`: custom data directory (defaults to `./data`).
