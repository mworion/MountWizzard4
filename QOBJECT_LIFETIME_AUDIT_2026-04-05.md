# QObject Lifetime & Pending-Events Audit – MountWizzard4

**Date:** 2026-04-05  
**Scope:** `src/mw4/**/*.py`  
**Relation to crash:** follow-up to `CRASH_ANALYSIS_2026-04-05.md`

---

## Executive Summary

The audit found **four confirmed critical issues** and **three medium issues** related
to QObject lifetime and/or illegal `processEvents()` calls from worker threads.
Taken together they explain why the SIGSEGV class documented in
`CRASH_ANALYSIS.md` / `CRASH_ANALYSIS_2026-04-05.md` persists even after the
`tpool.py` fix.

---

## 1. 🔴 CRITICAL – `sleepAndEvents()` called from QThreadPool Worker Threads

`sleepAndEvents()` (defined in `toolsQtWidget.py:59`) calls
`QCoreApplication.processEvents()` in a tight loop. This is the **same class of
violation** as the `tpool.py` bug fixed earlier. It appears in **four separate
worker-thread code paths**:

### 1-A  `plateSolve.py:138-146` — `workerSolveLoop`

```python
# plateSolve.py
def workerSolveLoop(self) -> None:          # ← executed as Worker in QThreadPool
    while self.solveLoopRunning:
        if self.solveQueue.empty():
            sleepAndEvents(500)             # ← processEvents() from worker thread!
            continue
        ...

def startSolveLoop(self) -> None:
    self.worker = Worker(self.workerSolveLoop)
    self.threadPool.start(self.worker)      # ← sends workerSolveLoop to thread pool
```

`workerSolveLoop` runs continuously in a thread pool thread for the entire lifetime
of the plate-solve connection. Every 500 ms it calls `processEvents()` from the
wrong thread.

### 1-B  `camera.py:184-216` — five `wait*` methods (called from `workerExpose`)

```python
# camera.py
def waitExposed(self, ...):
    while ...: sleepAndEvents(100)     # ← in worker thread

def waitStart(self):
    while ...: sleepAndEvents(100)     # ← in worker thread

def waitDownload(self):
    while ...: sleepAndEvents(100)     # ← in worker thread

def waitSave(self):
    while ...: sleepAndEvents(100)     # ← in worker thread

def waitFinish(self, ...):
    while ...: sleepAndEvents(100)     # ← in worker thread
```

All five methods are called from `workerExpose()` in every camera backend:

| File | Worker entry-point |
|------|--------------------|
| `cameraSGPro.py:80` | `workerExpose()` |
| `cameraAlpaca.py:78` | `workerExpose()` |
| `cameraAlpacaNew.py:78` | `workerExpose()` |
| `cameraAscom.py:78` | `workerExpose()` |
| `cameraNINA.py:82` | `workerExpose()` |

Example call chain (`cameraAlpaca.py`):

```python
def workerExpose(self) -> None:          # ← runs in QThreadPool worker
    ...
    self.parent.waitExposed(...)         # → sleepAndEvents(100) loop
    ...
    data = self.parent.retrieveImage(...)
    ...
# called by:
def expose(self) -> None:
    self.worker = Worker(self.workerExpose)
    self.threadPool.start(self.worker)
```

### 1-C  `ascomClass.py:137-155` — `workerConnectDevice`

```python
def workerConnectDevice(self) -> None:   # ← called via Worker(self.callerInitUnInit, ...)
    for retry in range(0, 10):
        ...
        sleepAndEvents(250)              # ← processEvents() from worker thread!

# called by:
self.workerConnect = Worker(self.callerInitUnInit, self.workerConnectDevice)
self.threadPool.start(self.workerConnect)
```

### 1-D  `alpacaClass.py:261-278` — `workerConnectDevice`

```python
def workerConnectDevice(self) -> None:   # ← runs as Worker
    for retry in range(0, 10):
        ...
        sleepAndEvents(250)              # ← processEvents() from worker thread!

# called by:
self.workerConnect = Worker(self.workerConnectDevice)
self.threadPool.start(self.workerConnect)
```

**Why this causes the crash:**  
`processEvents()` from a non-main thread dispatches queued events on the wrong
thread, corrupting the Qt event-dispatch state. Shiboken's `cppPointer()` then
dereferences a stale/corrupted pointer → `SIGSEGV` / PAC failure on Apple Silicon.

**Fix for all 1-A … 1-D:**  
Replace the busy-wait with a thread-safe alternative that does **not** call
`processEvents()`. Options:
- Use `QThread::msleep()` / Python `time.sleep()` for pure delay.
- For polling loops that need to communicate progress to the UI, emit a signal
  instead of calling `processEvents()`.

```python
# BEFORE (broken):
def waitExposed(self, exposureTime, func):
    while self.exposing and func():
        sleepAndEvents(100)
        ...

# AFTER (correct):
import time
def waitExposed(self, exposureTime, func):
    while self.exposing and func():
        time.sleep(0.1)           # plain sleep – no event processing
        self.signals.message.emit(...)  # signal is thread-safe
        ...
```

---

## 2. 🔴 CRITICAL – `WA_DeleteOnClose` + Queued Signals → Dangling C++ Pointer

### Where it is set

`MWidget.__init__` (`toolsQtWidget.py:151`) sets `WA_DeleteOnClose` on **every**
window subclass in the application:

```python
class MWidget(QWidget, Styles):
    def __init__(self):
        super().__init__()
        ...
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)  # line 151
```

All external windows (`HemisphereWindow`, `ImageWindow`, `SimulatorWindow`,
`DownloadPopup`, `UploadPopup`, …) inherit this attribute.

### What `WA_DeleteOnClose` does

When `close()` is called on a widget with this attribute, Qt processes the close
event synchronously and then calls `widget->deleteLater()`. On the next event-loop
cycle, the **C++ `QWidget` object is destroyed** while the Python wrapper may still
be referenced.

### The race condition

**`DownloadPopup` / `UploadPopup`:**

```
Worker thread emits:
  result signal  →  (queued)  →  closePopup()
  finished signal →  (queued)  →  procSourceData()   ← or finishLoadFinals...
```

`closePopup()` calls `sleepAndEvents(500)` then `self.close()`.
During the `sleepAndEvents(500)` wait, Qt processes events – including the delivery
of the `finished` signal. After `self.close()`, Qt schedules the C++ widget for
deletion. Any events still queued for that widget will be delivered to a
destroyed C++ object → `cppPointer()` crash.

Affected signal connections:
- `astroObjects.py:112`: `self.downloadPopup.worker.signals.finished.connect(self.procSourceData)`
- `tabTools_IERSTime.py:120`: `self.downloadPopup.worker.signals.finished.connect(...)`
- `tabTools_IERSTime.py:91`: `self.uploadPopup.workerStatus.signals.finished.connect(...)`

**External window toggling (`externalWindows.py:176`):**

```python
def toggleWindow(self, windowName) -> None:
    if not self.uiWindows[windowName]["classObj"]:
        self.buildWindow(windowName)
    else:
        self.uiWindows[windowName]["classObj"].close()   # WA_DeleteOnClose → schedules deletion
```

Meanwhile, cyclic signals (e.g., `update1s`, `update10s`) connected to methods on
that window may still be in the queue when the C++ object is deleted.

`deleteWindowResource` nulls out `classObj` only after the `destroyed` signal,
but between `close()` and `destroyed`, posted events are still being processed.

**Fix:**

Option A – Remove `WA_DeleteOnClose` from `MWidget` and use explicit lifetime
management (`deleteLater()` only after confirming no pending events).

Option B – Disconnect all signals to a window *before* calling `close()`:

```python
def toggleWindow(self, windowName) -> None:
    obj = self.uiWindows[windowName]["classObj"]
    if obj is None:
        self.buildWindow(windowName)
    else:
        # disconnect all app signals before closing
        try:
            self.app.update1s.disconnect(obj)
        except RuntimeError:
            pass
        obj.close()
```

Option C – Use `hide()` + deferred `deleteLater()` instead of relying on
`WA_DeleteOnClose`, and clear the `classObj` reference immediately in `close()`.

---

## 3. 🔴 HIGH – `MouseClickEventFilter` Python Wrapper GC vs C++ Lifetime

### The code (`toolsQtWidget.py:121-137`)

```python
def clickable(widget: QWidget) -> SignalInstance:

    class MouseClickEventFilter(QObject):
        clicked = Signal(object)
        def eventFilter(self, obj, event):    # ← virtual override
            ...

    clickEventFilter = MouseClickEventFilter(widget)   # widget = C++ parent
    widget.installEventFilter(clickEventFilter)
    return clickEventFilter.clicked                    # ← Python var goes out of scope!
```

After `clickable()` returns:
- The local variable `clickEventFilter` is destroyed (Python refcount drops to 0).
- The C++ object survives because Qt holds a parent-child reference from `widget`.
- **Shiboken's binding manager may lose the Python-side wrapper.**

When Qt delivers a mouse event and calls `clickEventFilter->eventFilter()`, the
C++ virtual dispatch mechanism (via `Sbk_GetPyOverride → getOverride →
PyObject_GetAttr → cppPointer`) tries to find the Python wrapper in Shiboken's
registry. If the Python wrapper was garbage-collected, `cppPointer()` returns
a stale pointer → **crash with the exact stack seen in the reports**.

### Where `clickable()` is called (16 sites)

```
tabPower.py:77,81           tabImage_Manage.py:31-46
tabMount_Move.py:98,99      tabEnviron_Seeing.py:41
tabMount_Sett.py:44-57      (and more)
```

These are all long-lived main-window addons, so the risk is real and ongoing.

**Fix:**  
Store the event filter as an instance attribute of the enclosing widget to prevent
Python GC:

```python
def clickable(widget: QWidget) -> SignalInstance:

    class MouseClickEventFilter(QObject):
        clicked = Signal(object)
        def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.MouseButtonRelease:
                if obj.rect().contains(event.pos()):
                    self.clicked.emit(widget)
                return True
            return False

    clickEventFilter = MouseClickEventFilter(widget)
    widget.installEventFilter(clickEventFilter)
    # Keep a Python reference on the widget to prevent GC:
    if not hasattr(widget, '_clickFilters'):
        widget._clickFilters = []
    widget._clickFilters.append(clickEventFilter)
    return clickEventFilter.clicked
```

---

## 4. 🟡 MEDIUM – `Worker` / `QRunnable` autoDelete vs Python Reference

### The issue (`tpool.py:35-47`)

```python
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        ...
        self.signals = WorkerSignals()  # ← no parent
```

`QRunnable` has `autoDelete() == True` by default. After `run()` completes, the
Qt thread pool calls `delete` on the C++ `QRunnable` object. Meanwhile Python still
holds a reference via `self.worker = Worker(...)`. The Python wrapper now wraps a
freed C++ object.

If code accesses `self.worker.signals` after the worker has finished (e.g., to
check or reconnect), the `Worker` Python object is still alive but its C++ part
is deleted.

Additionally, `WorkerSignals` is created without a parent. Its lifetime is tied
only to the Python reference chain. If the Python `Worker` wrapper is still alive
but its C++ counterpart was deleted, any emission from `WorkerSignals` into a
connected slot will go through a partially-invalid object graph.

**Fix:**  
Disable autoDelete explicitly:

```python
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.setAutoDelete(False)   # ← Python manages lifetime
        ...
```

This ensures the C++ object is never deleted while Python holds a reference.

---

## 5. 🟡 MEDIUM – Stale Signal Connections to Short-Lived Popup Objects

### `astroObjects.py:109-112`

```python
def runDownloadPopup(self, url, unzip) -> None:
    self.downloadPopup = DownloadPopup(self.window, url, self.dest, unzip)
    self.downloadPopup.show()
    self.downloadPopup.downloadFile()
    self.downloadPopup.worker.signals.finished.connect(self.procSourceData)
```

Each time `runDownloadPopup` is called, a new `DownloadPopup` is created and
`self.downloadPopup` is overwritten. The old popup object may still be referenced
by its own worker signal. If the old worker's `finished` fires after the popup was
replaced, `self.downloadPopup` now points to the *new* popup, but
`self.procSourceData` reads `self.downloadPopup.returnValues["success"]` — which
belongs to the new, not the completed, popup.

Same pattern in `tabTools_IERSTime.py:89-92` and `tabTools_IERSTime.py:118-121`.

**Fix:** Disconnect previous connections before reassigning:

```python
def runDownloadPopup(self, url, unzip) -> None:
    if self.downloadPopup is not None:
        try:
            self.downloadPopup.worker.signals.finished.disconnect(self.procSourceData)
        except RuntimeError:
            pass
    self.downloadPopup = DownloadPopup(self.window, url, self.dest, unzip)
    ...
    self.downloadPopup.worker.signals.finished.connect(self.procSourceData)
```

---

## 6. 🟡 MEDIUM – `indiClass.py:324` — `sleepAndEvents` in `discoverDevices`

```python
def discoverDevices(self, deviceType: str) -> list:
    ...
    self.client.connectServer()
    sleepAndEvents(2000)                   # ← 2-second processEvents loop
    self.client.signals.defText.disconnect(self.addDiscoveredDevice)
    self.client.disconnectServer()
    return self.discoverList
```

Currently `discoverDevices` is called from `devicePopupW.discoverDevices()` which
is triggered by a button click (main thread). The `sleepAndEvents(2000)` call is
therefore legal **today**. However, if this method is ever refactored to run in a
worker (a common pattern in this codebase), it will immediately become a critical
violation. Recommend replacing with a pure `time.sleep(2)` or an event-driven
approach.

---

## 7. Prioritised Fix Plan

| # | Severity | File | Change |
|---|----------|------|--------|
| 1-A | 🔴 | `plateSolve.py:142` | Replace `sleepAndEvents(500)` with `time.sleep(0.5)` |
| 1-B | 🔴 | `camera.py:184-216` | Replace `sleepAndEvents(100)` with `time.sleep(0.1)` in all `wait*` methods |
| 1-C | 🔴 | `ascomClass.py:153` | Replace `sleepAndEvents(250)` with `time.sleep(0.25)` |
| 1-D | 🔴 | `alpacaClass.py:278` | Replace `sleepAndEvents(250)` with `time.sleep(0.25)` |
| 2 | 🔴 | `toolsQtWidget.py:151` | Remove `WA_DeleteOnClose` from `MWidget`; add explicit disconnect-before-close |
| 3 | 🔴 | `toolsQtWidget.py:135` | Store `clickEventFilter` in `widget._clickFilters` list |
| 4 | 🟡 | `tpool.py:41` | `self.setAutoDelete(False)` in `Worker.__init__` |
| 5 | 🟡 | `astroObjects.py:109`, `tabTools_IERSTime.py:89,118` | Disconnect old popup signal before reassigning |
| 6 | 🟡 | `indiClass.py:324` | Replace `sleepAndEvents(2000)` with `time.sleep(2.0)` |

---

## 8. Notes on Main-Thread `sleepAndEvents` Usage

The following `sleepAndEvents` call sites are on the **main thread** and are
therefore technically legal (though they create UI re-entrancy risks):

| File | Line | Context |
|------|------|---------|
| `modelRun.py:225,329` | `runBatch` → `runModel` (button click, main thread) |
| `tabMount_Move.py:156` | Button click handler |
| `tabModel.py:202` | Button click handler |
| `tabSett_Misc.py:237` | Button click handler |
| `externalWindows.py:187` | `waitCloseExtendedWindows` (main thread shutdown) |
| `videoBase.py:145` | `restartVideo` (main thread button click) |
| `downloadPopupW.py:135` | `closePopup` called via queued signal → main thread |
| `uploadPopupW.py:210,216` | `closePopup` called via queued signal → main thread |
| `splashScreen.py:53,70` | Startup sequence, main thread |
| `gPlotBase.py:163` | Plot rendering, main thread |
| `tabTools_Rename.py:152` | File rename loop, main thread |

These are NOT the crash source but they do create **UI re-entrancy**: while waiting
in `sleepAndEvents`, timer callbacks (`cyclePointing`, `cycleSetting`, etc.) fire,
potentially starting new worker threads that make the thread-safety violations in
§1 above even more likely to race.

---

## 9. Crash Causality Chain (Connecting Issues to the Observed Crash)

```
User action: opens plate-solve or starts camera exposure
  → startSolveLoop() / expose() starts a Worker in QThreadPool
  → Worker runs workerSolveLoop / workerExpose
  → Inside worker: sleepAndEvents() calls QCoreApplication::processEvents()
  → Qt event loop dispatches queued events ON THE WRONG THREAD
  → One of those events targets a QObject (possibly a closing MWidget
    with WA_DeleteOnClose, or a MouseClickEventFilter whose Python wrapper
    was GC'd)
  → Shiboken: QObjectWrapper::event() → Sbk_GetPyOverride()
    → BindingManager::getOverride() → PyObject_GetAttr
    → Sbk_QObject_getattro() → cppPointer()
    → C++ pointer is garbage (freed, or PAC-corrupted)
    → EXC_BAD_ACCESS (SIGSEGV) / KERN_INVALID_ADDRESS
```

This is the **identical stack** seen in all crash reports.

---

## 10. Conclusion

The SIGSEGV crash class will persist as long as any of issues **1-A through 1-D**
remain. They represent `processEvents()` calls on non-main threads — the same
root cause as the already-fixed `tpool.py` bug, simply appearing in different
locations. Issues **2** and **3** are independent crash paths that can trigger the
same SIGSEGV even if §1 is fully resolved.

**Recommended fix order:**
1. Replace `sleepAndEvents` with `time.sleep` in all worker-thread code paths
   (1-A → 1-D). This is a mechanical one-line change per site.
2. Fix `clickable()` to keep a Python reference to the event filter (§3).
3. Decide on a window lifecycle strategy to handle `WA_DeleteOnClose` + pending
   events (§2).
4. Set `autoDelete(False)` on all Workers (§4).

