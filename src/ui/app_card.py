from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.process_manager import ProcessManager


class AppCard(ttk.Frame):
    SIZE_WIDTH = {"1x1": 1, "1x2": 1, "1x3": 1, "2x1": 2, "2x2": 2, "2x3": 2, "3x1": 3, "3x2": 3, "3x3": 3}
    SIZE_HEIGHT = {"1x1": 120, "2x1": 120, "3x1": 120, "1x2": 170, "2x2": 170, "3x2": 170, "1x3": 220, "2x3": 220, "3x3": 220}

    def __init__(self, master, app: dict, on_start: Callable[[str], None], on_stop: Callable[[str], None], on_setup: Callable[[str], None]):
        super().__init__(master, padding=(12, 10), relief="solid", borderwidth=1)
        self.app = app
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_setup = on_setup

        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.name_label = ttk.Label(header, text="App", font=("Segoe UI", 11, "bold"))
        self.name_label.grid(row=0, column=0, sticky="w")

        self.status_var = tk.StringVar(value="Stopped")
        self.status_label = ttk.Label(header, textvariable=self.status_var, foreground="#333333")
        self.status_label.grid(row=0, column=1, sticky="e")

        self.description_var = tk.StringVar(value="")
        self.description_label = ttk.Label(self, textvariable=self.description_var, wraplength=220, justify="left")
        self.description_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.details_var = tk.StringVar(value="")
        self.details_label = ttk.Label(self, textvariable=self.details_var, foreground="#4b4b4b")
        self.details_label.grid(row=2, column=0, sticky="w", pady=(6, 0))

        actions = ttk.Frame(self)
        actions.grid(row=3, column=0, sticky="ew", pady=(10, 5))
        actions.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_button = ttk.Button(actions, text="Start", command=lambda: self.on_start(self.app.get("id")))
        self.stop_button = ttk.Button(actions, text="Stop", command=lambda: self.on_stop(self.app.get("id")))
        self.setup_button = ttk.Button(actions, text="Setup", command=lambda: self.on_setup(self.app.get("id")))

        self.start_button.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.stop_button.grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.setup_button.grid(row=0, column=2, sticky="w")

        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)

        self.refresh()

    @staticmethod
    def normalize_card_size(value: str | None) -> str:
        normalized = str(value or "1x1").strip().lower()
        if normalized not in AppCard.SIZE_WIDTH:
            return "1x1"
        return normalized

    def card_width_units(self) -> int:
        return self.SIZE_WIDTH.get(self.normalize_card_size(self.app.get("card_size")), 3)

    def card_height(self) -> int:
        return self.SIZE_HEIGHT.get(self.normalize_card_size(self.app.get("card_size")), 220)

    def refresh(self):
        status = str(self.app.get("status") or "stopped").lower()
        mode = str(self.app.get("mode") or "application").lower()
        is_running = status == "running"
        card_size = self.normalize_card_size(self.app.get("card_size"))
        hide_description = card_size in {"1x1", "2x1", "3x1"}

        self.name_label.configure(text=self.app.get("name", "App"))
        self.status_var.set(status.title())
        self.configure(height=self.card_height())

        if hide_description:
            self.description_label.grid_remove()
            self.description_var.set("")
            self.grid_rowconfigure(1, weight=1)
            self.grid_rowconfigure(2, weight=0)
        else:
            self.description_label.grid()
            self.description_var.set(self.app.get("description") or "No description")
            self.description_label.configure(wraplength={"1x2": 180, "1x3": 180, "2x2": 300, "2x3": 300, "3x2": 420, "3x3": 420}.get(card_size, 420))
            self.grid_rowconfigure(1, weight=0)
            self.grid_rowconfigure(2, weight=1)

        self.grid_rowconfigure(3, weight=0)

        if mode == "port":
            self.start_button.state(["disabled"])
            self.stop_button.state(["disabled"])
            self.setup_button.state(["!disabled"])
        else:
            self.start_button.state(["!disabled"] if not is_running else ["disabled"])
            self.setup_button.state(["!disabled"] if not is_running else ["disabled"])
            self.stop_button.state(["!disabled"] if is_running else ["disabled"])

        if status == "running":
            self.status_label.configure(foreground="green")
        elif status == "error":
            self.status_label.configure(foreground="red")
        else:
            self.status_label.configure(foreground="#333333")

        details = f"Type: {str(self.app.get('type', 'python')).title()} | Mode: {mode.title()}"
        pid_value = self.app.get("pid")
        if pid_value is not None:
            details += f" | PID: {pid_value}"
        if mode == 'service':
            service_name = str(self.app.get('service_name') or '').strip()
            if service_name:
                details += f" | Service: {service_name}"
        elif mode == 'port':
            host = str(self.app.get('port_host') or 'localhost').strip() or 'localhost'
            port = self.app.get('port_number') or 0
            if port:
                details += f" | Port: {host}:{port}"
        self.details_var.set(details)


class LogCard(ttk.Frame):
    def __init__(self, master, app: dict):
        super().__init__(master, padding=(12, 10), relief="solid", borderwidth=1)
        self.app = app
        self.log_visible = False

        self.grid_columnconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.pack_propagate(False)

        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        self.toggle_button = ttk.Button(header, text="Show logs", command=self.toggle_visibility)
        self.toggle_button.grid(row=0, column=0, sticky="w", padx=(0, 8))

        self.name_label = ttk.Label(header, text="App", font=("Segoe UI", 11, "bold"))
        self.name_label.grid(row=0, column=1, sticky="w")

        self.refresh_button = ttk.Button(header, text="Refresh", command=self.refresh)
        self.refresh_button.grid(row=0, column=2, sticky="e", padx=(8, 0))
        self.refresh_button.grid_remove()

        self.status_var = tk.StringVar(value="Stopped")
        self.status_label = ttk.Label(header, textvariable=self.status_var, foreground="#333333")
        self.status_label.grid(row=0, column=3, sticky="e")

        self.details_var = tk.StringVar(value="")
        self.details_label = ttk.Label(self, textvariable=self.details_var, foreground="#4b4b4b")
        self.details_label.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        self.log_container = ttk.Frame(self)
        self.log_container.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.log_container.columnconfigure(0, weight=1)
        self.log_container.grid_remove()

        self.log_text = tk.Text(self.log_container, height=8, wrap="word", bg="#f8f8f8", relief="solid", borderwidth=1)
        self.log_text.configure(state="disabled")
        self.log_text.grid(row=0, column=0, sticky="ew")

        log_scroll = ttk.Scrollbar(self.log_container, orient="vertical", command=self.log_text.yview)
        log_scroll.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.refresh()

    def toggle_visibility(self):
        self.log_visible = not self.log_visible
        if self.log_visible:
            self.log_container.grid()
            self.toggle_button.configure(text="Hide logs")
            self.refresh_button.grid()
            self.refresh()
        else:
            self.log_container.grid_remove()
            self.toggle_button.configure(text="Show logs")
            self.refresh_button.grid_remove()

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
