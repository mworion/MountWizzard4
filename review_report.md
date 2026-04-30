# MountWizzard4 – Code Review Report

**Date:** 2026-04-30  
**Scope:** `src/mw4/` (232 Python files, ~1 974 function/method definitions)  
**Tools used:** Manual source analysis, `grep`, `ruff`, project conventions from  
`pyproject.toml` and `.github/copilot-instructions.md`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Type Annotation Coverage](#2-type-annotation-coverage)
3. [Critical Bugs](#3-critical-bugs)
4. [Architecture Issues](#4-architecture-issues)
5. [Incomplete / Stub Functions](#5-incomplete--stub-functions)
6. [Code Quality & Maintainability](#6-code-quality--maintainability)
7. [Tooling Gaps](#7-tooling-gaps)
8. [Prioritised Improvement Backlog](#8-prioritised-improvement-backlog)

---

## 1. Executive Summary

| Metric | Value |
|---|---|
| Total source files reviewed | 232 |
| Total function/method definitions | 1 974 |
| Definitions with return-type annotation | 1 722 (87.2 %) |
| **Missing return-type annotations** | **252 (12.8 %)** |
| Files with untyped `app` parameter | ≥ 41 (19 logic + 22 GUI) |
| Confirmed logic bugs | 3 |
| Stub / no-op methods (undocumented) | 5 |
| Critical architecture issues | 5 |

Overall the codebase is well-structured for a project of this size.
The separation between `logic/` and `gui/` is respected in most places,
signals & slots are used correctly, and the `DriverProtocol` abstraction
was a good design choice.
The main areas that need attention are:

- The remaining 252 un-annotated definitions (concentrated in a handful
  of files).
- Three confirmed runtime bugs in the camera wait-loop methods and the
  ASCOM disconnect log message.
- Five undocumented stub methods that silently do nothing.
- The `app: Any` pattern that defeats static analysis across the entire
  logic layer.

---

## 2. Type Annotation Coverage

### 2.1 Overall Statistics

```
Total defs (excl. auto-generated widgets): 1 974
With return-type annotation  :             1 722   (87.2 %)
Missing return-type annotation:              252   (12.8 %)
```

### 2.2 Files with Most Missing Annotations

| # Missing | File |
|---|---|
| 31 | `src/mw4/gui/styles/styles.py` |
| 22 | `src/mw4/gui/mainWaddon/tabMount_Sett.py` |
| 15 | `src/mw4/gui/extWindows/simulator/simulatorW.py` |
| 12 | `src/mw4/gui/mainWaddon/tabAnalysis.py` |
| 10 | `src/mw4/logic/satellites/satellite_calculations.py` |
|  9 | `src/mw4/gui/extWindows/image/imageTabs.py` |
|  9 | `src/mw4/gui/extWindows/simulator/buildPoints.py` |
|  7 | `src/mw4/gui/mainWaddon/tabSat_Search.py` |
|  7 | `src/mw4/gui/extWindows/splashScreen.py` |
|  7 | `src/mw4/gui/extWindows/simulator/tools.py` |
|  7 | `src/mw4/gui/extWindows/simulator/dome.py` |
|  5 | `src/mw4/logic/buildData/buildpoints.py` |
|  5 | `src/mw4/gui/mainWaddon/tabSett_Update.py` |
|  5 | `src/mw4/gui/utilities/qtMain.py` |
|  5 | `src/mw4/mountcontrol/mount.py` |

### 2.3 Recurring Patterns

#### a) `@property` setters / colour constants (`styles.py`)

All 30 `@property` colour accessors like `M_PRIM`, `M_SEC`, `M_RED`,
etc. lack `-> str`:

```python
# current (styles.py:34)
@property
def M_PRIM(self):
    return self._palette["primary"]

# recommended
@property
def M_PRIM(self) -> str:
    return self._palette["primary"]
```

#### b) GUI signal-slot callbacks (`tabMount_Sett.py`)

22 slot methods have no return-type annotation.  Example:

```python
# current (tabMount_Sett.py:71)
def updatePointGUI(self, obs):
    ...

# recommended
def updatePointGUI(self, obs: ObsSite) -> None:
    ...
```

#### c) Pure functions in `satellite_calculations.py`

10 module-level functions (e.g. `findSatUp`, `findRangeRate`,
`calcSatSunPhase`, `calcAppMag`, `calcPassEvents`,
`collectAllOrbits`, `sortFlipEvents`, `addMeridianTransit`)
lack both parameter types **and** return types.  Example:

```python
# current (satellite_calculations.py:32)
def findSatUp(
    satellite, observer, timescale, ...
):
    ...

# recommended
def findSatUp(
    satellite: EarthSatellite,
    observer: GeographicPosition,
    timescale: Timescale,
    timeStart: Time,
    timeEnd: Time,
) -> list[tuple[Time, bool]]:
    ...
```

#### d) `__init__` parameters in GUI window classes

22 GUI classes receive `app` with no type annotation:

```python
# current (mainWindow.py:38)
def __init__(self, app):

# recommended
def __init__(self, app: MountWizzard4) -> None:
```

#### e) `mountcontrol` methods

5 methods in `mount.py`, `connection.py`, `satellite.py`, and
`progStar.py` are missing return types.

---

## 3. Critical Bugs

### BUG-01 — `Camera.waitDownload` / `waitSave` logic is inverted

**File:** `src/mw4/logic/camera/camera.py`, lines 187–195  
**Severity:** HIGH – silently skips the wait; camera state machine
proceeds before data is ready.

```python
# current – exits immediately (wrong condition)
def waitDownload(self) -> None:
    self.signals.message.emit("download")
    while self.exposing and "downloading" in self.data.get("Device.Message"):
        time.sleep(0.1)

def waitSave(self) -> None:
    self.signals.message.emit("saving")
    while self.exposing and "image is ready" in self.data.get("Device.Message"):
        time.sleep(0.1)

# recommended – waits UNTIL the keyword appears
def waitDownload(self) -> None:
    self.signals.message.emit("download")
    msg = self.data.get("Device.Message", "")
    while self.exposing and "downloading" not in msg:
        time.sleep(0.1)
        msg = self.data.get("Device.Message", "")

def waitSave(self) -> None:
    self.signals.message.emit("saving")
    msg = self.data.get("Device.Message", "")
    while self.exposing and "image is ready" not in msg:
        time.sleep(0.1)
        msg = self.data.get("Device.Message", "")
```

### BUG-02 — `Camera.waitStart` / `waitDownload` / `waitSave` crash on missing key

**File:** `src/mw4/logic/camera/camera.py`, lines 184–195  
**Severity:** MEDIUM – `dict.get()` without a default returns `None`;
`"integrating" not in None` raises `TypeError` at runtime.

```python
# current – TypeError when key absent
while self.exposing and "integrating" not in self.data.get("Device.Message"):

# recommended
while self.exposing and "integrating" not in self.data.get("Device.Message", ""):
```

### BUG-03 — `AscomClass.stopCommunication` logs wrong driver class

**File:** `src/mw4/base/ascomClass.py`, line 277  
**Severity:** LOW – incorrect log/message emission; `"ALPACA"` is
emitted in the ASCOM stop path instead of `"ASCOM "`.

```python
# current (copy-paste error from AlpacaClass)
self.msg.emit(0, "ALPACA", "Device  remove", f"{self.deviceName}")

# recommended
self.msg.emit(0, "ASCOM ", "Device  remove", f"{self.deviceName}")
```

---

## 4. Architecture Issues

### ARCH-01 — `app: Any` suppresses static analysis in all logic classes

**Files:** All 19 classes in `src/mw4/logic/` that call
`Camera(app)`, `Dome(app)`, etc.

Every logic-layer class stores `self.app: Any`, which disables all
IDE type-checking for every `self.app.X` access.  `DriverProtocol`
already demonstrates the project's capability to define structural types.

**Recommendation:** Introduce a lightweight `AppProtocol` (or a
forward reference to `MountWizzard4`) so that type checkers can catch
attribute mismatches:

```python
# src/mw4/base/appProtocol.py  (new file)
from typing import Protocol
from PySide6.QtCore import QThreadPool

class AppProtocol(Protocol):
    threadPool: QThreadPool
    mount: ...       # forward-ref or Protocol
    camera: ...
    dome: ...
    # … other subsystems used by logic classes
```

Then in each logic class:

```python
# before
def __init__(self, app: Any) -> None:

# after
def __init__(self, app: AppProtocol) -> None:
```

The same applies to the 22 GUI window classes that receive `app`
without any annotation.

### ARCH-02 — `run: dict[str, Any]` ignores the existing `DriverProtocol`

**Files:** `src/mw4/logic/dome/dome.py:46`,
`src/mw4/logic/focuser/focuser.py:40`,
`src/mw4/logic/filter/filter.py:40`  
(and implicitly `camera.py`)

`DriverProtocol` was added to express exactly this contract, yet it is
not used in the `run` dict type:

```python
# current
self.run: dict[str, Any] = {"indi": ..., "alpaca": ...}

# recommended
from mw4.base.driverProtocol import DriverProtocol
self.run: dict[str, DriverProtocol] = {"indi": ..., "alpaca": ...}
```

This change immediately enables type checking for all
`self.run[self.framework].startCommunication()` calls.

### ARCH-03 — `MainWindowAddons` uses duck-typing instead of a Protocol

**File:** `src/mw4/gui/mainWindow/mainWindowAddons.py`, lines 83–99

```python
if hasattr(self.addons[addon], "initConfig"):
    self.addons[addon].initConfig()
if hasattr(self.addons[addon], "storeConfig"):
    self.addons[addon].storeConfig()
if hasattr(self.addons[addon], "setupIcons"):
    self.addons[addon].setupIcons()
if hasattr(self.addons[addon], "updateColorSet"):
    self.addons[addon].updateColorSet()
```

**Recommendation:** Define a `MainWindowAddonProtocol` that makes the
expected interface explicit and lets `mypy`/`pyright` verify
conformance:

```python
class MainWindowAddonProtocol(Protocol):
    def initConfig(self) -> None: ...
    def storeConfig(self) -> None: ...
    def setupIcons(self) -> None: ...
    def updateColorSet(self) -> None: ...
```

### ARCH-04 — GUI→Logic leakage via live widget-tree traversal

**File:** `src/mw4/mainApp.py`

`getActiveDrivers()` traverses
`mainW.mainWindowAddons.addons["SettDevice"].drivers`  –  the
application kernel reaches directly into a GUI widget to retrieve
driver state.  This couples the business layer to widget internals and
makes the method impossible to call without a running GUI (e.g. in
headless/test mode).

**Recommendation:** Introduce a `DeviceRegistry` singleton that both
the GUI settings tab and the device logic classes read from.  The
registry is populated by the settings tab via a signal and queried by
`getActiveDrivers()` without touching the widget tree.

### ARCH-05 — No type-checker integration; Ruff `ANN` rules are not enabled

`pyproject.toml` configures Ruff with rules `E, T2, UP, I, C, LOG, W,
SIM, A` but **not** the `ANN` (annotation) rule set.  There is no
`mypy` or `pyright` configuration.  As a result, the 252 missing
annotations are not surfaced automatically in CI.

**Recommendation:**

```toml
# pyproject.toml – add to [tool.ruff.lint] extend-select:
"ANN",   # annotation rules

# or add a separate type-checker:
[dependency-groups]
dev = [
    ...
    "mypy==1.15.0",
]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
```

---

## 5. Incomplete / Stub Functions

### STUB-01 — `NINAClass.workerPollData` and `workerGetInitialConfig`

**File:** `src/mw4/base/ninaClass.py`, lines 129–130, 139–140

```python
def workerPollData(self) -> None:
    pass          # ← no camera data ever polled for NINA

def workerGetInitialConfig(self) -> None:
    pass          # ← driver name/version never populated
```

These are **base-class stubs**, but are not decorated with
`@abstractmethod`.  Subclasses that forget to override them silently
do nothing, which can mask connection issues.

**Recommendation:** Either decorate as `@abstractmethod` (requires
`ABCMeta`) or add a `raise NotImplementedError` with a comment
explaining why they are intentional no-ops.

### STUB-02 — `AlpacaClass.processPolledData` and `workerPollData`

**File:** `src/mw4/base/alpacaClass.py`

Same pattern as STUB-01.  The base implementation is `pass` but not
marked abstract.

### STUB-03 — `AscomClass.processPolledData` and `workerPollData`

**File:** `src/mw4/base/ascomClass.py`, lines 232–237

Same pattern.

### STUB-04 — `loggerMW.redirectSTD` is a permanently disabled no-op

**File:** `src/mw4/base/loggerMW.py`, lines 60–68

```python
def redirectSTD() -> None:
    pass
    # sys.stderr = LoggerWriter(logging.getLogger().error, "STDERR", sys.stderr)
    # sys.stdout = LoggerWriter(logging.getLogger().info, "STDOUT", sys.stdout)
```

The function is called from `setupLogging()` but does nothing.
The commented-out code suggests an intentional feature that was
temporarily disabled.

**Recommendation:** Either re-enable the redirection, remove the dead
code and the call site, or add a docstring explaining why it is
intentionally empty (e.g. "disabled due to PySide6 signal-safe
logging").

---

## 6. Code Quality & Maintainability

### QA-01 — `baseTestApp.py` is a 1 238-line hand-rolled mock

**File:** `tests/unit_tests/unitTestAddOns/baseTestApp.py`

This file manually duplicates the entire public API of
`MountWizzard4` and all its subsystems.  Any API change requires a
parallel update to the mock, and divergence is not caught at
import time.

**Recommendation:** Replace gradually with
`unittest.mock.create_autospec(MountWizzard4)` constructed per test
module.  This ensures the mock always reflects the live API and
removes 1 200+ lines of maintenance burden.

### QA-02 — Satellite calculation functions lack docstrings and types

**File:** `src/mw4/logic/satellites/satellite_calculations.py`

10 module-level functions (astronomical coordinate transformations,
Doppler calculations, etc.) are the most scientifically complex code
in the project but have no docstrings and no type annotations.
Both are required for correctness validation.

### QA-03 — `tabMount_Sett.py` slot methods lack parameter annotations

22 slot methods receive domain objects (`obs`, `sett`, `fw`) without
annotated parameter types (see §2.3b).  Without annotations, callers
passing the wrong signal payload type are not caught statically.

### QA-04 — `mountcontrol/mount.py` public API partially unannotated

5 methods including `progTrajectory`, `calcTransformationMatricesTarget`,
`calcTransformationMatricesActual`, and `calcMountAltAzToDomeAltAz` lack
return-type annotations.  These are core astronomical calculation
entry points.

---

## 7. Tooling Gaps

| Gap | Impact | Recommended Fix |
|---|---|---|
| No `mypy`/`pyright` in CI | Annotation gaps silently accumulate | Add `mypy --strict` to `[dependency-groups] dev` |
| Ruff `ANN` rules not enabled | Missing annotations not flagged by linter | Add `"ANN"` to `extend-select` in `pyproject.toml` |
| No `@abstractmethod` on base stubs | Subclasses silently inherit no-op methods | Decorate base stubs with `@abstractmethod` or raise `NotImplementedError` |
| `baseTestApp.py` not auto-generated | Test mocks diverge silently from production API | Use `create_autospec` or generate from production classes |

---

## 8. Prioritised Improvement Backlog

### Tier 1 — Critical Bugs (fix immediately)

| ID | File | Description |
|---|---|---|
| BUG-01 | `camera.py:187–195` | Inverted loop condition in `waitDownload`/`waitSave` |
| BUG-02 | `camera.py:184–195` | `dict.get()` without default causes `TypeError` |
| BUG-03 | `ascomClass.py:277` | Wrong driver label `"ALPACA"` in ASCOM disconnect message |

### Tier 2 — Architecture & Maintainability (next sprint)

| ID | File(s) | Description |
|---|---|---|
| ARCH-01 | All 19 logic classes | Replace `app: Any` with `AppProtocol` |
| ARCH-02 | `dome.py`, `focuser.py`, `filter.py`, `camera.py` | Change `run: dict[str, Any]` → `dict[str, DriverProtocol]` |
| ARCH-03 | `mainWindowAddons.py` | Define `MainWindowAddonProtocol`; remove `hasattr` dispatch |
| ARCH-04 | `mainApp.py` | Decouple `getActiveDrivers()` from live widget tree |
| ARCH-05 | `pyproject.toml` | Add `mypy`/`ANN` Ruff rules to CI pipeline |
| QA-01 | `baseTestApp.py` | Replace with `create_autospec`-based fixtures |
| STUB-04 | `loggerMW.py` | Resolve `redirectSTD` dead code |

### Tier 3 — Annotation Sweep (background task)

| Priority | Files | Missing annotations |
|---|---|---|
| High | `gui/styles/styles.py` | 31 `@property` return types |
| High | `gui/mainWaddon/tabMount_Sett.py` | 22 slot parameter/return types |
| High | `logic/satellites/satellite_calculations.py` | 10 function signatures |
| Medium | `gui/extWindows/simulator/simulatorW.py` | 15 methods |
| Medium | `gui/mainWaddon/tabAnalysis.py` | 12 methods |
| Medium | `mountcontrol/mount.py` | 5 methods |
| Low | Remaining 22 GUI `__init__(self, app)` | Parameter type for `app` |
| Low | `base/indiClass.py:135` | `cleanupStop` return type |
| Low | `base/ascomClass.py:195` | `callMethodThreaded` return type |
| Low | `base/loggerMW.py:26` | `_set_defaults` return type |
| Low | `base/transform.py:52` | `J2000ToAltAz` return type |

Additionally: `STUB-01` / `STUB-02` / `STUB-03` – mark base
`workerPollData` / `processPolledData` / `workerGetInitialConfig`
as `@abstractmethod` or add `NotImplementedError`.

---

*Report generated by GitHub Copilot code review — MountWizzard4
v4.0.0b6, 2026-04-30.*

