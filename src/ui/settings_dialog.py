from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent=None, current_settings: dict | None = None):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("420x220")
        self.transient(parent)
        self.current_settings = current_settings or {"close_behavior": "tray"}
        self.result = None

        self.close_behavior_var = tk.StringVar(value=self.current_settings.get("close_behavior", "tray"))

        form = ttk.Frame(self, padding=16)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="When the app is closed:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))

        ttk.Radiobutton(form, text="Minimize to system tray", variable=self.close_behavior_var, value="tray").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Radiobutton(form, text="Close app and child processes", variable=self.close_behavior_var, value="close_children").grid(row=2, column=0, sticky="w", pady=4)

        buttons = ttk.Frame(self)
        buttons.pack(fill="x", padx=16, pady=(0, 16))
        ttk.Button(buttons, text="Save", command=self._save).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right", padx=(0, 8))

        self.grab_set()
        self.wait_window(self)

    def _save(self):
        self.result = {"close_behavior": self.close_behavior_var.get()}
        self.destroy()
