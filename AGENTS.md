# AGENTS.md — MountWizzard4

PySide6 desktop application for controlling 10micron telescope mounts.  
Python 3.11–3.13 · PySide6 · `uv` toolchain · `ruff` linter.

---

## Architecture overview

`MountWizzard4` (`src/mw4/mainApp.py`) is the **central application object** (a `QObject`).  
All subsystems live as attributes on it and communicate exclusively through Qt Signals – there are no direct calls back from logic to GUI.

```
loader.py → MountWizzard4
               ├── mount        (mountcontrol/ — proprietary TCP/IP protocol for 10micron)
               ├── camera / dome / cover / focuser / filter / telescope / …  (logic/)
               │    └── .run = {"indi": …, "alpaca": …, "ascom": …}   ← strategy dict
               ├── mainW        (gui/mainWindow/ — PySide6 QWidget tree)
               └── timerMgr     (base/timerManager.py — drives cyclic signals)
```

### Cyclic signal bus
`CyclicTimerManager` fires a 100 ms tick and emits named signals on `app`:  
`update0_1s`, `update1s`, `update3s`, `update10s`, `update30s`, `update3m`, `update30m`, `start3s`.  
Every subsystem hooks the relevant signal to trigger its poll cycle.

### Driver strategy pattern
Every device class (e.g. `Camera`) owns a `.run` dict:
```python
self.run = {"indi": CameraIndi(self), "alpaca": CameraAlpaca(self)}
# Windows only:
self.run["ascom"] = CameraAscom(self)
```
All adapters implement `DriverProtocol` (`base/driverProtocol.py`): `startCommunication`, `stopCommunication`, `pollData`, `pollStatus`, `processPolledData`, `getInitialConfig`.  
ASCOM / NINA / SGPro adapters are **only imported on Windows** (guarded by `platform.system() == "Windows"`).

### Threading
CPU-bound or blocking I/O always goes through `Worker` (`base/tpool.py`):
```python
worker = Worker(some_fn, *args)
worker.signals.result.connect(callback)
app.threadPool.start(worker)
```
The thread pool has a cap of 30 threads. Never call Qt GUI methods from inside a worker function.

---

## Developer workflows

### Environment
```bash
uv sync --all-groups        # install all deps + dev group
```

### Run the app
```bash
uv run mw4                  # normal start (workDir = cwd)
uv run mw4 -t 1             # auto-quit after ~10 s (used in CI smoke tests)
```

### GUI widget rebuild (required when editing .ui files)
Source files live in `src_add/widgets/*.ui`. **Never edit** `src/mw4/gui/widgets/*_ui.py` directly.
```bash
uv run invoke build-widgets
```

### Tests
```bash
uv run pytest tests/unit_tests/logic/camera   # run one directory
uv run pytest tests/unit_tests               # full suite (slow)
```
Coverage is auto-appended (`--cov-append`); reset with `coverage erase` before a clean run.
Test coverage of code should be at 100%

### Lint / format
```bash
uv run ruff check src/mw4
uv run ruff format src/mw4
```
Line length: **95**. Import sections: **none** (`no-sections = true`). Generated widget files (`src/mw4/gui/widgets/`) are excluded from ruff.

### Full build (widgets → data files → sdist)
```bash
uv run invoke build         # calls build-widgets + update-builtins + uv build
```

---

## Test conventions

Every logic/GUI test imports the shared **`App` mock fixture** instead of constructing a real `MountWizzard4`:
```python
from tests.unit_tests.unitTestAddOns.baseTestApp import App

@pytest.fixture(autouse=True, scope="module")
def function():
    func = Camera(app=App())
    yield func
```
`App` (`tests/unit_tests/unitTestAddOns/baseTestApp.py`) provides stub versions of all subsystems (mount, camera, dome, …) with the same signals and attribute shapes as the real classes.  
Use `monkeypatch.setattr("mw4.logic.camera.camera.sleepAndEvents", ...)` to intercept blocking helpers.

---

## Configuration & data files

- **Profiles**: YAML files in `{workDir}/config/`; active profile name stored in `{workDir}/config/profile`.  
  Profile version string checked on load — mismatches fall back to `defaultConfig()`.
- **Bundled data** (`src/mw4/assets/data/`): ephemeris (`de440_mw4.bsp`), leap-second tables, IERS finals.  
  Extracted to `{workDir}/data/` at startup (only if newer). Update them with `invoke update-builtins`.
- **workDir** defaults to `Path.cwd()` — run the app from the intended working directory.

---

## Key directories

| Path | Purpose |
|------|---------|
| `src/mw4/mainApp.py` | Central app object, all signals, device instantiation |
| `src/mw4/base/` | Thread pool, cyclic timer, driver protocol, logging |
| `src/mw4/logic/<device>/` | Device logic + per-protocol adapters |
| `src/mw4/mountcontrol/` | Self-contained TCP/IP library for 10micron mount protocol |
| `src/mw4/gui/mainWindow/` | Main window, addon mixin loader, external-window manager |
| `src/mw4/gui/widgets/` | Auto-generated from `src_add/widgets/*.ui` — do not edit |
| `src/mw4/gui/mainWaddon/` | One file per UI tab (tabMount.py, tabImage_Manage.py, …) |
| `tests/unit_tests/unitTestAddOns/baseTestApp.py` | Shared `App` stub used by all unit tests |

