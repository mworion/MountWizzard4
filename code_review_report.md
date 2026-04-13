# MountWizzard4 — Code Review Report

**Date:** 2026-04-12  
**Reviewer:** GitHub Copilot  
**Scope:** `src/mw4/` (excluding `src/mw4/gui/widgets/` — auto-generated; `src/mw4/indibase/` — third-party library)  

---

## Executive Summary

The codebase is well-structured and the project conventions are broadly followed. The ruff linter (with the project's own configuration) reports **zero violations**, and the architecture separation between `logic/`, `base/`, and `gui/` is mostly clean. However, four categories of issues require attention:

| Category | Severity | Count |
|---|---|---|
| Threading / safety | 🔴 High | 4 distinct patterns |
| Missing test coverage | 🟡 Medium | 3 untested source modules |
| Architecture violations | 🟡 Medium | 4 files with cross-layer imports |
| Readability / naming | 🟢 Low | ~15 specific items |

---


# MountWizzard4 — Code Review Report (updated)

**Date:** 2026-04-13
**Reviewer:** GitHub Copilot
**Scope:** `src/mw4/` (excluding `src/mw4/gui/widgets/` — auto-generated; `src/mw4/indibase/` — third-party library)

---

## Executive summary

I re-ran a repository inspection (static reads of source and tests). Several of the issues called out in the previous report have already been addressed in the codebase; a smaller set of correctness and threading items remain and should be actioned. Notable changes since the previous report:

- The problematic GUI-only helper `sleepAndEvents` is no longer used by core/logic modules; a thread-safe helper `mainThreadSleep` exists in `src/mw4/base/threadUtils.py` and is imported where a plain sleep is required.
- Most naming / style items mentioned (camelCase signal/function names and the `ImageManage` typo) have been fixed.
- Missing unit tests that were previously flagged (alignstars, measureAddOns, mountSignals, signalsDevices, indiClassAddOns) are present in `tests/unit_tests/`.
- `MAX_THREAD_COUNT` constant is present in `mainApp.py`.

Remaining important concerns (summary):

- A model build run (`ModelData.runModel` / `tabModel.runBatch`) still runs synchronously on the main thread and blocks using sleep calls — this is a re-entrancy / responsiveness risk and should be moved to a `Worker`.
- Some cross-thread boolean flags (e.g., `Camera.exposing`, `PlateSolve.solveLoopRunning`) are still plain booleans and would benefit from `threading.Event` or an atomic guard.
- `PlateSolve.startSolveLoop` does not guard against double-starting the same Worker (possible duplicate runs).
- `ModelData.sendModelProgress` still contains an unused expression (an unassigned `sum(...)`) that should be removed or assigned.
- A few remaining code paths (e.g., `UploadPopup.closePopup`) still block the main thread while waiting on background state; these should be rewritten to use signals or have the polling run in a worker.

The rest of the document below updates the earlier findings to the current project state and provides targeted recommendations.

---

## 1. Threading and concurrency (current state)

1.1 Removal / migration of GUI-only sleep helper

What changed:
- The project no longer exposes a `sleepAndEvents` helper from `gui.utilities.qtHelpers` to core modules. Instead `src/mw4/base/threadUtils.py` provides `mainThreadSleep(ms: int)` which wraps `time.sleep(ms / 1000.0)`. Core/logic modules import `mainThreadSleep` or use `time.sleep` directly.

Impact / recommendation:
- This eliminates the Qt-object creation-on-worker-thread safety issue previously reported. Continue to reserve any Qt event-loop helpers for GUI code; use `time.sleep` / `threading.Event.wait()` inside worker threads.

1.2 Long-running model build still runs on the main thread (action required)

Location:
- `src/mw4/gui/mainWaddon/tabModel.py::runBatch()` calls `self.modelData.runModel()` synchronously.
- `src/mw4/logic/modelBuild/modelRun.py::runModel()` / `runThroughModelBuildData()` loop using `mainThreadSleep(500)`.

Why this matters:
- Even though `mainThreadSleep` is a plain time.sleep helper, calling it on the main (GUI) thread blocks the event loop. The previous nested event-loop workaround was removed, but the blocking behavior remains and will make the GUI unresponsive during model runs.

Recommendation:
- Move the model run to a `Worker` (QThreadPool) and use signals for progress and status. Do not call blocking sleeps on the main thread.

1.3 Unprotected boolean flags

Location / status:
- `src/mw4/logic/camera/camera.py` — `self.exposing` is still a boolean.
- `src/mw4/logic/plateSolve/plateSolve.py` — `self.solveLoopRunning` remains a boolean and `startSolveLoop` still sets it unconditionally.

Recommendation:
- Replace cross-thread boolean guards with `threading.Event` (e.g., `self._stop_event = threading.Event()`) or use a small atomic wrapper. At minimum, guard `startSolveLoop` so the worker is not started twice.

1.4 discoverDevices re-entrancy / signal wiring

Location / status:
- `src/mw4/base/indiClass.py::discoverDevices()` now uses the `discoverMutex` (QMutex.tryLock) and calls `mainThreadSleep(2000)` while connected. The mutex prevents concurrent calls. The temporary signal connection is still performed and disconnected afterwards.

Recommendation:
- The current mutex approach is acceptable; optionally use `Qt.ConnectionType.UniqueConnection` to avoid duplicate connects.

1.5 upload popup blocking

Location / status:
- `src/mw4/gui/extWindows/uploadPopupW.py::closePopup()` still polls `self.pollStatusRunState` and calls `mainThreadSleep(250)` while waiting; the method runs on the main thread as it is a slot connected to a worker's result signal.

Recommendation:
- Convert the polling to a non-blocking pattern: either (a) let `pollStatus` emit a signal when the remote status is final and have `closePopup` respond, or (b) run the polling loop in a worker and signal the UI. Avoid busy/sleep loops on the main thread.

---

## 2. Tests and coverage (current state)

Status:
- Tests for modules that were previously missing have been added:
  - `tests/unit_tests/logic/buildData/test_alignstars.py` exists.
  - `tests/unit_tests/logic/measure/test_measureAddOns.py` exists.
  - `tests/unit_tests/mountcontrol/test_mountSignals.py` exists.
  - `tests/unit_tests/base/test_signalsDevices.py` exists.

Recommendation:
- Verify coverage runs (CI) to ensure lines are covered at the levels required by project policy. If the project policy enforces 100% coverage, run pytest --cov to check for remaining gaps.

---

## 3. Architecture & style (current state)

3.1 Cross-layer imports

Status:
- Import of GUI utilities from logic/base has been removed for the `sleepAndEvents` case (migrated to `base/threadUtils`). The one-way dependency between GUI ← logic/base is preserved.

Recommendation:
- Keep GUI-only helpers in `gui/` and non-GUI helpers in `base/` or `logic/` as appropriate.

3.2 Docstrings

Status:
- `src/mw4/mountcontrol/mountSignals.py` still lacks a descriptive module/class docstring. `MountDevice` in `mount.py` likewise has no explanatory docstring.

Recommendation:
- Add short class/module docstrings for public classes to improve readability and generated docs.

---

## 4. Readability / minor correctness issues (current state)

4.1 Naming fixes applied

What changed:
- `mainApp` uses `gameSL` and `gameSR` (camelCase) — the earlier snake_case issue was fixed.
- The `ImageManage` typo in `mainWindowAddons` is fixed.
- Several function renames to camelCase (CLI, sensors, satellite helper) have been applied.

4.2 Remaining small issues

- `modelRun.sendModelProgress` still has an unassigned `sum(...)` expression (dead code) and should be fixed by assigning or removing it.
- `mainApp.MAX_THREAD_COUNT` constant is present — good.

Recommendation:
- Remove or assign the unused `sum(...)`. Consider adding `successCount` to the progress payload if that information is useful to the UI.

---

## 5. Actionable checklist (recommended next steps)

1. Move `ModelData.runModel()` execution off the main thread by starting it in a `Worker`; wire its `progress` and status signals to the UI. (High priority)
2. Replace cross-thread boolean guards with `threading.Event` where appropriate and guard `startSolveLoop` against double-start. (Medium priority)
3. Refactor `UploadPopup.closePopup()` to avoid blocking the main thread; use signals or move polling into a worker. (Medium priority)
4. Remove the unused expression in `ModelData.sendModelProgress`. (Low priority)
5. Add short docstrings to `mountSignals.py` and `mount.py`. (Low priority)
6. Run the test suite and coverage tool (`pytest --cov=src/mw4`) and resolve any uncovered lines required by policy. (Medium priority)

---

If you want, I can now automatically apply the low-risk fixes (assign the unused sum, guard startSolveLoop) and create PR-ready patches for the higher-risk changes (moving model run into a Worker and refactoring upload popup). Which of these would you like me to do next?

*End of updated report*
