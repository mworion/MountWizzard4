# Code Review: `MountDevice` Class Improvements

**File:** `src/mw4/mountcontrol/mount.py`
**Class:** `MountDevice`
**Date:** 2026-06-11
**Reviewer:** GitHub Copilot

---

## Status Legend

- ✅ **Applied** — change implemented in `mount.py`.
- ❌ **Invalid** — re-investigation showed the original concern was wrong.
- ⏳ **Pending** — recommended, not yet implemented.

---

## Overview

This document tracks bugs, code-quality issues, and design improvements for the
`MountDevice` class. After re-reading `mount.py` and cross-checking the rest of
the codebase, several originally reported issues turned out to be invalid
(false positives) and have been marked accordingly. The applied fixes have
been verified against the unit-test suite (293 passing tests).

---

## 🐛 Bugs / Logic Issues

### ✅ Bug 1 — Inverted signal-emission logic in `checkMountIsUp()`
**Status:** Fixed (different approach than originally proposed).

The signal-emission flooding has been resolved by moving transition
detection into `startupMountData()` rather than keeping it inside
`checkMountIsUp()`. Connectivity probing is now strictly responsible for
updating `self.mountIsUp`, and the rising/falling-edge detection happens
once per cycle in `startupMountData()` based on `mountIsUpLastStatus`:

```python
def startupMountData(self) -> None:
    if self.mountIsUp and not self.mountIsUpLastStatus:
        self.mountIsUpLastStatus = True
        self.obsSite.setHighPrecision()
        self.getFW()
        self.getLocation()
        self.app.refreshModel.emit()
        self.app.refreshName.emit()
        self.getTLE()
        self.signals.deviceConnected.emit("mount")
    elif not self.mountIsUp and self.mountIsUpLastStatus:
        self.signals.deviceDisconnected.emit("mount")
        self.mountIsUpLastStatus = False

def checkMountIsUp(self) -> None:
    self.mountIsUp = False
    try:
        with socket.socket() as client:
            client.settimeout(self.SOCKET_TIMEOUT)
            client.connect(self.host)
            client.shutdown(socket.SHUT_RDWR)
            self.mountIsUp = True
    except TimeoutError:
        self.log.info("Mount connection timed out")
    except Exception as e:
        self.log.error(f"Mount {e}")
```

Benefits over the originally proposed local fix:
- Single source of truth for the rising/falling edge.
- `checkMountIsUp` no longer mixes state probing with signal side-effects.
- `startupMountData` now signature-free (the previous `mountIsUp: bool`
  parameter was redundant with `self.mountIsUp`).

---

### ✅ Bug 2 — Inconsistent default MAC format
**Status:** Fixed.

Default `__init__` argument changed from `"00.00.00.00.00.00"` (dot
separator) to `"00:00:00:00:00:00"` (standard colon separator).

---

### ✅ Bug 3 — `statTLE()` missing `mountIsUp` guard
**Status:** Fixed.

```python
def statTLE(self) -> None:
    if not self.mountIsUp:
        return
    ...
```

Now consistent with `getTLE()`, `calcTLE()`, `getModel()`, etc.

---

### ✅ Bug 4 — `startMountTimers()` did not start all timers
**Status:** Fixed (renamed).

Method renamed to `startMountCoreTimers()` to reflect its actual scope (it
intentionally omits dome/clock timers because those are configuration-driven).
A multi-line docstring explains the asymmetry with `stopAllMountTimers()`.
`mainApp.py` and the unit tests already consume the new name.

---

## ⚠️ Code Quality Issues

### ⏳ Issue 5 — Direct `lock()`/`unlock()` instead of context managers
**Status:** Pending.

Recommend wrapping the bodies of `cycle*()` methods in `try/finally` or
`QMutexLocker` so a thrown exception cannot leave a mutex locked forever.

Note: with the new `runWorker` helper (Issue 8) the mutex acquisition is
now centralised in one place; only the `clear*()` callbacks still call
`unlock()` directly. A future `try/finally` could be added inside
`runWorker` to release the mutex if `Worker(...)` ever raises before
`threadPool.start()`.

---

### ✅ Issue 6 — Magic numbers in `clearCyclePointing()`
**Status:** Fixed.

The codes `[1, 98, 99]` are now expressed in terms of the existing
`MountStatus` `IntEnum` (defined in `obsSite.py`):

```python
from mw4.mountcontrol.obsSite import MountStatus, ObsSite

class MountDevice(QObject):
    ALERT_STATUS_CODES: Final[frozenset[MountStatus]] = frozenset(
        {MountStatus.STOPPED, MountStatus.UNKNOWN, MountStatus.ERROR}
    )
    ...

    def clearCyclePointing(self, result: bool) -> None:
        if self.obsSite.status in self.ALERT_STATUS_CODES:
            ...
```

Because `MountStatus` is an `IntEnum`, the membership test stays compatible
with the integer status reported by the mount, while the code now reads
self-documenting (`STOPPED`, `UNKNOWN`, `ERROR`).

---

### ⏳ Issue 7 — Massive `__init__` method
**Status:** Pending.

Recommend extracting helpers (`initState`, `initDevices`, `initWorkers`,
`initMutexes`, `initTimers`, `connectAppSignals`).

---

### ✅ Issue 8 — Repetitive worker pattern
**Status:** Fixed.

A new helper centralises every cycle/get/poll dispatch:

```python
def runWorker(
    self,
    target: Callable[..., Any],
    clearMethod: Callable[..., Any],
    workerAttr: str,
    *args: Any,
    mutex: QMutex | None = None,
    useResult: bool = False,
    requireMountUp: bool = True,
    **kwargs: Any,
) -> None:
    if requireMountUp and not self.mountIsUp:
        return
    if mutex is not None and not mutex.tryLock():
        return
    worker = Worker(target, *args, **kwargs)
    sig = worker.signals.result if useResult else worker.signals.finished
    sig.connect(clearMethod)
    setattr(self, workerAttr, worker)
    self.threadPool.start(worker)
```

The 12 cycle/get/calcTLE/statTLE/getTLE/cycleClock/cycleDome/cyclePointing/
cycleSetting/progTrajectory/cycleCheckMountIsUp methods now reduce to one
self-documenting call apiece, e.g.:

```python
def cyclePointing(self) -> None:
    self.runWorker(
        self.obsSite.pollPointing,
        self.clearCyclePointing,
        "workerCyclePointing",
        mutex=self.mutexCyclePointing,
        useResult=True,
    )
```

This also resolves Issue 15 (the `cycle*` methods are no longer
near-duplicates).

---

## 🎯 Type-Annotation Issues

### ✅ Issue 9 — Missing / incorrect type hints on `__init__`
**Status:** Fixed.

```python
def __init__(
    self,
    app: Any,
    host: tuple[str, int] | None = None,
    MAC: str = "00:00:00:00:00:00",
    verbose: bool = False,
) -> None:
```

(The looser `app: Any` was left intentional pending introduction of an
application `Protocol`, which is out of scope for this change.)

---

### ❌ Issue 10 — `runnerProgTrajectory` parameter types incorrect
**Status:** Invalid (closed without changes).

Re-investigation showed:
- `satellite.addTrajectoryPoint` is also typed `(alt: Angle, az: Angle)`.
- Production callers in `tabSat_Track.py` pass a `skyfield` `Angle` that
  wraps a NumPy array (`Angle(degrees=np.array_split(alt, factor)[0])`),
  which is still a single `Angle` instance.
- The unit-test calls `runnerProgTrajectory([10, 20, 30], [10, 20, 30], …)`
  only because `addTrajectoryPoint` is mocked; that does not reflect real
  usage.

Therefore the existing annotation is correct.

---

## 🚀 Performance / Design Issues

### ✅ Issue 11 — `bootMount()` logic flaw
**Status:** Fixed.

Now builds `kwargs` incrementally so passing only `bAddress` (without a
port) is honored rather than silently falling back to defaults:

```python
kwargs: dict[str, Any] = {}
if bAddress:
    kwargs["ip_address"] = bAddress
if bPort:
    kwargs["port"] = bPort
wakeonlan.send_magic_packet(self.MAC, **kwargs)
```

---

### ✅ Issue 12 — Socket resource not properly cleaned in error paths
**Status:** Fixed.

`checkMountIsUp` now uses `with socket.socket() as client:` so the socket
is always released cleanly, even on `connect()` failure. The previous
`finally` block has been removed entirely.

---

### ✅ Issue 13 — `waitTimeFlip` setter has no validation
**Status:** Fixed.

```python
@waitTimeFlip.setter
def waitTimeFlip(self, value: float) -> None:
    if value < 0:
        raise ValueError("waitTimeFlip must be non-negative")
    self._waitTimeFlip = int(value * 1000)
```

A unit test (`test_waitTimeFlip_setter_rejects_negative`) verifies the
guard.

---

## 📋 Maintainability Issues

### ✅ Issue 14 — Inconsistent return types
**Status:** Fixed (documented).

The convention is now stated explicitly in the class docstring:

> - Imperative commands that can fail (``bootMount``, ``shutdown``) return
>   ``bool`` so callers can react to success/failure.
> - Scheduler / cycle / get methods communicate exclusively through Qt
>   signals and therefore return ``None``.
> - Pure computations (``calc*``) return their computed values and use
>   ``None`` to signal invalid input.

No signature changes were needed — the existing return types already match
this convention; the previous concern was lack of documentation.

---

### ✅ Issue 15 — `cycle*()` methods are nearly identical
**Status:** Fixed (via Issue 8).

All five `cycle*()` methods (plus the `get*` / TLE / trajectory variants)
now delegate to the shared `runWorker` dispatcher, eliminating the
duplication. See Issue 8 for the implementation details.

---

### ❌ Issue 16 — Worker reset asymmetry
**Status:** Closed (intentional — documented in source).

Re-investigation confirmed this is deliberate. `workerCycleClock` is the
public liveness indicator consumed by `tabMount_Sett.showOffset`, which
checks ``bool(self.app.dReg["mount"].instance.workerCycleClock)`` to colour
the PC↔mount time delta. Resetting it after each successful run lets the
GUI see when the periodic clock sync has stopped. No other worker has such
a consumer, so the asymmetry is justified.

A code comment was added inside `clearCycleClock` explaining the rationale
to deter future "consistency" refactors.

---

### ❌ Issue 17 — `pathToData` stored but unused
**Status:** Invalid (closed without changes).

`obsSite.py` reads `parent.pathToData`
(`self.pathToData = parent.pathToData`). The attribute is part of the public
parent-child contract, not dead code.

---

### ❌ Issue 18 — `loggingTrace` flag set but never used
**Status:** Invalid (closed without changes).

`geometry.py` and `connection.py` both pull this flag from the parent
(`self.loggingTrace = parent.loggingTrace`), and `loggerMW.py` toggles it on
the mount instance to enable verbose tracing. It is part of the public API.

---

## 🎨 Style / Documentation

### ✅ Issue 19 — No docstrings on any method
**Status:** Fixed (selective approach).

Per project preference, single-line docstrings have been removed because
they restated information already conveyed by the method name and signature.
Multi-line docstrings have been retained only where they add real value:

| Location                  | Reason for keeping the docstring                  |
|---------------------------|---------------------------------------------------|
| Class `MountDevice`       | Describes responsibilities and ownership graph.   |
| `startMountCoreTimers()`  | Documents why dome/clock timers are excluded.     |
| `checkMountIsUp()`        | Explains the no-side-effect probing contract.     |
| `bootMount()`             | Documents WoL parameter overrides and return.     |

This keeps the source compact while preserving the non-obvious semantics
that genuinely benefit from prose.

---

### ✅ Issue 20 — Class-level constants would benefit from `Final` typing
**Status:** Fixed.

```python
from typing import Final

CYCLE_POINTING: Final[int] = 500
CYCLE_DOME: Final[int] = 950
CYCLE_CLOCK: Final[int] = 1000
CYCLE_MOUNT_UP: Final[int] = 1000
CYCLE_SETTING: Final[int] = 3100
DEFAULT_PORT: Final[int] = 3492
SOCKET_TIMEOUT: Final[int] = 1
```

---

### ✅ Issue 21 — `MountDevice` should inherit from `QObject`
**Status:** Fixed.

`MountDevice` now inherits from `QObject` and calls `super().__init__()`.
This aligns with the rest of the Qt-based codebase (timers, mutexes, signal
container) and enables future use of Qt parent/child memory management or
`sender()` semantics if desired.

The public attribute `signals = MountSignals()` was retained to preserve
backward compatibility for callers that access `mount.signals.<signalName>`.

---

## 📊 Updated Status Summary

| Status      | Count | Items                                             |
|-------------|-------|---------------------------------------------------|
| ✅ Applied  | 16    | Bugs 1–4, Issues 6, 8, 9, 11, 12, 13, 14, 15, 19, 20, 21 |
| ❌ Invalid  | 4     | Issues 10, 16, 17, 18                             |
| ⏳ Pending  | 2     | Issues 5, 7                                       |

---

## ✅ Verification

After applying the changes:

```
ruff check src/mw4/mountcontrol/mount.py
→ All checks passed!

pytest tests/unit_tests/mountcontrol/test_mount.py
       tests/unit_tests/mountcontrol/test_mountSignals.py
       tests/unit_tests/base/test_deviceRegistry.py
       tests/unit_tests/gui/mainWaddon/test_tabMount_Sett.py
       tests/unit_tests/gui/extWindows/setting/test_tabSettMount.py
→ 298 passed
```

---

## 🛣️ Next Steps (Recommended Order)

Only two items remain:

1. **Mutex safety** — Issue 5 (wrap the body of `runWorker` in
   `try/finally` so a thrown `Worker(...)` constructor cannot leave a
   mutex locked).
2. **`__init__` decomposition** — Issue 7 (extract `initState`,
   `initDevices`, `initWorkers`, `initMutexes`, `initTimers`,
   `connectAppSignals`).

Each step must be accompanied by:
- Updated unit tests (maintain 100 % coverage).
- `ruff check` + `ruff format` clean.
- Full test-suite run.

