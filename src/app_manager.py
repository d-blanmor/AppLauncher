from __future__ import annotations

import subprocess
import uuid
from typing import Any

from .config_store import ConfigStore
from .process_manager import ProcessManager


class AppManager:
    def __init__(self, config_path: str | None = None):
        self.config_store = ConfigStore(config_path)
        self.apps: list[dict[str, Any]] = self.config_store.load_apps()
        self.settings: dict[str, Any] = self.config_store.load_settings()
        self.running_processes: dict[str, subprocess.Popen[str]] = {}

    def _save(self) -> None:
        self.config_store.save_apps(self.apps)

    def get_settings(self) -> dict[str, Any]:
        return self.settings

    def save_settings(self, settings: dict[str, Any]) -> None:
        self.settings = {"close_behavior": settings.get("close_behavior", "tray")}
        self.config_store.save_settings(self.settings)

    def get_apps(self) -> list[dict[str, Any]]:
        return self.apps

    def add_app(self, app: dict[str, Any]) -> dict[str, Any]:
        normalized = self._normalize_app(app)
        self.apps.append(normalized)
        self._save()
        return normalized

    def update_app(self, app_id: str, app: dict[str, Any]) -> dict[str, Any]:
        for index, current in enumerate(self.apps):
            if current.get("id") == app_id:
                merged = self._normalize_app({**current, **app})
                merged["id"] = app_id
                self.apps[index] = merged
                self._save()
                return merged
        raise ValueError(f"App with id '{app_id}' was not found.")

    def remove_app(self, app_id: str) -> None:
        self.apps = [app for app in self.apps if app.get("id") != app_id]
        self._save()

    def start_app(self, app_id: str) -> dict[str, Any]:
        app = self._find_app(app_id)
        if app.get("status") == "running":
            return app

        process = ProcessManager.start_process(app)
        if process is None:
            app["status"] = "error"
            self._save()
            return app

        app["status"] = "running"
        app["pid"] = process.pid
        app["last_log"] = str(ProcessManager.get_log_path(app))
        self.running_processes[app_id] = process
        self._save()
        return app

    def stop_app(self, app_id: str) -> dict[str, Any]:
        app = self._find_app(app_id)
        process = self.running_processes.get(app_id)
        ProcessManager.stop_process(process)
        app["status"] = "stopped"
        app["pid"] = None
        app["last_log"] = str(ProcessManager.get_log_path(app))
        self.running_processes.pop(app_id, None)
        self._save()
        return app

    def _find_app(self, app_id: str) -> dict[str, Any]:
        for app in self.apps:
            if app.get("id") == app_id:
                return app
        raise ValueError(f"App with id '{app_id}' was not found.")

    @staticmethod
    def build_app_id() -> str:
        return uuid.uuid4().hex[:8]

    @staticmethod
    def _normalize_app(app: dict[str, Any]) -> dict[str, Any]:
        args = app.get("args") or []
        if isinstance(args, str):
            args = [item.strip() for item in args.split() if item.strip()]

        normalized = {
            "id": app.get("id") or AppManager.build_app_id(),
            "name": str(app.get("name") or "New App"),
            "description": str(app.get("description") or ""),
            "type": str(app.get("type") or "python").lower(),
            "path": str(app.get("path") or ""),
            "args": [str(arg) for arg in args],
            "working_directory": str(app.get("working_directory") or ""),
            "enabled": bool(app.get("enabled", True)),
            "status": str(app.get("status") or "stopped"),
            "pid": app.get("pid"),
            "output_mode": str(app.get("output_mode") or "both").lower(),
            "last_log": app.get("last_log") or "",
        }
        return normalized
