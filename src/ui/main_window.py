from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox, ttk

import pystray
from PIL import Image, ImageDraw

from src.app_manager import AppManager
from src.ui.app_card import AppCard, LogCard
from src.ui.app_dialog import AppDialog
from src.ui.settings_dialog import SettingsDialog


class MainWindow:
    def __init__(self, root: tk.Tk, app_manager: AppManager):
        self.root = root
        self.app_manager = app_manager
        self.tray_icon = None

        self.root.title("App Launcher")
        self.root.geometry("980x680")
        self.root.minsize(760, 420)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        toolbar = ttk.Frame(self.root, padding=(12, 10, 12, 6))
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Add App", command=self._on_add_app).pack(side="left")
        ttk.Button(toolbar, text="Settings", command=self._on_open_settings).pack(side="left", padx=(8, 0))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.launcher_frame = ttk.Frame(self.notebook)
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.launcher_frame, text="Launcher")
        self.notebook.add(self.logs_frame, text="Logs")

        self.launcher_canvas = tk.Canvas(self.launcher_frame, highlightthickness=0)
        self.launcher_scrollbar = ttk.Scrollbar(self.launcher_frame, orient="vertical", command=self.launcher_canvas.yview)
        self.launcher_canvas.configure(yscrollcommand=self.launcher_scrollbar.set)
        self.launcher_scrollbar.pack(side="right", fill="y")
        self.launcher_canvas.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)

        self.launcher_container = ttk.Frame(self.launcher_canvas)
        self.launcher_container_id = self.launcher_canvas.create_window((0, 0), window=self.launcher_container, anchor="nw")
        self.launcher_container.bind("<Configure>", self._on_launcher_configure)
        for idx in range(3):
            self.launcher_container.grid_columnconfigure(idx, weight=1)

        self.logs_canvas = tk.Canvas(self.logs_frame, highlightthickness=0)
        self.logs_scrollbar = ttk.Scrollbar(self.logs_frame, orient="vertical", command=self.logs_canvas.yview)
        self.logs_canvas.configure(yscrollcommand=self.logs_scrollbar.set)
        self.logs_scrollbar.pack(side="right", fill="y")
        self.logs_canvas.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=12)

        self.logs_container = ttk.Frame(self.logs_canvas)
        self.logs_container_id = self.logs_canvas.create_window((0, 0), window=self.logs_container, anchor="nw")
        self.logs_container.bind("<Configure>", self._on_logs_configure)

        self._apply_close_behavior()

        if os.getenv("APP_LAUNCHER_ENABLE_TRAY", "1") == "1":
            self._create_tray_icon()

        self.load_apps()

    def _get_close_behavior(self) -> str:
        return str(self.app_manager.get_settings().get("close_behavior", "tray")).strip().lower()

    def _apply_close_behavior(self):
        behavior = self._get_close_behavior()
        if behavior not in {"tray", "close_children"}:
            behavior = "tray"
        self.close_behavior = behavior

    def _on_close(self):
        if self.close_behavior == "close_children":
            self._close_and_children()
            return
        self.hide_to_tray()

    def _close_and_children(self):
        for app in self.app_manager.get_apps():
            app_id = app.get("id")
            if app_id and app.get("status") == "running":
                try:
                    self.app_manager.stop_app(app_id)
                except ValueError:
                    pass
        if self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.root.destroy()

    def _create_tray_icon(self):
        image = Image.new("RGB", (64, 64), color=(33, 150, 243))
        draw = ImageDraw.Draw(image)
        draw.rectangle((10, 10, 54, 54), fill=(24, 67, 107))
        draw.text((18, 18), "A", fill=(255, 255, 255))

        self.tray_icon = pystray.Icon(
            "app_launcher",
            icon=image,
            menu=pystray.Menu(
                pystray.MenuItem("Show", self.show_window),
                pystray.MenuItem("Hide", self.hide_to_tray),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self.exit_app),
            ),
        )
        self.tray_icon.run_detached()

    def _on_launcher_configure(self, event):
        width = max(self.launcher_canvas.winfo_width(), 600)
        self.launcher_canvas.configure(scrollregion=self.launcher_canvas.bbox("all"))
        self.launcher_canvas.itemconfigure(self.launcher_container_id, width=width)

    def _on_logs_configure(self, event):
        width = max(self.logs_canvas.winfo_width(), 600)
        self.logs_canvas.configure(scrollregion=self.logs_canvas.bbox("all"))
        self.logs_canvas.itemconfigure(self.logs_container_id, width=width)

    def _schedule_ui(self, callback):
        try:
            self.root.after(0, callback)
        except Exception:
            callback()

    def show_window(self):
        self._schedule_ui(self._show_window_impl)

    def _show_window_impl(self):
        if self.root.winfo_exists():
            self.root.deiconify()
            self.root.state("normal")
            self.root.focus_force()

    def hide_to_tray(self):
        if self.tray_icon is not None:
            self._schedule_ui(self._hide_to_tray_impl)
            return
        self._schedule_ui(self.root.destroy)

    def _hide_to_tray_impl(self):
        if self.root.winfo_exists():
            self.root.withdraw()

    def exit_app(self):
        try:
            if self.tray_icon is not None:
                self.tray_icon.stop()
        except Exception:
            pass
        self._schedule_ui(self.root.destroy)

    def load_apps(self):
        for widget in self.launcher_container.winfo_children():
            widget.destroy()
        for widget in self.logs_container.winfo_children():
            widget.destroy()

        apps = self.app_manager.get_apps()
        if not apps:
            empty_launcher = ttk.Label(self.launcher_container, text="No apps configured yet.", foreground="#555555")
            empty_launcher.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

            empty_logs = ttk.Label(self.logs_container, text="No logs available yet.", foreground="#555555")
            empty_logs.pack(expand=True)
            return

        current_row = 0
        current_col = 0
        for app in apps:
            card = AppCard(
                self.launcher_container,
                app,
                on_start=self._on_start_app,
                on_stop=self._on_stop_app,
                on_setup=self._on_setup_app,
            )
            width_units = card.card_width_units()
            if current_col + width_units > 3:
                current_row += 1
                current_col = 0
            card.grid(row=current_row, column=current_col, columnspan=width_units, sticky="ew", padx=(0, 8), pady=6)
            self.launcher_container.grid_columnconfigure(current_col, weight=1)
            if width_units > 1:
                self.launcher_container.grid_columnconfigure(current_col + 1, weight=1)
            current_col += width_units
            if current_col >= 3:
                current_row += 1
                current_col = 0

            log_card = LogCard(self.logs_container, app)
            log_card.pack(fill="x", expand=True, pady=6)

    def _on_open_settings(self):
        dialog = SettingsDialog(self.root, self.app_manager.get_settings())
        if dialog.result is not None:
            self.app_manager.save_settings(dialog.result)
            self._apply_close_behavior()

    def _on_add_app(self):
        dialog = AppDialog(self.root)
        if dialog.result is not None:
            self.app_manager.add_app(dialog.result)
            self.load_apps()

    def _on_setup_app(self, app_id: str):
        app = self._find_app(app_id)
        if app is None:
            return
        dialog = AppDialog(self.root, app)
        if dialog.result is not None:
            self.app_manager.update_app(app_id, dialog.result)
            self.load_apps()

    def _on_start_app(self, app_id: str):
        try:
            self.app_manager.start_app(app_id)
        except ValueError:
            messagebox.showwarning("App not found", "The selected app could not be found.")
        self.load_apps()

    def _on_stop_app(self, app_id: str):
        try:
            self.app_manager.stop_app(app_id)
        except ValueError:
            messagebox.showwarning("App not found", "The selected app could not be found.")
        self.load_apps()

    def _find_app(self, app_id: str):
        for app in self.app_manager.get_apps():
            if app.get("id") == app_id:
                return app
        return None
