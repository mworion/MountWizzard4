# MountWizzard4 — Code Review Report

**Date:** 2026-04-12  
**Reviewer:** GitHub Copilot  
**Scope:** `src/mw4/` (excluding `src/mw4/gui/widgets/` — auto-generated; `src/mw4/indibase/` — third-party library)  

---

## Executive Summary

The codebase is well-structured and the project conventions are broadly followed. The ruff linter (with the project's own configuration) reports **zero violations**, and the architecture separation between `logic/`, `base/`, and `gui/` is mostly clean. However, four categories of issues require attention:

| Category | Severity | Count |
|---|---|---|
| Threading / safety | 🔴 High | 4 distinct patterns |
| Missing test coverage | 🟡 Medium | 3 untested source modules |
| Architecture violations | 🟡 Medium | 4 files with cross-layer imports |
| Readability / naming | 🟢 Low | ~15 specific items |

---

## 1. Threading Issues

### 1.1 `sleepAndEvents` called from `QThreadPool` worker threads — Qt Safety Violation

**Files affected:**
- `src/mw4/logic/plateSolve/plateSolve.py` — `workerSolveLoop()` (line 141)
- `src/mw4/logic/camera/camera.py` — `waitExposed()`, `waitStart()`, `waitDownload()`, `waitSave()`, `waitFinish()` (lines 176–199)
- `src/mw4/base/indiClass.py` — `discoverDevices()` (line 298)

**Details:**
`sleepAndEvents()` creates a `QEventLoop`, calls `QTimer.singleShot()` on it, and then calls `loop.exec()`. Both `QEventLoop` and `QTimer` are Qt objects that **must** be created and used on the main thread (or at least on the thread that owns the Qt event loop). When these functions are invoked inside a `QThreadPool` worker (a C++ thread managed by Qt's pool), the objects are created on the wrong thread, which is a documented Qt violation and can cause non-deterministic crashes or silent data corruption.

```python
# src/mw4/gui/utilities/qtHelpers.py
def sleepAndEvents(value: int) -> None:
    loop = QEventLoop()           # ← created on worker thread: UNSAFE
    QTimer.singleShot(value, loop.quit)  # ← QTimer on worker thread: UNSAFE
    loop.exec()
```

**Specific calling contexts:**
- `plateSolve.workerSolveLoop` — runs as a `QRunnable` in `app.threadPool`, calls `sleepAndEvents(500)` inside a `while` loop.
- `camera.waitExposed/waitStart/waitDownload/waitSave` — called from driver-specific `workerExpose` methods (e.g., `cameraAlpaca.workerExpose`), which are themselves started as `Worker` runnables.
- `indiClass.discoverDevices` — called from GUI context when discovering devices. Although it currently runs on the main thread, the function's signature and position make future worker use likely.

**Recommendation:** Replace `sleepAndEvents` with `time.sleep()` in all worker-thread contexts. The event processing purpose of `sleepAndEvents` is irrelevant inside worker threads (they have no event loop to process). Alternatively, introduce a `workerSleep(ms)` helper using `time.sleep(ms / 1000)` in `base/` (not `gui/`), and reserve `sleepAndEvents` strictly for the main thread.

---

### 1.2 `runBatch` / `runModel` blocking on the main thread via nested event loops

**File:** `src/mw4/gui/mainWaddon/tabModel.py` — `runBatch()` (line 254)  
**File:** `src/mw4/logic/modelBuild/modelRun.py` — `runModel()` / `runThroughModelBuildData()` (line 305–306)

**Details:**
`runBatch` is connected directly to a GUI button click:
```python
self.ui.runModel.clicked.connect(self.runBatch)  # tabModel.py:43
```

Inside `runBatch`, it calls `self.modelData.runModel()`, which contains a blocking `while` loop with `sleepAndEvents(500)`:

```python
# modelRun.py:305
while not self.cancelBatch and not self.endBatch and not self.checkModelFinished():
    sleepAndEvents(500)
```

`sleepAndEvents` runs a nested `QEventLoop` to keep the GUI alive, but **the entire call stack lives on the main thread**. This is a re-entrancy risk: signals fired during the nested event loop can invoke slots that modify shared state (e.g., `cancelBatch`, `pauseBatch`) while the while-loop is mid-iteration. The model run should be moved to a `Worker` in the thread pool; model progress signals can then safely cross thread boundaries via Qt's queued connections.

**Recommendation:** Wrap `runBatch`'s body in a `Worker` and start it on `app.threadPool`. Replace `sleepAndEvents` loops in worker functions with `time.sleep`. Use signal/slot connections (queued automatically across threads) for progress updates to the GUI.

---

### 1.3 Unprotected boolean flags used as thread guards

**File:** `src/mw4/logic/camera/camera.py` — `self.exposing` (lines 135, 147, 154, 208)  
**File:** `src/mw4/logic/plateSolve/plateSolve.py` — `self.solveLoopRunning` (lines 148, 170)

**Details:**
Both flags are read by worker threads and written from the main thread (e.g., `expose()` sets `self.exposing = True`, `abort()` sets it to `False`). In CPython, individual attribute assignments are typically GIL-protected, so actual tearing is unlikely, but:
- Python's GIL does not guarantee memory ordering semantics for multi-core CPUs.
- `self.solveLoopRunning = False` (in `stopCommunication`) is the only signal to terminate the solve loop worker — if the loop reads a stale value due to caching, the worker may not stop promptly.

**Recommendation:** Use `threading.Event` (or a `QAtomicInteger` / `QAtomicInt`) for cross-thread boolean flags where one thread reads and another writes. The `plateSolve.solveLoopRunning` stop-flag is the most critical case.

---

### 1.4 Re-entrant signal connection in `discoverDevices`

**File:** `src/mw4/base/indiClass.py` — `discoverDevices()` (lines 293–301)

**Details:**
```python
def discoverDevices(self, deviceType: str) -> list[str]:
    self.client.signals.defText.connect(self.addDiscoveredDevice)
    self.client.connectServer()
    sleepAndEvents(2000)          # ← nested event loop for 2 s
    self.client.signals.defText.disconnect(self.addDiscoveredDevice)
    self.client.disconnectServer()
    return self.discoverList
```

A temporary signal connection is made, then a nested event loop runs for 2 seconds. If `discoverDevices` is called twice (e.g., via a double-click), the second call will connect a second handler, resulting in `addDiscoveredDevice` being invoked twice per event and duplicating entries in `discoverList`.

**Recommendation:** Guard with a flag, or use `blockSignals` / `UniqueConnection`:
```python
self.client.signals.defText.connect(
    self.addDiscoveredDevice, Qt.ConnectionType.UniqueConnection
)
```

---

### 1.5 `uploadPopupW.closePopup` blocks a worker thread with a nested event loop

**File:** `src/mw4/gui/extWindows/uploadPopupW.py` (lines 192–199)

**Details:**
`closePopup` is a slot connected to a worker's `result` signal, so it runs on the main thread. But when `result=True`, it polls `self.pollStatusRunState` in a loop using `sleepAndEvents(250)`. This is the same re-entrant main-thread pattern as §1.2.

---

## 2. Missing Test Coverage

The project requires 100% test coverage per SKILL.md rule 4. The following source modules have **no corresponding test file**:

| Source Module | Lines | Test File | Issue |
|---|---|---|---|
| `src/mw4/logic/buildData/alignstars.py` | 841 | None | Single function `generateAlignStars()` generates a 111-entry star dictionary — not tested at all |
| `src/mw4/logic/measure/measureAddOns.py` | 87 | None | Pure data module (`measure` dict constant) — not directly tested |
| `src/mw4/mountcontrol/mountSignals.py` | 36 | None | `MountSignals` class (QObject with signals) — instantiation and signal existence not tested |
| `src/mw4/base/signalsDevices.py` | 32 | None | `Signals` class (QObject with signals) — not tested |
| `src/mw4/base/indiClassAddOns.py` | varies | None | Constants/type maps used in `indiClass` — untested |

> **Note:** `measureAddOns.py` _is_ exercised indirectly via `test_measureW.py` in `tests/unit_tests/gui/extWindows/measure/`, but there is no direct unit test for the module. Similarly, `mountSignals.py` is instantiated in `test_mount.py` but never explicitly asserted.

**Recommendation:**
- Add `tests/unit_tests/logic/buildData/test_alignstars.py` — verify the return type, key set, and value length.
- Add `tests/unit_tests/logic/measure/test_measureAddOns.py` — verify the `measure` dict structure.
- Add `tests/unit_tests/mountcontrol/test_mountSignals.py` — verify signal declarations.
- Add `tests/unit_tests/base/test_signalsDevices.py` — verify signal declarations.

---

## 3. Architecture Violations

### 3.1 Logic / base layer imports from `gui.utilities`

**Rule:** SKILL.md rule 11 — "clear separation between business logic in `src/mw4/logic` and gui in `src/gui`".

The following non-GUI files import `sleepAndEvents` from `mw4.gui.utilities.qtHelpers`:

| File | Import |
|---|---|
| `src/mw4/logic/plateSolve/plateSolve.py` | `from mw4.gui.utilities.qtHelpers import sleepAndEvents` |
| `src/mw4/logic/camera/camera.py` | `from mw4.gui.utilities.qtHelpers import sleepAndEvents` |
| `src/mw4/logic/modelBuild/modelRun.py` | `from mw4.gui.utilities.qtHelpers import sleepAndEvents` |
| `src/mw4/base/indiClass.py` | `from mw4.gui.utilities.qtHelpers import sleepAndEvents` |

This creates a **bidirectional dependency**: the `gui` layer depends on `logic` and `base`, but now `logic` and `base` also depend on `gui`. This breaks the clean unidirectional architecture.

**Recommendation:** Move `sleepAndEvents` (or a non-GUI equivalent `workerSleep`) to `src/mw4/base/tpool.py` or a new `src/mw4/base/threadUtils.py`. Logic and base modules should import from `base`, not from `gui`.

---

### 3.2 `MountSignals` has an empty docstring

**File:** `src/mw4/mountcontrol/mountSignals.py` (line 20)

```python
class MountSignals(QObject):
    """ """
```

This is a placeholder/empty docstring. Since the class is part of the public API, it should have a meaningful description.

---

### 3.3 `MountDevice` docstring is also empty

**File:** `src/mw4/mountcontrol/mount.py` (line 36)

```python
class MountDevice:
    """ """
```

Same pattern as above.

---

## 4. Readability Issues

### 4.1 Non-camelCase signal names in `mainApp.py`

**File:** `src/mw4/mainApp.py` (lines 94–95)

```python
game_sL = Signal(object, object)  # ← snake_case, breaks project convention
game_sR = Signal(object, object)  # ← snake_case, breaks project convention
```

All other signals in `mainApp.py` use camelCase (`gameABXY`, `gamePMH`, etc.). These two are inconsistent. They are consumed in:
- `tabImage_Manage.py:58` — `self.app.game_sL.connect(...)`
- `tabMount_Move.py:102` — `self.app.game_sR.connect(...)`
- `tabSett_Misc.py:158,160` — `self.app.game_sL.emit(...)`, `self.app.game_sR.emit(...)`

**Recommendation:** Rename to `gameSL` / `gameSR` and update all four consumers.

---

### 4.2 Dictionary key typo: `"ImageMange"` instead of `"ImageManage"`

**File:** `src/mw4/gui/mainWindow/mainWindowAddons.py` (line 58)

```python
"ImageMange": ImageManage(mainW),   # ← "Mange" should be "Manage"
```

This typo would cause a `KeyError` if any code looked up `addons["ImageManage"]`.

**Recommendation:** Rename the key to `"ImageManage"` and verify no existing code references the misspelled key.

---

### 4.3 Non-camelCase function names in several modules

**File:** `src/mw4/logic/environment/sensorWeatherBoltwood.py` (lines 50, 54)

```python
def convert_knots2kmh(knots: float) -> float: ...
def convert_mph2kmh(mph: float) -> float: ...
```

**File:** `src/mw4/logic/satellites/satellite_calculations.py` (line 109)

```python
def west_of_meridian_at(t): ...
```

**File:** `src/mw4/cli.py` (line 22)

```python
def read_options() -> argparse.Namespace: ...
```

All violate the camelCase convention (SKILL.md rule 1).

**Recommendation:** Rename:
- `convert_knots2kmh` → `convertKnots2Kmh`
- `convert_mph2kmh` → `convertMph2Kmh`
- `west_of_meridian_at` → `westOfMeridianAt` (note: this is also used as a skyfield function attribute setter, so care is needed)
- `read_options` → `readOptions`

---

### 4.4 Unused expression in `sendModelProgress`

**File:** `src/mw4/logic/modelBuild/modelRun.py` (line 231)

```python
def sendModelProgress(self) -> None:
    donePoints = sum(...)
    sum(1 for key in self.modelBuildData if self.modelBuildData[key]["success"])  # ← result discarded!
    fraction = donePoints / len(self.modelBuildData)
```

The second `sum()` call computes a count of successful points but the result is never assigned or used. This is dead code and may represent an unfinished feature (the progress dict does not include a `successCount` field).

**Recommendation:** Either remove the line or assign it:
```python
successPoints = sum(1 for key in self.modelBuildData if self.modelBuildData[key]["success"])
```
and add `"successCount": successPoints` to `progressData`.

---

### 4.5 Magic number `30` for `QThreadPool.setMaxThreadCount`

**File:** `src/mw4/mainApp.py` (line 134)

```python
self.threadPool.setMaxThreadCount(30)
```

The value 30 is not documented. For an astronomy-control application running on typical hardware, 30 simultaneous threads is extremely high and may exhaust system resources on a Raspberry Pi or other single-board computer targets listed in the classifiers.

**Recommendation:** Extract to a named constant:
```python
MAX_THREAD_COUNT: int = 30  # allows concurrent device polling + model workers
self.threadPool.setMaxThreadCount(MAX_THREAD_COUNT)
```

---

### 4.6 Broad type annotations using `Any` where more specific types exist

**Total violations across project:** 804 (as reported by `ruff --select ANN`)

The most impactful are in the GUI layer (`__init__` methods accepting `app`, `mainW`, `parent` as untyped or `Any`-typed parameters). Given the project's own type-annotation rule (SKILL.md rule 14), these should be progressively addressed.

Key hotspots:
- 79 `__init__` methods missing return type `-> None`
- 30 occurrences of `mainW` argument missing annotation
- 21 occurrences of `app` argument missing annotation
- Pervasive `ANN401` (`Any` used where a Protocol or concrete type could be used)

The `DriverProtocol` in `src/mw4/base/driverProtocol.py` is an excellent step in the right direction — it should be adopted more widely in place of `Any` in the `run` dictionaries of `camera.py`, `dome.py`, etc.

---

### 4.7 Missing type annotation for `clearAlignAndBackup` return type

**File:** `src/mw4/gui/mainWaddon/tabModel.py` (line 176)

```python
def clearAlignAndBackup(self):   # ← no return type annotation
```

This method returns `True`/`False` but lacks `-> bool`.

---

### 4.8 Missing type annotations on several GUI `__init__` methods

Widespread pattern — every addon class (`Model`, `BuildPoints`, `SettDevice`, etc.) in `gui/mainWaddon/` has `__init__(self, mainW)` without type annotation on `mainW` and without `-> None`. Since `MainWindow` is defined in `gui/mainWindow/mainWindow.py`, annotating these would require a forward reference or `TYPE_CHECKING` guard.

---

## 5. Additional Observations

### 5.1 Worker reuse with `setAutoDelete(False)` is correct but undocumented

`tpool.Worker` correctly calls `self.setAutoDelete(False)`, allowing the same `Worker` instance (e.g., `plateSolve.worker`) to be re-started after completion. However, `startSolveLoop` does not guard against starting the same worker while it is already running:

```python
def startSolveLoop(self) -> None:
    self.solveLoopRunning = True
    self.threadPool.start(self.worker)   # second call while loop is active?
```

If `startSolveLoop` is called twice (e.g., due to duplicate `serverConnected` signal emissions), two threads will execute `workerSolveLoop` concurrently, both reading from `solveQueue` — a data race.

**Recommendation:** Guard with a flag:
```python
def startSolveLoop(self) -> None:
    if self.solveLoopRunning:
        return
    self.solveLoopRunning = True
    self.threadPool.start(self.worker)
```

### 5.2 `indiClass.stopCommunication` does not wait for worker threads

**File:** `src/mw4/base/indiClass.py` (lines 160–163)

```python
def stopCommunication(self) -> None:
    self.client.disconnectServer(self.deviceName)
    self.deviceName = ""
    self.deviceConnected = False
```

After `disconnectServer`, active device-update slots (`updateNumber`, `updateSwitch`, etc.) may still fire on in-flight signals. Setting `self.deviceName = ""` inside those slots would cause silent no-ops (the `deviceName != self.deviceName` guard protects most of them), but there is a window where the client sends a final batch of updates after `disconnectServer` is called.

### 5.3 `CyclicTimerManager.counter` can overflow on long-running instances

**File:** `src/mw4/base/timerManager.py` (line 62)

```python
self.counter += 1
```

The counter is an unbounded Python `int`. For a session running 30 days at 100 ms ticks: `30 * 24 * 3600 * 10 = 25_920_000` — well within `int` range in Python. This is not a practical risk, but using `counter % lcm(all_intervals)` would keep the counter bounded and avoid theoretical long-running issues.

### 5.4 `sensorWeatherBoltwood` is not exported via `__init__` and lacks discovery wiring

**File:** `src/mw4/logic/environment/sensorWeatherBoltwood.py`

This module is tested via `tests/unit_tests/logic/environment/test_boltwoodWeather.py` (good), but it is not registered in `SensorWeather.run` dict (unlike `indi`, `alpaca`, `ascom`, `online`). It appears to be a standalone file-reader driver with a different activation path. The wiring should be documented.

---

## Summary Table

| # | Area | File(s) | Severity | Action |
|---|---|---|---|---|
| 1.1 | Threading | `plateSolve.py`, `camera.py`, `indiClass.py` | 🔴 High | Replace `sleepAndEvents` with `time.sleep` in workers |
| 1.2 | Threading | `tabModel.py`, `modelRun.py` | 🔴 High | Move `runBatch` body to Worker thread |
| 1.3 | Threading | `camera.py`, `plateSolve.py` | 🟡 Medium | Use `threading.Event` for stop flags |
| 1.4 | Threading | `indiClass.py` | 🟡 Medium | Use `UniqueConnection` in `discoverDevices` |
| 1.5 | Threading | `uploadPopupW.py` | 🟡 Medium | Replace nested event loop in `closePopup` |
| 2.1 | Coverage | `alignstars.py` | 🟡 Medium | Add `test_alignstars.py` |
| 2.2 | Coverage | `measureAddOns.py` | 🟢 Low | Add `test_measureAddOns.py` |
| 2.3 | Coverage | `mountSignals.py` | 🟢 Low | Add `test_mountSignals.py` |
| 3.1 | Architecture | `plateSolve.py`, `camera.py`, `modelRun.py`, `indiClass.py` | 🟡 Medium | Move `sleepAndEvents`/`workerSleep` to `base/` |
| 3.2 | Architecture | `mountSignals.py`, `mount.py` | 🟢 Low | Add meaningful docstrings |
| 4.1 | Readability | `mainApp.py` | 🟢 Low | Rename `game_sL`/`game_sR` to camelCase |
| 4.2 | Readability | `mainWindowAddons.py` | 🟢 Low | Fix `"ImageMange"` typo |
| 4.3 | Readability | `sensorWeatherBoltwood.py`, `satellite_calculations.py`, `cli.py` | 🟢 Low | Rename to camelCase |
| 4.4 | Readability | `modelRun.py:231` | 🟢 Low | Remove or assign unused `sum()` |
| 4.5 | Readability | `mainApp.py:134` | 🟢 Low | Extract magic number `30` to constant |
| 4.6 | Readability | Codebase-wide | 🟢 Low | Address 804 `ANN` violations progressively |
| 5.1 | Correctness | `plateSolve.py` | 🟡 Medium | Guard `startSolveLoop` against double-start |
| 5.2 | Correctness | `indiClass.py` | 🟢 Low | Document stop-communication race window |

---

*End of report*

