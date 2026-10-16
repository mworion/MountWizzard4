# Review of `src/mw4/mountcontrol` (from scratch)

Date: 2026-10-16
Scope: all 22 modules in `src/mw4/mountcontrol` (about 3500 lines).

## 1. Baseline

| Check                                  | Result                              |
|----------------------------------------|-------------------------------------|
| `ruff check src/mw4/mountcontrol`      | all checks passed                   |
| `pytest tests/unit_tests/mountcontrol` | 938 passed, 100 % coverage          |
| TODO / FIXME / `pragma: no cover`      | none                                |
| Methods with leading underscore        | none                                |
| Pyrefly                                | not re-run in this review           |
| `Any` usages                           | 31 across 8 modules (see 3.6)       |

The package is clean on style and coverage. The findings below are
behavioural risks, design issues and typing leftovers. Coverage is 100 %, but
several items below are not caught by the tests.

Findings marked (verified) were reproduced by running the code or by
`grep`. The others are from reading the code and should be confirmed before
fixing.

## 2. Findings by severity

### 2.1 High (likely bugs)

1. **`convertRaToAngle` rejects valid degree input (verified).**
   - Location: `convert.py:195-212`.
   - The float branch validates `angle >= 24` before converting
     `angle / 360 * 24`. Degree input of 24 or more is therefore reset to 0.
   - Example: `convertRaToAngle("180.0").hours == 0.0`, expected 12.
   - The same function treats floats as degrees and sexagesimal values as
     hours, which is undocumented.
2. **`MountTimeConn.shutdown()` suppresses the disconnect signal.**
   - Location: `mountTimeConn.py:55-59`.
   - It sets `parent.mountIsUp = False` directly. The following
     `signals.mountIsUp.emit(False)` then reaches
     `MountDevice.startupMountData`, whose `elif not status and self.mountIsUp`
     branch is false.
   - As a result `deviceDisconnected` is never emitted after a GUI shutdown.
     The GUI calls `mountTimeConn.shutdown()` in `tabSettMount.py:101`.
   - There are also two `shutdown()` entry points: `ObsSiteCommands.shutdown`
     and `MountTimeConn.shutdown`. Calling the first one skips the state
     change.
3. **Stale `flipped` state delays settling after later slews (verified).**
   - Location: `mount.py:150`, `obsSiteCommands.py:92`.
   - `obsSite.flipped` is written only in `startSlewing()`. Slews started
     any other way (the mount hand controller, `moveNorth` and similar) reuse
     the last value. The flip settle time can therefore be applied to a
     non-flip slew.
4. **Geometry offsets depend on the latitude at the time they are set.**
   - Location: `geometry.py:83-147`, `mount.py:128-140, 220-221`.
   - The `offNorth`, `offNorthGEM`, `offVert` and `offVertGEM` setters read
     `obsSite.location.latitude` when called.
   - `initializeGeometry` runs in `resultGetFW`. `getLocation` runs in
     parallel, so latitude may still be 0 and the derived `*GEM` values
     would be wrong.
   - Nothing recomputes them when the location arrives (`resultGetLocation`
     only emits). Please verify the order. A fix is to derive the `*GEM`
     values lazily or to call `loadParametersFromConfig` again after the
     location is received.
5. **`communicateRaw` still waits after a failed send.**
   - Location: `connection.py:438-446`.
   - `sucSend` is ignored and the code waits up to 10 s in
     `waitForReadyRead`. It should return early.
6. **`Setting.parseSetting` has no length or format validation.**
   - Location: `setting.py:129-174`.
   - It only checks `len(response) == numberOfChunks`. Malformed answers
     raise inside the worker:
     - `response[9][3:6]` on a short string.
     - `valid, expirationDate = response[11].split(",")` raises `ValueError`.
     - `config[3]` raises `IndexError`.
   - `parsePointing` validates its fields, so the two are inconsistent.
   - `Model.parseStars` has the same problem with
     `ra, dec, err, angle = starData.split(",")`.

### 2.2 Medium (robustness and design)

1. **Protocol fragility in `Connection`.**
   - Commands that answer without `#` (`COMMAND_B`) are concatenated with the
     next chunk when mixed with other commands. Example: `setTargetAltAz`
     expects `response[0] == "11<pier><alt>"`, via
     `parseSetTargetResponse`.
   - `receiveData` stops on the number of `#`, so a trailing `COMMAND_B` reply
     may not have arrived yet. It ignores `minBytes` when `numberOfChunks > 0`.
   - The behaviour is correct but not documented. A docstring and a
     regression test with mixed commands are recommended.
2. **A new TCP connection per command.**
   - Pointing is polled every 0.5 s and settings every 3 s.
   - Each `communicate` builds, uses and aborts a `QTcpSocket`, and every
     stage can block up to `SOCKET_TIMEOUT = 10 s` in a worker.
   - Persistent connections or shorter timeouts for the polling cycle are
     worth considering.
3. **Dead code and misleading checks in `buildClient`.**
   - `self.host` is always a 2-tuple because `__init__` builds it. The
     `not self.host` and `isinstance(tuple)` checks can never trigger.
   - `host[0] is None` is the only real check.
   - It returns `None` silently when `mountIsUp` is false.
4. **Config keys are unchecked.**
   - Location: `mount.py:58`, `geometry.py:176-186, 245-246, 353, 377`.
   - `domeConfig` is `app.config.setdefault("SettingDome", {})`. Keys
     `use10micronDef`, `northOffset`, `eastOffset`, `verticalOffset`,
     `offGEM`, `offLAT` and `radius` are indexed directly. An incomplete config
     raises `KeyError` as soon as the firmware answer arrives. The GUI uses
     `.get` with defaults, the logic layer does not. Please verify that the
     config is always populated before this code runs.
5. **`Geometry.offLAT` is created dynamically.**
   - `loadParametersFromConfig` sets `self.offLAT`. It is not declared in
     `__init__`, and `calcTransformationMatrices` reads `cfg["offLAT"]`
     instead.
   - `vars(self).update(geometryData[...])` also bypasses declarations.
6. **`calcTransformationMatrices` is about 200 lines.**
   - It runs the full chain P0 to P10 in one function, mutates `self.altAdj`
     as a side effect and rebinds the parameters `ha`, `dec` and `lat` from
     `Angle` to `float`.
   - Comments say "all angles are in radians" while the code uses degrees.
   - `azAdj` is never set inside the package, so it must be set externally.
   - It needs splitting and a typed result (a dataclass).
7. **`MountTimeConn` rtt and clock handling.**
   - `rtt` is an average over a 25-slot buffer initialised with zeros, so it
     is understated at start-up. `timeDiff` has the same issue.
   - `rtt_MA` breaks the camelCase convention. `2 * 999` and `999` are magic
     numbers. The ping needs raw-socket privileges on some systems
     (`ping3`).
   - Reads and writes of `_timeDiff` across the worker and the timer are not
     synchronised. This is harmless with the GIL but undocumented.
8. **Firmware race in `Setting`.**
   - `pollSetting` and `parseSetting` each call `firmware.checkNewer("3.2.5")`.
     If the firmware answer arrives between the two calls, the command set and
     the parser disagree. The window is tiny, but a single evaluation per
     cycle would remove it.
9. **`ObsSiteCommands` mixin relies on undeclared attributes.**
   - It declares only `parent`, `location` and `piersideTarget` (the last two
     as `Any`). It also uses `status`, `flipped`, `pierside`, `timeSidereal`,
     `ut1_utc`, `statusSat`, `raJNow` and others.
   - `startSlewing` raises `KeyError` for an unknown `slewType` and compares
     `self.status == 0` instead of `MountStatus.TRACKING`.
   - A Protocol or composition would make the contract explicit.
10. **Pierside validation is duplicated three times.**
    - `ObsSite.pierside`, `ObsSite.piersideTarget` and `ProgStar.pierside`
      each validate separately and with different failure behaviour:
      log only, silent ignore, and fall back to `"E"`.
    - `piersideTarget` takes an `int` and returns a `str`, which type
      checkers flag.
11. **`convert.py` has two responsibilities.**
    - Mount protocol parsing (`stringToDegree`, `valueTo*`, `sexagesimalizeToInt`)
      and GUI input/output formatting (`convertRaToAngle`, `formatLatToText`,
      `convertToDMS` and others) live in one module.
    - `valueToFloat` returns the int `0` in some paths and passes `"nan"` and
      `"inf"` through unchanged (verified: `nan`).

### 2.3 Low (minor)

- `convertToDMS` returns `-00:00:00` for 0 degrees (verified).
- `convertToHMS(ra: Angle | float)` calls the unbound `Angle.signed_hms(ra)`,
  which fails for a float, so the annotation is wrong.
- Unused or dead attributes:
  - `MountDevice._waitTime` (`mount.py:50`) is never read.
  - `ObsSite._haJNow` and `_haJNowTarget` (`obsSite.py:73-74`) are never
    used, because `haJNow` and `haJNowTarget` are computed.
- `Setting.weatherStatus` assigns `False` to an int field (`setting.py:123`).
  It should be `0`.
- `Setting` and `ObsSiteCommands` contain about 60 repetitions of
  `Connection(...)` plus `communicate(...)`. A small helper such as
  `sendCommand(cmd, check)` would shrink the code a lot.
- `setSlewSpeedMed` and `setSlewSpeedLow` format constants as `{255:02.0f}`
  (`setting.py:211, 216`).
- `Satellite`:
  - `slewTLE` returns an untyped `tuple`; it should be `tuple[bool, str]`.
  - `addTrajectoryPoint` rebinds `az` and `alt` from `Angle` to arrays. Its
    `zip(strict=True)` raises `ValueError` in the worker if the lengths
    differ.
  - `setTrackingOffsets()` with all arguments `None` opens a socket and
    returns `True` for an empty command.
  - The wrong-chunks check is copied six times.
  - Local variables named `_numberOfChunks` use the underscore style the
    project avoids.
- `Model.parseNumberNames` ignores its `numberOfChunks` argument.
  `Model.starList` has a setter that does nothing special.
  `Model.parseStars` passes the mount's first value (named `ra`) to
  `topoToAltAz(ha, ...)`. Please verify and document whether the mount
  returns an hour angle here.
- `Model.formatSexagesimalRA` can produce `24:00:00.0` for values just below
  24 h, because of the rounding in `sexagesimalizeToInt`.
- `setLocation` and `setElevation` use `elev > 0` for the sign, so 0 m is sent
  as `-000000.0`. Check that the mount accepts this.
- `Connection` log messages:
  - The `closeClientHard` warning has a misplaced bracket:
    `Error [{id} {e}]`.
  - The `sendData` warning is prefixed `[Trace]` although it is always logged.
  - A `# pyrefly: ignore[missing-attribute]` comment remains in
    `communicateRaw`.
- `MountDevice.run` stores a reference to itself (`{"10micron": self}`), which
  is a circular reference.
- `MountDevice.data` and `MountData.data` are typed as a bare `dict`.
- `ObsSite` assigns `ts` twice (in `__init__` and in `setLoaderAndTimescale`).
  `UTC2TT` is computed once at start-up.

## 3. Typing

### 3.1 `Any` that can be removed

| File                    | Place                                                                  | Suggested type              |
|-------------------------|------------------------------------------------------------------------|-----------------------------|
| `geometry.py:84-163`    | 9 setters (`offNorth`, `offNorthGEM`, `offEast`, ...)                  | `str \| float \| None`      |
| `angleProperty.py:44`   | `__set__(value: Any)`                                                  | `Angle \| str \| float \| None` |
| `model.py:53-85`        | `numberStars`, `nameList`, `numberNames` setters                       | `str \| int`, `list[str]`, `str \| int` |
| `setting.py:67`         | `typeConnection` setter                                                | `str \| int \| None`        |
| `obsSiteCommands.py:21-22` | `location`, `piersideTarget` class attributes                       | `GeographicPosition`, `str` |
| `mount.py:294, 303`     | return of `calcTransformationMatrices*`                                | `np.ndarray \| None` (x3)   |
| `convert.py`            | `valueToFloat`, `valueToInt`, `valueToAngle` inputs                    | `str \| float \| None`      |
| `jdParamMixin.py`       | five `# type: ignore[attr-defined]`                                    | a Protocol for `obsSite`    |

### 3.2 Other typing issues

- `Geometry.transMatrix` and `transVector` are assigned `None` and later
  lists, with no annotation.
- `mount.py:272`: `runnerProgTrajectory` returns the `replay` flag, which has
  no meaning as a result.

## 4. Strengths

- `MountContext` Protocol replaces `parent: Any`, with type-only imports that
  avoid cycles.
- `MountStatus` and `STATUS_LABELS` are a single source of truth.
- `MountData` separates derived values from `ObsSite`. `ObsSite` is now
  about 295 lines.
- Workers follow the `worker*` and `runner*` naming and use `startWorker`
  with a `guard`.
- All `Connection` I/O paths catch `OSError` and `RuntimeError` and close the
  socket.
- Every module has a test file and 100 % coverage.

## 5. Recommended order of work

1. Fix `convertRaToAngle` (2.1.1), `shutdown` signal handling (2.1.2) and
   stale `flipped` (2.1.3). Add regression tests for each.
2. Verify the geometry and location order (2.1.4) and the dome config keys
   (2.2.4).
3. Add validation to `Setting.parseSetting` and `Model.parseStars` (2.1.6).
4. Return early in `communicateRaw` when the send fails (2.1.5).
5. Remove `Any` (section 3) and re-run Pyrefly.
6. Refactoring, in separate steps:
   - Split `convert.py`.
   - Add a command helper for `Setting` and `ObsSiteCommands`.
   - Split `calcTransformationMatrices` and give it a typed result.
   - Replace the `ObsSiteCommands` mixin contract with a Protocol.
   - Unify pierside validation.
7. Clean up the low-severity items in 2.3.


## 6. Status update (after steps 6 and 7)

Steps 6 and 7 of section 5 are implemented, except for the open items
below. Checks after the change: `ruff check` clean, `pyrefly check
src/mw4/mountcontrol` 0 errors, `pytest tests/unit_tests/mountcontrol`
100 % coverage.

### 6.1 Done (section 5, step 6)

| Item                                    | Result                                                              |
|-----------------------------------------|---------------------------------------------------------------------|
| Split `convert.py` (2.2.11)             | `convert.py` (mount parsing) and `convertGui.py` (GUI formatting)   |
| Command helper (2.3)                    | `sendCommand` in `Setting` and `ObsSiteCommands`                    |
| Split `calcTransformationMatrices` (2.2.6) | Five helper methods; numeric tests unchanged. Still returns a tuple, no dataclass yet |
| `ObsSiteCommands` contract (2.2.9)      | Attributes declared; `MountStatus.TRACKING` used; unknown `slewType` returns `False`. No Protocol yet |
| Pierside validation (2.2.10)            | Shared `validatePierside` in `convert.py`                           |

### 6.2 Done (section 5, step 7)

- `convertToDMS(0)` returns `+00:00:00`.
- `convertToHMS` annotation is `Angle` only.
- Dead attributes `MountDevice._waitTime`, `ObsSite._haJNow` and
  `_haJNowTarget` removed.
- `Setting.weatherStatus` falls back to `0`.
- `setSlewSpeedMed` and `setSlewSpeedLow` send plain constants.
- `Satellite`:
  - `slewTLE` returns `tuple[bool, str]`.
  - `addTrajectoryPoint` returns `False` on a length mismatch and no
    longer rebinds `az` and `alt`.
  - `setTrackingOffsets()` without values returns `False` without a socket.
  - The chunk check is one helper, `checkChunks`.
  - The `_numberOfChunks` locals are removed.
- `Model.parseNumberNames` uses `numberOfChunks`.
- `Model.formatSexagesimalRA` wraps to `00:00:00.0`.
- `setElevation` and `setLocation` send `+` for 0 m.
- `Connection` log messages fixed; the `pyrefly` suppression is removed.
- `MountDevice.data` and `MountData.data` are typed `dict[str, float]`.

### 6.3 Still open

- `Model.starList` setter: kept, other modules and tests assign to it.
- `MountDevice.run` self reference: kept, other device classes use the same
  pattern.
- `ObsSite` assigns `ts` twice: needs a reorder in `__init__`.
- `Model.parseStars` hour angle: comment added, behaviour not verified
  against the 10micron documentation.
- Typed result (dataclass) for `calcTransformationMatrices` and a real
  Protocol for `ObsSiteCommands`.
- Section 5, steps 1 to 5 (high-severity fixes, validation, `Any` removal)
  are not part of this update and are still open.

### 6.4 Behaviour changes to be aware of

- `piersideTarget` now accepts lowercase `e` and `w`.
- `addTrajectoryPoint` and `setTrackingOffsets` return `False` instead of
  raising or sending an empty command.
- 0 m elevation is sent as `+` instead of `-`; confirm that the mount
  accepts both.

