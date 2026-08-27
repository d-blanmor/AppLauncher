# AppLauncher

A simple Windows desktop launcher for Python, Node.js, and batch-based applications.

## Features
- Card-based dashboard for each configured app
- Add, edit, start, and stop actions per app
- JSON-based configuration storage
- Process logs written to the `logs/` folder
- Optional tray icon support for minimize-to-tray behavior
- Configurable close behavior: minimize to tray or close the app and running child processes
- Per-app launcher card sizing (`small`, `medium`, `big`) controlling both width and height in the launcher tab
- Per-app execution mode: run a normal command or control a Windows service by name

## Run
From the project root:

```powershell
.\.venv\Scripts\python.exe -m src.main
```

## Test

Source compilation passed with the project venv:

```powershell
..venv\Scripts\python.exe -m compileall src
```

Config and app manager smoke test passed:

app manager loaded app data and settings successfully


## Generate an EXE
Install PyInstaller in the virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
```

Build the executable from the project root:

```powershell
.\.venv\Scripts\pyinstaller --onefile --windowed --name AppLauncher .\src\main.py
```

This creates a standalone executable in the `dist` folder. After build, you can run:

```powershell
.\dist\AppLauncher.exe
```

## Log handling
The main window has two tabs:

- `Launcher`: shows the app cards for starting and stopping managed applications
- `Logs`: shows one log card per app with the latest captured output

The app writes output to a per-app log file in the `logs/` folder and supports three output modes:

- `file`: capture output only to the app log file
- `console`: open a dedicated command window for the child process
- `both`: save to the file and also show the process in its own console window

The logs tab is the central place to monitor startup, errors, and runtime activity across all configured apps.

## Configuration file
The app saves its config in `app_launcher.json` at the project root.

Example structure:

```json
{
  "apps": [
    {
      "id": "demo-app",
      "name": "Demo App",
      "description": "Example Python app",
      "type": "python",
      "path": "script.py",
      "args": ["--port", "3000"],
      "working_directory": "C:\\Projects\\MyApp",
      "enabled": true,
      "status": "stopped",
      "output_mode": "both",
      "mode": "service",
      "service_name": "MyWindowsService",
      "card_size": "medium"
    }
  ],
  "settings": {
    "close_behavior": "tray"
  }
}
```
