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
        self.type_var = tk.StringVar(value=str(self.original_app.get("type") or "python").lower())
        self.path_var = tk.StringVar(value=self.original_app.get("path", ""))
        args_value = " ".join(str(arg) for arg in self.original_app.get("args", []))
        self.args_var = tk.StringVar(value=args_value)
        self.working_directory_var = tk.StringVar(value=self.original_app.get("working_directory", ""))
        self.enabled_var = tk.BooleanVar(value=bool(self.original_app.get("enabled", True)))
        self.output_mode_var = tk.StringVar(value=str(self.original_app.get("output_mode") or "both").lower())
        self.mode_var = tk.StringVar(value=str(self.original_app.get("mode") or "application").lower())
        self.service_name_var = tk.StringVar(value=str(self.original_app.get("service_name") or ""))
        self.port_host_var = tk.StringVar(value=str(self.original_app.get("port_host") or "localhost"))
        self.port_number_var = tk.StringVar(value=str(self.original_app.get("port_number") or ""))
        self.card_size_var = tk.StringVar(value=str(self.original_app.get("card_size") or "1x1").lower())

        form = ttk.Frame(self, padding=16)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(form, textvariable=self.name_var, width=48).grid(row=0, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Description").grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(form, textvariable=self.description_var, width=48).grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.type_label = ttk.Label(form, text="Type")
        self.type_label.grid(row=2, column=0, sticky="w", pady=(0, 8))
        self.type_combo = ttk.Combobox(form, textvariable=self.type_var, values=["python", "node", "batch"], state="readonly", width=46)
        self.type_combo.grid(row=2, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.path_label = ttk.Label(form, text="Path")
        self.path_label.grid(row=3, column=0, sticky="w", pady=(0, 8))
        self.path_entry = ttk.Entry(form, textvariable=self.path_var, width=48)
        self.path_entry.grid(row=3, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.args_label = ttk.Label(form, text="Arguments")
        self.args_label.grid(row=4, column=0, sticky="w", pady=(0, 8))
        self.args_entry = ttk.Entry(form, textvariable=self.args_var, width=48)
        self.args_entry.grid(row=4, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.working_label = ttk.Label(form, text="Working Directory")
        self.working_label.grid(row=5, column=0, sticky="w", pady=(0, 8))
        self.working_entry = ttk.Entry(form, textvariable=self.working_directory_var, width=48)
        self.working_entry.grid(row=5, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Log Output").grid(row=6, column=0, sticky="w", pady=(0, 8))
        ttk.Combobox(form, textvariable=self.output_mode_var, values=["file", "console", "both"], state="readonly", width=46).grid(row=6, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Mode").grid(row=7, column=0, sticky="w", pady=(0, 8))
        ttk.Combobox(form, textvariable=self.mode_var, values=["application", "service", "port"], state="readonly", width=46).grid(row=7, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.service_label = ttk.Label(form, text="Service Name")
        self.service_label.grid(row=8, column=0, sticky="w", pady=(0, 8))
        self.service_entry = ttk.Entry(form, textvariable=self.service_name_var, width=48)
        self.service_entry.grid(row=8, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))
        self.test_service_button = ttk.Button(form, text="Test service connection", command=self._test_service_connection)
        self.test_service_button.grid(row=8, column=2, sticky="w", padx=(8, 0), pady=(0, 8))

        self.port_host_label = ttk.Label(form, text="Port Host")
        self.port_host_label.grid(row=9, column=0, sticky="w", pady=(0, 8))
        self.port_host_entry = ttk.Entry(form, textvariable=self.port_host_var, width=48)
        self.port_host_entry.grid(row=9, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        self.port_number_label = ttk.Label(form, text="Port Number")
        self.port_number_label.grid(row=10, column=0, sticky="w", pady=(0, 8))
        self.port_number_entry = ttk.Entry(form, textvariable=self.port_number_var, width=48)
        self.port_number_entry.grid(row=10, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))
        self.test_port_button = ttk.Button(form, text="Test port", command=self._test_port_connection)
        self.test_port_button.grid(row=10, column=2, sticky="w", padx=(8, 0), pady=(0, 8))

        ttk.Label(form, text="Card Size").grid(row=11, column=0, sticky="w", pady=(0, 8))
        ttk.Combobox(form, textvariable=self.card_size_var, values=["1x1", "1x2", "1x3", "2x1", "2x2", "2x3", "3x1", "3x2", "3x3"], state="readonly", width=46).grid(row=11, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Checkbutton(form, text="Enabled", variable=self.enabled_var).grid(row=12, column=1, sticky="w", padx=(12, 0), pady=(0, 12))

        self.application_fields = [self.type_label, self.type_combo, self.path_label, self.path_entry, self.args_label, self.args_entry, self.working_label, self.working_entry]
        self.service_fields = [self.service_label, self.service_entry, self.test_service_button]
        self.port_fields = [self.port_host_label, self.port_host_entry, self.port_number_label, self.port_number_entry, self.test_port_button]
        self.mode_var.trace_add("write", lambda *_: self._refresh_mode_fields())
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
        is_application = mode == "application"
        is_service = mode == "service"
        is_port = mode == "port"

        for widget in self.application_fields:
            if is_application:
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
            "type": self.type_var.get().lower(),
            "path": self.path_var.get().strip(),
            "args": args,
            "working_directory": self.working_directory_var.get().strip(),
            "enabled": self.enabled_var.get(),
            "status": "stopped",
            "output_mode": self.output_mode_var.get().lower(),
            "mode": mode,
            "service_name": self.service_name_var.get().strip(),
            "port_host": self.port_host_var.get().strip() or "localhost",
            "port_number": port_number,
            "card_size": self.card_size_var.get().lower(),
        }
        if self.original_app.get("id"):
            data["id"] = self.original_app["id"]
        self.result = data
        self.destroy()
