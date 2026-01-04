# Acceptance Criteria (v1)

## A. App boots and runs
- App launches on Windows with a visible chat UI.
- README includes setup/run steps that work from a clean machine.

## B. Chat Q&A
- When user asks a general question, assistant responds with a coherent answer.
- Provider selection works:
  - If only OpenAI key is set, OpenAI provider works and Anthropic is disabled (and vice versa).
  - If neither key exists, app shows a clear error state and does not crash.

## C. Open apps
- User can click “Open App” and select from:
  - a small curated list (Notepad, Calculator, Chrome) + a “Custom path…” option.
- Assistant can also open apps via chat command/tool call.
- Opening an app does not freeze the UI.

## D. Screen capture + vision
- “Capture Screen” saves a timestamped screenshot to ./data/screens and shows a thumbnail preview.
- If “Allow sending screenshots” is OFF:
  - assistant can still save screenshot locally but must not call vision APIs.
- If ON:
  - user can ask: “What’s on my screen?” and receive a description.
  - user can ask a targeted question: “What does this error message mean?” and assistant answers using what it sees.

## E. Web login helper (Playwright persistent profile)
- Assistant can open a URL in a persistent browser profile.
- Sessions persist across runs (cookie/session reuse).
- No attempt is made to read passwords from other apps or capture credentials.
- For MFA/captcha, assistant instructs the user to complete it manually.

## F. Automation gating (if implemented)
- Mouse/keyboard automation is disabled by default.
- Enabling it requires explicit toggle in settings.
- Each automation action requires confirmation that displays:
  - action type
  - parameters (text to type, coordinates to click)
  - cancel option

## G. Quality
- `pytest` test suite runs.
- Basic unit tests exist for:
  - settings load/save
  - tool registry
  - screenshot capture function (mocked where needed)
  - provider selection logic (mocked network)
