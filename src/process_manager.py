from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


class ProcessManager:
    @staticmethod
    def read_log(app: dict[str, Any], max_lines: int = 20) -> str:
        log_path = ProcessManager.get_log_path(app)
        if not log_path.exists():
            return "No log output yet."

        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if max_lines and len(lines) > max_lines:
            lines = lines[-max_lines:]
        return "\n".join(lines) if lines else "No log output yet."

    @staticmethod
    def determine_python_executable() -> str:
        return shutil.which("python") or shutil.which("py") or "python"

    @staticmethod
    def determine_node_executable() -> str:
        return shutil.which("node") or "node"

    @staticmethod
    def get_log_path(app: dict[str, Any]) -> Path:
        root = Path(__file__).resolve().parents[1]
        logs_dir = root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in app.get("name", "app"))
        return logs_dir / f"{safe_name}.log"

    @staticmethod
    def build_command(app: dict[str, Any]) -> list[str]:
        app_type = str(app.get("type", "python")).lower()
        path_value = str(app.get("path", "")).strip()
        args = [str(arg) for arg in app.get("args", [])]

        if app_type == "python":
            executable = ProcessManager.determine_python_executable()
            command = [executable]
            if path_value:
                command.append(path_value)
            command.extend(args)
            return command

        if app_type == "node":
            executable = ProcessManager.determine_node_executable()
            command = [executable]
            if path_value:
                command.append(path_value)
            command.extend(args)
            return command

        if app_type == "batch":
            command = ["cmd.exe", "/c"]
            if path_value:
                command.append(path_value)
            command.extend(args)
            return command

        command = []
        if path_value:
            command.append(path_value)
        command.extend(args)
        return command

    @staticmethod
    def start_process(app: dict[str, Any]) -> subprocess.Popen[str] | None:
        command = ProcessManager.build_command(app)
        if not command:
            return None

        working_dir = app.get("working_directory") or os.path.dirname(app.get("path")) or None
        log_path = ProcessManager.get_log_path(app)
        output_mode = str(app.get("output_mode") or "both").lower()

        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n--- Starting: {app.get('name', 'App')} ---\n")
            log_file.write(f"Command: {' '.join(command)}\n\n")

        kwargs: dict[str, Any] = {
            "cwd": working_dir,
            "stdin": subprocess.DEVNULL,
            "shell": False,
            "text": True,
        }

        if output_mode in {"file", "both"}:
            stdout_target = open(log_path, "a", encoding="utf-8", newline="")
            stderr_target = open(log_path, "a", encoding="utf-8", newline="")
            kwargs["stdout"] = stdout_target
            kwargs["stderr"] = stderr_target

        if output_mode in {"console", "both"} and hasattr(subprocess, "CREATE_NEW_CONSOLE"):
            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE

        process = subprocess.Popen(command, **kwargs)
        if output_mode in {"file", "both"}:
            process._app_launcher_log_handles = kwargs["stdout"], kwargs["stderr"]
        return process

    @staticmethod
    def stop_process(process: subprocess.Popen[str] | None) -> None:
        if process is None:
            return
        handles = getattr(process, "_app_launcher_log_handles", None)
        if handles:
            for handle in handles:
                try:
                    handle.close()
                except Exception:
                    pass
        if process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
