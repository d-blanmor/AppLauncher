from __future__ import annotations

import subprocess
import uuid
from typing import Any

from .config_store import ConfigStore
from .process_manager import ProcessManager

class AppManager:
    def __init__(self, config_path: str | None = None):
        self.config_store = ConfigStore(config_path)
        payload = self.config_store.load_payload()
        self.title = str(payload.get("title") or "App Launcher").strip() or "App Launcher"
        self.apps: list[dict[str, Any]] = payload.get("apps", [])
        self.settings: dict[str, Any] = payload.get("settings", {"close_behavior": "tray"})
        self.running_processes: dict[str, subprocess.Popen[str]] = {}

    def _save(self) -> None:
        self.config_store.save_apps(self.apps)

    def _find_app(self, app_id: str) -> dict[str, Any]:
        for app in self.apps:
            if app.get("id") == app_id:
                return app
        raise ValueError(f"App with id '{app_id}' was not found.")

    def get_title(self) -> str:
        return str(self.title or "App Launcher").strip() or "App Launcher"

    def get_settings(self) -> dict[str, Any]:
        return self.settings

    def save_settings(self, settings: dict[str, Any]) -> None:
        self.settings = {"close_behavior": settings.get("close_behavior", "tray")}
        self.config_store.save_settings(self.settings)

    def get_apps(self) -> list[dict[str, Any]]:
        for app in self.apps:
            mode = str(app.get("mode") or "application").lower()
            if mode == "service":
                app["status"] = "running" if ProcessManager.is_service_running(app) else "stopped"
                app["pid"] = None
            elif mode == "port":
                app["status"] = "running" if ProcessManager.is_port_reachable(app) else "stopped"
                app["pid"] = None
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

        mode = str(app.get("mode") or "application").lower()
        if mode == "service":
            started = ProcessManager.start_service(app)
            app["status"] = "running" if started else "error"
            app["pid"] = None
            app["last_log"] = str(ProcessManager.get_log_path(app))
            self._save()
            return app
        if mode == "port":
            app["status"] = "stopped"
            app["pid"] = None
            app["last_log"] = str(ProcessManager.get_log_path(app))
            self._save()
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
        mode = str(app.get("mode") or "application").lower()
        if mode == "service":
            ProcessManager.stop_service(app)
            app["status"] = "stopped" if not ProcessManager.is_service_running(app) else "running"
            app["pid"] = None
            app["last_log"] = str(ProcessManager.get_log_path(app))
            self._save()
            return app
        if mode == "port":
            app["status"] = "stopped"
            app["pid"] = None
            app["last_log"] = str(ProcessManager.get_log_path(app))
            self._save()
            return app

        process = self.running_processes.get(app_id)
        ProcessManager.stop_process(process)
        app["status"] = "stopped"
        app["pid"] = None
        app["last_log"] = str(ProcessManager.get_log_path(app))
        self.running_processes.pop(app_id, None)
        self._save()
        return app

    @staticmethod
    def build_app_id() -> str:
        return uuid.uuid4().hex[:8]

    @staticmethod
    def normalize_card_size(value: Any) -> str:
        normalized = str(value or "1x1").strip().lower()
        if normalized not in {"1x1", "1x2", "1x3", "2x1", "2x2", "2x3", "3x1", "3x2", "3x3"}:
            return "1x1"
        return normalized

    @staticmethod
    def _normalize_app(app: dict[str, Any]) -> dict[str, Any]:
        args = app.get("args") or []
        if isinstance(args, str):
            args = [item.strip() for item in args.split() if item.strip()]

        mode = str(app.get("mode") or "application").lower()
        if mode not in {"application", "service", "port"}:
            mode = "application"

        normalized = {
            "id": app.get("id") or AppManager.build_app_id(),
            "name": str(app.get("name") or "New App"),
            "description": str(app.get("description") or ""),
            "card_size": AppManager.normalize_card_size(app.get("card_size")),
            "output_mode": str(app.get("output_mode") or "both").lower(),
            "status": str(app.get("status") or "stopped"),
            "enabled": bool(app.get("enabled", True)),
            "mode": mode,
            "type": str(app.get("type") or "python").lower(),
            "working_directory": str(app.get("working_directory") or ""),
            "venv": str(app.get("venv") or ""),
            "program": str(app.get("program") or ""),
            "args": [str(arg) for arg in args],
            "service_name": str(app.get("service_name") or "").strip(),
            "port_host": str(app.get("port_host") or "localhost").strip() or "localhost",
            "port_number": int(app.get("port_number") or 0) if str(app.get("port_number") or "0").strip().isdigit() else 0,
            "pid": app.get("pid"),
            "last_log": app.get("last_log") or "",
        }
        return normalized
