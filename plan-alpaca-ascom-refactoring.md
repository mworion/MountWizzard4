# Plan: Refactoring AlpacaClass & AscomClass into AlpacaAscomCommon

**Date:** 2026-05-18  
**Scope:** `src/mw4/base/`, `src/mw4/logic/` and their corresponding test files  
**New file:** `src/mw4/base/alpacaAscomCommon.py`  
**New test file:** `tests/unit_tests/base/test_alpacaAscomCommon.py`

---

## 1. Method Naming Alignment

`ascomClass.py` uses ASCOM-specific method names. All names must be aligned
to the generic pattern already established in `alpacaClass.py`.

| ascomClass (current)         | Target (= alpacaClass)       |
|------------------------------|------------------------------|
| `getAscomProperty`           | `getDeviceProp`              |
| `setAscomProperty`           | `setDeviceProp`              |
| `callAscomMethod`            | `callDeviceMethod`           |
| `setAscomPropertyQueued`     | `setDevicePropQueued`        |
| `callAscomMethodQueued`      | `callDeviceMethodQueued`     |
| `getAndStoreAscomProperty`   | `getAndStoreDeviceProp`      |
| `workerRunnerCoreLoop`       | stays ASCOM-specific         |

---

## 2. Duplicate Code to Extract

The following elements are identical or near-identical in both classes and
will move to `AlpacaAscomCommon`:

| Element                   | Status      | Notes                                       |
|---------------------------|-------------|---------------------------------------------|
| `CommandItem` dataclass   | identical   | Defined twice – move to common              |
| `__init__` shared attrs   | near-ident. | `app`, `msg`, `data`, `signals`,            |
|                           |             | `threadPool`, `loadConfig`,                 |
|                           |             | `propertyExceptions`, `device`,             |
|                           |             | `deviceName`, `deviceType`,                 |
|                           |             | `deviceConnected`, `serverConnected`,       |
|                           |             | `commandQueue`, `stopEvent`                 |
| `connectDevice`           | near-ident. | Only the `PROTOCOL_NAME` prefix differs     |
| `getInitialConfig`        | near-ident. | Uses `getAndStoreDeviceProp` after rename   |
| `pollData`                | identical   | Both `pass`                                 |
| `processCommandQueue`     | near-ident. | Uses `callDeviceMethod`/`setDeviceProp`     |
| `handleDeviceConnect`     | near-ident. | Only the `PROTOCOL_NAME` prefix differs     |
| `handleDeviceDisconnect`  | near-ident. | Only the `PROTOCOL_NAME` prefix differs     |
| `runnerCommunicationLoop` | near-ident. | Uses `getDeviceProp` after rename           |
| `stopCommunication`       | near-ident. | Uses `setDevicePropQueued`; only `PROTOCOL_NAME` differs |

---

## 3. Target Class Structure

### 3.1 New: `src/mw4/base/alpacaAscomCommon.py`

`AlpacaAscomCommon` inherits from `DriverData` and holds all shared code.

```
AlpacaAscomCommon(DriverData)
  ├── PROTOCOL_NAME: str = ""     # overridden: "ASCOM" / "ALPACA"
  ├── UPDATE_RATE: float = 0.5
  ├── __init__(parent)            # all 14 shared attributes
  ├── getDeviceProp()             # raises NotImplementedError (abstract)
  ├── setDeviceProp()             # raises NotImplementedError (abstract)
  ├── callDeviceMethod()          # raises NotImplementedError (abstract)
  ├── setDevicePropQueued()       # concrete – shared
  ├── callDeviceMethodQueued()    # concrete – shared
  ├── getAndStoreDeviceProp()     # concrete – shared
  ├── connectDevice()             # concrete – shared
  ├── getInitialConfig()          # concrete – shared
  ├── pollData()                  # concrete – pass
  ├── processCommandQueue()       # concrete – shared
  ├── handleDeviceConnect()       # concrete – shared
  ├── handleDeviceDisconnect()    # concrete – shared
  ├── runnerCommunicationLoop()   # concrete – shared
  └── stopCommunication()         # concrete – shared

CommandItem (dataclass)           # moved from both files to this module
```

### 3.2 Updated: `src/mw4/base/ascomClass.py`

`AscomClass` inherits from `AlpacaAscomCommon` instead of `DriverData`.

**Remove** (now in common):
- `CommandItem` dataclass
- `connectDevice`, `getInitialConfig`, `pollData`, `processCommandQueue`
- `handleDeviceConnect`, `handleDeviceDisconnect`, `runnerCommunicationLoop`
- `setDevicePropQueued`, `callDeviceMethodQueued`, `getAndStoreDeviceProp`
- `stopCommunication`

**Change**:
- Base class: `DriverData` → `AlpacaAscomCommon`
- Rename `getAscomProperty` → `getDeviceProp`
- Rename `setAscomProperty` → `setDeviceProp`
- Rename `callAscomMethod` → `callDeviceMethod`
- Rename `setAscomPropertyQueued` → `setDevicePropQueued` (also in `stopCommunication` before removal)
- Add `PROTOCOL_NAME = "ASCOM"`
- Update `runnerCoreLoop` internal calls to `setDeviceProp`/`getDeviceProp`

**Keep** (ASCOM-specific):
- Windows platform guard (`if platform.system() == "Windows"`)
- `workerRunnerCoreLoop` attribute in `__init__`
- `defaultConfig` (`{"deviceName": ""}`)
- `runnerCoreLoop` (COM: `CoInitialize`, `Dispatch`, `CoUninitialize`;
  the `finally` block calls `setDeviceProp("Connected", False)` directly
  as a safety net in the COM-initialized thread)
- `startCommunication` (guards on `deviceName`, starts `workerRunnerCoreLoop`)
- `selectAscomDriver`

### 3.3 Updated: `src/mw4/base/alpacaClass.py`

`AlpacaClass` inherits from `AlpacaAscomCommon` instead of `DriverData`.

**Remove** (now in common):
- `CommandItem` dataclass
- `connectDevice`, `getInitialConfig`, `pollData`, `processCommandQueue`
- `handleDeviceConnect`, `handleDeviceDisconnect`, `runnerCommunicationLoop`
- `setDevicePropQueued`, `callDeviceMethodQueued`, `getAndStoreDeviceProp`
- `stopCommunication`

**Change**:
- Base class: `DriverData` → `AlpacaAscomCommon`
- Add `PROTOCOL_NAME = "ALPACA"`

**Keep** (Alpaca-specific):
- `DEVICE_TYPE_MAP`
- Alpaca-specific `__init__` additions:
  `_host`, `_port`, `_hostaddress`, `protocol`, `apiVersion`,
  `number`, `workerCommunicationLoop`, `defaultConfig`
- `host`, `hostaddress`, `port`, `deviceName` properties with setters
- `getDeviceProp`, `setDeviceProp`, `callDeviceMethod`
  (use `AlpycaNotImplError` for `propertyExceptions`)
- `createAlpacaDevice`, `startCommunication`, `stopCommunication`
- `discoverAPIVersion`, `discoverAlpacaDevices`, `discoverDevices`

---

## 4. Logic Device Classes: Caller Impact

### 4.1 ASCOM Device Classes — Method Renames Required

All 9 ASCOM device classes use the old method names and must be updated.
The rename is a pure search-and-replace with no functional change.

| Source file (`src/mw4/logic/`)              | `getAndStoreAscomProperty` | `getAscomProperty` | `setAscomPropertyQueued` | `callAscomMethodQueued` | Total |
|---------------------------------------------|:--------------------------:|:------------------:|:------------------------:|:-----------------------:|:-----:|
| `camera/cameraAscom.py`                     | 18                         | 2                  | 8                        | 2                       | 30    |
| `dome/domeAscom.py`                         | 4                          | 2                  | 0                        | 5                       | 11    |
| `focuser/focuserAscom.py`                   | 1                          | 0                  | 0                        | 2                       | 3     |
| `filter/filterAscom.py`                     | 0                          | 2                  | 1                        | 0                       | 3     |
| `cover/coverAscom.py`                       | 0                          | 1                  | 0                        | 3                       | 4     |
| `lightPanel/lightPanelAscom.py`             | 2                          | 0                  | 0                        | 3                       | 5     |
| `environment/sensorWeatherAscom.py`         | 7                          | 0                  | 0                        | 0                       | 7     |
| `telescope/telescopeAscom.py`               | 0                          | 2                  | 0                        | 0                       | 2     |
| `powerswitch/pegasusUPBAscom.py`            | 25                         | 0                  | 0                        | 7                       | 32    |
| **Total**                                   | **57**                     | **9**              | **9**                    | **22**                  | **97**|

### 4.2 Alpaca Device Classes — No Method Renames Required

All 9 Alpaca device classes already use the correct generic names.
No functional changes are needed, only the minor `__init__` harmonisation
described in 4.3.

| Source file (`src/mw4/logic/`)             | Status                   |
|--------------------------------------------|--------------------------|
| `camera/cameraAlpaca.py`                   | no changes needed        |
| `dome/domeAlpaca.py`                       | no changes needed        |
| `focuser/focuserAlpaca.py`                 | no changes needed        |
| `filter/filterAlpaca.py`                   | no changes needed        |
| `cover/coverAlpaca.py`                     | harmonise `__init__`     |
| `lightPanel/lightPanelAlpaca.py`           | harmonise `__init__`     |
| `environment/sensorWeatherAlpaca.py`       | no changes needed        |
| `telescope/telescopeAlpaca.py`             | no changes needed        |
| `powerswitch/pegasusUPBAlpaca.py`          | no changes needed        |

### 4.3 `__init__` Harmonisation in Two Alpaca Classes

`coverAlpaca.py` and `lightPanelAlpaca.py` assign `self.alpacaSignals`
instead of `self.signals`. Rename `self.alpacaSignals` → `self.signals` for
consistency with all other device classes.

---

## 5. Intentional Behavioral Differences (Must Not Be Changed)

| Device | ASCOM file | Difference vs. Alpaca |
|--------|------------|-----------------------|
| Telescope | `telescopeAscom.py` | Multiplies `ApertureDiameter` and `FocalLength` by 1000 (m → mm) before storing. The Alpaca version stores the raw value. Both are correct per their respective protocol specifications. |
| SensorWeather | `sensorWeatherAscom.py` | Uses lowercase property names (`temperature`, `pressure`, `dewpoint`, …) as required by the ASCOM ObservingConditions interface. The Alpaca version uses PascalCase (`Temperature`, `Pressure`, `DewPoint`, …) as required by the Alpaca API. |

---

## 6. Test File Changes

### 6.1 New: `tests/unit_tests/base/test_alpacaAscomCommon.py`

A new platform-independent test file covering 100 % of `AlpacaAscomCommon`.
A concrete subclass (test double) implements `getDeviceProp`, `setDeviceProp`,
`callDeviceMethod` to exercise all shared methods.

| Test function                                    | Covers                                           |
|--------------------------------------------------|--------------------------------------------------|
| `test_commandItem`                               | `CommandItem` dataclass defaults and fields      |
| `test_init`                                      | all 14 shared `__init__` attributes              |
| `test_setDevicePropQueued`                       | enqueues correct `CommandItem`                   |
| `test_callDeviceMethodQueued`                    | enqueues correct `CommandItem` with kwargs       |
| `test_getAndStoreDeviceProp`                     | `getDeviceProp` + `storePropertyToData`          |
| `test_connectDevice_successFirst`                | connects on first retry                          |
| `test_connectDevice_successAfterRetry`           | connects after N retries                         |
| `test_connectDevice_allFail`                     | exhausts retries → `False`, emits msg            |
| `test_getInitialConfig`                          | stores Name, DriverVersion, DriverInfo           |
| `test_pollData`                                  | is a no-op (pass)                                |
| `test_processCommandQueue_empty`                 | returns immediately on empty queue               |
| `test_processCommandQueue_call`                  | dispatches `callDeviceMethod`                    |
| `test_processCommandQueue_callWithKwargs`        | dispatches with kwargs                           |
| `test_processCommandQueue_set`                   | dispatches `setDeviceProp`                       |
| `test_processCommandQueue_unknownType`           | logs warning for unknown `cmdType`               |
| `test_processCommandQueue_queueEmpty`            | handles `queue.Empty` gracefully                 |
| `test_handleDeviceConnect_fail`                  | `connectDevice` False → no signals emitted       |
| `test_handleDeviceConnect_success`               | sets flags, emits signals, calls config          |
| `test_handleDeviceDisconnect`                    | clears flag, emits signal and msg                |
| `test_runnerCommunicationLoop_stopImmediate`     | stops when event is set before first iteration   |
| `test_runnerCommunicationLoop_connectBranch`     | calls `handleDeviceConnect` when not connected   |
| `test_runnerCommunicationLoop_disconnectBranch`  | calls `handleDeviceDisconnect` when conn lost    |
| `test_runnerCommunicationLoop_pollCycle`         | calls `pollData` + `processCommandQueue`         |
| `test_getDeviceProp_notImplemented`              | raises `NotImplementedError`                     |
| `test_setDeviceProp_notImplemented`              | raises `NotImplementedError`                     |
| `test_callDeviceMethod_notImplemented`           | raises `NotImplementedError`                     |
| `test_stopCommunication`                         | sets stop event, queues disconnect, clears flags, emits signals and msg |

### 6.2 Updated: `tests/unit_tests/base/test_ascomClass.py`

Currently **46 tests** (Windows-only via `pytest.skip`).

**Remove** — migrated to `test_alpacaAscomCommon.py`:

| Test functions to remove (30 total) |
|-------------------------------------|
| `test_getAscomProperty_*` (4)       |
| `test_setAscomProperty_*` (3)       |
| `test_callAscomMethod_*` (5)        |
| `test_setAscomPropertyQueued` (1)   |
| `test_callAscomMethodQueued_*` (2)  |
| `test_getAndStoreAscomProperty` (1) |
| `test_processCommandQueue_*` (6)    |
| `test_connectDevice_*` (3)          |
| `test_getInitialConfig` (1)         |
| `test_pollData` (1)                 |
| `test_handleDeviceConnect_*` (2)    |
| `test_handleDeviceDisconnect` (1)   |
| `test_runnerCommunicationLoop_*` (5)|
| `test_stopCommunication` (1)        |

**Keep / rename** — ASCOM-specific (≈16 tests remain):

| Test functions to keep |
|------------------------|
| `test_init` (updated for new base class and `PROTOCOL_NAME`) |
| `test_getDeviceProp_*` (4, renamed from `getAscomProperty`) |
| `test_setDeviceProp_*` (3, renamed from `setAscomProperty`) |
| `test_callDeviceMethod_*` (5, renamed from `callAscomMethod`) |
| `test_runnerCoreLoop_*` (3) — COM-specific |
| `test_startCommunication_*` (2) — ASCOM-specific |
| `test_selectAscomDriver_*` (3) — ASCOM-specific |

### 6.3 Updated: `tests/unit_tests/base/test_alpacaClass.py`

Currently **53 tests**.

**Remove** — migrated to `test_alpacaAscomCommon.py`:

| Test functions to remove (36 total) |
|-------------------------------------|
| `test_getDeviceProp_*` (4)          |
| `test_setDeviceProp_*` (4)          |
| `test_callDeviceMethod_*` (4)       |
| `test_setDevicePropQueued_1` (1)    |
| `test_callDeviceMethodQueued_1` (1) |
| `test_getAndStoreDeviceProp` (1)    |
| `test_processCommandQueue_*` (7)    |
| `test_connectDevice_*` (3)          |
| `test_getInitialConfig` (1)         |
| `test_pollData` (1)                 |
| `test_handleDeviceConnect_*` (2)    |
| `test_handleDeviceDisconnect` (1)   |
| `test_runnerCommunicationLoop_*` (5)|
| `test_stopCommunication` (1)        |

**Keep** — Alpaca-specific (≈17 tests remain):

| Test functions to keep |
|------------------------|
| `test_init` (updated for new base class and `PROTOCOL_NAME`) |
| `test_properties_*` (3) — `host`, `hostaddress`, `port`, `deviceName` setters |
| `test_createAlpacaDevice_*` (3) — Alpaca-specific |
| `test_discoverAPIVersion_*` (3) — Alpaca-specific |
| `test_discoverAlpacaDevices_*` (3) — Alpaca-specific |
| `test_discoverDevices_*` (2) — Alpaca-specific |
| `test_startCommunication_*` (2) — Alpaca-specific |

### 6.4 Updated: Logic ASCOM Test Files (9 files)

In each file: rename all occurrences of old method names inside `mock.patch`
target strings, `assert_called_with`, and test function names.

| Test file                                          | Current tests |
|----------------------------------------------------|:-------------:|
| `logic/camera/test_cameraAscom.py`                 | 17            |
| `logic/dome/test_domeAscom.py`                     | 10            |
| `logic/focuser/test_focuserAscom.py`               | 3             |
| `logic/filter/test_filterAscom.py`                 | 6             |
| `logic/cover/test_coverAscom.py`                   | 5             |
| `logic/lightPanel/test_lightPanelAscom.py`         | 4             |
| `logic/environment/test_sensorWeatherAscom.py`     | 1             |
| `logic/telescope/test_telescopeAscom.py`           | 2             |
| `logic/powerswitch/test_pegasusUPBAscom.py`        | 13            |

### 6.5 Updated: Two Alpaca Logic Test Files

`test_coverAlpaca.py` and `test_lightPanelAlpaca.py`: replace all references
to `alpacaSignals` with `signals`.

| Test file                                        | Current tests |
|--------------------------------------------------|:-------------:|
| `logic/cover/test_coverAlpaca.py`               | 5             |
| `logic/lightPanel/test_lightPanelAlpaca.py`     | 4             |

All other Alpaca logic test files: **no changes required**.

---

## 7. Implementation Steps

1. **Create `src/mw4/base/alpacaAscomCommon.py`**  
   Define `CommandItem` dataclass and implement `AlpacaAscomCommon(DriverData)`
   with all shared concrete methods including `stopCommunication`. Declare
   `getDeviceProp`, `setDeviceProp`, `callDeviceMethod` as raising
   `NotImplementedError`.

2. **Refactor `src/mw4/base/ascomClass.py`**  
   - Change import + base class to `AlpacaAscomCommon`  
   - Add `PROTOCOL_NAME = "ASCOM"`  
   - Apply the 6 method renames (Section 1)  
   - Remove all methods now in common  
   - Update `runnerCoreLoop` to use `setDeviceProp` / `getDeviceProp`

3. **Refactor `src/mw4/base/alpacaClass.py`**  
   - Change import + base class to `AlpacaAscomCommon`  
   - Add `PROTOCOL_NAME = "ALPACA"`  
   - Remove all methods now in common (including `stopCommunication`)

4. **Update all 9 ASCOM logic source files** (Section 4.1)  
   Apply 97 method-name replacements.

5. **Harmonise `coverAlpaca.py` and `lightPanelAlpaca.py`** (Section 4.3)  
   Rename `self.alpacaSignals` → `self.signals`.

6. **Create `tests/unit_tests/base/test_alpacaAscomCommon.py`**  
   Implement all 26 tests from Section 6.1.

7. **Update `tests/unit_tests/base/test_ascomClass.py`** (Section 6.2)  
   Remove 29 migrated tests; rename remaining test functions.

8. **Update `tests/unit_tests/base/test_alpacaClass.py`** (Section 6.3)  
   Remove 35 migrated tests.

9. **Update the 9 ASCOM logic test files** (Section 6.4).

10. **Update `test_coverAlpaca.py` and `test_lightPanelAlpaca.py`**
    (Section 6.5).

11. **Run Ruff** — format and lint all changed files; fix all findings.

12. **Run full test suite** with 100 % coverage check:
    ```
    pytest --cov=src/mw4 --cov-report=term-missing tests/unit_tests/
    ```

---

## 8. Risk & Compatibility Notes

- The 97 call-site renames are purely mechanical; signatures and behaviour
  are identical.
- `runnerCoreLoop` in `AscomClass` remains ASCOM-only (COM threading model).
  Its `finally` block calls `setDeviceProp("Connected", False)` directly
  — this is a safety-net disconnect in the COM-initialized thread and must
  stay even after `stopCommunication` moves to common. The common
  `stopCommunication` queues the same command via `setDevicePropQueued`,
  but the queue may not be processed if the loop exits immediately; the
  `finally` block guarantees the actual disconnection.
- `stopCommunication` is now shared: both ASCOM and Alpaca use
  `setDevicePropQueued("Connected", False)` — the only previous difference
  was the hardcoded protocol string (`"ASCOM"` / `"ALPACA"`), which is
  replaced by `PROTOCOL_NAME`.
- `startCommunication` still differs between ASCOM and Alpaca:
  ASCOM guards on `deviceName` and starts `runnerCoreLoop` via
  `workerRunnerCoreLoop`; Alpaca calls `createAlpacaDevice` and starts
  `runnerCommunicationLoop` directly. Both stay class-specific.
- `PROTOCOL_NAME` provides the protocol label for all shared log/message
  calls, making `AlpacaAscomCommon` fully protocol-agnostic.
- `test_ascomClass.py` is Windows-only. The new `test_alpacaAscomCommon.py`
  must be platform-independent to achieve 100 % coverage on all platforms.

