# Plan – Roadmap item 7: break up oversized functions (M1) and move calculations out of tabs (A5)

Source: `2026-10-20_review_copilot.md`, roadmap *Medium* item 7.
Status: **plan only, nothing implemented yet.**

## 1. Goals

1. Remove the 7 `PLR0915` per-file ignores in `pyproject.toml` by splitting the functions
   they cover, then lower the global statement budget (50 → 40) if feasible.
2. Reduce the biggest "data in code" and "widget building in `__init__`" functions to short
   orchestration code.
3. Move pure calculations (no Qt, no `self.ui`) out of tabs into `src/mw4/logic`, so they
   are unit-testable without Qt.

Non-goals: behaviour changes, new features, GUI layout changes, edits to
`src/mw4/gui/widgets` (generated).

## 2. Rules for every step (project conventions)

- camelCase, type annotations incl. return types, no leading-underscore functions,
  line length 100, no `# pragma: no cover`.
- New helper methods keep **public camelCase names**, e.g. `createPlotAxes`.
- Behaviour-preserving refactor: existing tests must stay green *before* new tests are
  added; new logic modules get new mirrored tests under `tests/unit_tests/logic/...`.
- Every step ends with: `uv run ruff check src tests`, `uv run ruff format src tests`,
  full `uv run pytest tests/unit_tests --cov=src/mw4 --cov-branch` at 100 % line + branch.
- One commit per work package (WP) so each can be reviewed/reverted independently.
- Workers: a long calculation extracted to `logic` stays callable from a
  `runner{Name}`/`worker{Name}` as today; do not change threading.

## 3. Inventory (measured, statements = AST statements)

| WP | Function | File | Lines | Stmts | Nature |
|----|----------|------|------:|------:|--------|
| 1 | `dataPlots` | `gui/extWindows/measure/measureAddons.py` | 293 | 1 | one giant dict literal (chart definitions) |
| 2 | `materials.__init__` | `gui/extWindows/simulator/materials.py` | 140 | 110 | repetitive Qt3D material setup |
| 2 | `telescope.create` | `gui/extWindows/simulator/telescope.py` | 122 | 8 | long entity/transform tree |
| 3 | `qtFileDialog.__init__` | `gui/utilities/nativeQt/qtFileDialog.py` | 99 | 74 | widget construction |
| 3 | `qtInputDialog.__init__` | `gui/utilities/nativeQt/qtInputDialog.py` | 98 | 69 | widget construction, 12 params |
| 4 | `devicePopupW.__init__` | `gui/extWindows/devicePopupW.py` | 154 | 32 | per-framework widget building |
| 4 | `tabSettDevice.__init__` | `gui/extWindows/setting/tabSettDevice.py` | 103 | 18 | per-device wiring |
| 4 | `tabEnviron_Weather.__init__` | `gui/mainWaddon/tabEnviron_Weather.py` | 97 | 24 | wiring |
| 4 | `externalWindows.__init__` | `gui/mainWindow/externalWindows.py` | 95 | 7 | window table |
| 4 | `tabMount_Move.__init__` | `gui/mainWaddon/tabMount_Move.py` | 93 | 29 | wiring + direction table |
| 5 | `updateImageStats` | `gui/mainWaddon/tabImage_Stats.py` | 77 | 65 | **calculation + GUI** |
| 5 | `showTiltTriangle` | `gui/extWindows/image/imageTabs.py` | 90 | 61 | **geometry + plotting** |
| 5 | `updateSettingGUI` | `gui/mainWaddon/tabMount_Sett.py` | 86 | 67 | mapping settings → widgets |
| 6 | `writeAsteroidMPC` | `logic/databaseProcessing/dataWriter.py` | 90 | 68 | record formatting + file IO |

The four tab modules `tabMount_Sett`, `tabSat_Track`, `tabImage_Manage`, `tabModel_Manage`
(24–37 methods each, 400–520 lines) are the A5 candidates for extraction; see WP 7.

## 4. Work packages

Ordered by risk (lowest first); WPs are independent unless noted.

### WP 1 – `dataPlots` → data module (low risk) — ✅ done 2026-10-20

- Problem: 293-line dict literal in a function; `Styles()` is instantiated for every pen.
- Change: keep `dataPlots()` as public API, but build it from small module-level
  definitions: one function per chart (`axisStabilityPlot()`, `angularTrackingPlot()`, …)
  plus a helper `lineItem(name: str, pen: str) -> dict` that creates the repeated
  `{"plotItemRef": None, "name": …, "pen": …}` entries. `Styles()` created once.
- Result: ~293 lines → ~120 lines, each chart independently readable.
- Tests: extend `test_measureAddOns.py` with equality test of the produced structure for
  every chart name (snapshot of keys/line items) – first capture current output as the
  golden reference *before* refactoring.

### WP 2 – Simulator builders (low/medium risk) — ✅ done 2026-10-20

- `materials.__init__`: table-drive the 110 statements. A `materialSpec` list of
  `(attributeName, diffuse, ambient, specular, shininess, …)` plus one
  `createMaterial(spec)` helper; loop sets attributes.
- `telescope.create`: split into `createBase`, `createMount`, `createTube`, … each
  returning its entity; `create` only assembles them.
- Tests: existing simulator tests keep passing; add tests per new builder (entity count,
  parent, transform) using the mocked entity approach already used in
  `tests/unit_tests/gui/extWindows/simulator`.

### WP 3 – Native Qt dialogs (medium risk) — ✅ done 2026-10-20

- Split `__init__` into `createLayout`, `createButtons`, `createList`, `connectSignals`.
- `qtInputDialog.__init__` (12 params): introduce a keyword-only parameter dataclass
  `InputDialogOptions` (review M2) that **fully replaces** the long parameter list; the
  `getInt/getDouble/…` classmethods and all callers are migrated in the same commit (no
  compatibility shim).
- Tests: existing dialog tests; add tests for each helper and the options dataclass.

### WP 4 – Window/tab `__init__` wiring (low risk, many files) — ✅ done 2026-10-20

- Pattern: replace long runs of `self.ui.x.clicked.connect(...)` and widget lookups with
  `setupSignals()`, `setupWidgets()`, `setupValidators()` methods called from `__init__`;
  repeated per-device blocks become loops over a small table (e.g. `directionByVector`
  in `tabMount_Move`, window table in `externalWindows`, framework list in
  `devicePopupW`).
- Keep `initConfig`/`storeConfig`/`setupIcons` untouched (tab lifecycle contract).
- Tests: existing `test_init*` tests stay; add one test per new setup method asserting the
  signal connection (`qtbot.mouseClick`/`waitSignal`).

### WP 5 – Calculation + GUI mixed functions (medium risk, A5 core) — ✅ done 2026-10-20

For each function, first write characterization tests that pin current outputs, then split
into a **pure function in `logic`** and a thin GUI method:

| Function | New pure function (module) | GUI method keeps |
|----------|---------------------------|------------------|
| `updateImageStats` | `logic/photometry/imageStats.py::calcImageStats(focalLength, aperture, pixelSize, resolution, rotation) -> ImageStats` (dataclass: resolution, FOV, f-ratio, scale …) | read spin boxes, call function, set labels |
| `showTiltTriangle` | `logic/photometry/tiltGeometry.py::calcTriangleGeometry(w, h) -> TriangleGeometry` (centre, radii, point positions) | clear tab, draw items |
| `updateSettingGUI` | table `settingToWidget` (`attribute → widget, formatter`) in the tab; formatters in `gui/utilities` | loop over the table |

- Pure functions take plain numbers/dicts, return dataclasses; no Qt, no `app`.
- Constants such as `206.265` get a named module constant (`ARCSEC_PER_RAD_FACTOR`) with a
  comment on the unit.
- Tests: new `tests/unit_tests/logic/photometry/test_imageStats.py`, `test_tiltGeometry.py`
  incl. zero/None focal length branches; GUI tests reduced to wiring.

### WP 6 – `writeAsteroidMPC` (low risk) — ✅ done 2026-10-20

- Split into `formatAsteroidRecord(data: dict) -> str` (pure, handles old vs. new
  designation) and `writeAsteroidMPC` (open file, loop, write).
- Tests: parametrised tests for old-style (`Number` present) and new-style designations
  using existing test data; IO test with `tmp_path`.

### WP 7 – Tab extraction (A5), incremental (medium/high effort)

Scope limited to what is cheap and clearly separable; each tab is its own sub-step:

1. `tabSat_Track`: `calcTrajectoryData`, `selectStartEnd`, `filterHorizon*` (pure array /
   time logic) → `logic/satellites/trackCalculations.py`. Tab keeps UI + worker wiring.
2. `tabModel_Manage` / `tabImage_Manage`: list/sort/offset/gain computations →
   `logic/modelBuild/…` and `logic/file/…` as pure helpers.
3. `tabMount_Sett`: value conversion/validation → `gui/utilities` formatters (Qt-free where
   possible).

Rule: extract only if the function does not touch `self.ui`/`self.app`; otherwise leave it.
Candidate list is confirmed by an AST/grep scan per tab *before* starting each sub-step
(`self.ui` free methods).

### WP 8 – Enforcement and cleanup (last)

- Remove the 7 `PLR0915` entries from `pyproject.toml` as each WP lands.
- Statement budget: **decision deferred.** Only the 7 explicit `PLR0915` ignores are
  removed in this plan; the global limit stays at 50 until decided.
- Update `2026-10-20_review_copilot.md`: mark M1 and A5 progress, refresh the metrics
  table (functions > 50 lines: 25 → target ≤ 10).

## 5. Order, effort and dependencies

| Order | WP | Effort | Risk | Depends on |
|------:|----|--------|------|------------|
| 1 | WP 1 dataPlots | 0.5 d | low | – |
| 2 | WP 6 writeAsteroidMPC | 0.5 d | low | – |
| 3 | WP 2 simulator | 1 d | low/med | – |
| 4 | WP 4 init wiring | 1.5 d | low | – |
| 5 | WP 3 native dialogs | 1 d | med | – |
| 6 | WP 5 calc/GUI split | 2 d | med | – |
| 7 | WP 7 tab extraction | 3–4 d | med/high | WP 5 patterns |
| 8 | WP 8 enforcement | 0.5 d | low | all |

Total ≈ 10 working days. WPs 1–4 can be done in parallel by different agents/people since
they touch disjoint files.

## 6. Verification checklist (per WP)

- [ ] Characterization tests written first and green on the old code.
- [ ] Refactor done, same tests green without modification (except wiring tests).
- [ ] New tests for new helpers; 100 % line **and** branch coverage (`fail_under = 100`).
- [ ] `ruff check`/`ruff format` clean; matching `PLR0915` ignore removed.
- [ ] Manual smoke test of the affected window/tab (start app, open window, exercise).
- [ ] No public API or config-key changes (profiles keep loading).

## 7. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Silent behaviour change in GUI building (order of widgets, tab order, signals connected twice) | Characterization tests; keep call order; smoke test; one commit per WP |
| Qt3D simulator hard to test | Reuse existing mock entity approach; assert on spec table rather than on Qt objects |
| Extracted logic still imports Qt | Review imports in new `logic` modules; no `PySide6` except `Signal`/`QObject` where truly needed |
| 100 % coverage regressions from new branches | Add tests in the same commit; run full coverage before each commit |
| Merge conflicts across WPs | Disjoint files per WP; rebase between WPs |

## 8. Decisions

1. Dialog options dataclass (WP 3) is a **full replacement** of the 12-parameter signature;
   callers are migrated in the same commit.
2. Extracted tab logic (WP 5, WP 7) lives in the matching `logic/<domain>` package, no new
   `logic/calculations` package.
3. Global statement budget (50 → 40): **to be decided later**; not part of this plan.
