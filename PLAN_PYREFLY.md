# Plan: Reduce `uv run pyrefly check` errors (625 baseline)

## Goal
Remove real/cheap findings, configure the checker for known stub/platform
limits, and freeze the rest with a baseline so CI fails only on new errors.
No behavior change; 100 % test coverage and Ruff stay green.

## Baseline (625 errors)
| Category | Count | Main cause |
|----------|-------|-----------|
| missing-attribute | 319 | attributes initialised `None`, mixins without declared attrs |
| bad-argument-type | 126 | Optional / untyped values, numpy/skyfield/Qt stubs |
| unsupported-operation | 74 | Optional operands, stubs |
| bad-assignment | 36 | untyped `None` defaults |
| no-matching-overload | 17 | numpy/Qt stubs |
| bad-return | 13 | Optional returns |
| bad-override-param-name | 13 | `closeEvent(self, closeEvent)` vs Qt `event`, pyqtgraph |
| not-callable / bad-index / not-iterable | 20 | Optional values |
| missing-import | 3 | `pythoncom`, `win32com`, `hid` (platform/optional) |
| bad-override / bad-function-definition | 4 | Qt/pyqtgraph signatures, numpy dtype default |

Hotspots (NoneType): `tabImage_Manage.py` 34, `tabModel_Manage.py` 25,
`simulatorW.py` 19, `tabSat_Search.py` 14, `tabSat_Track.py` 13,
`modelRun.py` 10, `remote.py` 8, `imageW.py` 8.

## Phase 1 – Mechanical fixes (~20 errors)
1. Rename `closeEvent(self, closeEvent)` to `closeEvent(self, event: QCloseEvent)`
   in all 11 windows (`mainWindow.py`, `analyseW`, `hemisphereW`, `imageW`,
   `keypadW`, `measureW`, `messageW`, `satelliteW`, `simulatorW`, videoW base,
   ...) and fix usages inside the bodies. Update `MWidget.closeEvent` if needed.
2. `CustomViewBox.mouseDragEvent/mouseClickEvent`: align parameter names with
   pyqtgraph `ViewBox`.
3. Fix `bad-override` in `PolarScatter.plot`, `TimeMeasure.tickStrings`,
   `MouseClickEventFilter.eventFilter` (match parent signature, add types).
4. Fix numpy dtype default (`bad-function-definition`): use `np.dtype(np.float32)`.
5. Missing imports: add `[tool.pyrefly]` `replace-imports-with-any =
   ["pythoncom", "win32com.*", "hid"]` (Windows/optional packages, per
   project rule for platform-specific code).

## Phase 2 – Typed attribute declarations (~150–250 errors)
Work per hotspot file, one commit per area:
1. Declare typed attributes (`self.x: Foo | None = None`) at class/`__init__`
   level where currently untyped `None`; use class-level annotations in
   mixins (e.g. `AlpacaAscomCommon.config`, `HDUList` usages via a cast).
2. Where a value is guaranteed after setup, narrow with a local variable or
   `assert x is not None` only if no extra uncovered branches arise
   (100 % coverage rule); prefer typed local aliases / `cast`.
3. Order: tabImage_Manage, tabModel_Manage, simulatorW, tabSat_Search,
   tabSat_Track, modelRun, remote, imageW, then remaining files.
4. Re-run pyrefly after each file; stop when remaining errors are stub
   limitations.

## Phase 3 – Config for unfixable noise
In `[tool.pyrefly]` (pyproject.toml):
- add per-path `sub-config` or `[tool.pyrefly.errors]` to disable stub-driven
  kinds only where justified (e.g. `no-matching-overload` for numpy/Qt).
- Use targeted `# pyrefly: ignore[...]` with reason for isolated cases such
  as skyfield `.degrees` (`mountcontrol/satellite.py:305`).

## Phase 4 – Baseline and CI
1. `uv run pyrefly check --baseline=pyrefly-baseline.json --update-baseline`
   and commit the file.
2. Add `pyrefly check --baseline=...` to the existing lint step so only new
   errors fail.
3. Shrink the baseline over time.

## Validation (after every phase)
- `uv run pyrefly check` (error count must go down, never up)
- `uv run ruff format && uv run ruff check`
- targeted pytest of touched modules, then full suite with 100 % coverage
  (`uv run pytest --cov`)

## Constraints (project rules)
- camelCase, full type annotations, no leading-underscore helpers, no
  `# pragma: no cover`, do not touch `src/mw4/gui/widgets`, no new features.

## Expected result
625 → roughly 250 after Phases 1–2, → 0 reported (new errors only) after
Phases 3–4.

---

## Status (implementation log)

| Step | Result | Errors after |
|------|--------|--------------|
| Baseline | | 625 |
| Phase 1 (override names/signatures, import config) | done | 579 |
| Phase 2 (`DeviceEntry.instance: Any`, `Any` annotations for untyped `None` attrs) | done | 419 |
| Phase 3 (per-path `sub-config` disabling stub-driven kinds) | done | 212 |
| Hemisphere `parent` -> `parentWindow` (attribute and constructor), popup `parentWidget` removed | done | 208 |
| `AppProtocol` signals typed `Signal` | done | 201 |
| Type inconsistencies (`buildP` lists, `ArrayLike`, `Camera.run`, casts, ...) | done | 188 |
| Targeted `# pyrefly: ignore[...]` for 3rd-party stub gaps (astropy `HDUList`, skyfield `reify`/`lazyproperty`/`Satrec`, pyqtgraph `PlotItem`, `ctypes.windll`, ...) | done | 145 |
| Pattern A: lifecycle attributes typed `Any` (`PlotBase` items, `SatData.satellites`); no runtime change | done | 113 |
| Pattern B: `Remote.stopCommunication` guard for `tcpServer is None` (+ test), `clientConnection` / `VideoBase.capture` typed `Any` | done | 100 |

Full suite after each step: 100 % coverage, Ruff clean.

### Findings on the remaining `NoneType` errors
Most are not crash paths: the attribute is `None` only until a start-up
step (setup, `startVideo`, `addConnection`), and the code only runs after
it. The types did not express this order. Fixes are therefore split:
- pattern A (type annotation only, no behavior change): done
- pattern B (real guard where a call before start would fail): done, only
  `Remote.stopCommunication` was a real hole
- pattern C (entry points that need a selected satellite, `satelliteMapW`,
  `tabSat_Track`): open, check first whether a timer can fire early
- pattern D (single cases, e.g. `tpool.startWorker`, `devicePopupW`,
  `imageW`, `styles`, `fileHandler`, `hidController`, `photometry`): open

### What is left (100 errors)
- 61 `missing-attribute`, of which 24 are `NoneType` (patterns C and D);
  the rest are Qt/mixin attributes (`FunctionType`, `QWidget`, `TabAddon`,
  `list`).
- 25 `bad-argument-type`, 6 `unexpected-keyword`, 3 `bad-argument-count`
  (PySide `setData`, pyqtgraph kwargs), 4 `bad-assignment`, 1 `bad-index`.

### Remaining work
1. Pattern C and D (review case by case, guards need tests for 100 %
   coverage).
2. Qt/pyqtgraph kwargs and `setData` findings: targeted ignores or casts.
3. Phase 4: baseline file and CI step.
