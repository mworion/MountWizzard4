# Plan: Improve `modelRun.py` and `tabModel.py`

Scope: `../../src/mw4/logic/modelBuild/modelRun.py`,
`src/mw4/gui/mainWaddon/tabModel.py` (+ new/related modules in
`src/mw4/logic/modelBuild/`).
Tests: `tests/unit_tests/logic/modelBuild/test_modelRun*.py`,
`tests/unit_tests/gui/mainWaddon/test_tabModel.py`.

Rules for every phase: camelCase, full type annotations, no leading
underscore methods, no `# pragma: no cover`, 100 % coverage, Ruff
format + lint clean, module-scoped tests. Each phase is a separate,
independently mergeable commit.

---

## Phase 1 – Small bug fixes (low risk)

| # | Change | File |
|---|--------|------|
| 1.1 | Remove dead `if not self.modelData:` guards in `cancelBatch`, `pauseBatch`, `endBatch` (QObject is always truthy). | tabModel |
| 1.2 | `collectBuildModelResults`: append a **copy** (`dict(item)`) so metadata/angle conversion does not mutate `modelBuildData`. | modelRun |
| 1.3 | `addMountModelToBuildModel`: rename `mount_entry` -> `mount`; on length mismatch return a status (`bool`) so the caller can inform the user instead of silently writing an empty file. | modelRun, tabModel |
| 1.4 | `programModelToMountFinish`: if save data is empty, emit a `msg` warning and skip writing the file. | tabModel |
| 1.5 | `programModelToMount`: avoid handler leak/double connect (disconnect before connect, or use a one-shot guard flag). | tabModel |
| 1.6 | `runBatch`: do condition checks and the time-sync dialog **before** emitting `STATUS_MODEL_BATCH`. | tabModel |
| 1.7 | `startExposureAfterSlew`: reset `mountSlewed`/`domeSlewed` after triggering so stray `slewed` signals cannot restart the exposure. | modelRun |
| 1.8 | `startNewSlew`: set `modelRunKey` after the exhaustion check; cache `self.app.dReg[...]` lookups in locals. | modelRun |
| 1.9 | `startPass`: check cancel/end **before** emitting `statusRetry`. | modelRun |
| 1.10 | `showProgress`: replace `datetime(*localtime[:6], tzinfo=UTC)` hack with `datetime.now() + timedelta(seconds=...)`; format elapsed/estimated from seconds (no 24 h wrap). | tabModel |
| 1.11 | Type fixes: `showStatusRetry(statusData: int)`, `showStatusExposure/Slew(statusData: list)`, binning format `:1f` -> `:.0f`. | tabModel |
| 1.12 | Remove unused `self.model`, `self.timeStartModeling`, `pauseBuild` (verify no usage via grep first). | tabModel |

Tests: extend existing tests; add cases for mismatch warning, no
double connect, stray slewed signal, retry+cancel ordering.

## Phase 2 – Robust slew / cancel behaviour

| # | Change |
|---|--------|
| 2.1 | Replace the recursion in `startNewSlew` on "Slew not possible" (emit result + `startSlew.emit()`) by connecting `startSlew` with `Qt.QueuedConnection` (or an explicit loop) to bound stack depth. |
| 2.2 | REVERTED by decision: no device is stopped or aborted on cancel or end (no `abortDevices`, no in-flight tracking). |
| 2.3 | REVERTED by decision: *End* keeps the original semantics (stop scheduling, finish the pass immediately, program with solved points) and never stops or aborts any device. |
| 2.4 | Add a test for cancel during the 1 s clear wait in `runBatch` (explicit rather than accidental behaviour). |

## Phase 3 – Progress estimation (SKIPPED by decision – keep current behaviour)

| # | Change |
|---|--------|
| 3.1 | Do not reset `processed` for already processed points on retry; compute progress against the total number of points and keep the percentage monotonic. |
| 3.2 | Estimate remaining time from points done in the current pass vs. points of the current pass. |

## Phase 4 – Typed config (middle path, DONE)

Decision: only `ModelTiming` and `ModelRunConfig`; `modelBuildData` stays
`dict[str, dict[str, Any]]` (no `ModelPoint`, to avoid regression risk in the
run flow and the saved `.model` format).

- `../../src/mw4/logic/modelBuild/modelTypes.py`: `ModelTiming(IntEnum)` and frozen
  `ModelRunConfig` (`imageDir`, `numberRetries`, `retriesReverse`,
  `waitTimeExposure`, `modelTiming`, `plateSolveApp`).
- `ModelData.runModel(config)` stores `self.config`; the class constants and
  the six public config attributes are gone. `modelName` stays on
  `ModelData` because the file-model flow uses it too.
- Tab: `setupBatchData()` returns the config, `getModelTiming()` replaces
  `setModelTiming()`.

## Phase 5 – Move business logic out of the GUI (DONE)

| # | Change |
|---|--------|
| 5.1 | Pure functions `buildSaveData(buildData, meta, mountModel)` and `saveModelFile(path, data)` in `modelRunSupport`. `ModelData` no longer holds save data or `version/profile/firmware/latitude`; the tab builds the meta via `getSaveMeta()`. |
| 5.2 | `ModelData.loadFromFiles(paths) -> str` (stateful part). `runFileModel` stays in the tab (dialog, naming, operation state). |
| 5.3 | `ModelData` emits `pointStatus(index, status)` and `pointMarkersChanged`; the tab forwards them to `app.buildPoint` and `app.updatePointMarker`. `ModelData` no longer touches `app.buildPoint` / `app.updatePointMarker`. |

## Phase 6 – Finalisation (DONE for phases 1, 2, 5; repeat after Phase 4)

1. `uv run ruff format` / `uv run ruff check` on all touched files,
   fix all findings; verify line length from `../../pyproject.toml`.
2. Run the touched test modules with coverage (100 % for the changed
   modules).
3. Run the complete test suite as the last step.

## Order and dependencies

Phase 1 -> 2 -> (3 skipped) -> 4 -> 5 -> 6 (after each).

## Open questions

- Desired semantics of "End" (finish in-flight points vs. stop now)?
