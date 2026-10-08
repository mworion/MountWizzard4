# Plan – Review 2026-09-29, Recommendation 4

**Status:** implemented

Make the unit tests safe to run with `pytest-xdist` (`-n auto`).

Source: `gists/work_agent/2026-09-29-review.md`, section 7.1

---

## 1. Findings

A temporary order harness ran the suite reversed per module and shuffled with
six seeds, both serially and with `-n 8`. It found two independent causes:

1. **Shared work directory:** 30 test modules read, write, and delete files in
   `tests/work/*` (for example `glob("tests/work/image/*.fit*")` + `os.remove`
   in module fixtures). Parallel workers delete each other's files.
2. **Order-dependent tests:** 137 tests in 25 modules only pass when an
   earlier test in the same module has already set the needed state on the
   module-scoped fixture (for example `MountSetting.slewRate`,
   `measure.data["time"]`, `hidController.deviceConnected`, or a real modal
   `MWInputDialog.getInt`). xdist's default `load` mode splits a module across
   workers, so that state is missing.

## 2. Design

### (a) Per-worker sandbox – `tests/conftest.py`

When `PYTEST_XDIST_WORKER` is set, the worker's `pytest_configure`:

- creates a temporary sandbox directory,
- symlinks every top-level repo entry except `tests`, and every `tests/*`
  entry except `work`,
- copies `tests/work` into the sandbox,
- puts the repo root on `sys.path` and changes into the sandbox.

`pytest_unconfigure` changes back and removes the sandbox. The relative paths
(`tests/work/...`, `tests/testData/...`, `data`, `src/...`) stay the same, so
none of the 30 modules has to change. Serial runs are unchanged.

### (b) `--dist loadfile` – `pyproject.toml`

Add `--dist=loadfile` to `addopts`. Each module runs on one worker, so each
module-scoped fixture (for example a full `Ui_MainWindow` setup) is built once
per module instead of once per worker. Without `-n` the option has no effect.

### (c) Independent tests – 25 test modules

Every order-dependent test sets up its own preconditions: attribute values,
data dicts, worker/mutex state, and mocks for modal dialogs. Fixtures stay
module-scoped, as the project rules require. If many tests in a module depend
on the same state, a small function-scoped autouse `reset` fixture restores it.
Test intent and assertions are not weakened. Missing attributes in the shared
stubs (`tests/unit_tests/unitTestAddOns/*Stubs.py`) are added there.

Affected modules (failure count):

| Module | # |
|---|---|
| logic/buildData/test_buildpoints.py | 31 |
| gui/mainWaddon/test_tabMount_Sett.py | 26 |
| gui/mainWaddon/test_tabImage_Manage.py | 11 |
| gui/extWindows/test_devicePopupW.py | 7 |
| gui/extWindows/measure/test_measureW.py | 7 |
| base/test_alpacaAscomCommon.py | 6 |
| mountcontrol/test_mountTime.py | 5 |
| logic/modelBuild/test_modelRun.py | 5 |
| gui/mainWaddon/test_tabModel.py | 5 |
| logic/hidController/test_hidController.py | 4 |
| logic/profiles/test_profile.py | 3 |
| logic/measure/test_measure.py | 3 |
| logic/environment/test_sensorWeatherOnline.py | 3 |
| gui/mainWaddon/test_tabModel_Manage.py | 3 |
| gui/mainWaddon/test_tabAlmanac.py | 3 |
| base/test_audioManager.py | 3 |
| logic/databaseProcessing/test_dataWriter.py | 2 |
| gui/mainWaddon/test_tabMount_Move.py | 2 |
| gui/extWindows/image/test_imageW.py | 2 |
| logic/dome/test_domeAlpaca.py | 1 |
| gui/mainWaddon/test_tabModel_BuildPoints.py | 1 |
| gui/mainWaddon/test_astroObjects.py | 1 |
| gui/extWindows/simulator/test_s_horizon.py | 1 |
| gui/extWindows/setting/test_tabSettGui.py | 1 |
| gui/extWindows/hemisphere/test_hemisphereDraw.py | 1 |

## 3. Verification

1. Serial: `pytest tests/unit_tests --cov` → all pass, 100 % coverage.
2. Parallel: `pytest tests/unit_tests -n auto` → all pass, repeated 3×.
3. Order harness (temporary, not committed): reversed + shuffled per module
   → no failures except the nativeQt dialog tests, which fail only because
   the harness disables `exec`.
4. Ruff format/check clean.
5. Update the review (section 10, rec 4 ✅).
