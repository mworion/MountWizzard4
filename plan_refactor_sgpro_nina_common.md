# Plan: Refactor SGProClass & NINAClass → SgproNinaCommon (v4)

**Date:** 2026-05-19 (updated after aligning ninaClass lines 135/141)
**Scope:** `src/mw4/base/sgproClass.py`, `src/mw4/base/ninaClass.py`
**Goal:** Extract shared code into a new base class `SgproNinaCommon`
(analogous to `AlpacaAscomCommon`) to eliminate duplication.

---

## 1. Current state – precise diff result

`diff sgproClass.py ninaClass.py` reveals exactly **2 differences**:

| Line | sgproClass.py | ninaClass.py |
|------|---------------|--------------|
| 24 | `class SGProClass(DriverData):` | `class NINAClass(DriverData):` |
| 32 | `PROTOCOL_NAME: str = "SGPro"` | `PROTOCOL_NAME: str = "NINA"` |

All other constants, attributes, and methods are **byte-for-byte
identical** in both files. Additionally, `import json` is present in
both files but **unused**.

### 1.1 Gap between source and current test files

The test files were already written for the **target refactored state**
and currently do **not** match the source code. They define the required
API for each subclass:

**`test_sgproClass.py` expects `SGProClass` to expose:**
- `sgConnectDevice()` instead of `connectDevice()`
- `sgDisconnectDevice()` instead of `disconnectDevice()`
- `sgEnumerateDevice()` instead of `enumerateDevice()`
- `startSGProTimer()` instead of `startTimer()`
- `stopSGProTimer()` instead of `stopTimer()`
- `discoverDevices()` calls `sgEnumerateDevice()`
- `stopCommunication()` path goes through `stopSGProTimer()`
- `workerPollStatus` uses string `"DISCONNECTED"` comparison
  (unchanged from current source)

**`test_ninaClass.py` expects `NINAClass` to expose:**
- `connectDevice()`, `disconnectDevice()`, `enumerateDevice()`
  (same names, own HTTP implementations)
- `startNINATimer()` instead of `startTimer()`
- `stopNINATimer()` instead of `stopTimer()`
- `discoverDevices()` calls `enumerateDevice()`
- `stopCommunication()` path goes through `stopNINATimer()`
- `workerPollStatus` uses **integer** state comparison:
  `State == 0` → connected; `State != 0` → disconnected
  (this is a **behaviour change** from the current string comparison)

---

## 2. Target architecture

```
DriverData   (src/mw4/base/driverDataClass.py – unchanged)
    │
    └── SgproNinaCommon   (NEW: src/mw4/base/sgproNinaCommon.py)
            │
            │  Class constants (overridable):
            │    TIMEOUT, HOST_ADDR, PORT, PROTOCOL, BASE_URL,
            │    DEVICE_TYPE, UPDATE_RATE
            │    PROTOCOL_NAME = ""
            │
            │  Shared attributes (__init__):
            │    parent, app, data, msg, signals, threadPool,
            │    loadConfig, _deviceName, defaultConfig,
            │    signalRS, deviceConnected, serverConnected,
            │    workerGetConfig, workerStatus,
            │    mutexPollStatus, cycleDevice
            │
            │  Shared methods:
            │    deviceName property (getter + setter)
            │    requestProperty
            │    workerGetInitialConfig (pass)
            │    getInitialConfig
            │    workerPollStatus  ← uses self.isConnectedState()
            │    clearPollStatus
            │    pollStatus
            │    startCommunication  ← calls self.startTimer()
            │    stopCommunication   ← calls self.stopTimer()
            │    discoverDevices     ← calls self.enumerateDevice()
            │
            │  Abstract stubs (raise NotImplementedError):
            │    isConnectedState(state: Any) → bool
            │    startTimer() → None
            │    stopTimer() → None
            │    connectDevice() → bool
            │    disconnectDevice() → bool
            │    enumerateDevice() → list
            │
            ├── SGProClass   (src/mw4/base/sgproClass.py – slimmed)
            │      PROTOCOL_NAME = "SGPro"
            │
            │      # Protocol-specific named methods (own impl):
            │      sgConnectDevice() → bool
            │      sgDisconnectDevice() → bool
            │      sgEnumerateDevice() → list
            │      startSGProTimer() → None
            │      stopSGProTimer() → None
            │
            │      # Abstract method bridge implementations:
            │      isConnectedState(state) → state != "DISCONNECTED"
            │      startTimer()      → self.startSGProTimer()
            │      stopTimer()       → self.stopSGProTimer()
            │      connectDevice()   → self.sgConnectDevice()
            │      disconnectDevice()→ self.sgDisconnectDevice()
            │      enumerateDevice() → self.sgEnumerateDevice()
            │
            └── NINAClass   (src/mw4/base/ninaClass.py – slimmed)
                   PROTOCOL_NAME = "NINA"

                   # Protocol-specific named methods (own impl):
                   connectDevice()   → HTTP implementation
                   disconnectDevice()→ HTTP implementation
                   enumerateDevice() → HTTP implementation
                   startNINATimer()  → None
                   stopNINATimer()   → None

                   # Abstract method bridge implementations:
                   isConnectedState(state) → state == 0
                   startTimer()      → self.startNINATimer()
                   stopTimer()       → self.stopNINATimer()
                   # connectDevice / disconnectDevice / enumerateDevice
                   # serve as both the HTTP impl and the abstract method implementation
```

### 2.1 Call chain for stopCommunication

`stopCommunication` lives in `SgproNinaCommon` and calls
`self.stopTimer()`:

| Class | `stopTimer()` delegates to |
|-------|---------------------------|
| SGProClass | `stopSGProTimer()` |
| NINAClass | `stopNINATimer()` |

The test mocks (`stopSGProTimer`, `stopNINATimer`) are reached
transitively through the bridge. The additional mock of
`sgDisconnectDevice` / `disconnectDevice` in the tests is defensive
(precautionary) – neither is called by `stopCommunication`. ✓

### 2.2 workerPollStatus with isConnectedState

`workerPollStatus` in `SgproNinaCommon` replaces the direct string
comparison with `self.isConnectedState(state)`:

```python
state = response.get("State")
if not self.isConnectedState(state):
    if self.deviceConnected:
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.deviceName)
        self.msg.emit(
            0, self.PROTOCOL_NAME, "Device remove", self.deviceName
        )
else:
    if not self.deviceConnected:
        self.deviceConnected = True
        self.getInitialConfig()
        self.signals.deviceConnected.emit(self.deviceName)
        self.msg.emit(
            0, self.PROTOCOL_NAME, "Device found", self.deviceName
        )
```

| Class | `isConnectedState(state)` | State values (from tests) |
|-------|---------------------------|--------------------------|
| SGProClass | `state != "DISCONNECTED"` | `"DISCONNECTED"`, `"test"` |
| NINAClass | `state == 0` | `0` (connected), `3`/`5` (disconnected) |

Both classes already use `self.deviceName` directly (no f-string
wrapper) in these calls. The common base class keeps this convention
unchanged. ✓

---

## 3. Detailed implementation steps

### Step 3.1 – Create `src/mw4/base/sgproNinaCommon.py`

New class `SgproNinaCommon(DriverData)` with:
- All shared constants (`TIMEOUT`, `HOST_ADDR`, `PORT`, `PROTOCOL`,
  `BASE_URL`, `DEVICE_TYPE`, `UPDATE_RATE`)
- `PROTOCOL_NAME: str = ""` (overridden by subclasses)
- Complete `__init__` (identical to both current classes)
- `deviceName` property (getter + setter)
- `requestProperty`
- `workerGetInitialConfig` (pass)
- `getInitialConfig`
- `workerPollStatus` – calls `self.isConnectedState(state)`;
  uses `self.deviceName` without f-string wrapper
- `clearPollStatus`
- `pollStatus`
- `startCommunication` – calls `self.startTimer()`
- `stopCommunication` – calls `self.stopTimer()`
- `discoverDevices` – calls `self.enumerateDevice()`
- Abstract stubs raising `NotImplementedError`:
  `isConnectedState`, `startTimer`, `stopTimer`,
  `connectDevice`, `disconnectDevice`, `enumerateDevice`

Remove: unused `import json`.

### Step 3.2 – Rewrite `src/mw4/base/sgproClass.py`

```
class SGProClass(SgproNinaCommon):
    PROTOCOL_NAME = "SGPro"

    # Own protocol implementations:
    def sgConnectDevice(self) → bool
    def sgDisconnectDevice(self) → bool
    def sgEnumerateDevice(self) → list
    def startSGProTimer(self) → None
    def stopSGProTimer(self) → None

    # Abstract method bridge implementations:
    def isConnectedState(self, state) → state != "DISCONNECTED"
    def startTimer(self) → self.startSGProTimer()
    def stopTimer(self) → self.stopSGProTimer()
    def connectDevice(self) → self.sgConnectDevice()
    def disconnectDevice(self) → self.sgDisconnectDevice()
    def enumerateDevice(self) → self.sgEnumerateDevice()
```

Import: `from mw4.base.sgproNinaCommon import SgproNinaCommon`.
Remove: all other code (moved to base class), `import json`.

### Step 3.3 – Rewrite `src/mw4/base/ninaClass.py`

```
class NINAClass(SgproNinaCommon):
    PROTOCOL_NAME = "NINA"

    # Own protocol implementations (HTTP):
    def connectDevice(self) → bool
    def disconnectDevice(self) → bool
    def enumerateDevice(self) → list
    def startNINATimer(self) → None
    def stopNINATimer(self) → None

    # Abstract method bridge implementations:
    def isConnectedState(self, state) → state == 0
    def startTimer(self) → self.startNINATimer()
    def stopTimer(self) → self.stopNINATimer()
    # connectDevice / disconnectDevice / enumerateDevice serve as
    # both the HTTP impl and the abstract method implementation
```

Import: `from mw4.base.sgproNinaCommon import SgproNinaCommon`.
Remove: all other code (moved to base class), `import json`.

### Step 3.4 – Create `tests/unit_tests/base/test_sgproNinaCommon.py`

Cover every branch of `SgproNinaCommon` using a concrete test double:

```python
class ConcreteSgproNina(SgproNinaCommon):
    PROTOCOL_NAME = "TEST"
    def isConnectedState(self, state: Any) -> bool:
        return state == "CONNECTED"
    def startTimer(self) -> None:
        self.cycleDevice.start(self.UPDATE_RATE)
    def stopTimer(self) -> None:
        self.cycleDevice.stop()
    def connectDevice(self) -> bool:
        return True
    def disconnectDevice(self) -> bool:
        return True
    def enumerateDevice(self) -> list:
        return []
```

Tests to cover (100 %):
- `__init__` attribute defaults
- `deviceName` getter + setter
- `requestProperty` – POST branch, GET branch, HTTP error status,
  exception types Timeout, ConnectionError, generic Exception
  (6 test cases – mirrors existing `test_sgproClass.py` 1–6)
- `workerGetInitialConfig`
- `getInitialConfig` – worker dispatched into threadPool
- `workerPollStatus` – 5 branches (empty/falsy response, disconnect
  when was connected, stays disconnected, stays connected,
  connect when was not connected)
- `clearPollStatus`
- `pollStatus` – mutex locked (skip) + unlocked (run)
- `startCommunication` – first call (serverConnected=False)
- `stopCommunication` – flags cleared + signals emitted
- `discoverDevices` – delegates to `enumerateDevice()`
- Abstract stubs raise `NotImplementedError` (all 6 stubs)

### Step 3.5 – Trim `tests/unit_tests/base/test_sgproClass.py`

**Remove** tests now fully covered by `test_sgproNinaCommon.py`:
- `test_requestProperty_1` through `test_requestProperty_6`
- `test_workerGetInitialConfig_1`
- `test_getInitialConfig_1`
- `test_workerPollStatus_1` through `test_workerPollStatus_5`
- `test_clearPollStatus`
- `test_pollStatus_1`, `test_pollStatus_2`
- `test_startCommunication_1`

**Keep unchanged** (already written correctly, test SGProClass specifics):
- `test_properties_1`
- `test_sgConnectDevice_1`, `test_sgConnectDevice_2`
- `test_sgDisconnectDevice_1`, `test_sgDisconnectDevice_2`
- `test_sgEnumerateDevice_1`, `test_sgEnumerateDevice_2`
- `test_startTimer` → calls `startSGProTimer()`
- `test_stopTimer` → calls `stopSGProTimer()`
- `test_stopCommunication_1`
- `test_discoverDevices_1`, `test_discoverDevices_2`

**Add** to reach 100 % coverage on SGProClass bridge methods:
- `test_isConnectedState_1` – state `"test"` → True
- `test_isConnectedState_2` – state `"DISCONNECTED"` → False
- `test_connectDevice_bridge` – `connectDevice()` delegates to
  `sgConnectDevice()`
- `test_disconnectDevice_bridge` – delegates to `sgDisconnectDevice()`
- `test_enumerateDevice_bridge` – delegates to `sgEnumerateDevice()`
- `test_startTimer_bridge` – `startTimer()` delegates to
  `startSGProTimer()`
- `test_stopTimer_bridge` – `stopTimer()` delegates to
  `stopSGProTimer()`

### Step 3.6 – Trim `tests/unit_tests/base/test_ninaClass.py`

**Remove** tests now covered by `test_sgproNinaCommon.py`
(same set as Step 3.5 – `test_requestProperty_*`,
`test_workerGetInitialConfig_*`, `test_getInitialConfig_*`,
`test_workerPollStatus_*`, `test_clearPollStatus`,
`test_pollStatus_*`, `test_startCommunication_*`).

**Keep unchanged** (already written correctly, test NINAClass specifics):
- `test_properties_1`
- `test_connectDevice_1`, `test_connectDevice_2`
- `test_disconnectDevice_1`, `test_disconnectDevice_2`
- `test_enumerateDevice_1`, `test_enumerateDevice_2`
- `test_startTimer` → calls `startNINATimer()`
- `test_stopTimer` → calls `stopNINATimer()`
- `test_stopCommunication_1`
- `test_discoverDevices_1`, `test_discoverDevices_2`

**Add** to reach 100 % coverage on NINAClass bridge methods:
- `test_isConnectedState_1` – state `0` → True
- `test_isConnectedState_2` – state `5` → False
- `test_startTimer_bridge` – `startTimer()` delegates to
  `startNINATimer()`
- `test_stopTimer_bridge` – `stopTimer()` delegates to
  `stopNINATimer()`

### Step 3.7 – Run formatter / linter

```bash
ruff format src/mw4/base/sgproNinaCommon.py \
            src/mw4/base/sgproClass.py \
            src/mw4/base/ninaClass.py
ruff check  src/mw4/base/sgproNinaCommon.py \
            src/mw4/base/sgproClass.py \
            src/mw4/base/ninaClass.py \
            tests/unit_tests/base/test_sgproNinaCommon.py \
            tests/unit_tests/base/test_sgproClass.py \
            tests/unit_tests/base/test_ninaClass.py
```

Resolve all findings before proceeding.

### Step 3.8 – Coverage check for all three modules

```bash
pytest tests/unit_tests/base/test_sgproNinaCommon.py \
       tests/unit_tests/base/test_sgproClass.py \
       tests/unit_tests/base/test_ninaClass.py \
       --cov=src/mw4/base/sgproNinaCommon \
       --cov=src/mw4/base/sgproClass \
       --cov=src/mw4/base/ninaClass \
       --cov-report=term-missing
```

All three modules must reach **100 % coverage**.

### Step 3.9 – Run overall package tests

```bash
pytest tests/unit_tests/ --tb=short
```

No regressions permitted.

---

## 4. Files changed summary

| File | Action |
|------|--------|
| `src/mw4/base/sgproNinaCommon.py` | **CREATE** |
| `src/mw4/base/sgproClass.py` | **REWRITE** (bridges + sg-methods only) |
| `src/mw4/base/ninaClass.py` | **REWRITE** (bridges + HTTP methods only) |
| `tests/unit_tests/base/test_sgproNinaCommon.py` | **CREATE** |
| `tests/unit_tests/base/test_sgproClass.py` | **MODIFY** (trim + add) |
| `tests/unit_tests/base/test_ninaClass.py` | **MODIFY** (trim + add) |

No changes required in `cameraSGPro.py`, `cameraNINA.py`, or any other
file – the public interface of `SGProClass` and `NINAClass` is
preserved or extended (new named timer methods are additions only).

---

## 5. Key design decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | `isConnectedState()` abstract in base | Single `workerPollStatus` in common class while supporting SGPro string-based (`!= "DISCONNECTED"`) and NINA integer-based (`== 0`) state detection as required by tests |
| 2 | Abstract timer / device stubs in base | `startCommunication` and `stopCommunication` can call `self.startTimer()` / `self.stopTimer()` via bridge pattern |
| 3 | SGPro bridge methods (`connectDevice → sgConnectDevice`) | Keeps `sg`-prefix convention expected by existing tests while fulfilling the common class interface |
| 4 | NINA HTTP methods satisfy both roles | `connectDevice` etc. in NINAClass are simultaneously the HTTP implementation and the abstract method fulfilment – no extra bridge layer needed |
| 5 | Use `self.deviceName` (no f-string) in base | Both source files already use `self.deviceName` directly in `workerPollStatus`; the common class inherits this unchanged |
| 6 | Remove `import json` from all three files | `json` is unused in both current classes and will not be needed in the base class either |
| 7 | No changes to `cameraSGPro.py` / `cameraNINA.py` | These classes call methods that remain available in the subclasses |
