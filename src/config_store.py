from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigStore:
    def __init__(self, path: str | Path | None = None):
        base_path = Path(path) if path is not None else Path(__file__).resolve().parents[1]
        self.path = base_path if base_path.suffix.lower() == ".json" else base_path / "app_launcher.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save_payload({"apps": [], "settings": {"close_behavior": "tray"}})

    def load_payload(self) -> dict[str, Any]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {"apps": [], "settings": {"close_behavior": "tray"}}

        if not isinstance(raw, dict):
            return {"apps": [], "settings": {"close_behavior": "tray"}}

        apps = raw.get("apps", [])
        settings = raw.get("settings", {})
        if not isinstance(settings, dict):
            settings = {}

        settings.setdefault("close_behavior", "tray")
        return {"apps": apps if isinstance(apps, list) else [], "settings": settings}

    def load_apps(self) -> list[dict[str, Any]]:
        return self.load_payload().get("apps", [])

    def save_apps(self, apps: list[dict[str, Any]]) -> None:
        payload = self.load_payload()
        payload["apps"] = apps
        self.save_payload(payload)

    def load_settings(self) -> dict[str, Any]:
        return self.load_payload().get("settings", {"close_behavior": "tray"})

    def save_settings(self, settings: dict[str, Any]) -> None:
        payload = self.load_payload()
        payload["settings"] = {"close_behavior": settings.get("close_behavior", "tray")}
        self.save_payload(payload)

    def save_payload(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
