# Test Plan

## Commands
- Create venv, install deps, run tests:
  - Windows PowerShell:
    - py -m venv .venv
    - .\.venv\Scripts\Activate.ps1
    - pip install -r requirements.txt
    - pytest

## What must pass
- All pytest tests green.
- App launches:
  - python -m ai_assistant

## Manual checks
1. Open app from UI.
2. Capture screen saves file to ./data/screens.
3. Toggle screenshot sending OFF and verify vision is not called.
4. Toggle ON and verify “What’s on my screen?” returns a description.
5. Web login helper opens a persistent browser profile and stays logged in after restart.
