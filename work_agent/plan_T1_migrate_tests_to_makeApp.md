# Plan T1 – migrate unit tests to `makeApp`

Source: `2026-10-20_review_copilot_open.md`, item T1 (roadmap follow-up 3).

## Goal

Tests obtain their stub application through the `makeApp(**overrides)` factory
(fixture in `../tests/conftest.py`, implementation in
`tests/unit_tests/unitTestAddOns/baseTestApp.py`) instead of instantiating
`App()` directly. Test behaviour and 100 % coverage stay unchanged.

## Current state (measured 2026-10-22)

- 144 test modules under `../tests/unit_tests` call `App()` directly.
- 4 modules use `makeApp` (incl. `test_makeApp.py`).
- Hot spots:
  - `logic/drivers` 59 modules (`Camera(app=App())`, `Dome(app=App())`, ...)
  - `gui/extWindows` 34, `gui/mainWaddon` 25, `gui/mainWindow` 3
  - `logic/controllers` 5, other `logic` 3, `base` 3
  - `mountcontrol` 8 modules: `Satellite(App().mount)` (77x),
    `Setting(App().mount)` (56x), `App().mount.obsSite` (8x)
- Frequent patterns: `app = App()` (58), `mainW.app = App()` (27),
  `Sat/Setting(App().mount)`, `SimulatorWindow(app=App(), ...)` (9).

## Design decisions

1. `makeApp` fixture is the only public way to get a stub app in tests.
   `App` stays importable from `baseTestApp` only for `makeApp` itself and
   for `test_makeApp.py`.
2. Attribute overrides replace manual post-construction assignments
   (`app.mount.host = x` → `makeApp(mount__host=x)`), only where they
   directly follow the construction.
3. Module-level / `setup_method` / fixture-internal usage: request the
   `makeApp` fixture as parameter. Where a module-scoped fixture is needed,
   build the module fixture on top of `makeApp`.
4. No behavioural changes to `App`; no new features.
5. `mountcontrol` tests must stay free of `mw4.gui`/Qt-widget imports; they
   only need `makeApp().mount` – use a local fixture `mount(makeApp)`.

## Steps

1. **Baseline**: run full suite and coverage; record counts
   (5226 passed / 38 skipped, 100 %).
2. **Prepare fixtures** (`../tests/conftest.py`):
   - verify `makeApp` fixture teardown calls `app.shutdown()` for every
     created app (timer + thread pool cleanup); add tracking list if missing.
   - add `mount` convenience fixture only if used in ≥ 3 modules.
3. **Migrate in batches** (run the batch tests after each batch):
   1. `base` + `logic/file`, `logic/fits`, `logic/databaseProcessing`,
      `logic/controllers` (≈ 11 modules, pilot).
   2. `logic/drivers` (59 modules) – mechanical:
      `Camera(app=App())` → fixture parameter `makeApp` / `app`.
   3. `gui/mainWaddon`, `gui/mainWindow`, `gui/utilities` (≈ 29 modules).
   4. `gui/extWindows` (34 modules).
   5. `mountcontrol` (8 modules; `test_satellite.py`, `test_setting.py`
      via a single fixture instead of 133 inline `App().mount`).
   6. `test_deviceRegistry.py`, `test_loader.py`.
4. **Guard against regression**: add a ruff/grep check (e.g. a small test in
   `test_testMapping.py` or a CI step) failing when `App()` is called in
   `../tests/unit_tests` outside `baseTestApp.py` and `test_makeApp.py`.
5. **Optional** (roadmap note): trim per-device facade tests that duplicate
   `test_deviceFacade.py`. Only after step 3 is complete.
6. **Close out**: update `2026-10-20_review_copilot_open.md`
   (T1 done, remove roadmap item 3) and the changelog if required.

## Verification

- Per batch: `uv run pytest <batch paths> -n auto`.
- Final: `uv run ruff format && uv run ruff check`, `uv run lint-imports`,
  full `uv run pytest --cov` → 100 % line and branch coverage, same pass
  and skip counts as the baseline.
- Check that stress tests / `../tests/work` are not further polluted.

## Risks

- Tests relying on state shared through a module-level `App()` – convert to
  fixture scope carefully (function scope by default).
- Many threads/timers if apps are not shut down – ensure fixture teardown.
- Large mechanical diff – keep batches small and reviewable (≤ 30 modules).

## Out of scope

- Narrow protocols (A1/A6), in-memory fakes (T4), changes to `../src/mw4`.

