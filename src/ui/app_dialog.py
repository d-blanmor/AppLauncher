from __future__ import annotations

import shlex
import tkinter as tk
from tkinter import ttk


class AppDialog(tk.Toplevel):
    def __init__(self, parent=None, app: dict | None = None):
        super().__init__(parent)
        self.title("Add App" if app is None else "Edit App")
        self.geometry("540x420")
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

        form = ttk.Frame(self, padding=16)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(form, textvariable=self.name_var, width=48).grid(row=0, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Description").grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(form, textvariable=self.description_var, width=48).grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Type").grid(row=2, column=0, sticky="w", pady=(0, 8))
        ttk.Combobox(form, textvariable=self.type_var, values=["python", "node", "batch"], state="readonly", width=46).grid(row=2, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Path").grid(row=3, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(form, textvariable=self.path_var, width=48).grid(row=3, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Arguments").grid(row=4, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(form, textvariable=self.args_var, width=48).grid(row=4, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Working Directory").grid(row=5, column=0, sticky="w", pady=(0, 8))
        ttk.Entry(form, textvariable=self.working_directory_var, width=48).grid(row=5, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Label(form, text="Log Output").grid(row=6, column=0, sticky="w", pady=(0, 8))
        ttk.Combobox(form, textvariable=self.output_mode_var, values=["file", "console", "both"], state="readonly", width=46).grid(row=6, column=1, sticky="ew", padx=(12, 0), pady=(0, 8))

        ttk.Checkbutton(form, text="Enabled", variable=self.enabled_var).grid(row=7, column=1, sticky="w", padx=(12, 0), pady=(0, 12))

        buttons = ttk.Frame(self)
        buttons.pack(fill="x", padx=16, pady=(0, 16))

        ttk.Button(buttons, text="Save", command=self._save).pack(side="right")
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side="right", padx=(0, 8))

        form.columnconfigure(1, weight=1)
        self.grab_set()
        self.wait_window(self)

    def _save(self):
        args_text = self.args_var.get().strip()
        args = shlex.split(args_text) if args_text else []
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
        }
        if self.original_app.get("id"):
            data["id"] = self.original_app["id"]
        self.result = data
        self.destroy()
