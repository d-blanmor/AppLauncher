from __future__ import annotations

import tkinter as tk

from src.app_manager import AppManager
from src.ui.main_window import MainWindow


def main() -> None:
    root = tk.Tk()
    app_manager = AppManager()
    window = MainWindow(root, app_manager)
    root.mainloop()


if __name__ == "__main__":
    main()
