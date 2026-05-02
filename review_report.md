# MountWizzard4 – Code Review Report

**Date:** 2026-04-30 (updated 2026-04-30 after fixes)
**Scope:** `src/mw4/` (232 Python files, ~1 974 function/method definitions)  
**Tools used:** Manual source analysis, `grep`, `ruff`, project conventions from  
`pyproject.toml` and `.github/copilot-instructions.md`

---

## Changelog

| Date | Changes |
|---|---|
| 2026-04-30 | Initial report |
| 2026-04-30 | Applied fixes: BUG-01, BUG-02, BUG-03, STUB-01, STUB-02; annotation sweeps for `styles.py` (+31), `tabMount_Sett.py` (+22), `simulatorW.py` (+15), `tabAnalysis.py` (+12); `driverProtocol.py` deleted (ARCH-02 superseded) |
| 2026-04-30 | Commits `7344e992a`/`0e0aac8d9`: `tabMount_Sett.py` slot parameter types fully annotated (`ObsSite`, `Setting`, `Firmware`, `Angle`); dead `cycleData` timer references removed from `startNINATimer`/`stopNINATimer` and `startSGProTimer`/`stopSGProTimer`; QA-03 fully resolved |
| 2026-05-02 | Tier-3 annotation sweep completed: `satellite_calculations.py`, `imageTabs.py`, `buildPoints.py` (simulator), `tabSat_Search.py`, `splashScreen.py`, `tools.py` (simulator), `dome.py` (simulator), `indiClass.py`, `loggerMW.py`, `qtMain.py`, `tabSett_Update.py`; all 22 GUI `__init__(self, app)` methods annotated with `app: Any` and `-> None`; `simulatorW.py.__init__` `app: Any` added |

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

| Metric | Initial | Sprint 1 | Tier-3 Sweep |
|---|---|---|---|
| Total source files reviewed | 232 | 232 | 232 |
| Total function/method definitions | 1 974 | ~1 958 | ~1 958 |
| Definitions with return-type annotation | 1 722 (87.2 %) | ~1 805 (92.7 %) | **~1 889 (96.5 %)** |
| **Missing return-type annotations** | **252 (12.8 %)** | **~153 (7.8 %)** | **~69 (3.5 %)** |
| Files with untyped `app` parameter | ≥ 41 (19 logic + 22 GUI) | ≥ 41 (unchanged) | **22 GUI fixed; 19 logic still `Any`** |
| Confirmed logic bugs | 3 | **0 (all fixed)** | 0 |
| Stub / no-op methods (undocumented) | 5 | **2 (STUB-01/02 resolved; STUB-03/04 remain)** | 2 |
| Critical architecture issues | 5 | 4 (ARCH-02 superseded) | 4 |

Overall the codebase is well-structured for a project of this size.
The separation between `logic/` and `gui/` is respected in most places,
signals & slots are used correctly.

All three critical bugs have been resolved.  Two stub-method clusters
(`NINAClass` and `SGProClass` poll-data machinery) were cleaned up by
removing the entire cycle rather than marking as abstract; residual
dead `cycleData` timer calls were also removed.  Annotation coverage
has now reached approximately **96.5 %** following two successive
annotation sweeps — Sprint 1 (+83 definitions across
`styles.py`, `tabMount_Sett.py`, `simulatorW.py`, `tabAnalysis.py`)
and the Tier-3 sweep (+84 definitions across 13 source files and
22 GUI window constructors).

The remaining areas that need attention are:

- ~69 still-unannotated definitions, mainly scattered across smaller
  logic and GUI helper files not yet swept.
- The `app: Any` pattern in all 19 logic-layer classes that defeats
  static analysis for every `self.app.X` access (ARCH-01).
- STUB-03/STUB-04 and the four remaining architecture issues.

---

## 2. Type Annotation Coverage

### 2.1 Overall Statistics

```
                               Initial    Sprint 1    Tier-3 Sweep
Total defs reviewed          :  1 974       ~1 958        ~1 958
With return-type annotation  :  1 722        ~1 805        ~1 889
                                (87.2 %)    (92.7 %)      (96.5 %)
Missing return-type annotation:   252          ~153           ~69
                                (12.8 %)     (7.8 %)       (3.5 %)

Sprint-1 fixes (approx.):
  styles.py                    +31
  tabMount_Sett.py (returns)   +22
  simulatorW.py                +15
  tabAnalysis.py               +12
  tabMount_Sett.py (params)     +3
  NINAClass/SGProClass: ~12 methods removed (poll-data cycle)
  Sprint-1 total               +83 (net) / ~16 defs removed

Tier-3 sweep fixes (approx.):
  satellite_calculations.py     +2  (findSunlit ephemeris, westOfMeridianAt)
  imageTabs.py                  +9
  buildPoints.py (simulator)    +9
  tabSat_Search.py              +7
  splashScreen.py               +7
  tools.py (simulator)          +7
  dome.py (simulator)           +7
  qtMain.py                     +5
  tabSett_Update.py             +5
  22 GUI __init__ (app: Any)   +22
  keypadW.py clearCursor        +1
  indiClass.py cleanupStop      +1
  loggerMW.py _set_defaults     +1
  simulatorW.py app: Any        +1
  Tier-3 total                 +84
```

### 2.2 Files with Remaining Missing Annotations

All files from the initial audit have now been resolved.

| # Missing | File | Status |
|---|---|---|
| ~~31~~ | ~~`src/mw4/gui/styles/styles.py`~~ | ✅ Fixed (Sprint 1) |
| ~~22~~ | ~~`src/mw4/gui/mainWaddon/tabMount_Sett.py`~~ | ✅ Fixed (Sprint 1 — all return + parameter types) |
| ~~15~~ | ~~`src/mw4/gui/extWindows/simulator/simulatorW.py`~~ | ✅ Fixed (Sprint 1 + Tier-3) |
| ~~12~~ | ~~`src/mw4/gui/mainWaddon/tabAnalysis.py`~~ | ✅ Fixed (Sprint 1) |
| ~~10~~ | ~~`src/mw4/logic/satellites/satellite_calculations.py`~~ | ✅ Fixed (Tier-3) |
| ~~9~~ | ~~`src/mw4/gui/extWindows/image/imageTabs.py`~~ | ✅ Fixed (Tier-3) |
| ~~9~~ | ~~`src/mw4/gui/extWindows/simulator/buildPoints.py`~~ | ✅ Fixed (Tier-3) |
| ~~7~~ | ~~`src/mw4/gui/mainWaddon/tabSat_Search.py`~~ | ✅ Fixed (Tier-3) |
| ~~7~~ | ~~`src/mw4/gui/extWindows/splashScreen.py`~~ | ✅ Fixed (Tier-3) |
| ~~7~~ | ~~`src/mw4/gui/extWindows/simulator/tools.py`~~ | ✅ Fixed (Tier-3) |
| ~~7~~ | ~~`src/mw4/gui/extWindows/simulator/dome.py`~~ | ✅ Fixed (Tier-3) |
| ~~5~~ | ~~`src/mw4/logic/buildData/buildpoints.py`~~ | ✅ Fixed (already fully annotated) |
| ~~5~~ | ~~`src/mw4/gui/mainWaddon/tabSett_Update.py`~~ | ✅ Fixed (Tier-3) |
| ~~5~~ | ~~`src/mw4/gui/utilities/qtMain.py`~~ | ✅ Fixed (Tier-3) |
| ~~5~~ | ~~`src/mw4/mountcontrol/mount.py`~~ | ✅ Fixed (already fully annotated) |

### 2.3 Recurring Patterns

#### a) `@property` setters / colour constants (`styles.py`) — ✅ FIXED

All 31 `@property` colour accessors (`M_PRIM`, `M_SEC`, `M_RED`, etc.)
now carry `-> str` return-type annotations.

#### b) GUI signal-slot callbacks (`tabMount_Sett.py`) — ✅ FIXED

All 22 slot methods now carry both return-type and parameter-type
annotations.  Proper domain types (`ObsSite`, `Setting`, `Firmware`,
`Angle`) were imported and applied.

#### c) Pure functions in `satellite_calculations.py` — ✅ FIXED

`findSunlit` now has `ephemeris: Any` typed.  The inner
`westOfMeridianAt` closure received `t: Time` and `-> bool`.  All
other module-level functions (`findSatUp`, `findRangeRate`,
`calcSatSunPhase`, `calcAppMag`, `calcPassEvents`,
`collectAllOrbits`, `sortFlipEvents`, `addMeridianTransit`,
`calcSatelliteMeridianTransit`, `extractCorrectOrbits`,
`calcSatPasses`) were already fully annotated.

#### d) `__init__` parameters in GUI window classes — ✅ FIXED

All 22 GUI classes that previously received `app` with no type
annotation now have `app: Any` and `-> None`:

```python
# fixed (mainWindow.py:38)
def __init__(self, app: Any) -> None:
```

Files updated: `mainWindow.py`, `satelliteMapW.py`, `analyseW.py`,
`satelliteHorW.py`, `hemisphereW.py`, `messageW.py`, `bigPopupW.py`,
`measureW.py`, `keypadW.py`, `imageW.py`, `videoW.py`,
`videoBase.py`, `simulatorW.py`, and the six simulator subclasses
(`laser.py`, `telescope.py`, `horizon.py`, `light.py`, `world.py`,
`pointer.py`).

#### e) `mountcontrol` methods — ✅ FIXED (already annotated)

Inspection of `mount.py` confirmed that all five methods cited in the
initial report (`progTrajectory`, `calcTransformationMatricesTarget`,
`calcTransformationMatricesActual`, `calcMountAltAzToDomeAltAz`, and
`checkMountIsUp`) already carry full return-type annotations; no
changes were required.

---

## 3. Critical Bugs

### BUG-01 — ✅ FIXED — `Camera.waitDownload` / `waitSave` logic is inverted

**File:** `src/mw4/logic/camera/camera.py`  
**Severity:** HIGH – silently skips the wait; camera state machine
proceeds before data is ready.

The loop condition was inverted: both methods used `in` instead of
`not in`, causing the loop to exit immediately when the keyword
was absent (the normal start-up state) rather than waiting for it to
appear.

**Fix applied:** Loop condition changed to `not in`; the message is
re-read on every iteration via a local variable so new device
messages are picked up during the wait.

```python
# fixed
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

### BUG-02 — ✅ FIXED — `Camera.waitStart` / `waitDownload` / `waitSave` crash on missing key

**File:** `src/mw4/logic/camera/camera.py`  
**Severity:** MEDIUM – `dict.get()` without a default returns `None`;
`"integrating" not in None` raises `TypeError` at runtime.

**Fix applied:** Default value `""` added to all `dict.get("Device.Message")`
calls in `waitStart`, `waitDownload`, and `waitSave`.

### BUG-03 — ✅ FIXED — `AscomClass.stopCommunication` logs wrong driver class

**File:** `src/mw4/base/ascomClass.py`  
**Severity:** LOW – incorrect log/message emission; `"ALPACA"` was
emitted in the ASCOM stop path (copy-paste error from `AlpacaClass`).

**Fix applied:** Label changed from `"ALPACA"` to `"ASCOM"`.

```python
# fixed
self.msg.emit(0, "ASCOM", "Device  remove", f"{self.deviceName}")
```

---

## 4. Architecture Issues

### ARCH-01 — `app: Any` suppresses static analysis in all logic classes

**Files:** All 19 classes in `src/mw4/logic/` that call
`Camera(app)`, `Dome(app)`, etc.

Every logic-layer class stores `self.app: Any`, which disables all
IDE type-checking for every `self.app.X` access.  Note: `driverProtocol.py`
has since been deleted (see ARCH-02), so a new `AppProtocol` cannot
reference it directly.

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

### ARCH-02 — ~~`run: dict[str, Any]` ignores the existing `DriverProtocol`~~ — SUPERSEDED

`src/mw4/base/driverProtocol.py` has been **deleted**.  The
`DriverProtocol` structural type no longer exists in the codebase.
The `run` dicts in `dome.py`, `focuser.py`, `filter.py`, and
`camera.py` therefore remain `dict[str, Any]` as before.

**Open question:** If static-typing of the strategy dicts is still
desirable, a new `DriverProtocol` (or equivalent) must be reintroduced.
This is now tracked under ARCH-01 as part of the broader `AppProtocol`
effort.  Track as a separate backlog item if needed.

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

### STUB-01 — ✅ RESOLVED — `NINAClass` poll-data cycle removed

**File:** `src/mw4/base/ninaClass.py`

The entire poll-data machinery (`workerPollData`, `processPolledData`,
`pollData`, `cycleData` timer, `workerData` worker attribute) has been
**removed** from `NINAClass`.  The corresponding empty override in
`CameraNINA` (`cameraNINA.py`) was removed as well.  A follow-up
commit also removed the dead `self.cycleData.start/stop()` calls that
remained in `startNINATimer` / `stopNINATimer`.

The `workerGetInitialConfig` stub (`pass`) remains intentionally as a
base-class default.

### STUB-02 — ✅ RESOLVED — `SGProClass` poll-data cycle removed

**File:** `src/mw4/base/sgproClass.py`

Same resolution as STUB-01: the entire poll-data cycle
(`workerPollData`, `processPolledData`, `pollData`, `cycleData`,
`workerData`) has been removed from `SGProClass` and from its
`CameraSGPro` subclass.  Dead `cycleData` references in
`startSGProTimer` / `stopSGProTimer` were also removed.

### STUB-03 — `AscomClass.processPolledData` and `workerPollData` — ⚠️ Open

**File:** `src/mw4/base/ascomClass.py`

The `pass`-body base-class implementations remain and are not decorated
with `@abstractmethod`.  Subclasses that forget to override them
silently do nothing.

**Recommendation:** Decorate as `@abstractmethod` or add
`raise NotImplementedError`.

### STUB-04 — `loggerMW.redirectSTD` is a permanently disabled no-op — ⚠️ Open

**File:** `src/mw4/base/loggerMW.py`, lines 60–68

```python
def redirectSTD() -> None:
    pass
    # sys.stderr = LoggerWriter(logging.getLogger().error, "STDERR", sys.stderr)
    # sys.stdout = LoggerWriter(logging.getLogger().info, "STDOUT", sys.stdout)
```

The function is called from `setupLogging()` but does nothing.

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

### QA-03 — `tabMount_Sett.py` slot methods lack parameter annotations — ✅ FIXED

All 22 slot methods now carry both return-type **and** parameter-type
annotations.  Domain types `ObsSite`, `Setting`, `Firmware`, and
`Angle` were imported and applied.  The `setLocationValues` helper
also received proper `Angle | None` and `float | None` parameter
types.

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

### Tier 1 — Critical Bugs

| ID | File | Description | Status |
|---|---|---|---|
| BUG-01 | `camera.py:187–195` | Inverted loop condition in `waitDownload`/`waitSave` | ✅ Fixed |
| BUG-02 | `camera.py:184–195` | `dict.get()` without default causes `TypeError` | ✅ Fixed |
| BUG-03 | `ascomClass.py:277` | Wrong driver label `"ALPACA"` in ASCOM disconnect message | ✅ Fixed |

### Tier 2 — Architecture & Maintainability (next sprint)

| ID | File(s) | Description | Status |
|---|---|---|---|
| ARCH-01 | All 19 logic classes | Replace `app: Any` with `AppProtocol` | ⚠️ Open |
| ARCH-02 | `dome.py`, `focuser.py`, `filter.py`, `camera.py` | `DriverProtocol` deleted; `run: dict[str, Any]` typing gap remains | ⚠️ Open (superseded) |
| ARCH-03 | `mainWindowAddons.py` | Define `MainWindowAddonProtocol`; remove `hasattr` dispatch | ⚠️ Open |
| ARCH-04 | `mainApp.py` | Decouple `getActiveDrivers()` from live widget tree | ⚠️ Open |
| ARCH-05 | `pyproject.toml` | Add `mypy`/`ANN` Ruff rules to CI pipeline | ⚠️ Open |
| QA-01 | `baseTestApp.py` | Replace with `create_autospec`-based fixtures | ⚠️ Open |
| STUB-04 | `loggerMW.py` | Resolve `redirectSTD` dead code | ⚠️ Open |

### Tier 3 — Annotation Sweep (background task)

| Priority | Files | Missing annotations | Status |
|---|---|---|---|
| ~~High~~ | ~~`gui/styles/styles.py`~~ | ~~31 `@property` return types~~ | ✅ Fixed |
| ~~High~~ | ~~`gui/mainWaddon/tabMount_Sett.py`~~ | ~~22 slot return types~~ | ✅ Fixed (return types only) |
| ~~High~~ | ~~`gui/mainWaddon/tabMount_Sett.py`~~ | ~~3 slot parameter types (`obs`, `sett`, `fw`)~~ | ✅ Fixed |
| High | `logic/satellites/satellite_calculations.py` | 10 function signatures | ✅ Fixed |
| ~~Medium~~ | ~~`gui/extWindows/simulator/simulatorW.py`~~ | ~~15 methods~~ | ✅ Fixed |
| ~~Medium~~ | ~~`gui/mainWaddon/tabAnalysis.py`~~ | ~~12 methods~~ | ✅ Fixed |
| Medium | `gui/extWindows/image/imageTabs.py` | 9 methods | ✅ Fixed |
| Medium | `gui/extWindows/simulator/buildPoints.py` | 9 methods | ✅ Fixed |
| Medium | `gui/mainWaddon/tabSat_Search.py` | 7 methods | ✅ Fixed |
| Medium | `gui/extWindows/splashScreen.py` | 7 methods | ✅ Fixed |
| Medium | `gui/extWindows/simulator/tools.py` | 7 methods | ✅ Fixed |
| Medium | `gui/extWindows/simulator/dome.py` | 7 methods | ✅ Fixed |
| Medium | `mountcontrol/mount.py` | 5 methods | ✅ Fixed (already annotated) |
| Low | Remaining 22 GUI `__init__(self, app)` | Parameter type for `app` | ✅ Fixed |
| Low | `base/indiClass.py:135` | `cleanupStop` return type | ✅ Fixed |
| Low | `base/ascomClass.py:195` | `callMethodThreaded` return type | ✅ Fixed (already annotated) |
| Low | `base/loggerMW.py:26` | `_set_defaults` return type | ✅ Fixed |
| Low | `base/transform.py:52` | `J2000ToAltAz` return type | ✅ Fixed (already annotated) |

Additionally: STUB-03 – mark `AscomClass.workerPollData` /
`processPolledData` as `@abstractmethod` or add `NotImplementedError`.

---

*Report generated by GitHub Copilot code review — MountWizzard4
v4.0.0b6, 2026-04-30. Updated 2026-05-02 after Tier-3 annotation sweep.*
