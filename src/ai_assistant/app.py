from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PySide6 import QtCore, QtGui, QtWidgets

from ai_assistant.chat import build_system_prompt, parse_tool_call
from ai_assistant.profiles import GameProfile, load_profiles
from ai_assistant.providers.factory import select_provider
from ai_assistant.settings import Settings, load_settings, save_settings
from ai_assistant.storage import ensure_data_dirs
from ai_assistant.tools import ToolRegistry
from ai_assistant.user_context import user_context_path


@dataclass
class ToolContext:
    registry: ToolRegistry
    system_prompt: str


class ChatWorker(QtCore.QObject):
    finished = QtCore.Signal(str)
    tool_event = QtCore.Signal(str)
    error = QtCore.Signal(str)

    def __init__(self, messages: list[dict[str, str]], profile: GameProfile, settings: Settings):
        super().__init__()
        self.messages = messages
        self.profile = profile
        self.settings = settings

    def run(self) -> None:
        provider_choice = select_provider()
        if not provider_choice:
            self.error.emit("No provider configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY.")
            return

        system_prompt = build_system_prompt(self.profile, self.settings)
        registry = ToolRegistry(self.settings, provider_choice.provider)
        tool_context = ToolContext(registry=registry, system_prompt=system_prompt)

        sources: list[str] = []
        loop_guard = 0
        while loop_guard < 3:
            loop_guard += 1
            response = provider_choice.provider.send_chat(system_prompt, self.messages)
            tool_call = parse_tool_call(response)
            if not tool_call:
                final = response
                if sources and "Sources:" not in final:
                    final = f"{final}\n\nSources:\n" + "\n".join(sources)
                self.finished.emit(final)
                return
            tool_name, args = tool_call
            if tool_name == "web_search":
                keywords = " ".join(self.profile.keywords)
                if keywords:
                    query = args.get("query", "")
                    args["query"] = f"{query} {keywords}".strip()
            if tool_name == "describe_screen":
                args["system_prompt"] = system_prompt
            result = tool_context.registry.call(tool_name, **args)
            self.tool_event.emit(f"{tool_name}: {result.message}")
            if result.data:
                if tool_name == "fetch_url":
                    sources.append(result.data.get("url", ""))
                if tool_name == "web_search":
                    results = result.data.get("results", [])
                    sources.extend([item.get("url", "") for item in results])
            self.messages.append(
                {
                    "role": "assistant",
                    "content": f"Tool result ({tool_name}): {result.message}",
                }
            )

        self.error.emit("Tool loop reached its limit. Please try again.")


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings: Settings, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.settings = settings

        self.allow_screenshots = QtWidgets.QCheckBox("Allow sending screenshots to AI")
        self.allow_screenshots.setChecked(settings.allow_screenshots)
        self.allow_browsing = QtWidgets.QCheckBox("Allow browsing (network requests)")
        self.allow_browsing.setChecked(settings.allow_browsing)

        self.user_context_button = QtWidgets.QPushButton("Edit User Context")
        self.user_context_button.clicked.connect(self.open_user_context)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.allow_screenshots)
        layout.addWidget(self.allow_browsing)
        layout.addWidget(self.user_context_button)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def open_user_context(self) -> None:
        path = user_context_path()
        if not path.exists():
            path.write_text("# User Context\n", encoding="utf-8")
        os.startfile(path)  # nosec - Windows default editor

    def apply(self) -> None:
        self.settings.allow_screenshots = self.allow_screenshots.isChecked()
        self.settings.allow_browsing = self.allow_browsing.isChecked()
        save_settings(self.settings)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AI Assistant")
        ensure_data_dirs()
        self.settings = load_settings()
        self.profiles = load_profiles()
        self.current_profile = self.profiles[0]
        self.messages: list[dict[str, str]] = []

        self.profile_selector = QtWidgets.QComboBox()
        for profile in self.profiles:
            self.profile_selector.addItem(profile.name, profile)
        self.profile_selector.currentIndexChanged.connect(self.on_profile_changed)

        self.profile_label = QtWidgets.QLabel(f"Profile: {self.current_profile.name}")

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(QtWidgets.QLabel("Profile"))
        top_layout.addWidget(self.profile_selector)
        top_layout.addStretch()
        top_layout.addWidget(self.profile_label)

        self.chat_display = QtWidgets.QTextEdit()
        self.chat_display.setReadOnly(True)

        self.thumbnail_label = QtWidgets.QLabel()
        self.thumbnail_label.setFixedSize(200, 120)
        self.thumbnail_label.setStyleSheet("border: 1px solid #ccc;")
        self.thumbnail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail_label.setText("No screenshot")

        self.quick_actions_layout = QtWidgets.QHBoxLayout()
        self.quick_actions_widget = QtWidgets.QWidget()
        self.quick_actions_widget.setLayout(self.quick_actions_layout)

        self.input_box = QtWidgets.QLineEdit()
        self.input_box.returnPressed.connect(self.on_send)
        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.clicked.connect(self.on_send)

        self.capture_button = QtWidgets.QPushButton("Capture Screen")
        self.capture_button.clicked.connect(self.on_capture)
        self.open_app_button = QtWidgets.QPushButton("Open App")
        self.open_app_button.clicked.connect(self.on_open_app)
        self.settings_button = QtWidgets.QPushButton("Settings")
        self.settings_button.clicked.connect(self.on_settings)

        action_layout = QtWidgets.QHBoxLayout()
        action_layout.addWidget(self.capture_button)
        action_layout.addWidget(self.open_app_button)
        action_layout.addWidget(self.settings_button)
        action_layout.addStretch()

        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.chat_display)
        layout.addWidget(self.thumbnail_label)
        layout.addWidget(self.quick_actions_widget)
        layout.addLayout(action_layout)
        layout.addLayout(input_layout)

        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.update_quick_actions()

    def append_chat(self, role: str, content: str) -> None:
        self.chat_display.append(f"<b>{role}:</b> {content}")

    def on_profile_changed(self) -> None:
        self.current_profile = self.profile_selector.currentData()
        self.profile_label.setText(f"Profile: {self.current_profile.name}")
        self.update_quick_actions()

    def update_quick_actions(self) -> None:
        while self.quick_actions_layout.count():
            item = self.quick_actions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for action in self.current_profile.quick_actions:
            button = QtWidgets.QPushButton(action.label)
            button.clicked.connect(lambda checked=False, prompt=action.prompt: self.fill_prompt(prompt))
            self.quick_actions_layout.addWidget(button)
        self.quick_actions_layout.addStretch()

    def fill_prompt(self, prompt: str) -> None:
        self.input_box.setText(prompt)
        self.input_box.setFocus()

    def on_send(self) -> None:
        text = self.input_box.text().strip()
        if not text:
            return
        self.input_box.clear()
        self.append_chat("User", text)
        self.messages.append({"role": "user", "content": text})
        self.start_worker()

    def start_worker(self) -> None:
        self.send_button.setEnabled(False)
        self.capture_button.setEnabled(False)
        self.open_app_button.setEnabled(False)
        self.settings_button.setEnabled(False)

        self.thread = QtCore.QThread()
        self.worker = ChatWorker(self.messages.copy(), self.current_profile, self.settings)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_response)
        self.worker.tool_event.connect(self.on_tool_event)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_response(self, text: str) -> None:
        self.append_chat("Assistant", text)
        self.messages.append({"role": "assistant", "content": text})
        self.reset_controls()

    def on_tool_event(self, text: str) -> None:
        self.append_chat("Tool", text)
        self.reset_controls()

    def on_error(self, message: str) -> None:
        self.append_chat("Error", message)
        self.reset_controls()

    def reset_controls(self) -> None:
        self.send_button.setEnabled(True)
        self.capture_button.setEnabled(True)
        self.open_app_button.setEnabled(True)
        self.settings_button.setEnabled(True)

    def on_capture(self) -> None:
        registry = ToolRegistry(self.settings, None)
        result = registry.capture_screen()
        self.append_chat("Tool", result.message)
        if result.data and result.data.get("path"):
            pixmap = QtGui.QPixmap(result.data["path"]).scaled(
                self.thumbnail_label.width(),
                self.thumbnail_label.height(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
            self.thumbnail_label.setPixmap(pixmap)

    def on_open_app(self) -> None:
        base_targets = [
            {"label": "Steam", "type": "known_app", "value": "steam"},
            {"label": "Discord", "type": "known_app", "value": "discord"},
            {"label": "Chrome", "type": "known_app", "value": "chrome"},
            {"label": "Notepad", "type": "known_app", "value": "notepad"},
            {"label": "Calculator", "type": "known_app", "value": "calculator"},
        ]
        profile_targets = [
            {"label": t.label, "type": t.type, "value": t.value}
            for t in self.current_profile.app_targets
        ]
        all_targets = base_targets + profile_targets
        options = [target["label"] for target in all_targets]
        options.append("Custom path...")
        item, ok = QtWidgets.QInputDialog.getItem(
            self, "Open App", "Select app:", options, 0, False
        )
        if not ok or not item:
            return
        if item == "Custom path...":
            path, ok = QtWidgets.QFileDialog.getOpenFileName(self, "Select application")
            if not ok or not path:
                return
            target_value = path
        else:
            target = next((t for t in all_targets if t["label"] == item), None)
            if not target:
                return
            target_value = target["value"]
            if target["type"] == "url":
                registry = ToolRegistry(self.settings, None)
                result = registry.open_url(target_value)
                self.append_chat("Tool", result.message)
                return
        registry = ToolRegistry(self.settings, None)
        result = registry.open_app(target_value)
        self.append_chat("Tool", result.message)

    def on_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            dialog.apply()


def run() -> None:
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.resize(900, 700)
    window.show()
    app.exec()
