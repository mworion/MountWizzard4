# Plan: `alpacaClass.py` — Single-Loop Architecture (in-place edit)

Replace the timer-driven multi-worker design of `AlpacaClass` with a
single `threading.Event`-controlled loop worker that unifies connection
management, polling, and `queue.Queue`-based command dispatch — without
any `QTimer` instances and without multiple worker objects.

> **Scope**: The existing file `src/mw4/base/alpacaClass.py` is edited
> in-place. The class name remains `AlpacaClass`. No new file is
> created. All subclasses already import from `alpacaClass` — their
> imports require no change.

**Change history**
| Date | Change |
|------|--------|
| 2026-05-05 | Initial plan |
| 2026-05-05 | `self.propertyExceptions` removed entirely; `NotImplementedException` is only logged, polling continues |
| 2026-05-05 | `device is None` guards removed from `getDeviceProp`, `setDeviceProp`, `callDeviceMethod` — device is guaranteed to exist once the loop runs |
| 2026-05-05 | `CONNECTION_RETRY_DELAY` constant removed — `self.updateRate / 1000` is used uniformly for both the poll cycle and the connection-retry wait |
| 2026-05-05 | Added `DomeAlpaca` migration plan as a concrete subclass example |
| 2026-05-05 | Translated to English |
| 2026-05-05 | Clarified `getAndStoreDeviceProp` is not queue-routed; applied it to `Azimuth` in `DomeAlpaca.pollData`; kept `getDeviceProp` for `ShutterStatus` branching logic |
| 2026-05-05 | Added `callDeviceMethodSync` for synchronous direct device-method calls needed in `pollData` workflows; added all remaining device class migrations; moved local constants to class variables |
| 2026-05-05 | Changed target from new file `alpacaClassNew.py` to in-place edit of `alpacaClass.py`; class name stays `AlpacaClass`; subclass imports unchanged |

---

## Part 1 – `alpacaClass.py`

### Step 1 – Edit `src/mw4/base/alpacaClass.py`

Edit the existing file in-place. Remove the `QTimer` import. Add new
imports:

```python
import queue
import threading
import time
from dataclasses import dataclass, field
from alpaca.camera import Camera as AlpycaCamera
from alpaca.covercalibrator import CoverCalibrator as AlpycaCoverCalibrator
from alpaca.dome import Dome as AlpycaDome
from alpaca.exceptions import NotImplementedException as AlpycaNotImplError
from alpaca.filterwheel import FilterWheel as AlpycaFilterWheel
from alpaca.focuser import Focuser as AlpycaFocuser
from alpaca.observingconditions import ObservingConditions as AlpycaObsConditions
from alpaca.switch import Switch as AlpycaSwitch
from alpaca.telescope import Telescope as AlpycaTelescope
import alpaca.management as alpacaMgmt
from mw4.base.driverDataClass import DriverData
from mw4.base.tpool import Worker
from typing import Any
```

**Remove**: `from PySide6.QtCore import QTimer` (and any other
`QTimer`-only imports no longer needed).

Class: `AlpacaClass(DriverData)` — class name unchanged.

> No module-level constant needed — the retry wait on a failed
> connection attempt uses `self.updateRate / 1000`, identical to the
> poll cycle time.

---

### Step 2 – `__init__` — remove timers, add loop primitives

**Keep** (existing attributes):
- `host`, `port`, `hostaddress`, `protocol`, `apiVersion`
- `deviceName`, `deviceType`, `number`, `device`
- `updateRate`, `loadConfig`
- `defaultConfig`, `signals`, `msg`, `threadPool`, `data`
- `deviceConnected`, `serverConnected`

**Remove**:
- All `QTimer` instances (`cycleDevice`, `cycleData`)
- All per-task worker attributes
  (`workerGetConfig`, `workerStatus`, `workerData`, `workerConnect`)
- `self.propertyExceptions` — removed entirely

**Add**:
```python
self.commandQueue: queue.Queue = queue.Queue()
self.stopEvent: threading.Event = threading.Event()
self.workerCommunicationLoop: Worker | None = None
```

---

### Step 3 – `CommandItem` dataclass (module level)

Defined before the class definition:

```python
@dataclass
class CommandItem:
    cmdType: str          # "call" | "set"
    name: str             # method or attribute name
    kwargs: dict = field(default_factory=dict)
    value: Any = None     # only used for cmdType="set"
```

---

### Step 4 – Carry over and simplify methods

The following methods are carried over from `AlpacaClass` with
adjustments (no `propertyExceptions` references, no `device is None`
guard):

| Method | Change |
|--------|--------|
| `host` (property) | unchanged |
| `hostaddress` (property) | unchanged |
| `port` (property) | unchanged |
| `deviceName` (property) | unchanged |
| `createAlpacaDevice()` | unchanged |
| `getDeviceProp(attr)` | remove `device is None` guard and `propertyExceptions` guard; log `AlpycaNotImplError` only |
| `setDeviceProp(attr, value)` | remove `device is None` guard and `propertyExceptions` guard; log `AlpycaNotImplError` only |
| `getAndStoreDeviceProp(attr, element)` | unchanged — **not** routed through the command queue (see note below) |
| `discoverAPIVersion()` | unchanged |
| `discoverAlpacaDevices()` | unchanged |
| `discoverDevices(deviceType)` | unchanged |

> **Rationale for removing guards**: `createAlpacaDevice()` is called
> in `startCommunication()` **before** the loop starts. If it fails the
> loop never starts, so `self.device` is guaranteed to be a valid object
> for the entire loop lifetime. `self.device` is never reset to `None`.
> The architecture requirement *"the loop handles device connected, we
> can omit the self.deviceConnected guard"* applies equally to the
> `device is None` guard.

> **`getAndStoreDeviceProp` and the queue**: `getAndStoreDeviceProp` is
> a **read** helper — it calls `getDeviceProp` and stores the result in
> `self.data`. It is only ever called from within the worker loop thread
> (inside `pollData` and `getInitialConfig`), so it runs on the correct
> thread already. Routing it through the command queue would be wrong:
> the queue exists exclusively for **outbound write/call commands**
> originating from the GUI thread.

**New `getDeviceProp` signature:**
```python
def getDeviceProp(self, attr: str) -> Any:
    try:
        return getattr(self.device, attr)
    except AlpycaNotImplError:
        self.log.warning(f"[{self.deviceName}] [{attr}] not implemented")
        return None
    except Exception as e:
        self.log.error(
            f"[{self.deviceName}] get [{attr}] exception: [{e}]"
        )
        return None
```

**New `setDeviceProp` signature:**
```python
def setDeviceProp(self, attr: str, value: Any) -> bool:
    try:
        setattr(self.device, attr, value)
        return True
    except AlpycaNotImplError:
        self.log.warning(f"[{self.deviceName}] [{attr}] not implemented")
        return False
    except Exception as e:
        self.log.error(
            f"[{self.deviceName}] set [{attr}] exception: [{e}]"
        )
        return False
```

---

### Step 5 – `callDeviceMethod` — enqueue instead of direct call

**Signature**: `callDeviceMethod(self, method: str, **kwargs: Any) -> None`

- **Remove**: `self.deviceConnected` guard
- **Remove**: `device is None` guard
- **Remove**: `propertyExceptions` guard
- **Remove**: direct `getattr(self.device, method)(**kwargs)` call
- **Add**: place `CommandItem` on `self.commandQueue`:
  ```python
  self.commandQueue.put(
      CommandItem(cmdType="call", name=method, kwargs=kwargs)
  )
  ```

> ⚠️ **Breaking change**: return type changes from `Any` to `None`.
> All existing callers in subclasses are fire-and-forget and are
> unaffected by this change.
>
> **Exception** — two subclasses require synchronous return values:
> `PegasusUPBAlpaca.pollData` reads switch states via methods (e.g.
> `GetSwitch(Id=0)`), and `CameraAlpaca.workerExpose` must call
> `StartExposure` before waiting for the image. Both run on a worker
> thread and must use `callDeviceMethodSync` instead (see Step 5b).

---

### Step 5b – `callDeviceMethodSync` — direct synchronous device call

New method for callers that **already run on a worker thread** and need
the return value of a device method:

```python
def callDeviceMethodSync(self, method: str, **kwargs: Any) -> Any:
    try:
        return getattr(self.device, method)(**kwargs)
    except AlpycaNotImplError:
        self.log.warning(
            f"[{self.deviceName}] [{method}] not implemented"
        )
        return None
    except Exception as e:
        self.log.error(
            f"[{self.deviceName}] call [{method}] exception: [{e}]"
        )
        return None
```

| Use case | Method |
|----------|--------|
| Fire-and-forget GUI command (AbortSlew, OpenShutter, …) | `callDeviceMethod` (enqueue) |
| Synchronous read via method (GetSwitch, GetSwitchValue) | `callDeviceMethodSync` |
| Synchronous workflow step (StartExposure before wait) | `callDeviceMethodSync` |

---

### Step 6 – `connectDevice()` — connection attempt helper

New helper method (no leading underscore per project convention):

```python
def connectDevice(self) -> bool:
```

- Loop 0–9: `setDeviceProp("Connected", True)` →
  `getDeviceProp("Connected")` → break on success,
  `time.sleep(0.2)` on retry
- Returns `True` on success, `False` when all retries exhausted
- Emits `self.msg(2, "ALPACA", "Connect error", ...)` on failure

---

### Step 7 – `getInitialConfig()` — direct call inside the loop

Replaces both `workerGetInitialConfig` and `getInitialConfig`.
Called directly **inside the loop** (already on the worker thread):

```python
def getInitialConfig(self) -> None:
    self.data["DRIVER_INFO.DRIVER_NAME"] = self.getDeviceProp("Name")
    self.data["DRIVER_INFO.DRIVER_VERSION"] = (
        self.getDeviceProp("DriverVersion")
    )
    self.data["DRIVER_INFO.DRIVER_EXEC"] = self.getDeviceProp("DriverInfo")
```

Subclasses override this method and call `super().getInitialConfig()`
as the first step.

---

### Step 8 – `pollData()` — overrideable polling hook

Replaces `workerPollData`. Empty base implementation (`pass`). Called
directly in the loop without an additional worker.

> **Subclass migration note**: rename `workerPollData` → `pollData`.
> `processPolledData` is removed from the base class; any post-processing
> must be placed at the end of the subclass `pollData()` override.

---

### Step 9 – `processCommandQueue()` — drain queue inside the loop

```python
def processCommandQueue(self) -> None:
```

Drains the entire queue with `get_nowait()` in a
`while not self.commandQueue.empty()` loop. For each `CommandItem`:

- `cmdType == "call"`: call
  `getattr(self.device, cmd.name)(**cmd.kwargs)` in a try/except — on
  `AlpycaNotImplError` → log only, polling continues; on generic
  exception → log error
- `cmdType == "set"`: call `setDeviceProp(cmd.name, cmd.value)`
- Unknown type: `self.log.warning(...)` and skip

---

### Step 10 – `runnerCommunicationLoop()` — the single worker loop

```python
def runnerCommunicationLoop(self) -> None:
```

State machine with `while not self.stopEvent.is_set()`:

```
NOT CONNECTED (not self.deviceConnected):
    suc = self.connectDevice()
    if suc:
        self.serverConnected = True
        self.deviceConnected = True
        self.signals.serverConnected.emit()
        self.signals.deviceConnected.emit(self.deviceName)
        self.msg.emit(0, "ALPACA", "Device found", self.deviceName)
        self.getInitialConfig()
    continue  # fall through to wait at end of loop

CONNECTED (self.deviceConnected):
    suc = self.getDeviceProp("Connected")
    if not suc:   # includes None
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.deviceName)
        self.msg.emit(0, "ALPACA", "Device remove", self.deviceName)
        continue
    try:
        self.pollData()
    except Exception as e:
        self.log.error(...)
    self.processCommandQueue()

# end of every iteration — uniform cycle time for both states
self.stopEvent.wait(timeout=self.updateRate / 1000)
```

---

### Step 11 – `startCommunication()` — create device, start loop

```python
def startCommunication(self) -> None:
    self.data.clear()
    if not self.createAlpacaDevice():
        self.msg.emit(2, "ALPACA", "Device type error", self.deviceName)
        return
    self.stopEvent.clear()
    self.workerCommunicationLoop = Worker(self.runnerCommunicationLoop)
    self.threadPool.start(self.workerCommunicationLoop)
```

---

### Step 12 – `stopCommunication()` — signal stop, disconnect device

```python
def stopCommunication(self) -> None:
    self.stopEvent.set()
    self.setDeviceProp("Connected", False)
    self.deviceConnected = False
    self.serverConnected = False
    self.signals.deviceDisconnected.emit(self.deviceName)
    self.signals.serverDisconnected.emit({self.deviceName: 0})
    self.msg.emit(0, "ALPACA", "Device  remove", self.deviceName)
```

---

### Step 13 – Update `tests/unit_tests/base/test_alpacaClass.py`

The existing test file is updated in-place. The `Parent` fixture class
and the `AlpacaClass` import remain. The `mock.patch.object(QTimer,
"start")` context manager is **removed** from the fixture.

**Fixture change:**
```python
# before
@pytest.fixture(autouse=True, scope="function")
def function():
    with mock.patch.object(QTimer, "start"):
        func = AlpacaClass(parent=Parent())
        yield func

# after
@pytest.fixture(autouse=True, scope="function")
def function():
    func = AlpacaClass(parent=Parent())
    yield func
```

**Remove** `from PySide6.QtCore import QTimer` import if only used for
the fixture mock.

**Remove** all tests that covered behaviour that no longer exists:
`test_startTimer`, `test_stopTimer`, `test_workerConnectDevice_*`,
`test_workerGetInitialConfig_*`, `test_workerPollStatus_*`,
`test_processPolledData`, `test_workerPollData`, `test_pollData_*`,
`test_pollStatus_*`, `test_getInitialConfig_*`, `test_startCommunication`.

**Add** the following new tests:

| No. | Test | Logic covered |
|-----|------|---------------|
| T01 | `test_init` | `commandQueue`, `stopEvent`, `workerCommunicationLoop` present; no QTimer, `propertyExceptions`, or per-task worker attributes |
| T02 | `test_properties_1` | host/port/hostaddress setters |
| T03 | `test_properties_2` | host/port/hostaddress getters, default values |
| T04 | `test_properties_3` | deviceName split into deviceType/number |
| T05 | `test_createAlpacaDevice_1` | known type → success |
| T06 | `test_createAlpacaDevice_2` | unknown type → False |
| T07 | `test_createAlpacaDevice_3` | constructor exception → False |
| T08 | `test_getDeviceProp_1` | successful read → value returned |
| T09 | `test_getDeviceProp_2` | `AlpycaNotImplError` → log only, return None |
| T10 | `test_getDeviceProp_3` | generic exception → None |
| T11 | `test_setDeviceProp_1` | successful set → True |
| T12 | `test_setDeviceProp_2` | `AlpycaNotImplError` → log only, False |
| T13 | `test_setDeviceProp_3` | generic exception → False |
| T14 | `test_callDeviceMethod_1` | success → item placed on queue |
| T15 | `test_callDeviceMethodSync_1` | successful call → return value |
| T16 | `test_callDeviceMethodSync_2` | `AlpycaNotImplError` → log only, return None |
| T17 | `test_callDeviceMethodSync_3` | generic exception → None |
| T18 | `test_getAndStoreDeviceProp` | delegation correct |
| T19 | `test_discoverAPIVersion_1` | exception → 0 |
| T20 | `test_discoverAPIVersion_2` | empty list → 0 |
| T21 | `test_discoverAPIVersion_3` | maximum of versions |
| T22 | `test_discoverAlpacaDevices_1` | exception → [] |
| T23 | `test_discoverAlpacaDevices_2` | empty list → [] |
| T24 | `test_discoverAlpacaDevices_3` | device list returned |
| T25 | `test_discoverDevices_1` | filtered and formatted list |
| T26 | `test_discoverDevices_2` | empty device list → [] |
| T27 | `test_connectDevice_1` | all retries failed → False |
| T28 | `test_connectDevice_2` | first attempt succeeds → True |
| T29 | `test_connectDevice_3` | succeeds after retries → True |
| T30 | `test_getInitialConfig` | all three data keys stored |
| T31 | `test_pollData` | base implementation is no-op |
| T32 | `test_processCommandQueue_1` | empty queue → no action |
| T33 | `test_processCommandQueue_2` | "call" cmd → method called on device |
| T34 | `test_processCommandQueue_3` | "set" cmd → setDeviceProp called |
| T35 | `test_processCommandQueue_4` | unknown type → warning logged |
| T36 | `test_processCommandQueue_5` | exception in "call" → error logged, no crash |
| T37 | `test_processCommandQueue_6` | `AlpycaNotImplError` in "call" → log only, continues |
| T38 | `test_runnerCommunicationLoop_stopImmediately` | `stopEvent` pre-set → 0 iterations |
| T39 | `test_runnerCommunicationLoop_connectFails` | disconnected → `connectDevice` False → wait |
| T40 | `test_runnerCommunicationLoop_connectSucceeds` | `getInitialConfig` called, signals emitted |
| T41 | `test_runnerCommunicationLoop_pollCycle` | connected → `pollData`, `processCommandQueue`, wait |
| T42 | `test_runnerCommunicationLoop_deviceLost` | `getDeviceProp("Connected")` False → `deviceDisconnected` |
| T43 | `test_runnerCommunicationLoop_devicePropNone` | `getDeviceProp` returns None → treated as disconnect |
| T44 | `test_runnerCommunicationLoop_pollDataException` | `pollData` raises → logged, loop continues |
| T45 | `test_startCommunication_1` | `createAlpacaDevice` False → no worker started |
| T46 | `test_startCommunication_2` | success → worker started, `stopEvent.clear` called |
| T47 | `test_stopCommunication` | `stopEvent.set` called, signals emitted, state reset |

---

### Step 14 – Ruff linting

After implementation:

```bash
ruff check src/mw4/base/alpacaClass.py \
    tests/unit_tests/base/test_alpacaClass.py --fix
ruff format src/mw4/base/alpacaClass.py \
    tests/unit_tests/base/test_alpacaClass.py
```

Violations to eliminate:
- `E501` — lines over 95 characters (split long f-strings)
- `F401` — unused imports
- `I001` — import order (isort, no sections)
- `UP` — use Python 3.11 syntax

---

## Part 2 – `DomeAlpaca` migration example

`DomeAlpaca` is used as the reference subclass to validate the migration
pattern. The same pattern applies to all other `*Alpaca` subclasses
(`CameraAlpaca`, `FocuserAlpaca`, `FilterAlpaca`, etc.).

### Current `domeAlpaca.py` structure (before migration)

```
DomeAlpaca(AlpacaClass)
├── __init__
├── workerGetInitialConfig()   ← overrides base, calls super()
├── processPolledData()        ← called as Worker result callback
├── workerPollData()           ← run in separate Worker
├── slewToAltAz(altitude, azimuth)
├── openShutter()
├── closeShutter()
├── slewCW()
├── slewCCW()
└── abortSlew()
```

### Step 15 – Update `domeAlpaca.py`

**No import or base class change needed** — `DomeAlpaca` already
inherits from `AlpacaClass` via `from mw4.base.alpacaClass import
AlpacaClass`, which remains unchanged.

**Rename `workerGetInitialConfig` → `getInitialConfig`:**
```python
# before
def workerGetInitialConfig(self) -> None:
    super().workerGetInitialConfig()
    ...

# after
def getInitialConfig(self) -> None:
    super().getInitialConfig()
    self.getAndStoreDeviceProp("CanSetAltitude", "CanSetAltitude")
    self.getAndStoreDeviceProp("CanSetAzimuth", "CanSetAzimuth")
    self.getAndStoreDeviceProp("CanSetShutter", "CanSetShutter")
    self.log.debug(f"Initial data: {self.data}")
```

**Merge `processPolledData` into `pollData`, rename `workerPollData` →
`pollData`:**

`processPolledData` emitted `signals.azimuth` using the stored value.
`workerPollData` also emitted the same signal directly after storing the
value — a duplicate emission. Resolution: keep only the emission inside
`pollData` and remove `processPolledData` entirely.

**On using `getAndStoreDeviceProp` vs `getDeviceProp` inside `pollData`:**

| Property | Pattern used | Reason |
|----------|-------------|--------|
| `"Azimuth"` | `getAndStoreDeviceProp` + read back from `self.data` | value only needed to emit signal; storing first is cleaner and consistent |
| `"Slewing"` | `getAndStoreDeviceProp` (already correct) | value not needed locally |
| `"ShutterStatus"` | `getDeviceProp` (keep as-is) | return value drives branching logic; `getAndStoreDeviceProp` + read-back would obscure intent |

```python
# after  (single pollData method, processPolledData removed)
def pollData(self) -> None:
    shutterStates = ["Open", "Closed", "Opening", "Closing", "Error"]
    self.getAndStoreDeviceProp(
        "Azimuth", "ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION"
    )
    self.signals.azimuth.emit(
        self.data.get("ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION")
    )
    self.getAndStoreDeviceProp("Slewing", "Slewing")

    state = self.getDeviceProp("ShutterStatus")
    if state is None:
        self.data["DOME_SHUTTER.SHUTTER_OPEN"] = None
        self.data["DOME_SHUTTER.SHUTTER_CLOSED"] = None
        return

    stateIndex = int(state)
    if stateIndex == 0:
        stateText = shutterStates[stateIndex]
        self.storePropertyToData(stateText, "Status.Shutter")
        self.storePropertyToData(True, "DOME_SHUTTER.SHUTTER_OPEN")
        self.storePropertyToData(False, "DOME_SHUTTER.SHUTTER_CLOSED")
    elif stateIndex == 1:
        stateText = shutterStates[stateIndex]
        self.storePropertyToData(stateText, "Status.Shutter")
        self.storePropertyToData(False, "DOME_SHUTTER.SHUTTER_OPEN")
        self.storePropertyToData(True, "DOME_SHUTTER.SHUTTER_CLOSED")
    else:
        self.data["DOME_SHUTTER.SHUTTER_OPEN"] = None
        self.data["DOME_SHUTTER.SHUTTER_CLOSED"] = None
```

**Command methods** (`slewToAltAz`, `openShutter`, `closeShutter`,
`abortSlew`, `slewCW`, `slewCCW`) — **no changes needed**. They already
call `callDeviceMethod` which now enqueues the command. The
`data.get(...)` capability checks remain unchanged.

---

### Step 16 – Update `tests/unit_tests/logic/dome/test_domeAlpaca.py`

**Fixture**: remove `mock.patch.object(PySide6.QtCore.QTimer, "start")`
and `import PySide6` — no longer needed.

```python
# before
@pytest.fixture(autouse=True, scope="module")
def function():
    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        func = DomeAlpaca(parent=Parent())
        yield func

# after
@pytest.fixture(autouse=True, scope="module")
def function():
    func = DomeAlpaca(parent=Parent())
    yield func
```

**Update import line** — remove `import PySide6`; the `AlpacaClass`
import is unchanged:
```python
# remove:  import PySide6
from mw4.base.alpacaClass import AlpacaClass
from mw4.logic.dome.domeAlpaca import DomeAlpaca
```

**Test changes:**

| Before | After | Reason |
|--------|-------|--------|
| `test_workerGetInitialConfig_1` | `test_getInitialConfig_1` | method renamed |
| `test_workerPollData_1` … `_5` | `test_pollData_1` … `_5` | method renamed |
| `test_processPolledData_1` | **removed** | method no longer exists |
| `function.deviceConnected = False/True` in poll tests | remove — not checked inside `pollData` | loop owns connection state |
| `test_slewToAltAz_1` with `deviceConnected = False` | remove `deviceConnected` setup; check queue is empty when capabilities not set | `callDeviceMethod` always enqueues |
| `test_closeShutter_1/openShutter_1/abortSlew_1` with `deviceConnected = False` | remove `deviceConnected` setup | same reason |

**Full updated test list for `test_domeAlpaca.py`:**

| No. | Test | Logic covered |
|-----|------|---------------|
| D01 | `test_getInitialConfig_1` | super called, three capability keys stored |
| D02 | `test_pollData_1` | azimuth value stored, azimuth signal emitted |
| D03 | `test_pollData_2` | shutter state 0 (open) → correct flags stored |
| D04 | `test_pollData_3` | shutter state 1 (closed) → correct flags stored |
| D05 | `test_pollData_4` | shutter state 3 (other) → both flags None |
| D06 | `test_pollData_5` | `ShutterStatus` returns None → early return, flags None |
| D07 | `test_slewToAltAz_1` | capabilities not set → queue remains empty |
| D08 | `test_slewToAltAz_2` | both capabilities set → two items on queue |
| D09 | `test_closeShutter_1` | `CanSetShutter` not set → queue remains empty |
| D10 | `test_closeShutter_2` | `CanSetShutter` set → item on queue |
| D11 | `test_openShutter_1` | `CanSetShutter` not set → queue remains empty |
| D12 | `test_openShutter_2` | `CanSetShutter` set → item on queue |
| D13 | `test_slewCW_1` | no-op, no exception |
| D14 | `test_slewCCW_1` | no-op, no exception |
| D15 | `test_abortSlew_1` | item placed on queue |

---

### Step 17 – Ruff linting for `DomeAlpaca`

```bash
ruff check src/mw4/logic/dome/domeAlpaca.py \
    tests/unit_tests/logic/dome/test_domeAlpaca.py --fix
ruff format src/mw4/logic/dome/domeAlpaca.py \
    tests/unit_tests/logic/dome/test_domeAlpaca.py
```

---

## Design decisions summary

| Topic | Decision |
|-------|----------|
| Target file | `src/mw4/base/alpacaClass.py` edited in-place; class name `AlpacaClass` unchanged |
| Subclass imports | No change — all already use `from mw4.base.alpacaClass import AlpacaClass` |
| `propertyExceptions` | Removed entirely — `AlpycaNotImplError` is only logged |
| `device is None` guards | Removed — device guaranteed valid for loop lifetime |
| `CONNECTION_RETRY_DELAY` constant | Removed — `updateRate / 1000` used uniformly |
| `processPolledData` | Removed — post-processing moved to end of `pollData()` |
| `callDeviceMethod` return type | Changed `Any` → `None` (enqueue only, fire-and-forget) |
| `callDeviceMethodSync` | New method — direct synchronous call, returns `Any`; used inside worker threads that need return values (`pollData`, expose workflows) |
| Loop cycle time | Single `stopEvent.wait(updateRate / 1000)` at end of every iteration |
| Thread safety of `setDeviceProp` | Safe — alpyca is stateless HTTP; concurrent calls are harmless |
| `getAndStoreDeviceProp` and the queue | Not routed through the queue — read helper called from within the loop thread |
| `getAndStoreDeviceProp` vs `getDeviceProp` in `pollData` | Use `getAndStoreDeviceProp` + read from `self.data` when value only needed for signal emission; keep `getDeviceProp` when value drives local branching logic |
| Local list constants in `pollData` | Moved to class variables (`SCREAMING_SNAKE_CASE`) |
| `deviceConnected` guard in subclass command methods | Removed — loop owns connection state; alpyca HTTP exceptions are caught and logged |

---

## File overview

| File | Action |
|------|--------|
| `src/mw4/base/alpacaClass.py` | **Edit in-place** (new loop architecture) |
| `tests/unit_tests/base/test_alpacaClass.py` | **Edit in-place** (remove QTimer mock, replace obsolete tests) |
| `src/mw4/logic/dome/domeAlpaca.py` | Update (class var, rename methods, merge pollData) |
| `tests/unit_tests/logic/dome/test_domeAlpaca.py` | Update |
| `src/mw4/logic/camera/cameraAlpaca.py` | Update (rename methods, workerExpose → callDeviceMethodSync) |
| `tests/unit_tests/logic/camera/test_cameraAlpaca.py` | Update |
| `src/mw4/logic/cover/coverAlpaca.py` | Update (class var, rename method) |
| `tests/unit_tests/logic/cover/test_coverAlpaca.py` | Update |
| `src/mw4/logic/filter/filterAlpaca.py` | Update (rename methods, remove deviceConnected guard) |
| `tests/unit_tests/logic/filter/test_filterAlpaca.py` | Update |
| `src/mw4/logic/focuser/focuserAlpaca.py` | Update (rename method, trivial) |
| `tests/unit_tests/logic/focuser/test_focuserAlpaca.py` | Update |
| `src/mw4/logic/environment/sensorWeatherAlpaca.py` | Update (rename method, trivial) |
| `tests/unit_tests/logic/environment/test_sensorWeatherAlpaca.py` | Update |
| `src/mw4/logic/lightPanel/lightPanelAlpaca.py` | Update (rename method, getAndStoreDeviceProp) |
| `tests/unit_tests/logic/lightPanel/test_lightPanelAlpaca.py` | Update |
| `src/mw4/logic/telescope/telescopeAlpaca.py` | Update (rename method, trivial) |
| `tests/unit_tests/logic/telescope/test_telescopeAlpaca.py` | Update |
| `src/mw4/logic/powerswitch/pegasusUPBAlpaca.py` | Update (migrate, callDeviceMethod reads → callDeviceMethodSync) |
| `tests/unit_tests/logic/powerswitch/test_pegasusUPBAlpaca.py` | Update |
| `src/mw4/base/architecture.md` | No change (reference document) |
| `src/mw4/base/alpacaClass.py` | No change (remains in place) |

---

## Part 3 – Remaining device class migrations

All subclasses follow the same migration pattern. The table below shows
the changes for each; full `pollData` code is given only where the
transformation is non-trivial.

### Common migration checklist for every subclass

- [ ] **No import or base class change** — all subclasses already inherit from `AlpacaClass`
- [ ] Rename `workerGetInitialConfig` → `getInitialConfig`, update `super()` call
- [ ] Rename `workerPollData` → `pollData`
- [ ] Remove `processPolledData` (if present); merge logic into `pollData`
- [ ] Replace local list constants with class variables (`SCREAMING_SNAKE_CASE`)
- [ ] Replace `callDeviceMethod(read)` with `callDeviceMethodSync(read)` where return value is used
- [ ] Remove `deviceConnected` guards in command methods
- [ ] Update test fixture (remove QTimer mock, remove `import PySide6` if unused)
- [ ] Rename test functions accordingly

---

### Step 18 – `FocuserAlpaca`

**`focuserAlpaca.py` changes:**

| Item | Change |
|------|--------|
| Base class | `AlpacaClass` → `AlpacaClassNew` |
| `workerPollData` | renamed → `pollData` |
| All `getAndStoreDeviceProp` calls | unchanged |
| Command methods (`move`, `halt`) | unchanged — already fire-and-forget |

```python
# after
def pollData(self) -> None:
    self.getAndStoreDeviceProp(
        "Position", "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION"
    )
```

**`test_focuserAlpaca.py` changes:** remove QTimer mock, rename
`test_workerPollData_1` → `test_pollData_1`.

---

### Step 19 – `SensorWeatherAlpaca`

**`sensorWeatherAlpaca.py` changes:**

| Item | Change |
|------|--------|
| Base class | `AlpacaClass` → `AlpacaClassNew` |
| `workerPollData` | renamed → `pollData` |
| All `getAndStoreDeviceProp` calls | unchanged |

No command methods — no further changes.

**`test_sensorWeatherAlpaca.py` changes:** remove QTimer mock, rename
test.

---

### Step 20 – `TelescopeAlpaca`

**`telescopeAlpaca.py` changes:**

| Item | Change |
|------|--------|
| Base class | `AlpacaClass` → `AlpacaClassNew` |
| `workerGetInitialConfig` | renamed → `getInitialConfig`; `super()` call updated |
| No `workerPollData` | base `pollData` (`pass`) is sufficient |

**`test_telescopeAlpaca.py` changes:** remove QTimer mock, rename
`test_workerGetInitialConfig_1` → `test_getInitialConfig_1`.

---

### Step 21 – `FilterAlpaca`

**`filterAlpaca.py` changes:**

| Item | Change |
|------|--------|
| Base class | `AlpacaClass` → `AlpacaClassNew` |
| `workerGetInitialConfig` | renamed → `getInitialConfig`; `super()` call updated |
| `workerPollData` | renamed → `pollData`; logic unchanged |
| `sendFilterNumber` | remove `if not self.deviceConnected: return` guard |

`getInitialConfig` iterates over filter names — using `getDeviceProp` is
correct here (return value drives local logic):

```python
def getInitialConfig(self) -> None:
    super().getInitialConfig()
    names = self.getDeviceProp("Names")
    if names is None:
        return
    for i, name in enumerate(names):
        if name is None:
            continue
        self.data[f"FILTER_NAME.FILTER_SLOT_NAME_{i:1.0f}"] = name
```

`pollData` — `getDeviceProp` kept (return value drives `return` guard):

```python
def pollData(self) -> None:
    position = self.getDeviceProp("Position")
    if position == -1 or position is None:
        return
    self.storePropertyToData(position, "FILTER_SLOT.FILTER_SLOT_VALUE")
```

**`test_filterAlpaca.py` changes:** remove QTimer mock; rename tests;
remove `deviceConnected = False` setups from `sendFilterNumber` test.

---

### Step 22 – `CoverAlpaca`

**`coverAlpaca.py` changes:**

| Item | Change |
|------|--------|
| Base class | `AlpacaClass` → `AlpacaClassNew` |
| `workerPollData` | renamed → `pollData` |
| `states` local list | moved to class variable `COVER_STATES` |

```python
class CoverAlpaca(AlpacaClassNew):
    COVER_STATES: list[str] = [
        "NotPresent", "Closed", "Moving", "Open", "Unknown", "Error"
    ]

    def pollData(self) -> None:
        state = self.getDeviceProp("CoverState")
        if state is None:
            return
        self.storePropertyToData(
            self.COVER_STATES[int(state)], "Status.Cover"
        )
```

**`test_coverAlpaca.py` changes:** remove QTimer mock; rename test.

---

### Step 23 – `LightPanelAlpaca`

**`lightPanelAlpaca.py` changes:**

| Item | Change |
|------|--------|
| Base class | `AlpacaClass` → `AlpacaClassNew` |
| `workerPollData` | renamed → `pollData` |
| `getDeviceProp("Brightness")` + `storePropertyToData` | replace with `getAndStoreDeviceProp` |
| `getDeviceProp("MaxBrightness")` + `storePropertyToData` | replace with `getAndStoreDeviceProp` |

```python
def pollData(self) -> None:
    self.getAndStoreDeviceProp(
        "Brightness",
        "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE",
    )
    self.getAndStoreDeviceProp(
        "MaxBrightness",
        "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX",
    )
```

**`test_lightPanelAlpaca.py` changes:** remove QTimer mock; rename test.

---

### Step 24 – `CameraAlpaca`

**`cameraAlpaca.py` changes:**

| Item | Change |
|------|--------|
| Base class | `AlpacaClass` → `AlpacaClassNew` |
| `workerGetInitialConfig` | renamed → `getInitialConfig`; `super()` call updated |
| `workerPollData` | renamed → `pollData`; all calls are `getAndStoreDeviceProp` — unchanged |
| `workerExpose` | `callDeviceMethod("StartExposure", …)` → `callDeviceMethodSync("StartExposure", …)` |

> **Why `callDeviceMethodSync` in `workerExpose`**: `workerExpose` runs
> in its own dedicated `Worker` thread (not the communication loop). It
> must call `StartExposure` synchronously before entering
> `waitExposed()`. Enqueueing via `callDeviceMethod` would only execute
> the command at the next loop iteration, by which time `waitExposed`
> has already started polling for `ImageReady` — a race condition.

```python
def workerExpose(self) -> None:
    self.sendDownloadMode()
    self.setDeviceProp("BinX", self.parent.binning)
    self.setDeviceProp("BinY", self.parent.binning)
    self.setDeviceProp("StartX", self.parent.posXASCOM)
    self.setDeviceProp("StartY", self.parent.posYASCOM)
    self.setDeviceProp("NumX", self.parent.widthASCOM)
    self.setDeviceProp("NumY", self.parent.heightASCOM)
    self.callDeviceMethodSync(          # ← changed from callDeviceMethod
        "StartExposure",
        Duration=self.parent.exposureTime,
        Light=True,
    )
    self.parent.waitExposed(self.parent.exposureTime, self.waitFunc)
    ...
```

**`test_cameraAlpaca.py` changes:** remove QTimer mock; rename tests;
update `workerExpose` test to mock `callDeviceMethodSync` instead of
`callDeviceMethod`.

---

### Step 25 – `PegasusUPBAlpaca`

This is the most complex migration. `workerPollData` uses
`callDeviceMethod` as a **read** mechanism — it captures the return value
and passes it to `storePropertyToData`. In `AlpacaClassNew`,
`callDeviceMethod` returns `None` (enqueues only), so all such calls
must become `callDeviceMethodSync`.

**`pegasusUPBAlpaca.py` changes:**

| Item | Change |
|------|--------|
| Base class | `AlpacaClass` → `AlpacaClassNew` |
| `workerPollData` | renamed → `pollData` |
| All `callDeviceMethod` in `pollData` (read calls) | → `callDeviceMethodSync` |
| `callDeviceMethod` in `togglePowerPort`, `togglePortUSB`, `toggleAutoDew`, `sendDew` | unchanged — fire-and-forget commands from GUI |

```python
# after (excerpt from pollData — UPB branch, pattern applies to UPBv2)
def pollData(self) -> None:
    model = "UPB" if self.getDeviceProp("MaxSwitch") == 15 else "UPBv2"
    self.data["FIRMWARE_INFO.VERSION"] = "1.4" if model == "UPB" else "2.1"
    if model == "UPB":
        self.storePropertyToData(
            self.callDeviceMethodSync("GetSwitch", Id=0),  # ← sync
            "POWER_CONTROL.POWER_CONTROL_1",
        )
        # … all remaining callDeviceMethod → callDeviceMethodSync
```

> **Rule**: inside `pollData`, every `callDeviceMethod` whose return
> value is captured must become `callDeviceMethodSync`. Command methods
> called from the GUI (`togglePowerPort`, etc.) keep `callDeviceMethod`.

**`test_pegasusUPBAlpaca.py` changes:** remove QTimer mock; rename
`test_workerPollData_*` → `test_pollData_*`; mock `callDeviceMethodSync`
instead of `callDeviceMethod` in poll tests.

---

### Step 26 – Run full test suite and Ruff

After all subclass migrations:

```bash
# lint and format all changed files
ruff check src/mw4/base/alpacaClass.py \
    src/mw4/logic/dome/domeAlpaca.py \
    src/mw4/logic/camera/cameraAlpaca.py \
    src/mw4/logic/cover/coverAlpaca.py \
    src/mw4/logic/filter/filterAlpaca.py \
    src/mw4/logic/focuser/focuserAlpaca.py \
    src/mw4/logic/environment/sensorWeatherAlpaca.py \
    src/mw4/logic/lightPanel/lightPanelAlpaca.py \
    src/mw4/logic/telescope/telescopeAlpaca.py \
    src/mw4/logic/powerswitch/pegasusUPBAlpaca.py \
    tests/unit_tests/base/test_alpacaClass.py \
    tests/unit_tests/logic/dome/test_domeAlpaca.py \
    tests/unit_tests/logic/camera/test_cameraAlpaca.py \
    tests/unit_tests/logic/cover/test_coverAlpaca.py \
    tests/unit_tests/logic/filter/test_filterAlpaca.py \
    tests/unit_tests/logic/focuser/test_focuserAlpaca.py \
    tests/unit_tests/logic/environment/test_sensorWeatherAlpaca.py \
    tests/unit_tests/logic/lightPanel/test_lightPanelAlpaca.py \
    tests/unit_tests/logic/telescope/test_telescopeAlpaca.py \
    tests/unit_tests/logic/powerswitch/test_pegasusUPBAlpaca.py \
    --fix
ruff format <same files>

# run full test coverage for all changed units
uv run pytest tests/unit_tests/base/test_alpacaClass.py \
    tests/unit_tests/logic/dome/test_domeAlpaca.py \
    tests/unit_tests/logic/camera/test_cameraAlpaca.py \
    tests/unit_tests/logic/cover/test_coverAlpaca.py \
    tests/unit_tests/logic/filter/test_filterAlpaca.py \
    tests/unit_tests/logic/focuser/test_focuserAlpaca.py \
    tests/unit_tests/logic/environment/test_sensorWeatherAlpaca.py \
    tests/unit_tests/logic/lightPanel/test_lightPanelAlpaca.py \
    tests/unit_tests/logic/telescope/test_telescopeAlpaca.py \
    tests/unit_tests/logic/powerswitch/test_pegasusUPBAlpaca.py \
    --cov=src/mw4/base/alpacaClass \
    --cov=src/mw4/logic/dome/domeAlpaca \
    --cov=src/mw4/logic/camera/cameraAlpaca \
    --cov=src/mw4/logic/cover/coverAlpaca \
    --cov=src/mw4/logic/filter/filterAlpaca \
    --cov=src/mw4/logic/focuser/focuserAlpaca \
    --cov=src/mw4/logic/environment/sensorWeatherAlpaca \
    --cov=src/mw4/logic/lightPanel/lightPanelAlpaca \
    --cov=src/mw4/logic/telescope/telescopeAlpaca \
    --cov=src/mw4/logic/powerswitch/pegasusUPBAlpaca \
    --cov-report=term-missing
```

Target: **100% coverage** on all listed source files.

