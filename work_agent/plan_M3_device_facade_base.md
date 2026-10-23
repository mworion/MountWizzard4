# Plan M3 – remove copy-paste from the device facades

Source: `2026-10-20_review_copilot_open.md`, finding M3.
Status: **implemented** (all nine facades migrated; the "possible result" below is the
approach taken, with PEP 695 generics `DeviceFacade[AppT: HasThreadPool]` so camera and dome
keep their `AppProtocol` typing). Closed: `Measure`, `PlateSolve`, `Remote`, `KMRelay`,
`SeeingWeather`, `DirectWeather`, `HidController` and `Keypad` are deliberately not migrated
(own signals, custom start/stop or fixed framework).

## Findings (manual scan of `../src/mw4/logic/drivers`)

The framework back-ends are already DRY: per device there is one `*AlpacaAscomBase` class, and
`<Device>Alpaca` / `<Device>Ascom` are 9-line shells (`class X(Base, AlpacaClass): pass`).
Shared protocol code sits in `frameworks/alpacaAscomCommon.py`. No further extraction there.

The real copy-paste is one level up, in the **device facades** (`focuser.py`, `filter.py`,
`cover.py`, `telescope.py`, `lightPanel.py`, `sensorWeather.py`, `pegasusUPB.py`, and the
first part of `dome.py` / `camera.py`). Each repeats:

- the same `__init__` (`app`, `threadPool`, `signals`, `data`, `framework`),
- the same `run` table with `indi` / `alpaca` and the Windows factory block,
- identical `startCommunication` / `stopCommunication`,
- the same `log` and `DEVICE_TYPE` class attributes,
- one-line delegates `self.run[self.framework].<method>(...)`.

That is ~25 identical lines in 9 files, plus ~450 lines of near-identical facade tests
(`test_init`, `test_startCommunication`, `test_stopCommunication`, `test_<dev>Ascom_in_run`).

## Target

```
src/mw4/logic/drivers/frameworks/deviceFacade.py     new, DeviceFacade base class
tests/unit_tests/logic/drivers/frameworks/test_deviceFacade.py   new, covers the base once
```

Facades only declare their back-ends and their device specific methods.

## Rules

- No behaviour change; public names (`run`, `framework`, `data`, `signals`, `DEVICE_TYPE`,
  `startCommunication`, device methods) stay – `deviceRegistry` and the GUI tabs use them.
- Windows-only back-ends stay lazily constructed (classes only exist on Windows).
- Base class gets `AppProtocol`/`HasThreadPool` via the existing protocol types, no `app`
  type widening.
- Camera and dome set their extra attributes **before** the back-ends are built, because the
  back-end constructors read from the parent.
- Camera `sgpro` and the `ascom` factories stay in `windowsBackends`.
- 100 % coverage, camelCase, no leading underscores, line length 100.

## Steps

1. Add `DeviceFacade` (below). Test it once with a dummy subclass: run-table building,
   Windows factories (monkeypatch `IS_WINDOWS`), start/stop, `delegate`.
2. Migrate the simple facades one by one (focuser, filter, cover, telescope, sensorWeather,
   lightPanel, pegasusUPB). Run `pytest tests/unit_tests/logic/drivers/<dev>` after each.
3. Migrate `dome` and `camera` (extra state; call `buildBackends()` last).
4. Reduce each facade test file to the device specific delegates; the generic tests
   (`startCommunication`, `stopCommunication`, `run` table) live in `test_deviceFacade.py`.
   Keep one `*_ascom_in_run` test per device only where `test_testMapping` or windows
   coverage needs it.
5. Verify: `ruff`, `pyrefly`, `lint-imports`, full unit run with 100 % coverage.
6. Mark M3 done in `2026-10-20_review_copilot_open.md`.

## Risks

- Tests patching `mw4.logic.drivers.<dev>.<dev>.<Dev>Ascom` break if the Windows import
  moves. Mitigation: keep the `if platformInfo.IS_WINDOWS:` import in each facade module.
- `framework == ""` before configuration: base keeps today's `KeyError` behaviour in
  `startCommunication` (filter's `sendFilterNumber` guard stays in the filter facade).
- Expected gain: ~25 lines × 9 facades ≈ 200 source lines and ~300 test lines.

## Possible result (illustration, NOT applied)

`frameworks/deviceFacade.py`:

```python
import logging
from collections.abc import Callable
from mw4.base import platformInfo
from mw4.base.appProtocol import HasThreadPool
from mw4.base.signalsDevices import Signals
from typing import Any, ClassVar


class DeviceFacade:
    """common part of all device facades: back-end table, signals, start / stop."""

    log = logging.getLogger("MW4")
    DEVICE_TYPE: ClassVar[str] = ""

    def __init__(self, app: HasThreadPool) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        self.framework: str = ""
        self.run: dict[str, Any] = {}

    def buildBackends(
        self,
        backends: dict[str, Callable[[Any], Any]],
        windowsBackends: dict[str, Callable[[], Any]] | None = None,
    ) -> None:
        self.run = {name: backend(self) for name, backend in backends.items()}
        platformInfo.registerWindowsBackends(self.run, windowsBackends or {})

    def startCommunication(self) -> None:
        self.run[self.framework].startCommunication()

    def stopCommunication(self) -> None:
        self.run[self.framework].stopCommunication()
```

`focuser/focuser.py` (today 47 lines):

```python
from mw4.base import platformInfo
from mw4.base.appProtocol import HasThreadPool
from mw4.logic.drivers.focuser.focuserAlpaca import FocuserAlpaca
from mw4.logic.drivers.focuser.focuserIndi import FocuserIndi
from mw4.logic.drivers.frameworks.deviceFacade import DeviceFacade

if platformInfo.IS_WINDOWS:
    from mw4.logic.drivers.focuser.focuserAscom import FocuserAscom


class Focuser(DeviceFacade):
    DEVICE_TYPE = "focuser"

    def __init__(self, app: HasThreadPool) -> None:
        super().__init__(app)
        self.buildBackends(
            {"indi": FocuserIndi, "alpaca": FocuserAlpaca},
            {"ascom": lambda: FocuserAscom(self)},
        )

    def move(self, position: int) -> None:
        self.run[self.framework].move(position=position)

    def halt(self) -> None:
        self.run[self.framework].halt()
```

`camera/camera.py` keeps its own state, then ends `__init__` with:

```python
        super().__init__(app)
        self.exposing = False
        ...                       # extra camera attributes as today
        self.buildBackends(
            {"indi": CameraIndi, "alpaca": CameraAlpaca},
            {"sgpro": lambda: CameraSGPro(self), "ascom": lambda: CameraAscom(self)},
        )
```

Optional step 2 (not part of M3): the one-line delegates could be generated with a small
`delegate(name, **kwargs)` helper, but explicit methods keep type checking and grep-ability,
so they stay.

