# Plan: mountcontrol architecture refactoring

Scope: `src/mw4/mountcontrol` and its tests in `tests/unit_tests/mountcontrol`.
Public behaviour (commands sent to the mount, signals, `MountDevice` API used
by GUI/logic) stays unchanged. Each step is a separate, green, 100 % covered
commit.

Out of scope (decided): `Connection` stays instantiated per call
(`Connection(self.parent)`); its constructor signature is only touched as far
as step 1 requires for typing.

## Step 1 – Typed parent context instead of `parent: Any`

Problem: sub-objects (`Connection`, `Firmware`, `Setting`, `Model`,
`Satellite`, `Geometry`, `MountTime`, `ObsSite`) take `parent: Any` and reach
into `MountDevice` internals.

Attributes actually used on `parent` (from grep):
`config` (hostAddress, port, syncTimeNone, syncTimeNotTrack), `obsSite`
(location, ts, UTC), `mountIsUp`, `signals.mountIsUp`, `loggingTrace`,
`firmware.checkNewer`, `threadPool`, `pathToData`, `app` (config,
updateDomeSettings, timeMgr).

Actions:
1. Add `src/mw4/mountcontrol/mountContext.py` with a `MountContext`
   `typing.Protocol` listing exactly the members above.
2. Replace `parent: Any` by `parent: MountContext` in all sub-objects.
3. Remove the direct `parent.app.*` access from sub-objects where possible:
   - `Geometry`: get the dome config dict and connect to `updateDomeSettings`
     via explicit context members (`domeConfig`, `updateDomeSettings`) rather
     than `parent.app`.
   - `MountTime`: use `parent.timeMgr` (context member) instead of `app.timeMgr`.
4. Tests: replace the full-`MountDevice` mocks with a small fake context in
   `tests/unit_tests/mountcontrol/conftest.py` (or per module fixture).

Acceptance: pyrefly/ruff clean, no `Any` for `parent`, tests pass, 100 %
coverage.

## Step 2 – Split `ObsSite`

Problem: `obsSite.py` (~726 lines) mixes `MountStatus` enum, Skyfield/time
setup, many repetitive property getter/setter pairs and parsing.

Actions:
1. Move `MountStatus` (IntEnum) to `mountStatus.py`; update imports in
   `mount.py`, `mountTime.py`, `gui/extWindows/setting/tabSettMount.py`
   and tests. Do not re-export from `obsSite` (no compatibility alias).
2. Reduce the property boilerplate (`raJNow`, `decJNow`, `angularPosRA`, `Alt`,
   `Az`, targets, ...) with a small descriptor class for Angle-valued
   attributes (conversion `Any -> Angle | None` in one place).
   Keep public attribute names and behaviour identical.
3. Keep time/Skyfield loader setup (`setLoaderAndTimescale`, `ts`, `timeJD`,
   `ut1_utc`) in `ObsSite`; revisit separate class only if still > 400 lines.
4. Tests: existing `test_obsSite.py` stays the behavioural safety net; add
   `test_mountStatus.py` and tests for the descriptor.

Acceptance: `obsSite.py` clearly smaller, identical public API, 100 %
coverage.

## Step 3 – Slim down `MountDevice`

Problem: `mount.py` mixes QObject/signals, ~10 worker handles with
`getX`/`resultX` pairs, cyclic polling, wake-on-LAN, derived data
(`collectData`, `raRef`/`decRef`) and direct wiring to `app.timeMgr`.

Actions:
1. Extract derived-data logic (`resetAfterStart`, `collectData`, `raRef`,
   `decRef`, `data`) into `mountData.py` (`MountData` class, no Qt).
   `MountDevice.data` keeps exposing the same dict.
2. Extract wake-on-LAN/boot/shutdown (`bootMount`, `shutdown`) into
   `mountPower.py` if it reduces `MountDevice` meaningfully; otherwise keep.
3. Inject the time manager through the context (see step 1) so the timer
   connections are made in one `connectTimers()` method, not scattered over
   `__init__` and `MountTime`.
4. Keep the worker naming rule: `worker{NameOfFunction}` /
   `runner{NameOfFunction}`.
5. Tests: move/duplicate the relevant tests into `test_mountData.py` (and
   `test_mountPower.py`); `test_mount.py` shrinks accordingly.

Acceptance: `MountDevice` only orchestrates (signals, timers, workers);
GUI/logic callers unchanged.

## Step 4 – Move connectivity check out of `MountTime`

Problem: `MountTime.checkMountUp` pings and opens a raw socket and sets
`mountIsUp` – connection-layer responsibility.

Actions:
1. Create `mountMonitor.py` with class `MountMonitor` holding
   `checkMountUp` / `setMountStatusOff` (ping + socket probe, emits
   `signals.mountIsUp`).
2. `MountTime` keeps only clock sync (`syncClock`, `timeDiff`).
3. `MountDevice` creates `MountMonitor` and connects it to the 1 s timer.
4. Tests: split `test_mountTime.py` into `test_mountTime.py` and
   `test_mountMonitor.py`.

Acceptance: `mountTime.py` contains no network probing; behaviour (messages,
signals) unchanged.

## Step 5 – Typing cleanup

1. Replace `Any` in `ObsSite` setters by `float | str | Angle | None` unions
   as appropriate (after the descriptor from step 2 this is mostly one place).
2. Add missing annotation on `MountDevice.startupMountData(self, status)`.
3. Run `uv run pyrefly check`.

## Order and dependencies

1 → 2 → 3 → 4 → 5. Steps 2 and 4 are independent of each other once step 1 is
merged.

## Finalisation (after each step and at the end)

- `ruff format` and `ruff check` over `src` and `tests`, resolve all findings.
- `pytest tests/unit_tests/mountcontrol --cov=mw4.mountcontrol` with 100 %.
- Finally run the whole test suite and overall coverage.
- Check line length (100) and camelCase / no leading-underscore helpers.

## Risks

- `MountDevice` is used widely (`app.dReg["mount"].instance...`): keep its
  public attributes stable; verify with grep for each moved symbol.
- Signals/timer wiring order matters at startup (`mountIsUp`, `start3s`);
  cover with tests that assert the connections.
