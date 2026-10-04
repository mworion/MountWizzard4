# Fixture Scope & Isolation Audit

## Goal
Decide whether to (a) harden the few risky module-scoped fixtures, and (b) whether it is
safe to push the expensive shared setup down to **session** scope.

## What was done
1. **Static audit** of all ~157 `scope="module"` fixtures for leak patterns
   (permanent mock reassignment, unrestored state, unstopped patchers, `monkeypatch`
   misuse, signal connects without disconnect).
2. **Hardened the 3 genuine latent spots** found statically (see below).
3. **Added `pytest-randomly`** and ran the whole suite in randomized order to empirically
   prove/disprove isolation.

## Static audit result
Most module-scoped fixtures are safe because tests either use `mock.patch.object(...)`
context managers (auto-restored) or an `autouse` function-scoped reset fixture
(`test_alpacaClass.py::resetState` is the gold-standard pattern). Three in-test mutations
had no auto-restore; all three were **latent** (no later test depended on them) and are now
hardened with context managers:

- `tests/unit_tests/gui/mainWaddon/test_tabMount_Sett.py::test_showOffset_8`
  — `obsSite.timeJD` now patched via `mock.patch.object`.
- `tests/unit_tests/logic/environment/test_sensorWeatherOnline.py`
  — `function.location` now patched via `mock.patch.object`.
- `tests/unit_tests/logic/powerswitch/test_pegasusUPBIndi.py`
  — already disconnected its signal slots (no change needed).

## Randomized run result — the decisive finding
Running the full suite in random order (`pytest -p randomly`) produced **24 failures**
(4193 passed, 12 skipped). Deterministic order is fully green (4217 passed). So the suite
is **order-coupled**: it passes only because of the fixed collection order.

Failure categories (representative):

| Category | Example | Root cause |
|---|---|---|
| Shared fixture state leak | `test_sgproClass::test_init_config` → `deviceName == ''` got `'TestCamera'` | earlier test mutated the shared instance; default-asserting test ran after it |
| Counter/list accumulation | `test_buildpoints::test_genGridData2` → `len==12` got `16` | build points accumulated |
| Default reset assumption | `test_cameraAlpacaAscomBase::initAttributes` → `startTimeExposure==0` got epoch | prior test set it |
| Resource ordering | `test_seeingWeather::*` → `FileNotFoundError meteoblue.data` | relies on another test creating the file first |
| Qt object lifecycle | `test_s_horizon::test_create_1` → shiboken "C++ object already deleted" | shared Qt3D objects across tests |
| **Cross-module** leak | `test_buildpoints` passes **alone** in random order but fails **in the full** random run | shared global state beyond the per-module fixture |

The cross-module case is the most significant: it means some state is shared **between
modules**, not just within one.

## Decision on session scope
**Do not move to session scope now.** Session scope increases the lifetime and reach of
shared objects; on a suite that is already order-coupled (and has cross-module leaks),
it would make isolation strictly worse and create hard-to-debug flakiness.

Recommended order of work instead:
1. Keep default runs deterministic (done — see below) so CI stays green.
2. Fix isolation incrementally, module by module, using the randomized run to verify
   (each fixed module should pass under `-p randomly`).
3. Identify and remove the **cross-module** shared state (top priority).
4. Only after the suite is green under randomization, revisit pushing **read-only**
   resources (e.g. the loaded Skyfield ephemeris/timescale) to session scope. Mutable
   objects like `App()`/device stubs should stay module-scoped.

## Tooling / current state
- `pytest-randomly` is installed in the venv and configured **opt-in**: default `addopts`
  now include `-p no:randomly`, so normal/CI runs are deterministic and green.
- Run an isolation audit with:
  ```
  pytest -p randomly                                   # random order
  pytest -p randomly -p no:cacheprovider --randomly-seed=<n>   # reproduce a run
  ```
- Note: `pytest-randomly` was **not** added to project dependencies (the current
  `requires-python >=3.11` vs `scipy-stubs>=3.12` constraint makes `uv` re-resolution
  fail). Add it to the dev dependency group once that constraint is resolved.

## Net change in this pass
- 3 latent fixtures hardened; default suite still 4217 passed / 12 skipped, ~15.7 s.
- Randomized auditing capability added (opt-in), with 24 pre-existing order-dependencies
  now visible and categorized for follow-up.

