# Plan – Rec 10 (P4): Extend Ruff Rules and Add a Type Checker

**Date:** 2026-09-30
**Source:** [2026-09-29-status-review.md](2026-09-29-status-review.md), rec 10,
finding P4 (from [2026-09-26-review.md](2026-09-26-review.md))
**Scope:** `pyproject.toml` (Ruff / dev dependencies), `src/mw4` (excluding
`gui/widgets`), `tests`, `.github/workflows`. P5 (return annotations) is
already done.

---

## 1. Finding and Measured State

> Ruff rule set / no type checker: `ignore = ["N999", "BLE001"]`; no `B`,
> `BLE`, `ANN`; no mypy/pyright.

Current config:

```toml
[tool.ruff.lint]
extend-select = ["E", "T2", "UP", "I", "C", "LOG", "W", "SIM", "A", "RUF"]
ignore = ["N999", "BLE001"]
```

- `BLE` is not selected, so the `BLE001` ignore has no effect. **Correction
  (2026-09-30, phase 2):** `N999` is *not* dead config – removing it reports
  157 camelCase module names (project convention), so it stays ignored.
- **CI does not run Ruff** (`unit_macOS/ubuntu/win.yml` only run `pytest`).
  Ruff is only run by hand.
- No type checker is installed (`mypy` / `pyright` / `pyrefly` not in `dev`).

Findings with the extra rules (measured 2026-09-30):

| Rule | `src` | `tests` | Meaning |
|------|------:|--------:|---------|
| `B905` zip-without-explicit-strict | 31 (16 files) | 13 | `zip()` silently cuts to the shortest input |
| `B007` unused-loop-control-variable | 6 | 12 | Loop variable not used |
| `B011` assert-false | 0 | 1 | `assert False` is removed with `python -O` |
| `BLE001` blind-except | 8 | 0 | `except Exception` |
| `ANN001` missing-type-function-argument | 67 (30 files) | – | Parameter without a type |
| `ANN401` any-type | 169 | – | `Any` used as a type (mostly `parent: Any`) |

`B905` in `src`: `hemisphereDraw` (4), `buildpoints` (3), `tabAlmanac` (3),
`horizonDraw` (3), `analyseW` (3), `photometry_analysis` (2), `gPlotBase` (2),
`tabSat_Track` (2), `measureW` (2), and one each in `satellite`,
`satellite_calculations`, `gCustomViewBox`, `tabRelay`, `tabModel_Manage`,
`tabEnviron_Seeing`, `simulator/horizon`.

---

## 2. Decisions Taken in This Plan

| Topic | Decision | Reason |
|-------|----------|--------|
| `ANN401` | **Not enabled** | Most hits are `parent: Any`, kept by decision (rec 13, section 8 of the review). |
| `ANN` for tests | **Not enabled** (per-file ignore `tests/**`) | Test functions and fixtures stay light; the rules target production code. |
| `ANN` subset | `ANN001`, `ANN2xx` (keeps P5 clean) | `ANN002/003` (`*args`, `**kwargs`) are included; `ANN401` excluded. |
| `N999` ignore | **Kept** (corrected in phase 2) | Active; camelCase module names are the project convention. |
| `BLE001` ignore | **Removed** (rule enabled) | Replaced by concrete exceptions or one documented per-line reason. |
| Type checker | **pyrefly** (`pyrefly==1.3.2`, current on PyPI 2026-09-30) as a `dev` dependency | Rust binary wheel, **no Node.js** needed (pyright's PyPI wrapper downloads Node); fast; config in `pyproject.toml` (`[tool.pyrefly]`); supports a baseline file and per-line suppressions. Decision 2026-09-30. |
| CI | New job in `unit_ubuntu.yml`: `ruff format --check`, `ruff check`, `pyrefly check` | Linux only is enough; lint results do not depend on the OS. |

---

## 3. Steps

### Phase 1 – `B` (bugbear), S

1. `extend-select` += `"B"`.
2. **`B905` (31 src, 13 tests):** check every `zip` one by one.
   - Inputs that must have the same length (points/values, x/y, alt/az) →
     `strict=True`. A length mismatch then raises `ValueError` instead of
     dropping data silently. For each changed call in `src`, check whether the
     data can be of different length at runtime (e.g. user-edited horizon or
     build point lists); if so, keep `strict=False` and add a short comment on
     why truncation is intended.
   - Test code: `strict=True`.
3. **`B007` (6 src, 12 tests):** rename to `_` / `_name`.
4. **`B011` (1 test):** `pytest.fail(...)` instead of `assert False`.
5. Tests: for each `src` call switched to `strict=True` where the lists come
   from outside (files, mount, user input), one test with lists of different
   length that shows the handling (exception caught or intended).

### Phase 2 – `BLE` (blind except), S–M

Enable `"BLE"`, remove `BLE001` from `ignore`, then fix the 8 sites:

| Site | Change |
|------|--------|
| `alpacaClass.py:70` `createAlpacaDevice` | Drop `Exception` from the tuple; keep `(ConnectionError, TimeoutError, OSError, RuntimeError)` plus `requests.RequestException` / alpyca `DriverException` if the constructor can raise them (check alpyca). |
| `alpacaClass.py:95,103` `discoverAPIVersion` / `discoverAlpacaDevices` | Same: remove `Exception`; add `requests.RequestException` and `ValueError` (JSON decode). |
| `sgproClass.py:76` `sgproCall` | Remove `Exception`; `requests.RequestException` already covers connection errors and timeouts. Keep `ValueError` if JSON decode is inside the `try`. |
| `alpacaAscomCommon.py:90,103,116` `get/set/callDeviceProp` | **Keep** the broad catch: driver code (alpyca, COM via `pywin32`) can raise anything, and `handleDeviceError` classifies it (rec 3). Add `BLE001` to `per-file-ignores` for this file (no `# noqa` in code; the project has 0). |
| `tpool.py:110` `Worker.run` | **Keep**: the worker boundary must not let anything escape into the pool thread (busy flag, rec 4). Same per-file ignore; the current formatted traceback log stays. |

Result: `per-file-ignores` lists exactly 2 files for `BLE001`, each with a
reason comment in `pyproject.toml`. Tests: existing tests with
`side_effect=Exception` in `alpacaClass` / `sgproClass` switch to the concrete
exceptions; one new test per site shows that an unexpected exception type now
propagates.

### Phase 3 – `ANN001`, S–M

1. `extend-select` += `"ANN001", "ANN002", "ANN003", "ANN201", "ANN202",
   "ANN204", "ANN205", "ANN206"`; `per-file-ignores`: `"tests/**" = ["ANN"]`.
2. Annotate the 67 parameters in 30 files (largest: `astroObjects` 7,
   `satelliteHorW` 7, `qtMain` 4, `gCustomViewBox` 4, `tabModel_Manage` 4,
   `satelliteMapW` 4, `hemisphereW` 4). Use concrete types; `Any` only where
   the value really is untyped (Qt event objects → `QEvent` / subclasses,
   pyqtgraph items → their classes).
3. No behaviour change; the suite must stay green without test changes.

### Phase 4 – Type checker (pyrefly), M

1. `dev` += `"pyrefly==1.3.2"` (pinned like the other dev tools); `uv lock`.
   Config in `pyproject.toml`:

   ```toml
   [tool.pyrefly]
   project-includes = ["src/mw4"]
   project-excludes = ["src/mw4/gui/widgets/**"]
   python-version = "3.12"
   ```

   Run with `uv run pyrefly check`, so pyrefly uses the project venv
   (PySide6, pyqtgraph, skyfield stubs). Check the resolved config once with
   `uv run pyrefly dump-config`.
2. First run with `--summarize-errors=2` → record the number of errors per
   package. Fix them package by package in this order: `base/`,
   `mountcontrol/`, `logic/`, `gui/`.
3. pyrefly has no "basic" mode like pyright. Noisy error kinds that come from
   stub gaps (not from our code) are switched off one by one under
   `[tool.pyrefly.errors]`, each with a comment. No blanket suppressions:
   only targeted `# pyrefly: ignore[<kind>]` with a reason where a stub is
   wrong. The existing `# type: ignore` in `tabMount_Move.py:221` is checked
   on the way (`pyrefly check --remove-unused-ignores` shows unused ones).
4. If the first run shows more than ~150 errors in `gui/` (PySide6 /
   pyqtgraph stub gaps), limit `project-includes` to `base`, `mountcontrol`,
   `logic` for this cycle and record `gui` as a follow-up. A `--baseline`
   file is the fallback only if a package cannot be made clean in this cycle;
   it is committed next to `pyproject.toml` and shrinks over time.
   `--suppress-errors` (writes ignore comments into the code) is **not** used.
5. Known item: `DeviceRegistry(mount=...)` receives a test stub; tests are not
   checked, production is consistent.

### Phase 5 – CI

New job `lint` in `.github/workflows/unit_ubuntu.yml` (after `uv sync`):

```yaml
- name: Lint and type check
  run: |
    uv run ruff format --check src tests
    uv run ruff check src tests
    uv run pyrefly check
```

No Node.js setup step is needed.

### Phase 6 – Verification and documentation

1. `uv run ruff format --check src tests`, `uv run ruff check src tests`,
   `uv run pyrefly check` → clean.
2. `uv run pytest tests/unit_tests -n auto --cov=mw4` → all passed, 100 %.
3. Status review: P4 → ✅ Fixed (or 🟡 if `gui/` is deferred in phase 4),
   rec 10 → ✅ Done; section 2 (`except Exception` counts), section 7 row,
   section 8 decision row (pyrefly as type checker).
4. `.github/copilot-instructions.md`: add pyrefly to the tech stack table
   (Linting row → "Ruff, pyrefly").

---

## 4. Order and Commits

**Status 2026-09-30:** phase 1 ✅ and phase 2 ✅ done (see the status review,
section 7). Phase 4 step 1 ✅ (pyrefly in `dev`, `[tool.pyrefly]`, `uv.lock`);
steps 2–5 (first run, fixes) open. Phase 5 ✅ (`lint` job in `unit_ubuntu.yml`;
`pyrefly check` is present but commented out until phase 4 is clean). Phase 3
open.

One commit per phase (1 → 5); each phase leaves Ruff, tests and coverage
green, so the work can stop after any phase. Phases 1–3 are independent of the
type checker and give most of the value at low risk.

---

## 5. Risks

| Risk | Mitigation |
|------|------------|
| `zip(strict=True)` raises at runtime on data that used to be truncated silently | Case-by-case check in phase 1; `strict=False` with a comment where truncation is intended; tests with unequal lengths. |
| Narrowed excepts in `alpacaClass` / `sgproClass` let an unknown driver or library error escape | Check which exceptions alpyca / `requests` raise; the `tpool` worker boundary still catches and logs anything that reaches it. |
| pyrefly reports many PySide6 / pyqtgraph false positives | Per-kind switches in `[tool.pyrefly.errors]`; scope limited to non-GUI packages if needed (phase 4.4). |
| pyrefly is younger than mypy / pyright; rules or defaults change between versions | Version pinned in `dev`; upgrades are separate commits that re-run the check. |
| Line length | Ruff format; 95 columns. |

---

## 6. Effort

- Phase 1 (`B`): S – 44 sites, mostly mechanical, `zip` review needs care.
- Phase 2 (`BLE`): S – 8 sites, 2 per-file ignores.
- Phase 3 (`ANN001`): S–M – 67 parameters.
- Phase 4 (pyrefly): M – unknown count until the first run.
- Phase 5 (CI): S.



