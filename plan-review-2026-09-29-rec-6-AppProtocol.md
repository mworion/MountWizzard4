# Plan – Review 2026-09-29, Recommendation 6 (June #4): `App` Protocol

Source: `gists/work_agent/2026-09-29-review.md` (section 4.1, rec 6),
proposal `gists/work_agent/2026-06-10-proposal-rec4-AppProtocol.md`.

Goal: replace the untyped `app: Any` seams with one structural contract
(`AppProtocol`) and type `mainW: Any` against the concrete `MainWindow`.
No runtime behavior changes, except the latent bugs from Phase 1.

---

## 0. Findings (current baseline)

| Item                         | Count / fact                                                      |
|------------------------------|-------------------------------------------------------------------|
| `app: Any`                   | 53 occurrences in 51 files (base 7, logic 22, gui 21, mount 1)    |
| `mainW: Any`                 | 24 (23 tabs in `gui/mainWaddon` + `mainWindowAddons.py`)          |
| `parent: Any`                | 51 – heterogeneous (framework drivers, mount sub-objects, plots)  |
| Type checker                 | none configured (no mypy/pyright), no `TYPE_CHECKING` anywhere    |
| `requires-python`            | `>=3.12` (no `&` intersection types → composite protocols)        |
| Import cycles logic → gui    | none today; must stay that way                                    |

Most used `app.*` attributes: `dReg` 558, `config` 103, `timeMgr` 75,
`buildPoint` 61, `mwGlob` 47, `msg` 42, `threadPool` 33, `operationRunning` 21,
`colorChange` 17, `isOnline` 11, `redrawHorizon` 11, plus the remaining UI signals.

**Latent bugs found while mapping the surface** (attributes that exist only on
the test stub `baseTestApp.App`, not on `MountWizzard4` → `AttributeError` in
production):

| Access                        | Location                                                   | Correct access                      |
|-------------------------------|------------------------------------------------------------|-------------------------------------|
| `app.relay.switch/pulse/status` | `gui/mainWaddon/tabRelay.py:54,56,63`                    | `app.dReg["relay"].instance`        |
| `app.measure.run["csv"]`      | `gui/extWindows/measure/measureW.py:96`                    | `app.dReg["measure"].run["csv"]`    |
| `app.deviceStat.get("mount")` | `gui/extWindows/hemisphere/hemisphereDraw.py:81`           | `app.dReg["mount"].stat`            |
| `app.deviceStat.get("dome")`  | `hemisphereDraw.py:348`, `tabModel_BuildPoints.py:336`     | `app.dReg["dome"].stat`             |

`app.mount` is set dynamically by `DeviceRegistry.__init__` (test hook, rec 10)
and is **not** part of the protocol.

---

## 1. Phase 1 – Fix the latent bugs (prerequisite) – ✅ Done

The protocol must describe the real `MountWizzard4`. The accesses above are
changed to the `dReg` form. The related tests (≈50 references to
`app.relay` / `app.measure` / `app.deviceStat` in `tests/unit_tests`) are updated
to set up state through `app.dReg[...]`. The stub keeps its attributes until
Phase 5 so the unrelated tests stay green.

**Result:** sources fixed as in the table. Additionally `KMRelay.switch` now
returns `bool` (reply `OK`) and `KMRelay.pulse` returns `True` after starting
the worker. Before, both returned `None`, so `doRelayAction` would always have
reported "Action cannot be done". Tests migrated to `app.dReg[...]` and now assert
the outcomes (title text, status color, `sortDomeAz` call, relay return values).
`relay`, `measure` and `deviceStat` were removed from `baseTestApp.App` already
(Phase 5 part), because no test needs them anymore. Ruff clean, 4554 passed,
38 skipped (serial and `-n auto`), coverage 100 %.

## 2. Phase 2 – `src/mw4/base/appProtocol.py`

- One module, no runtime `mw4` imports (all referenced classes are imported
  under `if TYPE_CHECKING:` with `from __future__ import annotations`). Consumers
  can therefore import it at runtime without cycles, so **no** `TYPE_CHECKING`
  block is needed in the 51 consumer files.
- Content: a single `@runtime_checkable class AppProtocol(Protocol)` with
  - attributes: `__version__`, `mwGlob`, `application`, `threadPool`,
    `MAX_THREAD_COUNT`, `expireData`, `isOnline`, `statusOperationRunning`,
    `messageQueue`, `config`, `timeMgr`, `dReg`, `audioMgr`, `buildPoint`,
    `hipparcos`, `ephemeris`, `mainW`;
  - the 25 signals as `SignalInstance`;
  - methods `initConfig() -> None`, `storeConfig() -> None`.
- Narrow sub-protocols (`HasThreadPool`, …) from the proposal are **not**
  added now (see decision D2).
- `pyproject.toml`: add `"if TYPE_CHECKING:"` to
  `[tool.coverage.report] exclude_also` (config, not a pragma) so the one
  import block does not break the 100 % gate.
- Spike: check that the PySide6 stubs resolve `Signal` on the class to
  `SignalInstance` on the instance, so `MountWizzard4` matches the protocol
  structurally. If not, type the signals as `Signal` in the protocol.

**Result – ✅ Done**

- `src/mw4/base/appProtocol.py` added. Deviation from the list above: the
  protocol contains only the members that consumers **actually use** (checked by
  grep outside `mainApp.py`). `application`, `audioMgr`, `expireData` and the
  signals `material` / `drawHorizonPoints` are used only inside `MountWizzard4`
  and are therefore not included. Result: 16 attributes, 23 signals,
  `initConfig`, `storeConfig`.
- Spike: PySide6 6.11.2 `QtCore.pyi` declares
  `Signal.__get__(instance: QObject, …) -> SignalInstance`, so typing the
  signals as `SignalInstance` is correct.
- `pyproject.toml`: `"if TYPE_CHECKING:"` added to `exclude_also`.
- Tests: new `tests/unit_tests/base/test_appProtocol.py` (the stub `App`
  satisfies the protocol, `object()` and a partial object do not, and the
  member set is checked) plus `test_satisfiesAppProtocol` in
  `tests/unit_tests/mainApp/test_mainApp.py` against the real `MountWizzard4`
  (part of Phase 5 done early).
- Ruff clean, 4559 passed, 38 skipped (serial and `-n auto`), coverage 100 %.

## 3. Phase 3 – Replace `app: Any` (53 sites)

Mechanical `app: Any` → `app: AppProtocol` (and `self.app: AppProtocol` where
annotated). Order, one package per step, suite green after each:

1. `base/`: `audioManager`, `deviceRegistry` (`__init__`, `addDevices`),
   `timeManager`, `loggerMW` (`setTrace`, `setCustomLoggingLevel`), and the
   `self.app: Any = parent.app` lines in `indiClass`, `sgproClass`,
   `alpacaAscomCommon`.
2. `logic/`: 22 files (`buildData`, `camera`, `cover`, `databaseProcessing`,
   `dome`, `environment`, `filter`, `focuser`, `hidController`, `lightPanel`,
   `measure`, `modelBuild/modelRun`, `plateSolve`, `powerswitch`, `remote`,
   `telescope`).
3. `mountcontrol/mount.py`.
4. `gui/`: `mainWindow/mainWindow.py` and the 20 `extWindows` files
   (analyse, hemisphere, image, keypad, measure, message, satelliteHor/Map,
   setting, simulator/*, video/*).

`MountWizzard4` is **not** changed to inherit from the protocol (structural
matching is enough; avoids metaclass mixing with `QObject`).

## 4. Phase 4 – Replace `mainW: Any` (24 sites)

`mainW: Any` → `mainW: MainWindow` in the 23 tab addons and
`MainWindowAddons`. `mainWindow.py` imports `mainWindowAddons`, which imports
the tabs, so the import is placed under `if TYPE_CHECKING:` in these files
(covered by the Phase 2 coverage exclusion). `MainWindow.app` gets the
annotation `self.app: AppProtocol`, so `self.app = mainW.app` in the tabs is
typed transitively.

## 5. Phase 5 – Tests

- New `tests/unit_tests/base/test_appProtocol.py` (module scope):
  - `isinstance(App(), AppProtocol)` for the test stub;
  - `isinstance(<real MountWizzard4 from the existing mainApp fixture>,
    AppProtocol)` so production drift is caught at test time.
- `baseTestApp.App`: remove `relay`, `measure`, `deviceStat` after Phase 1
  migrated their tests (keeps the stub honest). `mount` stays until rec 10.

## 6. Finish

- Full suite serial and `-n auto`, coverage 100 % (macOS rules), Ruff
  check/format clean.
- Update section 10 of the review with the status of rec 6.

## Result Phases 3–6 – ✅ Done

- **Phase 3:** all 53 `app: Any` sites in 51 files now use `AppProtocol`
  (including `self.app: AppProtocol = parent.app` in `indiClass`, `sgproClass`
  and `alpacaAscomCommon`, and `setTrace` / `setCustomLoggingLevel`). The
  migration was done in one step with a script, followed by Ruff import sorting.
  Unused `Any` imports were removed.
- **Deviation:** five constructors had `app: Any = None` (`DirectWeather`,
  `SeeingWeather`, `Hipparcos`, `MeasureDataCSV`, `MeasureDataRaw`). Production
  always passes the app, so the default was removed (`app: AppProtocol`) instead
  of weakening the type to `AppProtocol | None`. The only caller relying on it
  (`test_measureRaw` fixture) now passes a mock app.
- **Phase 4:** all 24 `mainW: Any` sites are `mainW: "MainWindow"`, with the
  import under `if TYPE_CHECKING:`. The quoted form keeps Python 3.12/3.13
  compatible without `from __future__ import annotations`. `MainWindow.__init__`
  takes `app: AppProtocol`, so `self.app = mainW.app` in the tabs is typed
  transitively.
- **Phase 5:** done together with Phases 1 and 2 (see above).
- **Phase 6:** Ruff clean, 4559 passed, 38 skipped (serial and `-n auto`),
  coverage 100 % (18,444 statements). `python -c "import mw4.mainApp"` confirms
  no import cycle.
- The `QMutex: destroying locked mutex` teardown message still appears
  sometimes. It already existed before this change (review 3.4).

---

## Out of scope

- `parent: Any` (51 sites, heterogeneous parents) → own follow-up.
- `DeviceEntry.instance/run/signals: Any` → typed per device later.
- Typing `Signal(object, …)` payloads (rec 9) and removing test hooks (rec 10).

## Decisions needed before implementation

| #  | Question                                                                 | Proposal            |
|----|--------------------------------------------------------------------------|---------------------|
| D1 | Include the Phase 1 bug fixes in this change, or as a separate change?   | Include (prereq)    |
| D2 | Single `AppProtocol` only, or also narrow sub-protocols now?             | Single only         |
| D3 | Add a static checker (pyright or mypy) as dev dependency and run it on `src/mw4/base` + `logic`? Without it the protocol only helps the IDE. | Separate follow-up |
| D4 | `mainW` typed as concrete `MainWindow` (proposal) vs. a `MainWindowProtocol`? | Concrete `MainWindow` |





