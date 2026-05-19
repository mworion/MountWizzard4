# Plan: Refactor CameraSGPro & CameraNINA → CameraSgproNinaBase

**Date:** 2026-05-19
**Scope:** `src/mw4/logic/camera/cameraSGPro.py`,
`src/mw4/logic/camera/cameraNINA.py`
**Goal:** Extract shared code into a new mixin base class
`CameraSgproNinaBase` to eliminate duplication, analogous to the
`SgproNinaCommon` refactoring of the base protocol classes.

---

## 1. Current state – precise diff result

`diff cameraSGPro.py cameraNINA.py` reveals exactly **3 differences**:

| Line | cameraSGPro.py | cameraNINA.py |
|------|----------------|---------------|
| 16 | `from mw4.base.sgproClass import SGProClass` | `from mw4.base.ninaClass import NINAClass` |
| 20 | `class CameraSGPro(SGProClass):` | `class CameraNINA(NINAClass):` |
| `__init__` | sets `parent`, `app`, `data` **before** `super().__init__`, then `threadPool`, `signals` **after** | calls `super().__init__` **first**, then sets all attributes |

All constants, method bodies, and imports other than the class base
are **byte-for-byte identical** in both files.

### 1.1 Gap between current source and test files

The test files are already written for the **target refactored state**
and currently do **not** fully match the source code (see existing
`plan_refactor_sgpro_nina_common.md`, section 1.1 for the analogous base
class situation).

**`test_cameraNINA.py` expects `CameraNINA` to expose:**
- `getCameraTemp()` – unprefixed HTTP implementation
- `setCameraTemp()` – unprefixed HTTP implementation
- `captureImage()` – unprefixed HTTP implementation
- `abortImage()` – unprefixed HTTP implementation
- `getImagePath()` – unprefixed HTTP implementation
- `getCameraProps()` – unprefixed HTTP implementation
- `abort()` returns `self.abortImage()` with return value
- `workerExpose()` calls `self.captureImage()`

**`test_cameraSGPro.py` expects `CameraSGPro` to expose:**
- `sgGetCameraTemp()` instead of `getCameraTemp()`
- `sgSetCameraTemp()` instead of `setCameraTemp()`
- `sgCaptureImage()` instead of `captureImage()`
- `sgAbortImage()` instead of `abortImage()`
- `sgGetImagePath()` instead of `getImagePath()`
- `sgGetCameraProps()` instead of `getCameraProps()`
- `workerExpose()` calls `self.sgCaptureImage()` (via bridge)
- `abort()` calls `self.sgAbortImage()` (via bridge)

---

## 2. Target architecture

```
CameraSgproNinaBase   (NEW: src/mw4/logic/camera/cameraSgproNinaBase.py)
    │
    │  Common methods (moved here from both subclasses):
    │    workerGetInitialConfig() → storePropertyToData(1, "CCD_BINNING.HOR_BIN")
    │    sendDownloadMode()       → pass
    │    waitFunc()               → "integrating" in self.data.get("Device.Message")
    │    workerExpose()           → calls self.captureImage() [abstract stub]
    │                                and self.getImagePath   [abstract stub]
    │    expose()                 → Worker(self.workerExpose)
    │    abort()                  → return self.abortImage() [abstract stub]
    │    sendCoolerSwitch()       → pass
    │    sendCoolerTemp()         → pass
    │    sendOffset()             → pass
    │    sendGain()               → pass
    │
    │  Abstract stubs (raise NotImplementedError):
    │    getCameraTemp()          → tuple[bool, dict]
    │    setCameraTemp()          → bool
    │    captureImage()           → tuple[bool, dict]
    │    abortImage()             → bool
    │    getImagePath()           → bool
    │    getCameraProps()         → tuple[bool, dict]
    │
    ├── CameraNINA(NINAClass, CameraSgproNinaBase)
    │     # HTTP implementations (unprefixed names):
    │     getCameraTemp()   → requestProperty("cameratemp")
    │     setCameraTemp()   → requestProperty(f"setcameratemp/{temperature}")
    │     captureImage()    → requestProperty("image", params=params)
    │     abortImage()      → requestProperty("abortimage")
    │     getImagePath()    → requestProperty(f"imagepath/{receipt}")
    │     getCameraProps()  → requestProperty("cameraprops")
    │     # captureImage / abortImage / getImagePath also fulfill abstract stubs
    │
    └── CameraSGPro(SGProClass, CameraSgproNinaBase)
          # Protocol-specific sg-prefixed HTTP implementations:
          sgGetCameraTemp()   → requestProperty("cameratemp")
          sgSetCameraTemp()   → requestProperty(f"setcameratemp/{temperature}")
          sgCaptureImage()    → requestProperty("image", params=params)
          sgAbortImage()      → requestProperty("abortimage")
          sgGetImagePath()    → requestProperty(f"imagepath/{receipt}")
          sgGetCameraProps()  → requestProperty("cameraprops")
          # Bridge implementations (fulfill abstract stubs):
          getCameraTemp()     → return self.sgGetCameraTemp()
          setCameraTemp()     → return self.sgSetCameraTemp(temperature)
          captureImage()      → return self.sgCaptureImage(params)
          abortImage()        → return self.sgAbortImage()
          getImagePath()      → return self.sgGetImagePath(receipt)
          getCameraProps()    → return self.sgGetCameraProps()
```

### 2.1 Inheritance and MRO

`CameraSgproNinaBase` does **not** inherit from any protocol class
(it is a pure mixin). The MRO for both camera classes resolves without
conflicts:

```
CameraNINA  → NINAClass  → SgproNinaCommon → DriverData
                         → CameraSgproNinaBase → object
CameraSGPro → SGProClass → SgproNinaCommon → DriverData
                         → CameraSgproNinaBase → object
```

### 2.2 workerExpose call chain for SGPro

`CameraSgproNinaBase.workerExpose()` calls `self.captureImage(params)`
and passes `self.getImagePath` as a callback to `self.parent.waitFinish`.

In `CameraSGPro`, the bridge method `captureImage()` delegates to
`sgCaptureImage()`. Therefore, the test mock on `sgCaptureImage` is
reached transitively:

```
workerExpose()  →  self.captureImage()  →  self.sgCaptureImage()  [mocked]
```

### 2.3 abort call chain for SGPro

`CameraSgproNinaBase.abort()` calls `return self.abortImage()`.
In `CameraSGPro`, `abortImage()` delegates to `sgAbortImage()`:

```
abort()  →  self.abortImage()  →  self.sgAbortImage()  [mocked]
```

### 2.4 __init__ placement

The `__init__` methods remain in the **subclasses** (`CameraNINA` and
`CameraSGPro`), preserving their current order of `super().__init__`
calls and attribute overrides (`threadPool`, `signals`, `worker`).
`CameraSgproNinaBase` does **not** define an `__init__`, avoiding MRO
complications.

---

## 3. Detailed implementation steps

### Step 3.1 – Create
`src/mw4/logic/camera/cameraSgproNinaBase.py`

New class `CameraSgproNinaBase` (no parent class beyond `object`) with:
- All common methods listed in section 2 above (10 methods)
- Six abstract stubs raising `NotImplementedError` with type annotations
- Standard file header (copyright comment block)
- Imports: `from pathlib import Path`, `from typing import Any`,
  `from mw4.base.tpool import Worker`

```python
class CameraSgproNinaBase:

    def workerGetInitialConfig(self) -> None:
        self.storePropertyToData(1, "CCD_BINNING.HOR_BIN")

    def sendDownloadMode(self) -> None:
        pass

    def waitFunc(self) -> bool:
        return "integrating" in self.data.get("Device.Message")

    def workerExpose(self) -> None:
        params = {
            "BinningMode": self.parent.binning,
            "ExposureLength": max(self.parent.exposureTime, 1),
            "Path": str(self.parent.imagePath),
        }
        suc, response = self.captureImage(params=params)
        if not suc:
            self.log.debug(f"No capture image. {response}")
            return
        receipt = response.get("Receipt", "")
        if not receipt:
            self.log.debug(f"No receipt received. {response}")
            return
        self.parent.waitStart()
        self.parent.waitExposed(self.parent.exposureTime, self.waitFunc)
        self.signals.exposed.emit(self.parent.imagePath)
        self.parent.waitDownload()
        self.signals.downloaded.emit(self.parent.imagePath)
        self.parent.waitSave()
        self.parent.waitFinish(self.getImagePath, receipt)
        if not self.parent.exposing:
            self.parent.imagePath = Path()
        else:
            self.parent.imagePath.with_suffix(".fit")
            self.parent.updateImageFitsHeaderPointing()

    def expose(self) -> None:
        self.worker = Worker(self.workerExpose)
        self.worker.signals.finished.connect(self.parent.exposeFinished)
        self.threadPool.start(self.worker)

    def abort(self) -> bool:
        return self.abortImage()

    def sendCoolerSwitch(self, coolerOn: bool = False) -> None:
        pass

    def sendCoolerTemp(self, temperature: float = 0) -> None:
        pass

    def sendOffset(self, offset: int = 0) -> None:
        pass

    def sendGain(self, gain: int = 0) -> None:
        pass

    # Abstract stubs – must be implemented by subclasses
    def getCameraTemp(self) -> tuple[bool, dict]:
        raise NotImplementedError

    def setCameraTemp(self, temperature: float) -> bool:
        raise NotImplementedError

    def captureImage(self, params: dict) -> tuple[bool, dict]:
        raise NotImplementedError

    def abortImage(self) -> bool:
        raise NotImplementedError

    def getImagePath(self, receipt: str) -> bool:
        raise NotImplementedError

    def getCameraProps(self) -> tuple[bool, dict]:
        raise NotImplementedError
```

### Step 3.2 – Rewrite `src/mw4/logic/camera/cameraNINA.py`

```python
from mw4.base.ninaClass import NINAClass
from mw4.base.tpool import Worker
from mw4.logic.camera.cameraSgproNinaBase import CameraSgproNinaBase
from pathlib import Path
from typing import Any


class CameraNINA(NINAClass, CameraSgproNinaBase):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        self.signals = parent.signals
        self.threadPool = parent.threadPool
        self.worker: Worker | None = None

    def getCameraTemp(self) -> tuple[bool, dict]:
        response = self.requestProperty("cameratemp")
        return response.get("Success", False), response

    def setCameraTemp(self, temperature: float) -> bool:
        response = self.requestProperty(f"setcameratemp/{temperature}")
        return response.get("Success", False)

    def captureImage(self, params: dict) -> tuple[bool, dict]:
        response = self.requestProperty("image", params=params)
        return response.get("Success", False), response

    def abortImage(self) -> bool:
        response = self.requestProperty("abortimage")
        return response.get("Success", False)

    def getImagePath(self, receipt: str) -> bool:
        response = self.requestProperty(f"imagepath/{receipt}")
        return response.get("Success", False)

    def getCameraProps(self) -> tuple[bool, dict]:
        response = self.requestProperty("cameraprops")
        return response.get("Success", False), response
```

Remove: `Path` import (still needed for `workerExpose` in base),
`Worker` import (needed for `__init__` type annotation). Keep as is.

### Step 3.3 – Rewrite `src/mw4/logic/camera/cameraSGPro.py`

```python
from mw4.base.sgproClass import SGProClass
from mw4.base.tpool import Worker
from mw4.logic.camera.cameraSgproNinaBase import CameraSgproNinaBase
from typing import Any


class CameraSGPro(SGProClass, CameraSgproNinaBase):
    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        super().__init__(parent=parent)
        self.threadPool = parent.threadPool
        self.signals = parent.signals
        self.worker: Worker | None = None

    # Protocol-specific sg-prefixed HTTP implementations:
    def sgGetCameraTemp(self) -> tuple[bool, dict]:
        response = self.requestProperty("cameratemp")
        return response.get("Success", False), response

    def sgSetCameraTemp(self, temperature: float) -> bool:
        response = self.requestProperty(f"setcameratemp/{temperature}")
        return response.get("Success", False)

    def sgCaptureImage(self, params: dict) -> tuple[bool, dict]:
        response = self.requestProperty("image", params=params)
        return response.get("Success", False), response

    def sgAbortImage(self) -> bool:
        response = self.requestProperty("abortimage")
        return response.get("Success", False)

    def sgGetImagePath(self, receipt: str) -> bool:
        response = self.requestProperty(f"imagepath/{receipt}")
        return response.get("Success", False)

    def sgGetCameraProps(self) -> tuple[bool, dict]:
        response = self.requestProperty("cameraprops")
        return response.get("Success", False), response

    # Bridge implementations (fulfill abstract stubs from base class):
    def getCameraTemp(self) -> tuple[bool, dict]:
        return self.sgGetCameraTemp()

    def setCameraTemp(self, temperature: float) -> bool:
        return self.sgSetCameraTemp(temperature)

    def captureImage(self, params: dict) -> tuple[bool, dict]:
        return self.sgCaptureImage(params)

    def abortImage(self) -> bool:
        return self.sgAbortImage()

    def getImagePath(self, receipt: str) -> bool:
        return self.sgGetImagePath(receipt)

    def getCameraProps(self) -> tuple[bool, dict]:
        return self.sgGetCameraProps()
```

### Step 3.4 – Create
`tests/unit_tests/logic/camera/test_cameraSgproNinaBase.py`

Cover every branch of `CameraSgproNinaBase` using a concrete test
double that inherits from `CameraSgproNinaBase` and implements all
abstract stubs:

```python
class ConcreteCameraBase(CameraSgproNinaBase):
    def getCameraTemp(self) -> tuple[bool, dict]: ...
    def setCameraTemp(self, temperature: float) -> bool: ...
    def captureImage(self, params: dict) -> tuple[bool, dict]: ...
    def abortImage(self) -> bool: ...
    def getImagePath(self, receipt: str) -> bool: ...
    def getCameraProps(self) -> tuple[bool, dict]: ...
```

Tests to cover (100 %):
- `test_workerGetInitialConfig` – verifies `CCD_BINNING.HOR_BIN == 1`
- `test_sendDownloadMode` – call returns None
- `test_waitFunc_true` – `Device.Message` contains "integrating"
- `test_waitFunc_false` – `Device.Message` does not contain "integrating"
- `test_workerExpose_1` – `captureImage` returns `(False, {})` → early return
- `test_workerExpose_2` – `captureImage` returns `(True, {})`,
  no receipt → early return
- `test_workerExpose_3` – full path, `parent.exposing = True`
- `test_workerExpose_4` – full path, `parent.exposing = False`
  (imagePath reset to `Path()`)
- `test_expose_1` – Worker is queued into threadPool
- `test_abort_1` – delegates to `abortImage()`, returns result
- `test_sendCoolerSwitch_1` – passes without error
- `test_sendCoolerTemp_1` – passes without error
- `test_sendOffset_1` – passes without error
- `test_sendGain_1` – passes without error
- `test_getCameraTemp_notImplemented` – raises `NotImplementedError`
- `test_setCameraTemp_notImplemented` – raises `NotImplementedError`
- `test_captureImage_notImplemented` – raises `NotImplementedError`
- `test_abortImage_notImplemented` – raises `NotImplementedError`
- `test_getImagePath_notImplemented` – raises `NotImplementedError`
- `test_getCameraProps_notImplemented` – raises `NotImplementedError`

### Step 3.5 – Update
`tests/unit_tests/logic/camera/test_cameraSGPro.py`

**Rename / update** existing tests that now call the `sg`-prefixed methods
(tests already match target state per section 1.1 – verify no changes
needed).

**Remove** tests for `workerExpose`, `expose`, `abort`,
`sendCoolerSwitch`, `sendCoolerTemp`, `sendOffset`, `sendGain`,
`workerGetInitialConfig`, `sendDownloadMode`, `waitFunc` if they are now
fully covered by `test_cameraSgproNinaBase.py`.
Keep SGPro-specific tests to reach 100 % coverage:
- `test_sgGetCameraTemp_1`, `test_sgGetCameraTemp_2`
- `test_sgSetCameraTemp_1`, `test_sgSetCameraTemp_2`
- `test_sgCaptureImage_1`, `test_sgCaptureImage_2`
- `test_sgAbortImage_1`, `test_sgAbortImage_2`
- `test_sgGetImagePath_1`, `test_sgGetImagePath_2`
- `test_sgGetCameraProps_1`, `test_sgGetCameraProps_2`
- Bridge delegation tests (covers bridge methods in CameraSGPro):
  - `test_getCameraTemp_bridge`
  - `test_setCameraTemp_bridge`
  - `test_captureImage_bridge`
  - `test_abortImage_bridge`
  - `test_getImagePath_bridge`
  - `test_getCameraProps_bridge`

### Step 3.6 – Update
`tests/unit_tests/logic/camera/test_cameraNINA.py`

**Remove** tests now fully covered by `test_cameraSgproNinaBase.py`:
- `test_workerGetInitialConfig_1`
- `test_sendDownloadMode_1`
- `test_waitFunc`
- `test_workerExpose_1` through `test_workerExpose_4`
- `test_expose_1`
- `test_abort_1` (covered by base + abortImage delegation)
- `test_sendCoolerSwitch_1`
- `test_sendCoolerTemp_1`
- `test_sendOffset_2`
- `test_sendGain_2`

**Keep** NINA-specific tests (HTTP implementations, not in base):
- `test_getCameraTemp_1`, `test_getCameraTemp_2`
- `test_setCameraTemp_1`, `test_setCameraTemp_2`
- `test_captureImage_1`, `test_captureImage_2`
- `test_abortImage_1`, `test_abortImage_2`
- `test_getImagePath_1`, `test_getImagePath_2`
- `test_getCameraProps_1`, `test_getCameraProps_2`
- `test_abort_1` (kept to cover `abort()` → `abortImage()` return value
  delegation, specific to NINA)

### Step 3.7 – Run formatter / linter

```bash
ruff format src/mw4/logic/camera/cameraSgproNinaBase.py \
            src/mw4/logic/camera/cameraNINA.py \
            src/mw4/logic/camera/cameraSGPro.py
ruff check  src/mw4/logic/camera/cameraSgproNinaBase.py \
            src/mw4/logic/camera/cameraNINA.py \
            src/mw4/logic/camera/cameraSGPro.py \
            tests/unit_tests/logic/camera/test_cameraSgproNinaBase.py \
            tests/unit_tests/logic/camera/test_cameraNINA.py \
            tests/unit_tests/logic/camera/test_cameraSGPro.py
```

Resolve all findings before proceeding.

### Step 3.8 – Coverage check for all three modules

```bash
pytest tests/unit_tests/logic/camera/test_cameraSgproNinaBase.py \
       tests/unit_tests/logic/camera/test_cameraNINA.py \
       tests/unit_tests/logic/camera/test_cameraSGPro.py \
       --cov=src/mw4/logic/camera/cameraSgproNinaBase \
       --cov=src/mw4/logic/camera/cameraNINA \
       --cov=src/mw4/logic/camera/cameraSGPro \
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
| `src/mw4/logic/camera/cameraSgproNinaBase.py` | **CREATE** |
| `src/mw4/logic/camera/cameraNINA.py` | **REWRITE** (HTTP methods only + updated inheritance) |
| `src/mw4/logic/camera/cameraSGPro.py` | **REWRITE** (sg-methods + bridges + updated inheritance) |
| `tests/unit_tests/logic/camera/test_cameraSgproNinaBase.py` | **CREATE** |
| `tests/unit_tests/logic/camera/test_cameraNINA.py` | **MODIFY** (remove duplicated tests) |
| `tests/unit_tests/logic/camera/test_cameraSGPro.py` | **MODIFY** (sg-prefix + remove duplicated tests) |

No changes required in `camera.py`, `cameraAlpaca.py`, or any other
file – the public interface of `CameraNINA` and `CameraSGPro` is
preserved or extended with the `sg`-prefixed names.

---

## 5. Key design decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | `CameraSgproNinaBase` as pure mixin (no parent class) | Avoids diamond inheritance conflicts with `SgproNinaCommon`; both camera classes already inherit protocol-specific behaviour from their respective base classes |
| 2 | Abstract stubs for `captureImage`, `abortImage`, `getImagePath` | Called internally by `workerExpose` and `abort` in the base; stubs enforce subclass implementation and enable testing of `NotImplementedError` branches |
| 3 | SGPro bridge methods (`captureImage → sgCaptureImage`) | Fulfils base class abstract contract while exposing `sg`-prefixed convention expected by tests; call chain `workerExpose → captureImage → sgCaptureImage` keeps `workerExpose` fully in the common base |
| 4 | NINA HTTP methods fulfil both roles | `captureImage` etc. in `CameraNINA` are simultaneously the HTTP implementation and the abstract stub fulfilment – no extra bridge layer needed |
| 5 | `__init__` stays in subclasses | Current super() call order differs between the two classes (`NINAClass` child calls super first, `SGProClass` child sets attributes before super); keeping inits separate avoids MRO-dependent subtleties |
| 6 | Remove workerExpose/expose/abort from both subclasses | All 10 common methods are entirely moved; no duplication remains |
| 7 | Additional abstract stubs for `getCameraTemp`, `setCameraTemp`, `getCameraProps` | Makes the full Camera API contract explicit on the base class; enables type-checking tooling to verify completeness of subclass implementations |

