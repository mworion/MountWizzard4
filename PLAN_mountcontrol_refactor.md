# Plan: mountcontrol architecture refactoring

Scope: `src/mw4/mountcontrol` and `tests/unit_tests/mountcontrol` (plus the import
sites of moved symbols). Behaviour is preserved: commands sent to the mount, signals,
and the `MountDevice` API used by GUI/logic stay the same.

Decisions:
- `Connection` stays instantiated per call (`Connection(self.parent)`). Its constructor
  keeps taking the parent object; only the type annotation changes (step 1).
- No backwards-compatibility aliases for moved symbols; all import sites are updated.
- Every step is one self-contained change set: green tests, 100 % coverage, ruff clean.
- Naming: camelCase, no leading-underscore helpers (existing private backing
  attributes like `_raJNow` stay, they are state, not helpers), type annotations
  everywhere, line length 100.

## 0. Baseline (before any change)

1. `pytest tests/unit_tests/mountcontrol --cov=mw4.mountcontrol --cov-report=term-missing`
   and record results (must be green, 100 %).
2. Record the public surface used from outside the package:
   `grep -rn "mountcontrol" src --include=*.py` (about 20 modules: `deviceRegistry`,
   `modelRun*`, `fileHandler`, `fitsFunction`, `tabMount_*`, `tabModel_*`, `tabPower`,
   `mainWindow`, `qtHelpers`, `imageW`, `tabSett*`, ...). These must still work after
   each step.
3. `uv run pyrefly check` baseline error count (for step 5 comparison).

## Step 1 - Typed parent context instead of `parent: Any`

### Current state (measured by grep on `parent.*`)

| Sub-object   | Members it uses on `parent`                                            |
|--------------|------------------------------------------------------------------------|
| `Connection` | `config.hostAddress`, `config.port`, `loggingTrace`, `mountIsUp`       |
| `ObsSite`    | `pathToData`, `mountIsUp`                                              |
| `Firmware`   | only passes `parent` on to `Connection`                                |
| `Setting`    | `firmware.checkNewer` (2x), passes parent to `Connection`              |
| `Model`      | `obsSite.location`, passes parent to `Connection`                      |
| `Satellite`  | `obsSite` (also builds `TLEParams`/`TrajectoryParams`), `Connection`   |
| `Geometry`   | `app.config`, `app.updateDomeSettings`, `loggingTrace`, `obsSite.location` |
| `MountTime`  | `app` (`timeMgr`, `dReg["mount"]`), `threadPool`, `obsSite` (`ts`, `UTC2TT`, `status` via `dReg`), `config` (`hostAddress`, `port`, `syncTimeNone`, `syncTimeNotTrack`), `mountIsUp`, `signals.mountIsUp` |

Findings that drive the design:
- `MountTime.syncClock` reads the mount through `self.app.dReg["mount"].obsSite.status`
  although `self.parent.obsSite.status` is the same object -> remove the registry detour.
- `Geometry` writes `parent.app.config["SettingDome"]` and connects to
  `parent.app.updateDomeSettings`; `MountTime` connects to `app.timeMgr.*`.
  These are the only places where the sub-objects depend on the application object.

### Actions

1. New module `src/mw4/mountcontrol/mountContext.py`:
   - `class MountContext(Protocol)` with read-only attributes typed exactly as used:
     `config: DeviceConfigMount`, `loggingTrace: bool`, `mountIsUp: bool` (settable),
     `signals: MountSignals`, `obsSite: ObsSite`, `firmware: Firmware`,
     `threadPool: QThreadPool`, `pathToData: Path`.
   - To avoid import cycles (`mount.py` imports all sub-modules) the Protocol is
     defined with `TYPE_CHECKING` imports, and `DeviceConfigMount` stays in `mount.py`
     unless it must move (then move it to `mountContext.py` and update imports).
   - The two application couplings are exposed explicitly on the context instead of
     `parent.app`: `timeMgr: TimeManagerProtocol` (members `update1s`, `update30s`) and
     `domeConfig: dict` + `updateDomeSettings: SignalInstance`.
     Check `src/mw4/base/appProtocol.py` first: reuse its existing protocol types for
     `timeMgr` rather than inventing new ones.
2. Change `parent: Any` -> `parent: MountContext` in `Connection`, `ObsSite`, `Firmware`,
   `Setting`, `Model`, `Satellite`, `Geometry`, `MountTime`.
3. `Geometry.__init__`: replace `parent.app.config` handling by
   `self.cfg = parent.domeConfig` (the `setdefault("SettingDome", {})` stays in
   `MountDevice`, where the app is known) and
   `parent.updateDomeSettings.connect(self.loadParametersFromConfig)`.
4. `MountTime.__init__`: drop `self.app`; use `parent.timeMgr` for the three timer
   connections (they move in step 4, see there). `syncClock` uses `self.parent.obsSite`.
5. `MountDevice`: provide `timeMgr`, `domeConfig`, `updateDomeSettings` as attributes
   set in `__init__` from `app` (before the sub-objects are created!).
6. Tests:
   - Add `tests/unit_tests/mountcontrol/conftest.py` with a `mountContext` fixture
     returning a `types.SimpleNamespace`/small fake class that satisfies the Protocol
     (real `DeviceConfigMount`, `MountSignals`, mock `timeMgr`, mock thread pool).
   - Replace the per-test `Parent` classes and `App().mount` hacks
     (`test_firmware.py`, `test_mountTime.py` incl. `m.MountStatus = MountStatus`)
     by the fixture.
   - Add a test that `MountDevice` satisfies `MountContext` (attribute presence).

### Acceptance
- No `parent: Any` left in `mountcontrol`; `grep -n "parent.app" src/mw4/mountcontrol`
  returns nothing except in `mount.py`.
- Tests green, 100 % coverage, `pyrefly` error count not higher than baseline.

## Step 2 - Split `ObsSite`

### Current state of `obsSite.py` (726 lines)

- Lines 23-68: `MountStatus` enum and module-level `_STATUS_LABELS`.
- Class constants: `_STATUS_VALID`, `STAT` (legacy string-keyed map used by the GUI),
  `STAT_SAT`.
- `__init__`: ~30 private backing attributes.
- ~25 property getter/setter pairs. Setters fall in four groups:
  1. Angle via `valueToAngle(value, preference=...)` (numeric/mount value):
     `raJNow`, `decJNow`, `angularPosRA/DEC`, `errorAngularPosRA/DEC`,
     `angularPosRATarget/DECTarget`, `Alt`, `Az`.
  2. Angle via `stringToAngle(value, preference=...)` (string input):
     `raJNowTarget`, `decJNowTarget`, `AltTarget`, `AzTarget`, `timeSidereal`
     (plus a numeric branch).
  3. Special logic: `location`, `timeJD`, `ut1_utc`, `status`, `statusSat`,
     `statusSlew`, `pierside`, `piersideTarget`.
  4. Derived read-only: `haJNow`, `haJNowTarget`, `isTracking`, `isStopped`,
     `isParked`, `isFollowingSatellite`.
- Command methods (`startSlewing`, `park`, `moveNorth`, ... ~25 methods) all following
  the same `Connection(...).communicate(...)` pattern.

### Actions

2a. `MountStatus` extraction
1. New module `mountStatus.py` containing `MountStatus` and `_STATUS_LABELS`
   (rename without underscore: `STATUS_LABELS`, since it becomes module-public).
2. `ObsSite` imports from `mountStatus`; keeps `_STATUS_VALID`/`STAT` derivation as is.
3. Update import sites: `mount.py`, `mountTime.py`, tests (`test_mountTime.py`), and
   whichever GUI module references it (`grep -rn "MountStatus" src tests`).
4. New `tests/unit_tests/mountcontrol/test_mountStatus.py`: all enum codes have a label,
   labels unique, codes match the 10micron status table.

2b. Angle descriptor
1. New module `angleProperty.py` with `class AngleProperty` (data descriptor):
   - Parameters: `preference: Literal["hours", "degrees"]`,
     `parser: Literal["value", "string"]` (selects `valueToAngle` vs `stringToAngle`).
   - `__set_name__` derives the backing attribute `_name` so existing tests and
     `haJNow` (which reads `_timeSidereal`/`_raJNow`) keep working.
   - `__set__`: `Angle` instances stored directly (current behaviour), otherwise
     converted by the configured parser; `__get__` returns the stored `Angle`.
2. Replace the group 1 and group 2 property pairs (except `timeSidereal`, which has the
   extra numeric branch - either extend the descriptor with a `parser="auto"` mode or
   keep it as an explicit property).
3. Group 3 stays as explicit properties (real logic), group 4 unchanged.
4. Behaviour guard: before removing the old properties, add parametrized tests per
   attribute covering `Angle`, numeric, string and malformed input, assert identical
   results against the old implementation (run once, then keep as regression tests).
5. Expected effect: roughly 25 property pairs (~250 lines) -> ~12 descriptor lines.

2c. Optional (only if `obsSite.py` is still > 400 lines after 2a/2b)
- Move the command methods into `obsSiteCommands.py` as a mixin `ObsSiteCommands`
  used by `ObsSite`. Decide after measuring; do not do it speculatively.

### Acceptance
- Public attribute/method names and semantics of `ObsSite` unchanged
  (`grep` of external usages passes, `test_obsSite.py` untouched or only import changes).
- 100 % coverage for `mountStatus.py`, `angleProperty.py`, `obsSite.py`.

## Step 3 - Slim down `MountDevice` (`mount.py`, 332 lines)

### Current state

- Orchestration: signals, 10 `worker*` handles, `getX`/`resultX` pairs
  (`getFW`, `getLocation`, `getModel`, `getNames`, `getTLE`, `calcTLE`, `statTLE`,
  `progTrajectory`, `cyclePointing`, `cycleSetting`).
- Derived data: `raRef`, `decRef`, `data`, `resetAfterStart`, `collectData`.
- Power: `bootMount` (wake-on-LAN), `shutdown`.
- Wiring: four `app.timeMgr.*.connect(...)` calls in `__init__`.
- `startupMountData(self, status)` has no type annotation.

### Actions

3a. Derived data -> `mountData.py`
1. `class MountData` (no Qt) with `raRef`, `decRef`, `data`, `reset()`, `collect()`;
   constructor takes `obsSite` and `mountTime` (explicit dependencies, not parent).
2. `MountDevice` creates `self.mountData` and keeps `self.data` as a property that
   returns `self.mountData.data` so GUI/logic callers (`mount.data[...]`) do not change.
   `collectData`/`resetAfterStart` stay on `MountDevice` as thin timer slots calling
   `mountData` (their names are connected to timer signals and may be patched in tests).
3. Tests: `test_mountData.py` (slew resets reference, delta computation, arcsec
   conversion of error values, timeDiff/rtt in ms); remove the same assertions from
   `test_mount.py`.

3b. Power -> decide after 3a
- If `bootMount`/`shutdown` stay as small methods they remain on `MountDevice`
  (no extraction for two short methods). Only extract to `mountPower.py` if more
  power logic (e.g. mount off timing) is planned. Default decision: keep.

3c. Timer wiring
1. One method `connectTimers(self) -> None` in `MountDevice` that makes all
   timer connections currently spread over `MountDevice.__init__` (4) and
   `MountTime.__init__` (3): 0.5 s pointing, 3 s setting, 1 s collect, start3s reset,
   1 s mount-up check, 30 s clock sync, 1 s poll clock.
2. `__init__` calls `connectTimers()` last, after all sub-objects exist.
3. Test: assert each timer signal is connected (patch `timeMgr` with mocks and check
   `.connect.assert_any_call`).

3d. Typing
- `startupMountData(self, status: bool) -> None`.
- Worker attributes keep the `worker{NameOfFunction}` / `runner{NameOfFunction}`
  naming rule.

### Acceptance
- `MountDevice` only orchestrates; no arithmetic on mount data inside it.
- All external usages (`app.dReg["mount"].instance.data[...]`, signals) unchanged.

## Step 4 - Connectivity probe out of `MountTime`

### Current state
`MountTime` holds two unrelated responsibilities:
1. Reachability: `runnerMountUp`, `checkMountUp`, `setMountStatusOff`, `rtt`, `rtt_MA`,
   `errorCounter`, `workerCycleMountUp`, `SOCKET_TIMEOUT` (ping3 + raw socket).
2. Clock: `timePC`, `_timeDiff`, `timeDiff`, `deltaAdjustClock`,
   `absolutAdjustClock`, `syncClock`, `runnerPollSyncClock`, `pollSyncClock`,
   `workerPollSyncClock`.

`MountTime.runnerPollSyncClock` subtracts `self.rtt` (written by the probe) from the
clock delta -> the two parts share the round-trip time.

### Actions

1. New module `mountMonitor.py`: `class MountMonitor(parent: MountContext)` with the
   whole reachability part (incl. `rtt` property). Behaviour, log texts and the
   `errorCounter` throttling stay identical.
2. `MountTime.__init__(parent, monitor: MountMonitor)` (or `rttProvider: Callable[[], float]`;
   prefer the monitor reference, it is simpler) and uses `monitor.rtt` in
   `runnerPollSyncClock`.
3. `MountDevice.__init__` creates `MountMonitor` before `MountTime` and passes it.
   `MountDevice.collectData` reads `rtt` from `self.monitor.rtt`.
   Timer connection `update1s -> monitor.checkMountUp` is made in `connectTimers()`.
4. Tests: split `test_mountTime.py` into `test_mountTime.py` (clock) and
   `test_mountMonitor.py` (ping None/False, socket OSError, success path, error
   counter, worker start). Preserve the existing module-scoped fixture/cleanup of
   workers (`workerCycleMountUp.signals.finished.emit()`).
5. Windows/platform: none of this code is platform specific; no guards needed.

### Acceptance
- `mountTime.py` imports neither `ping3` nor `socket`.
- Same log messages and the same `mountIsUp` signal emissions as before.

## Step 5 - Typing cleanup

1. `ObsSite` explicit setters (`location`, `timeJD`, `ut1_utc`, `status`, `statusSlew`,
   `pierside*`): replace `value: Any` with a narrower union where the accepted input
   is known (`str | float | int | Angle | None`, `list | tuple | GeographicPosition`
   for `location`); keep `Any` only where the converter genuinely accepts anything.
2. `Connection.__init__`: already `MountContext` after step 1.
3. `uv run pyrefly check`: error count must be <= baseline; fix new findings.
4. Remove the leftover `Any` imports.

## Order and dependencies

```
0 baseline -> 1 context -> 2a status ->- 2b descriptor -> 5 typing
                       \-> 3a data -> 3c timers -> 4 monitor
```
- Steps 2 and 3/4 are independent after step 1 and can be done in either order.
- 3c and 4 both touch timer wiring: do 3c first, then 4 only moves one connection.
- Step 5 last.

## Verification after each step

1. `ruff format src tests` and `ruff check src tests` (all findings resolved).
2. `pytest tests/unit_tests/mountcontrol --cov=mw4.mountcontrol --cov-report=term-missing`
   -> 100 %.
3. `pytest` for the callers touched by moved symbols (`tests/unit_tests/gui/mainWaddon`,
   `tests/unit_tests/logic`, `tests/unit_tests/base/test_deviceRegistry.py` ...).
4. `uv run pyrefly check`.
5. Smoke run of the application against the simulator/dummy mount if available:
   start, mount comes up (`deviceConnected`), pointing updates in the status panel.

Final: run the complete test suite with overall coverage, ruff over everything.

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Many external modules use `MountDevice`/`ObsSite` | Keep public names stable; grep every moved symbol; step-wise commits |
| Descriptor changes setter semantics (`valueToAngle` vs `stringToAngle`, `Angle` passthrough) | Parametrized regression tests per attribute before replacing; `parser` parameter keeps the two variants explicit |
| Startup/timer order (`mountIsUp`, `start3s`, signals) | `connectTimers()` called last; tests assert connections; smoke run |
| Tests rely on `_privateAttr` of sub-objects | Descriptor uses the same `_name` backing attribute |
| Module-scoped worker fixtures leak threads when splitting tests | Copy the existing cleanup block into the new test modules |
| Import cycles from `MountContext` | `TYPE_CHECKING` imports only; Protocol lives in its own module |

## Out of scope

- Per-call `Connection` creation (kept as is, by decision).
- Behaviour/protocol changes towards the mount, new features, GUI changes.
- `src/mw4/gui/widgets` (generated).
