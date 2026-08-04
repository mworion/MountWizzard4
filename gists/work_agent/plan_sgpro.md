# Plan: Add SGPro Protocol Support to MountWizzard4 (Camera Use-Case)

## Scope
This plan covers only the **logic/protocol layer** for adding Sequence Generator Pro (SGPro) camera support. UI changes (separate SGPro tab in `devicePopup.ui`) are assumed to be added separately and are therefore out of scope here. Existing ALPACA/ASCOM code must not be modified.

## Goal
Introduce a generic `SGProClass` protocol base and a single camera driver `CameraSGPro`, integrated into the existing camera dispatcher so SGPro becomes a selectable camera framework alongside INDI, ALPACA and ASCOM.

## Architecture Decision
`SGProClass` will **not** inherit from `AlpacaAscomCommon`. Although both protocols use HTTP, their interaction models differ:

- ALPACA/ASCOM are **property/method based**: a device object exposes `Connected`, `CameraState`, `StartExposure(...)`, etc.
- SGPro is **endpoint based**: explicit REST URLs such as `connectdevice/Camera/<name>`, `image`, `abortimage`, `devicestatus/Camera`.

Reusing `AlpacaAscomCommon` would force `SGProClass` to override almost every lifecycle method and to fake the `getDeviceProp` / `setDeviceProp` / `callDeviceMethod` abstraction. That creates more indirection than value. Instead, `SGProClass` stays a standalone protocol class (inheriting only from `DriverData`) but exposes the **same public lifecycle interface** as `AlpacaAscomCommon` and uses **method names aligned with the ALPACA implementation**.

## 1. Analysis of Current Code

### 1.1 ALPACA camera stack (reference, unchanged)
```
src/mw4/base/alpacaAscomCommon.py   # common lifecycle: connect, poll, queue, stop
src/mw4/base/alpacaClass.py          # ALPACA-specific device creation / discovery
src/mw4/logic/camera/cameraAlpacaAscomBase.py  # shared camera behaviour
src/mw4/logic/camera/cameraAlpaca.py           # thin mixin: CameraAlpacaAscomBase + AlpacaClass
```

`CameraAlpaca` is essentially empty: it combines `CameraAlpacaAscomBase` (camera API) with `AlpacaClass` (protocol). The same pattern should be used for SGPro.

### 1.2 SGPro gist stack (starting point)
```
gists/sgpro/sgproClass.py      # SGProClass – HTTP/REST protocol class
gists/sgpro/cameraSGPro.py      # CameraSGPro – camera driver
```

Observations:
- `SGProClass` currently inherits from `DriverData` and re-implements large parts of the lifecycle that also exist in `AlpacaAscomCommon` (command queue, communication loop, connect/disconnect handling).
- `CameraSGPro` already implements the camera contract (`expose`, `abort`, `sendCoolerSwitch`, `sendCoolerTemp`, `sendOffset`, `sendGain`, `sendDownloadMode`) but is not connected to the production `Camera` dispatcher.
- The SGPro API is HTTP-based (`requests`), similar in transport to ALPACA but with a different interaction model: explicit REST endpoints (`connectdevice/...`, `image`, `abortimage`, `devicestatus/Camera`) instead of device properties/methods. This makes direct reuse of `AlpacaAscomCommon` awkward.

## 2. Target Architecture

```
DriverData
   ├── AlpacaAscomCommon          (existing, unchanged)
   │      ├── AlpacaClass         (existing, unchanged)
   │      └── AscomClass          (existing, unchanged)
   └── SGProClass                 (new, moved from gist)

Camera
   ├── run["indi"]   = CameraIndi
   ├── run["alpaca"] = CameraAlpaca
   ├── run["ascom"]  = CameraAscom   (Windows)
   └── run["sgpro"]  = CameraSGPro   (new)
```

`SGProClass` is a **generic protocol class** (not tied to a specific device type), but this plan only wires it up for the **camera** use-case. Future device types can reuse the same class later. It mirrors the public surface of `AlpacaAscomCommon` without sharing its property-based internals.

## 3. Required Changes

### 3.1 Create `../../src/mw4/base/sgproClass.py`
Move the gist implementation into the production tree as a standalone protocol class. It keeps its own lifecycle implementation because the SGPro interaction model does not map cleanly onto the property-based `AlpacaAscomCommon` base.

Keep:
- `CommandItem` dataclass.
- `DeviceConfigSGPro` dataclass with fields:
  - `deviceName: str = ""`
  - `hostAddress: str = "127.0.0.1"`
  - `port: int = 59590`
  - `UPDATE_RATE: float = 0.25`
  - `PROTOCOL_NAME: str = "SGPro"`

Add class constants:
- `PROTOCOL_NAME: str = "SGPro"`
- `SGPRO_TIMEOUT: int = 3`
- `DEVICE_TYPE: str = "Camera"`

Public lifecycle interface (same names as in `AlpacaAscomCommon`):
- `startCommunication() -> None`
- `stopCommunication() -> None`
- `connectDevice() -> bool`
- `handleDeviceConnect() -> None`
- `handleDeviceDisconnect() -> None`
- `runnerCommunicationLoop() -> None`
- `processCommandQueue() -> None`
- `callDeviceMethod(valueProp: str, **kwargs) -> dict`
- `callDeviceMethodQueued(valueProp: str, **kwargs) -> None`
- `getInitialConfig() -> None` (no-op base)
- `pollData() -> None` (no-op base)

SGPro-specific protocol methods (renamed to match ALPACA conventions):
- `requestProperty(valueProp: str, params: dict | None = None) -> dict`
  - HTTP GET when `params` is `None`, POST otherwise.
  - URL pattern: `http://{host}:{port}/{valueProp}?format=json`.
  - Return `{}` on any exception or non-200 status.
- `createDevice() -> bool`
  - Formerly `sgConnectDevice()`.
  - Endpoint: `connectdevice/{DEVICE_TYPE}/{deviceName}` with URL-encoded spaces.
  - Return `response.get("Success", False)`.
- `enumerateDevices() -> list`
  - Formerly `sgEnumerateDevice()`.
  - Endpoint: `enumdevices/{DEVICE_TYPE}`.
  - Return `response.get("Devices", [])`.
- `discoverDevices(deviceType: str) -> list`
  - Delegate to `enumerateDevices()`.
  - Keep `deviceType` parameter for interface compatibility; ignore it for now (SGPro camera API only).
- `pollDeviceStatus() -> None`
  - Formerly `workerPollStatus()`.
  - Endpoint: `devicestatus/{DEVICE_TYPE}`.
  - Update `Device.Status`, `Device.Message` and `deviceConnected` based on the `State` field.

Implementation notes:
- `connectDevice()` retries up to 25 times calling `createDevice()` with `time.sleep(0.2)` between attempts and emits an error message on failure.
- `runnerCommunicationLoop()` follows the same structure as `AlpacaAscomCommon` but uses `pollDeviceStatus()` to detect connection state instead of `getDeviceProp("Connected")`.
- `processCommandQueue()` supports only `cmdType == "call"` because SGPro has no property-setter concept.

### 3.2 Create `../../src/mw4/logic/camera/cameraSGPro.py`
Move the gist implementation into the production tree and adapt it to the production `Camera` dispatcher.

Class definition:
```python
class CameraSGPro(SGProClass):
    ...
```

Keep/adapt:
- `__init__(self, parent)` calling `super().__init__(parent=parent)`.
- `captureImage(params) -> tuple[bool, dict]` (formerly `sgCaptureImage`).
- `abortImage() -> bool` (formerly `sgAbortImage`).
- `getImagePath(receipt) -> bool` (formerly `sgGetImagePath`).
- `getCameraProps() -> tuple[bool, dict]` (formerly `sgGetCameraProps`).
- `workerExpose()` – calls `captureImage`, waits until SGPro status leaves "integrating", emits `exposed`/`downloaded`/`message` signals, waits for `getImagePath(receipt)` and finally calls `parent.updateImageFitsHeaderPointing`.
- `expose()` – starts `workerExpose` via `Worker` and connects its finished signal to `parent.exposeFinished`.
- `abort()` – calls `abortImage()`.
- `sendCoolerSwitch`, `sendCoolerTemp`, `sendOffset`, `sendGain`, `sendDownloadMode` – keep as no-ops or map to SGPro endpoints if available.

Add camera-specific data mapping:
- `getInitialConfig() -> None`
  - Store at least `CCD_BINNING.HOR_BIN = 1` so the `Camera.binning` setter works.
  - Optionally call `getCameraProps()` and store useful keys.
- `pollData() -> None`
  - Poll SGPro status and store minimal keys such as `Device.Status`, `Device.Message`.
  - If SGPro exposes temperature/cooler state, map them to `CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE`, `CCD_COOLER.COOLER_ON`, etc.

### 3.3 Wire into `../../src/mw4/logic/camera/camera.py`
Add SGPro as a camera framework without touching ALPACA/ASCOM/INDI code.

```python
from mw4.logic.camera.cameraSGPro import CameraSGPro

self.run = {
    "indi": CameraIndi(self),
    "alpaca": CameraAlpaca(self),
    "sgpro": CameraSGPro(self),
}
if platform.system() == "Windows":
    self.run["ascom"] = CameraAscom(self)
```

No other changes in `Camera` are required because all framework-specific calls are already dispatched through `self.run[self.framework]`.

### 3.4 Device registry / config persistence
No changes required. `DeviceRegistry.collectConfigFromSingleDevice` and `writeConfigToSingleDevice` already iterate over `self.d[device].run` and use dataclass fields, so the new `"sgpro"` entry and its `DeviceConfigSGPro` config will be persisted automatically once the framework is selected in the UI.

## 4. Out of Scope
- UI changes in `../../src_add/widgets/devicePopup.ui` and `../../src/mw4/gui/widgets/devicePopup_ui.py`.
- Wiring in `../../src/mw4/gui/extWindows/devicePopupW.py` (discovery button, framework2gui mapping, etc.).
- Changes to any ALPACA/ASCOM/INDI source files.

## 5. Tests

### 5.1 Move unit tests
Move `../sgpro/test_sgproClass.py` to `../../tests/unit_tests/base/test_sgproClass.py` and update imports:
```python
from mw4.base.sgproClass import CommandItem, DeviceConfigSGPro, SGProClass
```

### 5.2 Add camera driver tests
Create `../../tests/unit_tests/logic/camera/test_cameraSGPro.py` covering:
- `CameraSGPro` instantiation.
- Inheritance from `SGProClass`.
- `expose()` starts a worker.
- `abort()` returns result of `abortImage()`.
- `sendCoolerSwitch`, `sendCoolerTemp`, `sendOffset`, `sendGain`, `sendDownloadMode` are callable.
- `getInitialConfig()` stores expected data keys.

### 5.3 Update camera dispatcher test
In `../../tests/unit_tests/logic/camera/test_camera.py` add:
```python
def test_camera_sgpro_in_run(function):
    assert "sgpro" in function.run
    assert function.run["sgpro"] is not None
```

## 6. Acceptance Criteria
- [ ] `../../src/mw4/base/sgproClass.py` exists as a standalone protocol class with the same public lifecycle interface as `AlpacaAscomCommon`.
- [ ] `../../src/mw4/logic/camera/cameraSGPro.py` exists and implements the camera contract.
- [ ] `Camera.run` contains a `"sgpro"` entry.
- [ ] Existing ALPACA/ASCOM/INDI camera code is unchanged.
- [ ] Unit tests for `SGProClass` and `CameraSGPro` pass.
- [ ] Overall test coverage remains at 100 % for non-platform-guarded code.
- [ ] Ruff linting passes.
