# Test Plan

## Windows PowerShell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
python -m ai_assistant

## Manual checks
1) Open App -> Notepad opens
2) Capture Screen -> file appears in ./data/screens and thumbnail shows
3) Toggle screenshot sending OFF -> vision blocked
4) Toggle ON -> “What’s on my screen?” produces description
5) Browsing ON -> “Summarize latest patch notes for <game>” returns answer + Sources list
