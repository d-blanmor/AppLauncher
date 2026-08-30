from __future__ import annotations

import shlex
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk


class AppDialog(tk.Toplevel):
    def __init__(self, parent=None, app: dict | None = None):
        super().__init__(parent)
        self.title("Add App" if app is None else "Edit App")
        self.geometry("540x520")
        self.transient(parent)
        self.original_app = app or {}
        self.result = None

        self.name_var = tk.StringVar(value=self.original_app.get("name", ""))
        self.description_var = tk.StringVar(value=self.original_app.get("description", ""))
        self.card_size_var = tk.StringVar(value=str(self.original_app.get("card_size") or "1x1").lower())
        self.output_mode_var = tk.StringVar(value=str(self.original_app.get("output_mode") or "both").lower())
        self.mode_var = tk.StringVar(value=str(self.original_app.get("mode") or "application").lower())

        # mode = Application
        self.type_var = tk.StringVar(value=str(self.original_app.get("type") or "python").lower())
        self.working_directory_var = tk.StringVar(value=self.original_app.get("working_directory", ""))
        self.virtual_environment_var = tk.StringVar(value=self.original_app.get("venv", ""))
        self.program_var = tk.StringVar(value=self.original_app.get("program", ""))
        args_value = " ".join(str(arg) for arg in self.original_app.get("args", []))
        self.args_var = tk.StringVar(value=args_value)

        # mode = Service
        self.service_name_var = tk.StringVar(value=str(self.original_app.get("service_name") or ""))

        # mode = port
        self.port_host_var = tk.StringVar(value=str(self.original_app.get("port_host") or "localhost"))
        self.port_number_var = tk.StringVar(value=str(self.original_app.get("port_number") or ""))

        self.enabled_var = tk.BooleanVar(value=bool(self.original_app.get("enabled", True)))

        form = ttk.Frame(self, padding=16)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(form, textvariable=self.name_var, width=48).grid(row=0, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Description").grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(form, textvariable=self.description_var, width=48).grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Card Size").grid(row=2, column=0, sticky="w", pady=(0, 8))
        ttk.Combobox(form, textvariable=self.card_size_var, values=["1x1", "1x2", "1x3", "2x1", "2x2", "2x3", "3x1", "3x2", "3x3"], state="readonly", width=46).grid(row=2, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Log Output").grid(row=3, column=0, sticky="w", pady=(0, 8))
        ttk.Combobox(form, textvariable=self.output_mode_var, values=["file", "console", "both"], state="readonly", width=46).grid(row=3, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Mode").grid(row=4, column=0, sticky="w", pady=(0, 8))
        ttk.Combobox(form, textvariable=self.mode_var, values=["application", "service", "port"], state="readonly", width=46).grid(row=4, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        # mode = Application
        self.type_label = ttk.Label(form, text="Type")
        self.type_label.grid(row=5, column=0, sticky="w", pady=(0, 8))
        self.type_combo = ttk.Combobox(form, textvariable=self.type_var, values=["python", "uvicorn (python)", "node", "executable"], state="readonly", width=46)
        self.type_combo.grid(row=5, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.working_label = ttk.Label(form, text="Working Directory")
        self.working_label.grid(row=6, column=0, sticky="w", pady=(0, 8))
        self.working_entry = ttk.Entry(form, textvariable=self.working_directory_var, width=48)
        self.working_entry.grid(row=6, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.venv_label = ttk.Label(form, text="Virtual Environment")
        self.venv_label.grid(row=7, column=0, sticky="w", pady=(0, 8))
        self.venv_entry = ttk.Entry(form, textvariable=self.virtual_environment_var, width=48)
        self.venv_entry.grid(row=7, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.program_label = ttk.Label(form, text="Program/Script")
        self.program_label.grid(row=8, column=0, sticky="w", pady=(0, 8))
        self.program_entry = ttk.Entry(form, textvariable=self.program_var, width=48)
        self.program_entry.grid(row=8, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.args_label = ttk.Label(form, text="Arguments")
        self.args_label.grid(row=9, column=0, sticky="w", pady=(0, 8))
        self.args_entry = ttk.Entry(form, textvariable=self.args_var, width=48)
        self.args_entry.grid(row=9, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        # mode = Service
        self.service_label = ttk.Label(form, text="Service Name")
        self.service_label.grid(row=10, column=0, sticky="w", pady=(0, 8))
        self.service_entry = ttk.Entry(form, textvariable=self.service_name_var, width=48)
        self.service_entry.grid(row=10, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))
        self.test_service_button = ttk.Button(form, text="Test", command=self._test_service_connection)
        self.test_service_button.grid(row=10, column=2, sticky="w", padx=(8, 0), pady=(0, 8))

        # mode = port
        self.port_host_label = ttk.Label(form, text="Port Host")
        self.port_host_label.grid(row=11, column=0, sticky="w", pady=(0, 8))
        self.port_host_entry = ttk.Entry(form, textvariable=self.port_host_var, width=48)
        self.port_host_entry.grid(row=11, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.port_number_label = ttk.Label(form, text="Port Number")
        self.port_number_label.grid(row=12, column=0, sticky="w", pady=(0, 8))
        self.port_number_entry = ttk.Entry(form, textvariable=self.port_number_var, width=48)
        self.port_number_entry.grid(row=12, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))
        self.test_port_button = ttk.Button(form, text="Test", command=self._test_port_connection)
        self.test_port_button.grid(row=12, column=2, sticky="w", padx=(8, 0), pady=(0, 8))

        ttk.Checkbutton(form, text="Enabled", variable=self.enabled_var).grid(row=13, column=1, sticky="w", padx=(12, 0), pady=(0, 12))

        self.application_fields = [self.type_label, self.type_combo, self.program_label, self.program_entry, self.working_label, self.working_entry]
        self.app_python_fields = [self.venv_label, self.venv_entry]
        self.application_args_fields = [self.args_label, self.args_entry]
        self.service_fields = [self.service_label, self.service_entry, self.test_service_button]
        self.port_fields = [self.port_host_label, self.port_host_entry, self.port_number_label, self.port_number_entry, self.test_port_button]
        self.mode_var.trace_add("write", lambda *_: self._refresh_mode_fields())
        self.type_var.trace_add("write", lambda *_: self._refresh_mode_fields())
        self._refresh_mode_fields()

        buttons = ttk.Frame(self)
        buttons.pack(fill="x", padx=16, pady=(0, 16))

        ttk.Button(buttons, text="Save", command=self._save).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right", padx=(0, 8))

        form.columnconfigure(1, weight=1)
        self.grab_set()
        self.wait_window(self)

    def _refresh_mode_fields(self):
        mode = self.mode_var.get().lower()
        selected_type = self.type_var.get().lower()
        is_application = mode == "application"
        is_python_app = mode == "application" and selected_type in {"python", "uvicorn (python)"}
        is_service = mode == "service"
        is_port = mode == "port"
        show_arguments = is_application and selected_type in {"python", "uvicorn (python)", "executable"}

        program_label = "Program/script"
        if selected_type == "executable":
            program_label = "Program"
        elif selected_type == "python" or selected_type == "uvicorn (python)":
            program_label = "Script"
        self.program_label.config(text=program_label)

        for widget in self.application_fields:
            if is_application:
                widget.grid()
            else:
                widget.grid_remove()

        for widget in self.app_python_fields:
            if is_python_app:
                widget.grid()
            else:
                widget.grid_remove()

        for widget in self.application_args_fields:
            if show_arguments:
                widget.grid()
            else:
                widget.grid_remove()

        for widget in self.service_fields:
            if is_service:
                widget.grid()
            else:
                widget.grid_remove()

        for widget in self.port_fields:
            if is_port:
                widget.grid()
            else:
                widget.grid_remove()

    def _test_service_connection(self):
        service_name = self.service_name_var.get().strip()
        if not service_name:
            messagebox.showwarning("Service missing", "Please enter a Windows service name before testing the connection.")
            return

        try:
            result = subprocess.run(["sc", "query", service_name], capture_output=True, text=True, shell=False)
        except FileNotFoundError:
            messagebox.showerror("Windows service check failed", "The 'sc' command is not available in this environment.")
            return

        output = (result.stdout or "") + (result.stderr or "")
        normalized = output.upper()
        if "SERVICE_NAME" in normalized or "STATE" in normalized:
            messagebox.showinfo("Service status", f"Service '{service_name}' was found.\n\n{output.strip()[:400]}")
        else:
            messagebox.showwarning("Service not found", f"Service '{service_name}' could not be found or queried.\n\n{output.strip()[:400]}")

    def _test_port_connection(self):
        host = self.port_host_var.get().strip() or "localhost"
        port_text = self.port_number_var.get().strip()
        if not port_text:
            messagebox.showwarning("Port missing", "Please enter a port number before testing the connection.")
            return

        try:
            port = int(port_text)
        except ValueError:
            messagebox.showwarning("Port invalid", "The port number must be an integer.")
            return

        try:
            import socket
            with socket.create_connection((host, port), timeout=2):
                messagebox.showinfo("Port status", f"Port {host}:{port} is reachable.")
        except OSError as exc:
            messagebox.showwarning("Port status", f"Port {host}:{port} is not reachable.\n\n{exc}")

    def _save(self):
        args_text = self.args_var.get().strip()
        args = shlex.split(args_text) if args_text else []
        mode = self.mode_var.get().lower()
        port_number = 0
        try:
            port_number = int(self.port_number_var.get().strip()) if self.port_number_var.get().strip() else 0
        except ValueError:
            port_number = 0

        data = {
            "name": self.name_var.get().strip() or "New App",
            "description": self.description_var.get().strip(),
            "card_size": self.card_size_var.get().lower(),
            "output_mode": self.output_mode_var.get().lower(),
            "status": "stopped",
            "enabled": self.enabled_var.get(),
            "mode": mode,
            "type": self.type_var.get().lower(),
            "working_directory": self.working_directory_var.get().strip(),
            "venv": self.virtual_environment_var.get().strip(),
            "program": self.program_var.get().strip(),
            "args": args,
            "service_name": self.service_name_var.get().strip(),
            "port_host": self.port_host_var.get().strip() or "localhost",
            "port_number": port_number,
        }
        if self.original_app.get("id"):
            data["id"] = self.original_app["id"]
        self.result = data
        self.destroy()
