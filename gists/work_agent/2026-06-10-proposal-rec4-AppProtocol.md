# Proposal: Recommendation #4 — Replace `app: Any` Seams With an `App` Protocol

**Status:** Proposal (no code change yet)
**Recommendation:** #4 in [2026-06-10-review.md](2026-06-10-review.md)
**Impact:** ★★★  **Effort:** M
**Goal:** Replace the ~20 `app: Any` parameters across `logic/`, `gui/`,
`base/`, and `mountcontrol/` with a single typed contract, without introducing
import cycles or runtime cost.

---

## 1. Problem Recap

Today, almost every device, window, and tab takes an untyped reference to the
application:

```python
# src/mw4/logic/camera/camera.py
class Camera:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.threadPool = app.threadPool
        ...

# src/mw4/gui/mainWaddon/tabMount_Move.py
class MountMove:
    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        ...
```

Consequences:

- **No static checking.** Typos like `self.app.dRegg["mount"]` are not caught.
- **Hidden dependency surface.** A reader cannot see *which* attributes a class
  actually uses on `app` without scanning the whole file.
- **Refactor friction.** Renaming or splitting a signal/attribute on
  `MountWizzard4` requires manual grep across the tree.
- **Test-stub drift.** `tests/unit_tests/unitTestAddOns/baseTestApp.App` must
  re-declare every signal/attribute by hand (and quietly diverges over time —
  the missing `MAX_THREAD_COUNT` we just had to add is a typical symptom).

The fix is to publish a *structural* type — a `Protocol` — that captures only
the surface area consumers actually rely on, and use it as the parameter type
in place of `Any`.

---

## 2. Why a `Protocol` (and not the concrete `MountWizzard4` class)

A `Protocol` (PEP 544) is structural: any object with the right attributes
satisfies it, with **no runtime check** and **no inheritance requirement**. This
gives us four properties we want simultaneously:

1. **No import cycles.** Logic modules must not import the GUI/`MountWizzard4`
   class. A `Protocol` can be imported freely because it is just a type.
2. **Test stubs satisfy it for free.** `baseTestApp.App` already exposes the
   right attributes; with a `Protocol`, that is *all* that is required — no
   inheritance, no registration.
3. **Narrow contracts.** Different layers can depend on smaller sub-protocols
   (`HasThreadPool`, `HasMessageBus`, `HasDeviceRegistry`) instead of pulling in
   the whole god-object surface.
4. **Zero runtime cost.** Protocols live in `typing` and are only consulted by
   type checkers (`mypy`, `pyright`, IDEs).

---

## 3. Proposed Layout

A single new module, `src/mw4/base/appProtocol.py`, defines the typed contracts.
It is imported under `TYPE_CHECKING` everywhere so it never causes a runtime
import cycle.

```python
# src/mw4/base/appProtocol.py
from __future__ import annotations

from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from PySide6.QtCore import QThreadPool, SignalInstance
    from mw4.base.deviceRegistry import DeviceRegistry
    from skyfield.jpllib import SpiceKernel


# --- Narrow capability protocols ----------------------------------------

class HasThreadPool(Protocol):
    threadPool: "QThreadPool"
    MAX_THREAD_COUNT: int


class HasMessageBus(Protocol):
    # msg.emit(level: int, source: str, title: str, body: str)
    msg: "SignalInstance"
    messageQueue: Queue


class HasDeviceRegistry(Protocol):
    dReg: "DeviceRegistry"
    config: dict[str, Any]


class HasCyclicSignals(Protocol):
    update0_1s: "SignalInstance"
    update1s: "SignalInstance"
    update3s: "SignalInstance"
    update10s: "SignalInstance"
    update30s: "SignalInstance"
    update3m: "SignalInstance"
    update30m: "SignalInstance"
    start3s: "SignalInstance"


# --- Aggregate application protocol -------------------------------------

@runtime_checkable
class AppProtocol(
    HasThreadPool,
    HasMessageBus,
    HasDeviceRegistry,
    HasCyclicSignals,
    Protocol,
):
    """Structural type describing the surface of :class:`MountWizzard4`
    that the rest of the application is allowed to depend on.

    Anything (including the test ``App`` stub) that exposes the listed
    attributes satisfies this protocol — no inheritance required.
    """

    __version__: str
    mwGlob: dict[str, Path]
    ephemeris: "SpiceKernel"
    onlineMode: bool
    statusOperationRunning: int

    # Operational signals (kept small on purpose; expand only as needed).
    operationRunning: "SignalInstance"
    stopDevices: "SignalInstance"
    startDevice: "SignalInstance"
    stopDevice: "SignalInstance"
    colorChange: "SignalInstance"
    playSound: "SignalInstance"
```

Notes:

- The narrow sub-protocols let leaf modules ask only for what they use.
  A pure worker like `MeasureData` can take `app: HasThreadPool & HasMessageBus`
  instead of the full `AppProtocol`.
- `@runtime_checkable` is added on the aggregate only, to support the rare
  `isinstance(obj, AppProtocol)` test guard. Subprotocols stay
  non-runtime-checkable to keep them free.
- All forward refs are quoted so the file imports cleanly even before its
  dependencies exist.

---

## 4. Before / After Example: `Camera`

### Before — `src/mw4/logic/camera/camera.py`

```python
class Camera:
    log = logging.getLogger("MW4")
    DEVICE_TYPE: str = "camera"

    def __init__(self, app: Any) -> None:
        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        ...
```

A type checker sees `app.threadPool` as `Any` — every downstream usage is
unchecked.

### After

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mw4.base.appProtocol import AppProtocol


class Camera:
    log = logging.getLogger("MW4")
    DEVICE_TYPE: str = "camera"

    def __init__(self, app: "AppProtocol") -> None:
        self.app: "AppProtocol" = app
        self.threadPool = app.threadPool        # → QThreadPool
        self.signals = Signals()
        self.data: dict[str, Any] = {}
        ...
```

What changes for the developer:

- `app.threadPool`, `app.msg.emit(...)`, `app.dReg["camera"]`, `app.update1s`
  are now all type-checked and autocompleted.
- A typo (`app.threadpool`) is flagged immediately by `mypy`/`pyright`.
- Splitting/renaming a signal on `MountWizzard4` produces compile-time errors
  at every call site — no more silent drift.

### Even narrower (preferred for leaf classes)

```python
from mw4.base.appProtocol import HasThreadPool, HasMessageBus

class Camera:
    def __init__(self, app: "HasThreadPool & HasMessageBus") -> None:
        ...
```

This documents that `Camera` does *not* need the device registry or cyclic
signals — useful for tests, future refactors, and for splitting the god-object
hub (recommendation #5).

> Note: `&` intersections require Python 3.12+/PEP 695 syntax or a typing
> extension; on 3.11 we declare a tiny composite `Protocol` instead, e.g.
> `class _CameraDeps(HasThreadPool, HasMessageBus, Protocol): ...`.

---

## 5. Before / After Example: A GUI tab (`MountMove`)

### Before

```python
class MountMove:
    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
```

### After

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mw4.gui.mainWindow.mainWindow import MainWindow


class MountMove:
    def __init__(self, mainW: "MainWindow") -> None:
        self.mainW = mainW
        self.app = mainW.app               # → AppProtocol via MainWindow.app
        self.msg = mainW.app.msg           # → SignalInstance
        self.ui = mainW.ui                 # → Ui_MainWindow
```

Here a concrete forward reference is cheaper than a second protocol, because a
tab is **inherently** coupled to `MainWindow.ui` (the generated Qt UI class).
`TYPE_CHECKING` keeps the import cycle out of the runtime graph.

`MainWindow` itself then types its `app` attribute against the protocol:

```python
class MainWindow(MWidget):
    def __init__(self, app: "AppProtocol") -> None:
        super().__init__()
        self.app: "AppProtocol" = app
```

---

## 6. Migration Plan

The migration is mechanical and can be staged so the suite stays green at each
step.

| Step | Change                                                                  | Risk |
|:----:|-------------------------------------------------------------------------|:----:|
| 1 | Add `src/mw4/base/appProtocol.py` with `AppProtocol` + sub-protocols.       | None |
| 2 | Annotate `MountWizzard4` as `class MountWizzard4(QObject, AppProtocol)` (purely declarative; `Protocol` allows inheritance). Or just rely on structural matching. | None |
| 3 | Replace `app: Any` → `app: "AppProtocol"` in `src/mw4/logic/**` (leaf-first: `cover`, `filter`, `focuser`, `lightPanel`, `remote`, `telescope`). One file per commit. | Low |
| 4 | Repeat for `src/mw4/base/**`, `src/mw4/mountcontrol/mount.py`.              | Low |
| 5 | Repeat for `src/mw4/gui/**` — `MainWindow`, then each addon tab uses `mainW: "MainWindow"`. | Low |
| 6 | Tighten chosen leaves to narrow sub-protocols (`HasThreadPool`, …).         | Low |
| 7 | Add `mypy --strict` (or `pyright`) to CI on `src/mw4/logic` and gradually expand. | Medium (catches real bugs) |
| 8 | Optionally make the test stub class explicitly `class App(QObject, AppProtocol)` to get checker errors when production grows a new attribute the stub lacks. | None |

Each step is independently mergeable, fully backward-compatible at runtime, and
verifiable by the existing test suite (no behavior changes).

---

## 7. Trade-offs / FAQ

**Q: Why not just annotate `app: "MountWizzard4"` everywhere with `TYPE_CHECKING`?**
A: It works, but forces every logic module to acknowledge the GUI/app class and
makes test stubs second-class (they would have to inherit or be cast). The
protocol decouples the contract from the implementation, which is the whole
point of recommendation #4 (and feeds directly into #5).

**Q: Does this affect runtime behavior or performance?**
A: No. `Protocol` and `TYPE_CHECKING` imports are erased at runtime. Imports
under `if TYPE_CHECKING:` are never executed.

**Q: What about `Signal` vs `SignalInstance`?**
A: On a *class*, a `Signal(...)` declaration is a `Signal` descriptor; on an
*instance*, accessing it yields a `SignalInstance`. We type the protocol with
`SignalInstance` because consumers always interact with the bound form
(`app.msg.emit(...)`, `app.update1s.connect(...)`). PySide6 ships stubs for
both.

**Q: Will it catch the bug we just fixed (test stub missing `MAX_THREAD_COUNT`)?**
A: Yes. If `MainWindow.updateThreadAndOnlineStatus` is typed against
`AppProtocol`, then either (a) the production `MountWizzard4` and the test
`App` both declare `MAX_THREAD_COUNT`, or (b) the type checker fails before
the test is ever run.

---

## 8. Expected Outcomes

- ~20 `app: Any` parameters become typed.
- New attribute on `MountWizzard4`? → one place to update (`AppProtocol`), and
  the type checker shows every consumer that needs to react.
- Future signal-hub split (recommendation #5) becomes straightforward:
  retire signals from `AppProtocol`, move them onto a dedicated
  `MountSignals` / `GameSignals` object, and let the checker enumerate the
  call-site fixes.
- IDE navigation ("Go to definition" / autocomplete) lights up across the GUI
  and logic layers.

This is the single highest-leverage typing change available in the codebase
short of the full god-object split.

