# Crash Analysis – 2026-04-05 (Mac16,11)

**Date:** 2026-04-05
**System:** macOS 26.4 (25E246), Apple Silicon (arm64, Mac16,11)
**Python:** 3.13 | **PySide6/Qt:** 6.11.0 | **shiboken6:** 6.11.0
**Process:** python3.13 [62647] | **Parent:** pycharm [62143]

---

## TL;DR

**Same root cause as documented in `CRASH_ANALYSIS.md` (2026-04-04), new machine.**
`EXC_BAD_ACCESS (SIGSEGV)` with `KERN_INVALID_ADDRESS` inside the Shiboken/PySide6
binding layer. A C++ `QObject` is being accessed after its memory has been corrupted
or freed — ARM64 PAC hardware detects the mangled pointer and raises the fault.

---

## 1. Key Differences vs. Yesterday's Report (Apr 4)

| | Apr 4 | Apr 5 (this report) |
|---|---|---|
| **Machine** | Mac15,8 | **Mac16,11** (newer, M4-class) |
| **PID** | (various) | 62647 |
| **Stack trace** | identical | identical |
| **Crash address** | various | `0xf971db9d8693e064` |
| **macOS** | 26.4 (25E246) | 26.4 (25E246) |

---

## 2. Original Crash Report Header

```
Process:             python3.13 [62647]
Path:                /Volumes/VOLUME/*/python
Identifier:          python3.13
Code Type:           ARM-64 (Native)
Role:                Foreground
Parent Process:      pycharm [62143]

Date/Time:           2026-04-05 22:09:12.5914 +0200
Launch Time:         2026-04-05 22:09:09.8538 +0200
Hardware Model:      Mac16,11
OS Version:          macOS 26.4 (25E246)

Exception Type:    EXC_BAD_ACCESS (SIGSEGV)
Exception Subtype: KERN_INVALID_ADDRESS at 0xf971db9d8693e064
Termination Reason:  Namespace SIGNAL, Code 11, Segmentation fault: 11
```

---

## 3. Stack Trace Decoded

### Faulting Thread (Main Thread / Qt Event Loop):

```
Frame 0  libshiboken6.abi3.6.11  Shiboken::Conversions::cppPointer()   ← CRASH HERE
Frame 1  QtCore.abi3.so           Sbk_QObject_getattro()
Frame 2  libpython3.13            PyObject_GetAttr
Frame 3  libshiboken6             Shiboken::BindingManager::getOverride()
Frame 4  libshiboken6             Sbk_GetPyOverride()
Frame 5  QtCore.abi3.so           QObjectWrapper::event()
Frame 6  QtWidgets                QApplicationPrivate::notify_helper()
Frame 7  QtWidgets                QApplication::notify()
Frame 8  QtWidgets.abi3.so        QApplicationWrapper::notify()
Frame 9  QtCore                   QCoreApplication::sendEvent()
Frame 10 QtCore                   QCoreApplicationPrivate::sendPostedEvents()   ← entry point
Frame 11 libqcocoa.dylib          (Cocoa platform plugin)
...
Frame 13 CoreFoundation           __CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE0_PERFORM_FUNCTION__
...
Frame 24 AppKit                   -[NSApplication nextEventMatchingMask:...]
```

### What this sequence means

1. **`sendPostedEvents()`** — Qt is draining its *deferred* event queue (events that
   were posted earlier with `QCoreApplication::postEvent()`).
2. **`QObjectWrapper::event()`** — the C++ Qt event dispatcher looks for a Python
   override of `event()` on the target object.
3. **`Sbk_GetPyOverride → getOverride → PyObject_GetAttr`** — Shiboken looks up the
   Python method on the wrapped Python/C++ object.
4. **`Sbk_QObject_getattro → cppPointer()`** — Shiboken dereferences the internal
   C++ pointer stored in the `SbkObject`. **This pointer is garbage → CRASH.**

### Why the pointer is garbage

The crash address `0xf971db9d8693e064` is **not in any VM region** (confirmed by
"UNUSED SPACE AT START / UNUSED SPACE AT END"). On **Apple Silicon (arm64)** the OS
uses **Pointer Authentication Codes (PAC)**: the high bits of a valid pointer carry a
cryptographic signature. When Shiboken tries to dereference a corrupted/freed pointer,
the hardware detects the invalid PAC and raises `EXC_BAD_ACCESS`.

**Root pattern:** a `QObject`-subclass C++ object was destroyed (either by Qt's
parent-child ownership or by Python garbage collection), but Qt still had *posted events*
queued for it. When the event loop drained those events, Shiboken found a dangling
pointer.

---

## 4. Current State of Fixes

### ✅ Already fixed: `tpool.py` – `QApplication.processEvents()` in worker

`tpool.py` no longer contains a `processEvents()` call in `Worker.run()`.
The CRASH_ANALYSIS.md from Apr 4 documented this as the primary cause; it is
already resolved in the current codebase.

### ❌ Still open: `geometry.py` – shared mutable state written from worker thread

Lines 422–435 still write `self.transMatrix` and `self.transVector` without any lock:

```python
# geometry.py  lines 422–435
self.transMatrix = [T0, T1, T2, T3, T4, T5, T6, T7, T8, T9]
self.transVector = [P0[:-1], P1[:-1], P2[:-1], P3[:-1],
                    P4[:-1], P5[:-1], P6[:-1], P7[:-1],
                    P8[:-1], P9[:-1], P10[:-1]]
```

If any worker thread calls `calcTransformationMatrices()` while the main thread
reads these lists (e.g., for 3-D animation or dome correction), the Python list
objects can be in a partially-constructed state, causing memory corruption upstream.

### ❌ Still open: `obsSite.py` – properties read/written across threads

Mount pointing properties (`raJNow`, `decJNow`, `haJNow`, …) are written from a
worker thread (`pollPointing`) and read from the main thread without synchronisation.

### ⚠️ Possible new contributor: PySide6 6.11 + Python 3.13 on M4

`Mac16,11` is a next-generation Apple Silicon Mac. PySide6 6.11 + Python 3.13 on M4
hardware is a very fresh combination. Any latent thread-safety issue that previously
manifested rarely can be exposed more aggressively on hardware with higher IPC and
stricter PAC enforcement.

---

## 5. Why the Crash Still Happens After the `tpool.py` Fix

The `processEvents()` removal was the *most likely* trigger, but it was not the
*only* path to this crash. The underlying pattern — **Qt delivering posted events to
an object whose C++ memory has been corrupted by a concurrent write** — can also
arise from:

| Trigger | File | Status |
|---------|------|--------|
| `processEvents()` in worker thread | `tpool.py:72` | ✅ Fixed |
| Race on `transMatrix`/`transVector` | `geometry.py:422` | ❌ Open |
| Race on mount pointing properties | `obsSite.py` | ❌ Open |
| GC collecting a QObject with pending events | any | ❌ Not audited |

---

## 6. Recommended Next Actions (prioritised)

### 🔴 Priority 1 — Protect `geometry.py` shared state

Convert `calcTransformationMatrices()` to return values instead of storing them,
or protect the assignment with `QMutex`:

```python
# src/mw4/mountcontrol/geometry.py
from PySide6.QtCore import QMutex, QMutexLocker

class Geometry:
    def __init__(self, parent):
        # ...existing code...
        self._geomMutex = QMutex()

    def calcTransformationMatrices(self, ha, dec, lat, pierside="W"):
        # ...existing calculation...
        with QMutexLocker(self._geomMutex):
            self.transMatrix = [T0, T1, T2, T3, T4, T5, T6, T7, T8, T9]
            self.transVector = [P0[:-1], P1[:-1], P2[:-1], P3[:-1],
                                P4[:-1], P5[:-1], P6[:-1], P7[:-1],
                                P8[:-1], P9[:-1], P10[:-1]]
        return altDome, azDome, intersect, PB, PD
```

Also protect all *read* sites of `self.transMatrix`/`self.transVector` with the
same mutex.

### 🔴 Priority 2 — Protect `obsSite.py` pointing properties

Use a `threading.Lock` or `QMutex` around the properties that are written from
a worker and read from the main thread.

### 🟡 Priority 3 — Enable `faulthandler` for better crash diagnostics

Add to `loader.py` `main()`:

```python
import faulthandler
faulthandler.enable()   # prints Python traceback on SIGSEGV to stderr
```

### 🟡 Priority 4 — Audit QObject lifetime + pending events

Search for patterns where a `QObject` may be destroyed (`deleteLater`, out-of-scope,
or Python GC) while events are still queued. In PySide6, always keep a Python
reference to long-lived QObjects, or call `obj.deleteLater()` instead of letting
Python GC them.

### 🟢 Priority 5 — Verify pyqtgraph compatibility

`pyqtgraph==0.14.0` has known issues with PySide6 ≥ 6.7. Upgrade to ≥ 0.14.1.

---

## 7. Summary

This is a **repeat of the same SIGSEGV class** documented on 2026-04-04, now
observed on a different (newer) machine (Mac16,11). The immediate trigger in
`tpool.py` is already fixed, but the **underlying race conditions on shared C++
state** (`geometry.py`, `obsSite.py`) remain open and are sufficient to reproduce
the crash independently — especially on newer M4 hardware with higher IPC and
stricter PAC enforcement that makes previously rare races hit more frequently.

**Address Priorities 1 and 2 to eliminate the remaining paths to this crash class.**

