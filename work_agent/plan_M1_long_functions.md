# Plan M1 – remaining long functions (roadmap item 2)

Source: `2026-10-20_review_copilot_open.md`, finding M1, roadmap item 2.
Status: **plan only – nothing of this is executed.**

## Scope

Split the ~12 remaining functions > 50 lines into small, named helpers without changing
behaviour. Optional follow-up: same controller pattern as A5 for three tabs and the
`update*Gui` tri-state button logic.

Out of scope: new features, behaviour changes, `src/mw4/gui/widgets` (generated).

## Known candidates (from the review)

| Function | Length | Approach |
|----------|--------|----------|
| `measureAddons.dataPlots` | 91 L | declarative; one table of plot specs + one builder loop |
| `createFramework2gui` | 63 L | builder helper per framework group |
| `extractSources` | 61 L | separate background estimate / detection / filtering steps |
| `astrometry.solve` | 57 L | split command build, run, result parsing |

The remaining ~8 are found in step 1 (`ruff --select PLR0915` at a low threshold lists
statement-heavy ones; a short AST script lists line-heavy ones). Many statement-heavy hits
are `__init__` methods (`mount.py`, `setting.py`, `obsSite.py`, `mainApp.py`) – those are
declarative attribute lists and are **not** split; decide explicitly per case.

## Steps

1. **Inventory.** Script (AST, not committed) listing all functions > 50 lines in
   `src/mw4` excluding `gui/widgets`; store the list in this plan. Per entry decide:
   split / keep (declarative) with a one-line reason.
2. **Lock behaviour.** For each function to split, check that existing tests cover every
   branch (100 % branch coverage is the project rule). Add tests first where a branch is
   only covered indirectly.
3. **Split, one function per commit.** Extract helpers as public camelCase methods (no
   leading underscore), typed, in the same module. Keep signatures of the original
   function. Run the module's tests after each split.
4. **Budget decision.** After step 3 decide on a global `PLR0915` limit in
   `[tool.ruff.lint.pylint]` (`max-statements`, default 50) – lowest value for which the
   remaining hits are only justified declarative code; record that in `pyproject.toml`
   with per-file ignores for those.
5. **Optional A5 follow-up.** Apply the controller pattern of `plan_A5_tab_logic_extraction.md`
   to `tabModel_Manage.py`, `tabAlmanac.py`, `tabModel_BuildPoints.py`; move the
   `update*Gui` tri-state button logic of `tabImage_Manage.py` into `logic`. Each tab is a
   separate change with its own tests; keep layering (`gui → logic`) and no Qt in controllers
   except `QObject` workers.

## Verification (every step)

- `uv run pytest tests/unit_tests/<module>` for the touched module, then full suite with
  100 % line and branch coverage at the end.
- `uv run ruff check src` and `uv run ruff format`, `uv run lint-imports`, pyrefly.

## Risks

- Hidden coupling through instance attributes when extracting helpers in GUI tabs →
  keep state on `self`, do not introduce new tab-to-tab dependencies.
- Plot specs in `dataPlots` are order-sensitive → keep table order identical, compare
  rendered plot item counts in tests.

## Done when

- No function > 50 lines except documented declarative ones.
- Lower `PLR0915` budget enforced in ruff; full suite, 100 % coverage, lint clean.

## Result steps 1–4 (2026-10-23)

Inventory (13 functions > 50 lines):

| Function | Decision |
|----------|----------|
| `devicePopupW.createFramework2gui` | split: `createSolverGui` |
| `measureAddons.dataPlots` | split: `mountPlots`, `environmentPlots`, `devicePlots` (key order kept) |
| `telescope.updatePositions` | split: `updateOtaPositions` |
| `tabAlmanac.plotTwilightData` | split: `setupTwilightAxes` |
| `tabAlmanac.calcMoonPhase` | split: `calcMoonRiseSet`, `calcMoonNodes` |
| `photometry_core.extractSources` | split: `measureCatalog` |
| `astrometry.solve` | split: `buildSolveCommand` |
| `simulator/dome.create`, `telescope.createOta` | keep, declarative model tables |
| `tabSat_Track.__init__`, `mainWindow.__init__`, `qtMessageDialog.__init__` | keep, declarative setup |
| `geometry.calcAxisTransforms` | keep, length is mostly derivation comments |

Budget: `max-statements = 40` in `[tool.ruff.lint.pylint]`; per-file `PLR0915` ignores for
`qtMessageDialog.py`, `photometry.py`, `setting.py` (declarative / field-by-field parser).


## Result step 5 (2026-10-23)

| Tab | Moved to `logic/controllers` |
|-----|------------------------------|
| `tabModel_Manage` | `model/modelManage.py`: `deleteWorstStar`, `isTargetReached`, `starCount`, `writeOptimizedModel`; `runTargetRMS`/`runSingleRMS` share `runOptimizeStep` |
| `tabAlmanac` | new area `almanac/almanacCalculations.py`: twilight, moon phase / rise-set / nodes, `MoonPhaseData`, `phasesText`; added to the import-linter independence contract |
| `tabModel_BuildPoints` | `model/buildpointsSupport.py`: `generateUntilTarget` (DSO and spiral loops), `querySimbad` |
| `tabImage_Manage` | `image/cameraCalculations.py`: `switchPairState`, `strictPairState`, `filterNames`, `filterNumberForName`, `hidDomeAction`; tab keeps `setRunPair` |

Notes: message texts for deleting the worst star during optimization are now identical for
overall and single mode ("Point: n, RMS of x arcsec deleted."). `tests/**` is exempt from
`PLR0915` (fixtures).
