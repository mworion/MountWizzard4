# Plan P1 – review of remaining `getattr` / `hasattr` / `setattr`

**Status: implemented 2026-10-23** (5265 passed, 100 % coverage, ruff/pyrefly/lint-imports clean). Deviations: `qtMain.titleBar` guard simply removed (always set in `__init__`); `clickFilters` list dropped (filters are children of the widget); `httpClient` unchanged.

Goal: finish P1 of `2026-10-20_review_copilot_open.md`. `HasSignals`/`HasDriverConfig`
already replaced the `hasattr` checks in `deviceRegistry`, `tabSettDevice`, `devicePopupW`.
The remaining 65 calls (excluding `gui/widgets/`) are reviewed case by case below.
Scope stays small: change only where a typed alternative is clearly better; document
and keep the rest. No behaviour change.

## 1. Inventory and decision

| Group | Where | Decision |
|-------|-------|----------|
| **A. Dynamic UI-name lookup** `getattr(self.ui, f"…{i}")` | `tabPower` (6), `tabMount_Park`, `tabMount_Sett` (2), `tabSat_Search` (4), `tabEnviron_Weather`, `imageW` (2), `tabSettPark` (5), `tabSettAudio` (4), `tabSettRelay` (2), `tabSettDome`, `tabSettDevice` (2), `devicePopupW` (5) | **Keep.** `.ui` files are generated; names are indexed by design. Add one helper `uiWidget(ui, name) -> Any` in `gui/utilities/qtHelpers.py` only if it removes duplication; otherwise leave. Tests already cover every lookup (a typo raises `AttributeError`). |
| **B. Dataclass field access** | `deviceRegistry` 276/294, `devicePopupW` 185/247–254 | **Keep.** Iterating `fields(config)` is the intended dataclass pattern; `HasDriverConfig` already types `config`. |
| **C. Spec-driven mount settings** | `mountSettings.py` 151–180 | **Change (small).** `spec.attribute/minAttribute/maxAttribute/setterName` are strings resolved on `self.setting`. Keep the table, but add a test asserting every spec name exists on `Setting` (guards typos), instead of rewriting to lambdas. |
| **D. Signal-by-name scheduling** | `timeManager.py` 74/79 | **Change.** Replace the `signalName` strings in `CYCLIC_SCHEDULE`/`START_SCHEDULE` by the signal attribute lookup done once in `__init__` (dict `name -> SignalInstance`) or keep `getattr` but validate in a test. Prefer the dict: no runtime `getattr`. |
| **E. Optional attribute probes (real `hasattr`)** | `qtMain.setWindowTitle` (`titleBar`), `qtHelpers` (`clickFilters`), `gPlotBase.findItemByName` (`nameStr`) | **Change.** `qtMain`: initialise `self.titleBar: ... \| None = None` and test `is not None`. `qtHelpers`: store filters in a typed `weakref`-free list attribute declared via a small `ClickFilterHost` protocol or a module-level `WeakKeyDictionary`; removes two `pyrefly: ignore`. `gPlotBase`: `getattr(item, "nameStr", None) == name`. |
| **F. Python-version shim** | `loggerMW.py` 14 (`Logger._set_defaults`) | **Keep**, add a comment why (compat patch). |
| **G. Callable name / duck-typing** | `tpool.py` (3× `__name__`), `alpacaAscomCommon` (`excepinfo`, dynamic COM props), `httpClient` (`requests.<method>`), `angleProperty` (descriptor by attr name) | **Keep.** Dynamic by nature (COM, descriptors, arbitrary callables). `tpool`: factor the triple `getattr(..., "__name__", repr(...))` into one helper. `httpClient` stays (an explicit method map would bind `requests.get` at import and break `mock.patch`). |

## 2. Steps

1. D: `timeManager` signal dict + adapt tests.
2. E: `qtMain.titleBar` init, `qtHelpers` click-filter storage, `gPlotBase` probe; remove the matching `pyrefly: ignore` lines.
3. G: `tpool` name helper; `httpClient` explicit method map.
4. C: spec-name consistency test for `mountSettings`.
5. F: comment in `loggerMW`.
6. A/B: no code change; note in review file that remaining `getattr` are dynamic UI-name or dataclass iteration.

## 3. Validation

- Tests mirror `src/mw4` under `tests/unit_tests/`, module scope, 100 % line and branch coverage, no `pragma: no cover`.
- `uv run pytest tests/unit_tests/<touched modules>`, then full suite.
- `uv run ruff check src && uv run ruff format src`, `uv run pyrefly check`, `uv run lint-imports`.

## 4. Done when

- Only groups A, B, F, G (dynamic by nature) still use `getattr`/`hasattr`/`setattr`.
- P1 in the review file is marked done with the rationale above.
