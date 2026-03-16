# Unit test optimization plan (`tests/unit_tests`)

## Scope checked
I reviewed the full `tests/unit_tests` tree and generated a suite inventory.

Current snapshot:
- **174** test files
- **3387** test functions
- Heavy concentration in:
  - `tests/unit_tests/gui` (**81** files)
  - `tests/unit_tests/logic` (**59** files)
- Large monolithic modules (examples):
  - `mountcontrol/test_obsSite.py` (~1286 lines)
  - `mountcontrol/test_setting.py` (~1244 lines)
  - `mountcontrol/test_model.py` (~1085 lines)
  - `indibase/test_indiClient.py` (~955 lines)
- Pattern observations:
  - Very high use of `autouse` fixtures (especially `function` fixtures)
  - Almost no parameterized tests (`@pytest.mark.parametrize` usage is effectively absent)
  - Many numbered test names (e.g. `test_xxx_1`, `test_xxx_2`) that obscure intent
  - A meaningful subset of files contains mostly smoke-style tests with weak/no assertions

---

## Goals (keeping pytest + coverage)
1. Keep **pytest** as the only test infrastructure.
2. Improve readability, execution speed, and maintainability.
3. Improve trustworthiness of tests by increasing assertion quality.
4. Keep and improve **coverage** reporting with `pytest-cov`.

---

## Optimization plan

### Phase 1 — Baseline and segmentation (no behavior change)
- Keep current file tree runnable while introducing markers:
  - `@pytest.mark.gui`
  - `@pytest.mark.logic`
  - `@pytest.mark.mountcontrol`
  - `@pytest.mark.slow` (for expensive tests)
- Add fast/targeted run profiles to developer workflow (still pytest):
  - `pytest tests/unit_tests -m "not slow"`
  - `pytest tests/unit_tests/logic`
  - `pytest tests/unit_tests/gui -m "gui and not slow"`
- Keep CI stable by first mirroring current behavior, then tightening subsets.

### Phase 2 — Fixture refactor and de-duplication
- Create shared fixture modules under `tests/unit_tests/unitTestAddOns/` and move repeated setup there.
- Replace many `autouse=True` fixtures with explicit fixture injection where practical.
- Consolidate repeated mocks (`mock.patch` clusters) into reusable helper fixtures/factories.
- Introduce lightweight factory helpers for common app/device objects from `baseTestApp`.

Expected result: lower setup overhead, easier to reason about dependencies, fewer hidden side effects.

### Phase 3 — Test naming and parametrization
- Rename numbered tests to behavior-driven names:
  - from `test_sendAnalyseFile_1` / `test_sendAnalyseFile_2`
  - to `test_send_analyse_file_handles_empty_input` / `test_send_analyse_file_updates_state`
- Replace repetitive, near-identical tests with parametrization:
  - table-driven inputs/outputs via `@pytest.mark.parametrize`
- Keep one assertion intent per test block where possible.

Expected result: fewer lines, better failure diagnostics, simpler maintenance.

### Phase 4 — Break up oversized files
Split very large files into topic-based modules while preserving the same coverage target:
- `mountcontrol/test_obsSite.py` → e.g. `test_obsSite_coordinates.py`, `test_obsSite_validation.py`, `test_obsSite_io.py`
- `mountcontrol/test_setting.py` → protocol/features grouped modules
- `indibase/test_indiClient.py` → connection/message/event modules

Expected result: faster navigation, smaller review scope, reduced merge conflicts.

### Phase 5 — Strengthen assertions and remove weak smoke tests
- Audit files with weak/no assertions and convert smoke tests to state/output verification.
- Prefer asserting:
  - return values
  - emitted signals/events
  - state transitions
  - interactions (`mock.assert_called_once_with(...)`)
- Keep smoke tests only where construction/import checks are intentionally the contract.

### Phase 6 — Coverage strategy (pytest-cov)
Keep `pytest` + `pytest-cov` and report both terminal + XML/HTML:

```bash
pytest tests/unit_tests \
  --cov=src/mw4 \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml \
  --cov-report=html:htmlcov
```

Then enforce practical thresholds in stages:
1. Start with a non-blocking baseline report.
2. Add per-area targets (`logic`, `mountcontrol`, `gui`).
3. Finally enable CI gate (`--cov-fail-under=<agreed baseline>`).

---

## Suggested execution order (incremental, low risk)
1. Add markers and run profiles.
2. Refactor shared fixtures/mocks.
3. Rename + parametrize in highest-duplication files first.
4. Split largest files.
5. Strengthen weak assertions.
6. Enable staged coverage thresholds in CI.

This sequence keeps existing behavior stable while progressively improving speed, clarity, and measurable quality.
