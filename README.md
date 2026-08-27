# AppLauncher

A simple Windows desktop launcher for Python, Node.js, and batch-based applications.

## Features
- Card-based dashboard for each configured app
- Add, edit, start, and stop actions per app
- JSON-based configuration storage
- Process logs written to the `logs/` folder
- Optional tray icon support for minimize-to-tray behavior
- Configurable close behavior: minimize to tray or close the app and running child processes
- Per-app launcher card sizing (`1x1`, `1x2`, `1x3`, `2x1`, `2x2`, `2x3`, `3x1`, `3x2`, `3x3`) controlling both width and height in the launcher tab
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
For best portability, build the package from a clean Python environment that is not tied to Anaconda's base installation. The EXE bundles the runtime and libraries from that build environment, but it still needs a compatible Windows runtime and the Tk/Tcl DLL chain that was available when it was built.

Recommended approach:

1. Install a standard Python 3.12/3.13 from python.org and create a clean venv (do not rely on Anaconda base for packaging):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller
```

If you must use Anaconda, prefer a dedicated Conda environment created explicitly for this app, not the base environment, and make sure `tk` is installed there:

```powershell
conda create -n applauncher python=3.13 tk -y
conda activate applauncher
python -m pip install -r requirements.txt pyinstaller
```

2. Build the executable from the project root:

```powershell
.\.venv\Scripts\pyinstaller --onefile --windowed --name AppLauncher .\src\main.py
```

3. Run the generated package:

```powershell
.\dist\AppLauncher.exe
```

Notes:
- The app is portable across Windows systems that match the same architecture (for example x64 Windows 10/11) when the bundled runtime is used.
- It is not truly independent from the Windows OS: Microsoft runtime libraries and the Tk/Tcl DLL chain still need to be compatible.
- If you build from a system Python or from Anaconda, the resulting EXE can fail to start with `ImportError: DLL load failed while importing _tkinter` because Tk is not available in the same way as it is in a clean venv.
- If you need more control, use a dedicated build venv and avoid mixing with Conda unless you specifically installed a Tk-enabled Python there.

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
  "title": "App Launcher",
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
