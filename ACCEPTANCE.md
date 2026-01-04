# Acceptance Criteria (v1)

## A) Launch + UI
- App launches on Windows 11.
- Main window shows:
  - chat transcript
  - input box + Send
  - buttons: Capture Screen, Open App, Settings
- UI remains responsive during tool calls (use threads/async where needed).

## B) Q&A (no browsing)
- If user asks a general question, assistant responds (using provider model).
- If no keys are configured, app shows a clear “No provider configured” message and does not crash.

## C) Open App
- “Open App” supports a curated list + “Custom path…”
  - Steam, Discord, Chrome, Notepad, Calculator (minimum set)
- Can also open by chat command/tool call.
- Returns success/failure message in chat.

## D) Screen vision
- Capture Screen saves an image to ./data/screens with timestamp filename.
- After capture, app shows a thumbnail preview in UI.
- If “Allow sending screenshots” is OFF:
  - describe_screen is blocked with an explanation.
- If ON:
  - Asking “What’s on my screen?” returns a description.
  - Asking “Explain this error” returns an explanation referencing visible text.

## E) Browsing
- If “Allow browsing” is ON:
  - Asking “Find sources about X” triggers web_search + fetch_url, then answers with citations (URLs listed).
  - At least 2 sources are used when available.
- If OFF:
  - browsing tools are blocked with an explanation.

## F) Source handling
- When using browsing, assistant response includes:
  - a short answer
  - “Sources:” list of URLs used

## G) Tests
- `pytest` passes.
- Tests exist for:
  - settings load/save
  - tool registry + dispatch
  - capture_screen (can be integration-ish but should skip in CI if no display; provide fallback)
  - browsing pipeline (fully mocked HTTP/search)
  - provider selection logic (mocked)

## H) Repo quality
- requirements.txt present
- README has copy/paste steps for Windows PowerShell
- Optional: GitHub Actions workflow runs pytest on PRs

## I) Game Profiles
- UI includes a Profile selector (dropdown or segmented control) with:
  - Siege, Rust, Valorant, D&D
- Selecting a profile changes the assistant behavior:
  - A profile label is visible in the UI.
  - Quick action buttons update to that profile’s set.
  - Browsing queries automatically include profile keywords.

## J) Quick Actions
- The UI shows 4–6 quick action buttons per profile.
- Clicking a quick action fills the input box (or sends immediately) with a templated prompt.

## K) Profile Defaults (Open App / URLs)
- For Siege/Rust/Valorant profiles:
  - “Open App” includes sensible defaults (launchers) and a “Custom path…” option.
- For D&D profile:
  - “Open App” includes opening a default URL (e.g., a D&D reference site) instead of a launcher.
