# Test Performance Analysis & Improvements

## Summary
The earlier conclusion ("performance is optimal, keep as-is") was **incorrect**. A real
review found several tests that were paying genuine wall-clock penalties due to
**ineffective mocks** and **heavy background workers started during fixture construction**.
Fixing these removed the slow outliers without any loss of coverage.

The worst-case single-test duration dropped from **~0.7s to ~0.22s**, and the remaining
top entries are now unavoidable one-time module setup (App / ephemeris loading) plus one
test that intentionally measures real sleeping.

## Root Causes Found & Fixed

### 1. Dead mock in download popup tests (~1.0s)
`test_closePopup_1/2` used a fixture `mocked_sleepAndEvents` that patched `time.sleep`
and set `pollStatusRunState`. But `closePopup()` does **not** call `time.sleep` — it calls
`mainThreadSleep(500)` (a real 500 ms `QEventLoop`), and `pollStatusRunState` no longer
exists. The mock was dead code, so each test really waited 500 ms.
**Fix:** patch `downloadPopupW.mainThreadSleep` instead. Also removed the now-unnecessary
fixture from `test_downloadFileWorker_9` (it never sleeps).

### 2. Heavy Almanac worker started in fixture construction (~0.65s each, 3 modules)
`Almanac.__init__` calls `plotAll()` → `showTwilightDataPlot()`, which starts a worker
computing a **full year** of twilight events (`almanac.find_discrete`). This ran during
construction in three module fixtures:
- `test_tabAlmanac.py` (Almanac directly)
- `test_mainWindowAddons.py` (`MainWindowAddons` builds `Almanac`)
- `test_mainWindow.py` (`MainWindow` builds `MainWindowAddons` → `Almanac`)

The module-teardown `waitForDone()` then blocked until that computation finished.
**Fix:** patch `Almanac.showTwilightDataPlot` only around the construction call in each
fixture. The worker itself is still covered by the dedicated `showTwilightDataPlot` tests.

### 3. `switchProfile` waited on the real thread pool (~0.7s)
`test_switchProfile_switches_config` exercised `switchProfile()`, which calls
`self.threadPool.waitForDone(10000)`. With the module-scoped fixture this blocked on
worker threads left over from other tests.
**Fix:** mock `threadPool.waitForDone` in that unit test (it tests config switching logic,
not the thread pool).

### 4. Wrong patch target for the game-controller loop (~0.4s)
`workerGameController()` loops with `mainThreadSleep(100)`. `tabSettGui` imports the symbol
directly (`from ... import mainThreadSleep`), so the test patch on
`mw4.base.threadUtils.mainThreadSleep` had no effect and the real 100 ms sleeps ran every
iteration.
**Fix:** patch `mw4.gui.extWindows.setting.tabSettGui.mainThreadSleep` (the bound name) in
both `test_workerGameController_with_new_data` and
`test_workerGameController_continues_on_same_data`.

## Key Lesson
`threadPool.waitForDone(10000)` is **not** a 10 s cost — it returns as soon as workers
finish; the number is only a max timeout. The real cost was the **work** the threads were
doing (year-long astronomy calculations) and **real sleeps** that mocks failed to patch.
Tuning the timeout numbers (the earlier "experiment") was measuring noise.

## Result
- All **4,217** tests pass, 12 skipped — no coverage lost.
- Eliminated the slow outliers: 0.7 s teardowns, 0.5 s popup waits, 0.3–0.4 s controller
  loops, and the 0.7 s profile-switch wait.
- Remaining top durations are one-time module setup (App + ephemeris load) and
  `test_mainThreadSleep_sleeps_at_least_specified_time`, which legitimately sleeps.

## Files Changed (tests only)
- `tests/unit_tests/gui/extWindows/test_downloadPopupW.py`
- `tests/unit_tests/gui/mainWaddon/test_tabAlmanac.py`
- `tests/unit_tests/gui/mainWindow/test_mainWindowAddons.py`
- `tests/unit_tests/gui/mainWindow/test_mainWindow.py`
- `tests/unit_tests/gui/extWindows/setting/test_tabSettGui.py`

