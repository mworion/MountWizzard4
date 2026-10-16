# Plan: mountcontrol refactoring and low-severity cleanup

Source: `gists/work_agent/2026-10-16-mountcontrol-review.md`, steps 6 and 7.
Scope: `src/mw4/mountcontrol`, tests in `tests/unit_tests/mountcontrol`.

## Rules for every step

- One step = one separate change set. Do not start the next before the
  previous one is green.
- Behaviour stays identical unless the step says otherwise.
- Before and after each step:
  - `uv run pytest tests/unit_tests/mountcontrol --cov=mw4.mountcontrol`
    (100 % coverage, no `# pragma: no cover`)
  - `uv run ruff format` and `uv run ruff check`
- Type annotations on all functions, camelCase, no leading underscore.
- Tests are module scoped and mirror the `src/mw4/mountcontrol` layout.
- Callers outside `mountcontrol` (grep `src/mw4`) must be updated in the same step.
- At the end: run the full test suite.

---

## Step 6: Refactoring (separate steps)

### 6.1 Split `convert.py`

1. Grep all importers of `convert` in `src/mw4` and `tests`.
2. Create two modules:
   - `convert.py`: mount protocol parsing (`stringToDegree`, `valueToFloat`,
     `valueToInt`, `valueToAngle`, `sexagesimalizeToInt`, ...).
   - `convertGui.py`: GUI input/output formatting (`convertRaToAngle`,
     `convertDecToAngle`, `formatLatToText`, `convertToDMS`, `convertToHMS`, ...).
3. Update imports in all callers. No re-export shims.
4. Split `tests/unit_tests/mountcontrol/test_convert.py` the same way.
5. Done when: both modules are covered 100 % and ruff is clean.

### 6.2 Command helper for `Setting` and `ObsSiteCommands`

1. Inventory the ~60 repeated `Connection(...)` + `communicate(...)` blocks
   and group them by response check (`COMMAND_A`, `COMMAND_B`, with or
   without `numberOfChunks`).
2. Add one helper, e.g. `sendCommand(self, command: str, chunks: int = 0) -> tuple[bool, list[str]]`,
   in a shared place that both classes can use (a small mixin or a method of
   `Connection`). Decide after reading both classes.
3. Convert the methods in small batches (about 10 at a time), running tests
   after each batch.
4. Keep public method names and return values unchanged.
5. Done when: no raw `Connection(...)` + `communicate(...)` pairs remain in
   these two modules, except for justified special cases.

### 6.3 Split `Geometry.calcTransformationMatrices`

1. Add characterization tests first: fixed inputs and expected matrices and
   vectors for a GEM and a non-GEM case, so the split can be proven
   numerically identical.
2. Introduce a typed result dataclass (e.g. `TransformationResult` with
   `transMatrix`, `transVector`, `altAdj`, ...).
3. Split the P0..P10 chain into small methods (about 20-30 lines each):
   - Input normalisation to float degrees (no rebinding of `ha`, `dec`,
     `lat` from `Angle` to `float`; use new local names).
   - Each transformation stage as its own method.
   - No hidden side effect on `self.altAdj`; return it in the result.
4. Fix the wrong comment "all angles are in radians".
5. Declare `offLAT`, `azAdj`, `transMatrix`, `transVector` in `__init__`
   with annotations.
6. Update `MountDevice.calcTransformationMatrices*` to use the result
   and give them a proper return type (`np.ndarray | None`).

### 6.4 Replace the `ObsSiteCommands` mixin contract with a Protocol

1. List all attributes the mixin uses (`status`, `flipped`, `pierside`,
   `timeSidereal`, `ut1_utc`, `statusSat`, `raJNow`, ...).
2. Define a `Protocol` (e.g. `ObsSiteProtocol`) with these attributes and
   types. Place it next to `MountContext` using type-only imports.
3. Annotate `self` in the mixin methods (or make the mixin generic over the
   protocol) and drop `Any` for `location` and `piersideTarget`
   (`GeographicPosition`, `str`).
4. Use `MountStatus.TRACKING` instead of `self.status == 0` in
   `startSlewing`.
5. Handle an unknown `slewType` explicitly (return `False` with a log
   message) and add a test.
6. Optionally reuse the protocol in `jdParamMixin.py` to remove its five
   `# type: ignore[attr-defined]`.

### 6.5 Unify pierside validation

1. Compare `ObsSite.pierside`, `ObsSite.piersideTarget` and
   `ProgStar.pierside`; write down the current failure behaviour of each
   (log only / ignore / fall back to `"E"`).
2. Add one shared helper (e.g. `validatePierside(value: str | int) -> str | None`)
   and let all three use it. Keep each caller's current failure behaviour
   unless a decision is made to change it.
3. Fix `piersideTarget` typing (`int` in, `str` out) with a clear
   signature.
4. Tests: one parametrised test for the helper, plus the existing
   per-class tests.

---

## Step 7: Low-severity cleanup (section 2.3)

Done as small commits, one theme each. Verify each item before changing it.

| #  | Item                                                                      | Action                                                         |
|----|---------------------------------------------------------------------------|----------------------------------------------------------------|
| 1  | `convertToDMS` returns `-00:00:00` for 0                                  | Fix sign handling; add test                                    |
| 2  | `convertToHMS(ra: Angle \| float)` uses unbound `Angle.signed_hms`        | Fix annotation or convert float to `Angle`; add test           |
| 3  | Dead attributes `MountDevice._waitTime`, `ObsSite._haJNow`, `_haJNowTarget` | Remove, grep for usage first                                 |
| 4  | `Setting.weatherStatus` assigns `False` to an int                         | Use `0`                                                        |
| 5  | `setSlewSpeedMed/Low` format `{255:02.0f}`                                | Replace with plain constant strings                            |
| 6  | `Satellite.slewTLE` returns untyped `tuple`                               | Annotate `tuple[bool, str]`                                    |
| 7  | `Satellite.addTrajectoryPoint` rebinds `az`/`alt`, `zip(strict=True)` raises | Use new local names; check lengths and return `False`        |
| 8  | `Satellite.setTrackingOffsets()` with all `None` opens a socket           | Return early without connecting; decide return value; add test |
| 9  | Wrong-chunks check copied six times in `Satellite`                        | Extract into one helper                                        |
| 10 | Local `_numberOfChunks` variables                                         | Rename to camelCase without underscore                         |
| 11 | `Model.parseNumberNames` ignores `numberOfChunks`                         | Use the argument or remove it                                  |
| 12 | `Model.starList` setter does nothing special                              | Turn into a plain attribute, if no callers need the setter     |
| 13 | `Model.parseStars` passes first value (`ra`) to `topoToAltAz(ha, ...)`    | Verify against 10micron docs; rename variable or document      |
| 14 | `Model.formatSexagesimalRA` can give `24:00:00.0`                         | Wrap to `00:00:00.0`; add test                                 |
| 15 | `setLocation`/`setElevation` send `-000000.0` for 0 m                     | Use `elev >= 0` for the sign; verify mount accepts it          |
| 16 | `Connection.closeClientHard` bracket in message `Error [{id} {e}]`        | Fix message                                                    |
| 17 | `Connection.sendData` warning prefixed `[Trace]`                          | Remove prefix                                                  |
| 18 | `# pyrefly: ignore[missing-attribute]` in `communicateRaw`                | Remove by fixing the type, or keep with reason                 |
| 19 | `MountDevice.run` stores `{"10micron": self}`                             | Remove circular reference if no consumer needs it              |
| 20 | `MountDevice.data` / `MountData.data` bare `dict`                         | Annotate `dict[str, Any]` or more specific                     |
| 21 | `ObsSite` assigns `ts` twice; `UTC2TT` computed once                      | Single assignment; document `UTC2TT` caching                   |

Items 13 and 15 need external verification. If not verifiable, document in
a docstring and leave the behaviour as is.

---

## Order and checkpoints

1. 6.1 convert split
2. 6.5 pierside unification (small, independent)
3. 6.4 Protocol for `ObsSiteCommands`
4. 6.2 command helper
5. 6.3 `calcTransformationMatrices` split
6. Step 7 items, grouped by module: `convert`, `setting`, `satellite`,
   `model`, `connection`, `mount`/`obsSite`
7. Final: `ruff format`, `ruff check`, full test suite, Pyrefly, coverage
   100 %, update the review document with the resolved items.

## Risks

- 6.1 and 6.4 touch many imports and callers outside `mountcontrol`.
- 6.2 touches every command; keep batches small and keep wire strings unchanged.
- 6.3 is numerical; characterization tests must be in place before the split.

