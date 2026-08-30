from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
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
    def determine_python_executable(app_type: str, base_dir: str, v_env: str) -> str:
        if (base_dir != '' ) and (v_env != ''):
            rx = re.compile(".*\\$")
            if not rx.match(base_dir):
                base_dir = base_dir + "\\"
            if not rx.match(v_env):
                v_env = v_env + "\\"
            root = base_dir + v_env + "Scripts\\"

        elif (base_dir != '' ):
            root = base_dir
        else:
            root = ""

        if app_type == "uvicorn (python)":
            return shutil.which(root + "uvicorn")
        else:
            return shutil.which(root + "python") or shutil.which(root + "py") or root + "python"

    @staticmethod
    def determine_uvicorn_executable(base_dir: str) -> str:
        return shutil.which("uvicorn") or "uvicorn"

    @staticmethod
    def determine_node_executable() -> str:
        return shutil.which("node") or "node"

    @staticmethod
    def get_log_path(app: dict[str, Any]) -> Path:
        if getattr(sys, "frozen", False):
            root = Path(sys.executable).resolve().parent
        else:
            root = Path(__file__).resolve().parents[1]
        logs_dir = root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in app.get("name", "app"))
        return logs_dir / f"{safe_name}.log"

    @staticmethod
    def build_command(app: dict[str, Any]) -> list[str]:
        app_type = str(app.get("type", "python")).lower()
        dir_value = str(app.get("working_directory")).lower()
        v_env_value = str(app.get("venv")).lower()
        program_value = str(app.get("program", "")).strip()
        args = [str(arg) for arg in app.get("args", [])]

        if app_type == "python":
            executable = ProcessManager.determine_python_executable(app_type = app_type, base_dir = dir_value, v_env = v_env_value)
            command = [executable]
            if program_value != "":
                command.extend([program_value])
            command.extend(args)
            return command

        if app_type == "uvicorn (python)":
            executable = ProcessManager.determine_python_executable(app_type = app_type, base_dir = dir_value, v_env = v_env_value)
            command = [executable]
            if program_value != "":
                command.extend([program_value])
            command.extend(args)
            return command

        if app_type == "node":
            executable = ProcessManager.determine_node_executable()
            command = [executable]
            if program_value:
                command.append(program_value)
            command.extend(args)
            return command

        if app_type == "executable":
            command = ["cmd.exe", "/c"]
            if program_value:
                command.append(program_value)
            command.extend(args)
            return command

        command = []
        if program_value:
            command.append(program_value)
        command.extend(args)
        return command

    @staticmethod
    def get_service_name(app: dict[str, Any]) -> str:
        return str(app.get("service_name") or "").strip()

    @staticmethod
    def get_port_host(app: dict[str, Any]) -> str:
        return str(app.get("port_host") or "localhost").strip() or "localhost"

    @staticmethod
    def get_port_number(app: dict[str, Any]) -> int:
        try:
            return int(app.get("port_number") or "0")
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def is_port_reachable(app: dict[str, Any]) -> bool:
        host = ProcessManager.get_port_host(app)
        port = ProcessManager.get_port_number(app)
        if not host or port <= 0:
            return False
        try:
            import socket
            with socket.create_connection((host, port), timeout=2):
                return True
        except OSError:
            return False

    @staticmethod
    def is_service_running(app: dict[str, Any]) -> bool:
        service_name = ProcessManager.get_service_name(app)
        if not service_name:
            return False
        result = subprocess.run(["sc", "query", service_name], capture_output=True, text=True, shell=False)
        output = (result.stdout or "") + (result.stderr or "")
        return "RUNNING" in output.upper()

    @staticmethod
    def start_service(app: dict[str, Any]) -> bool:
        service_name = ProcessManager.get_service_name(app)
        if not service_name:
            return False

        log_path = ProcessManager.get_log_path(app)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n--- Starting service: {service_name} ---\n")

        result = subprocess.run(["sc", "start", service_name], capture_output=True, text=True, shell=False)
        output = (result.stdout or "") + (result.stderr or "")
        if output:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(output)
        return result.returncode == 0 or "STARTED" in output.upper() or ProcessManager.is_service_running(app)

    @staticmethod
    def stop_service(app: dict[str, Any]) -> bool:
        service_name = ProcessManager.get_service_name(app)
        if not service_name:
            return False

        log_path = ProcessManager.get_log_path(app)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n--- Stopping service: {service_name} ---\n")

        result = subprocess.run(["sc", "stop", service_name], capture_output=True, text=True, shell=False)
        output = (result.stdout or "") + (result.stderr or "")
        if output:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(output)
        return result.returncode == 0 or "STOPPED" in output.upper() or not ProcessManager.is_service_running(app)

    @staticmethod
    def start_process(app: dict[str, Any]) -> subprocess.Popen[str] | None:
        command = ProcessManager.build_command(app)
        if not command:
            return None

        working_dir = app.get("working_directory") or os.path.dirname(app.get("program")) or None
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
