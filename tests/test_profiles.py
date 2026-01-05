from __future__ import annotations

from ai_assistant.profiles import load_profiles


def test_load_profiles():
    profiles = load_profiles()
    assert profiles
    names = {profile.name for profile in profiles}
    assert "Rainbow Six Siege" in names
