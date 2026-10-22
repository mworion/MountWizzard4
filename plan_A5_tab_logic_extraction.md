# Plan A5 – move remaining logic out of the big main-window tabs

Source: `2026-10-20_review_copilot_open.md`, finding A5 (first round already done:
`formatSatPass`, `dataAgeColor`, `reduceTrajectory`, `pickListEntry`, `filterSlotRange`,
`activeTrackingMode`).

## Target structure (decided)

```
src/mw4/logic/
  drivers/                     device drivers, one package per device type
    frameworks/                shared framework classes (moved from base/)
      alpacaAscomCommon.py alpacaClass.py ascomClass.py indiClass.py
      indiClassAddOns.py sgproClass.py driverDataClass.py
    camera/ cover/ dome/ environment/ filter/ focuser/ hidController/ keypad/
    lightPanel/ measure/ plateSolve/ powerswitch/ remote/ telescope/
  controllers/                 GUI-independent logic, one package per GUI area (A5)
    satellites/                Sat tabs: satellite_calculations, trackCalculations
    image/                     Image tabs: cameraCalculations
    model/                     Model tabs: alignstars, buildpoints, hipparcos, modelRun*,
                               modelTypes (from buildData/ and modelBuild/)
    mount/                     Mount tabs: trackingMode
    imageWindow/               extWindows/image: photometry*, imageStats, tiltGeometry
  fits/ profiles/ file/ databaseProcessing/    shared foundations, no GUI counterpart
```

Rule: a controller package exists only for a GUI area that has extracted logic.

- `base/` keeps infrastructure only; `driverProtocol.py` and `signalsDevices.py` stay in `base/`
  because `deviceRegistry` and `mountcontrol` use them (no `mountcontrol → logic` dependency).
- `mountcontrol/` (the mount driver) is not moved.
- Extractions of the first A5 round left the driver packages:
  `controllers/image/cameraCalculations.py`, `controllers/mount/trackingMode.py`.
- Done in Phase 0b: `measure`, `keypad` → `drivers/`; `satellites`, `buildData`,
  `modelBuild`, `photometry` → `controllers/<GUI area>/` (flat, no name clashes).
- New A5 modules below follow the GUI area: `controllers/mount/` (mountSettings,
  locationCalculations), `controllers/image/`, `controllers/satellites/`.

## Phase 0 – directory cleanup (pure move, own commit, no logic change)

1. `git mv` the device packages and the framework classes as shown above; mirror the move in
   `tests/unit_tests/logic/...` (`base/test_<framework>.py` → `logic/drivers/frameworks/`).
2. Rewrite all imports and dotted strings (`mock.patch("mw4.base.ascomClass...")`,
   `find_spec("mw4.logic.focuser...")`) with a scripted regex over `src` and `tests`.
3. Update path-bound configuration: `pyproject.toml` (coverage conditional paths, ruff
   per-file-ignores, pyrefly sub-configs, import-linter), the CI workflow test paths
   (`unit_*.yml`), and docs.
4. Verify: `lint-imports`, `ruff`, `pyrefly`, `test_testMapping.py`, full unit test run with
   unchanged results and coverage.

## Goal

The three biggest tabs keep only Qt wiring (read widgets, show dialogs, set text, emit
messages). Decisions, calculations and state transitions live in plain classes/functions in
`src/mw4/logic` that import no `gui` module and can be tested without Qt widgets.

| Tab | Lines now | Target |
|-----|-----------|--------|
| `tabMount_Sett.py` | 492 | ≤ 330 |
| `tabImage_Manage.py` | 462 | ≤ 350 |
| `tabSat_Track.py` | 406 | ≤ 320 |

Line counts are indicators; the real criterion is that no decision logic is left in the
tab methods listed below.

## Rules

- No behaviour change; public tab method names stay (signals, `clickable` connections and
  existing tests keep working).
- New code: camelCase, full type annotations, no leading-underscore helpers, line length 100.
- New `logic` modules do not import `gui` (enforced by `uv run lint-imports`).
- One test file per new module under the mirrored `tests/unit_tests/logic/...` (enforced by
  `test_testMapping.py`), 100 % line and branch coverage.
- Composition: the tab owns a controller (`self.controller = ...`) instead of inheriting.
- Controllers receive the objects they need (`mount`, `camera`, a `notify` callable), never
  `app` or `mainW`.
- Dialogs stay in the tab; a controller never opens a dialog.

## Phase 1 – `tabMount_Sett` (largest win, most duplication)

Findings in the current code:

- `setUnattendedFlip`, `setWebinterface`, `setDualAxisTracking`, `setWOL`, `setAPO`,
  `setRefraction` are the same sequence: ON/OFF dialog → `sett.setX(value == "ON")` →
  message (success / failure).
- `setMeridianLimitTrack/Slew`, `setHorizonLimitHigh/Low`, `setSlewRate`,
  `setRefractionTemp/Press`, `setSettleTimeMount` are the same sequence: numeric dialog with
  bounds → setter → message.
- `setLocationValues` mixes geometry (build `wgs84` position from partial lat/lon/elev) with
  mount/offline branching.

Steps:

1. New `logic/controllers/mount/mountSettings.py` with `MountSettingsController(setting, notify)`:
   - `applySwitch(label, setter, enabled: bool) -> bool` – calls the setter, emits the
     matching success/error text through `notify(level, "Mount", "Setting", text)`.
   - `applyValue(label, setter, value) -> bool` – same for numeric values with the text
     `"{label}: [{value}]"` / `"{label} cannot be set"`.
   - Keep the exact message texts of today (existing tests assert them); where wording
     differs per setter, pass the texts via a small `SettingSpec` dataclass
     (`label`, `title`, `minVal`, `maxVal`, `step`, `setterName`).
2. Table-drive the specs for limits/rates/refraction/settle; the tab keeps one generic
   `askAndApplyValue(spec)` and `askAndApplySwitch(spec)` and the public `setX` methods
   become one-liners (`return self.askAndApplyValue(self.LIMITS["meridianTrack"])`).
3. New `logic/controllers/mount/locationCalculations.py`: `buildLocation(current, lat, lon, elev)`
   (fills missing parts from the current location, returns `wgs84` position and the log
   text). `setLocationValues` keeps only the mount-online vs. offline branch.
4. Tests: controller (success/failure for switch and value, message texts), every spec row,
   `buildLocation` (each missing part). Adapt `test_tabMount_Sett.py` only where internals
   moved; public methods stay covered.

## Phase 2 – `tabImage_Manage`

Findings:

- `setOffset` / `setGain` are the same algorithm (list → item dialog and index lookup;
  min/max → int dialog with step `(max - min) / 20`; else plain int dialog).
- `updateOffset` / `updateGain` share the "list or number" display rule (partly extracted).
- Cover, light panel, focuser and dome methods are one-line delegates and stay.
- `updateImagingParam` / `checkEnableCameraUI` derive enable flags from `camera.data`.

Steps:

1. `logic/controllers/image/cameraCalculations.py`: add
   `describeRange(data, prefix) -> RangeSpec` (`kind`: `"list" | "range" | "free"`, values,
   `minVal`, `maxVal`, `step`) for keys such as `CCD_GAIN.GAIN_LIST/_MIN/_MAX`; add
   `cameraCapabilities(data) -> CameraCapabilities` (dataclass with `hasGain`, `hasOffset`,
   `hasCooler`, `hasSubFrame`, ... ) used by `checkEnableCameraUI`.
2. In the tab replace `setOffset`/`setGain` bodies by one `askRange(title, prefix, sender)`
   that switches on `RangeSpec.kind`; the sender callable (`sendOffset`, `sendGain`) is passed
   in.
3. Tests: `describeRange` for list/min-max/free/missing data, `cameraCapabilities` for each
   flag; tab tests keep asserting the dialog calls and the `send*` calls.

## Phase 3 – `tabSat_Track`

Findings:

- `startProg` contains the whole "prepare trajectory" pipeline (select start/end → compute →
  horizon filter → reduce → skyfield `Angle`) between the GUI messages.
- `startTrack` / `stopTrack` contain mount state transitions (unpark if parked, avoid dome
  overshoot, slew to TLE, set offsets).
- `followMount` maps `statusSat` to texts and decides whether the dome follows.

Steps:

1. `logic/controllers/satellites/trackProgram.py`: `prepareTrajectory(...) -> TrajectoryResult | None`
   (start, end, `Angle` alt/az, or `None` + reason `"noPass" | "noData"`), built from the
   existing `selectStartEnd`, `calcTrajectoryData`, `filterHorizon`, `reduceTrajectory`.
   Parameters are keyword-only (see M2); no `app`.
2. `logic/controllers/satellites/trackControl.py`: `SatelliteTrackController(mount, dome, notify)` with
   `start() -> bool` (unpark, dome overshoot, `slewTLE`, offsets) and `stop() -> bool`;
   messages via `notify`.
3. `logic/controllers/satellites/trackCalculations.py`: `satStatusText(statusSat)` (the `TLESCK` map as
   module constant) and `shouldDomeFollow(status, followEnabled, domeOnline)`.
4. The tab methods become: read widgets → call logic → `setText` / `changeStyleDynamic`.
5. Tests: `prepareTrajectory` (no pass, no data, reduced, filtered), controller with fake
   mount/dome (not online, parked/unparked, slew failure, success, stop failure), status
   texts and follow decision.

## Phase 4 – consolidation

1. Re-measure: `wc -l` of the three tabs, `ruff check` (PLR0915), `lint-imports`, `pyrefly`.
2. Update `2026-10-20_review_copilot_open.md` (A5, roadmap) with the new numbers.
3. Optional follow-up (not part of A5): `tabModel_Manage.py` (404 L), `tabAlmanac.py`
   (391 L), `tabModel_BuildPoints.py` (372 L) with the same pattern.

## Order, risk and verification

- Order: Phase 1 → 2 → 3 (decreasing duplication; each phase independently mergeable).
- Main risk: changed message texts or dialog arguments. Mitigation: keep the existing tab
  tests unchanged first, run them after each step, and only then add the logic tests.
- Per phase: `uv run pytest <new logic tests> <tab test file> --cov` (100 % on touched
  modules), `uv run ruff format src tests && uv run ruff check src tests`,
  `uv run pyrefly check`, `uv run lint-imports`.
- Final step: full package run `uv run pytest tests/unit_tests` with 100 % coverage.

## Out of scope

- Editing generated `src/mw4/gui/widgets`.
- Changing widget names, signals or the tab lifecycle (`TabAddon`).
- Typed configuration (A3) and global signal documentation (A6).
