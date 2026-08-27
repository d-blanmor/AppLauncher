from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.process_manager import ProcessManager


class AppCard(ttk.Frame):
    def __init__(self, master, app: dict, on_start: Callable[[str], None], on_stop: Callable[[str], None], on_setup: Callable[[str], None]):
        super().__init__(master, padding=(12, 10), relief="solid", borderwidth=1)
        self.app = app
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_setup = on_setup

        self.grid_columnconfigure(0, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.name_label = ttk.Label(header, text="App", font=("Segoe UI", 11, "bold"))
        self.name_label.grid(row=0, column=0, sticky="w")

        self.status_var = tk.StringVar(value="Stopped")
        self.status_label = ttk.Label(header, textvariable=self.status_var, foreground="#333333")
        self.status_label.grid(row=0, column=1, sticky="e")

        self.description_var = tk.StringVar(value="")
        self.description_label = ttk.Label(self, textvariable=self.description_var, wraplength=800, justify="left")
        self.description_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.details_var = tk.StringVar(value="")
        self.details_label = ttk.Label(self, textvariable=self.details_var, foreground="#4b4b4b")
        self.details_label.grid(row=2, column=0, sticky="w", pady=(6, 0))

        actions = ttk.Frame(self)
        actions.grid(row=3, column=0, sticky="w", pady=(10, 0))

        self.start_button = ttk.Button(actions, text="Start", command=lambda: self.on_start(self.app.get("id")))
        self.stop_button = ttk.Button(actions, text="Stop", command=lambda: self.on_stop(self.app.get("id")))
        self.setup_button = ttk.Button(actions, text="Setup", command=lambda: self.on_setup(self.app.get("id")))

        self.start_button.pack(side="left", padx=(0, 8))
        self.stop_button.pack(side="left", padx=(0, 8))
        self.setup_button.pack(side="left")

        self.refresh()

    def refresh(self):
        status = str(self.app.get("status") or "stopped").lower()
        self.name_label.configure(text=self.app.get("name", "App"))
        self.description_var.set(self.app.get("description") or "No description")
        self.status_var.set(status.title())

        if status == "running":
            self.status_label.configure(foreground="green")
        elif status == "error":
            self.status_label.configure(foreground="red")
        else:
            self.status_label.configure(foreground="#333333")

        details = f"Type: {str(self.app.get('type', 'python')).title()}"
        pid_value = self.app.get("pid")
        if pid_value is not None:
            details += f" | PID: {pid_value}"
        self.details_var.set(details)


class LogCard(ttk.Frame):
    def __init__(self, master, app: dict):
        super().__init__(master, padding=(12, 10), relief="solid", borderwidth=1)
        self.app = app

        self.grid_columnconfigure(0, weight=1)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.name_label = ttk.Label(header, text="App", font=("Segoe UI", 11, "bold"))
        self.name_label.grid(row=0, column=0, sticky="w")

        self.status_var = tk.StringVar(value="Stopped")
        self.status_label = ttk.Label(header, textvariable=self.status_var, foreground="#333333")
        self.status_label.grid(row=0, column=1, sticky="e")

        self.details_var = tk.StringVar(value="")
        self.details_label = ttk.Label(self, textvariable=self.details_var, foreground="#4b4b4b")
        self.details_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.log_text = tk.Text(self, height=8, wrap="word", bg="#f8f8f8", relief="solid", borderwidth=1)
        self.log_text.configure(state="disabled")
        self.log_text.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        log_scroll = ttk.Scrollbar(self, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=2, column=1, sticky="ns", pady=(8, 0))
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.refresh()

    def refresh(self):
        status = str(self.app.get("status") or "stopped").lower()
        self.name_label.configure(text=self.app.get("name", "App"))
        self.status_var.set(status.title())

        if status == "running":
            self.status_label.configure(foreground="green")
        elif status == "error":
            self.status_label.configure(foreground="red")
        else:
            self.status_label.configure(foreground="#333333")

        details = f"Type: {str(self.app.get('type', 'python')).title()} | Mode: {str(self.app.get('output_mode') or 'both').title()}"
        pid_value = self.app.get("pid")
        if pid_value is not None:
            details += f" | PID: {pid_value}"
        self.details_var.set(details)

        log_text = ProcessManager.read_log(self.app, max_lines=40)
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", log_text)
        self.log_text.configure(state="disabled")
