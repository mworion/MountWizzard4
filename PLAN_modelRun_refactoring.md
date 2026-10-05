# Plan: Improve `modelRun.py` and `tabModel.py`

Scope: `src/mw4/logic/modelBuild/modelRun.py`,
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

## Phase 4 – Typed data model (internal refactoring, OPEN)

State after phases 1, 2 and 5 (this is the baseline for Phase 4):
- `OperationStatus(IntEnum)` exists (`mw4/base/operationStatus.py`).
- `ModelData` no longer owns save data or `version/profile/firmware/latitude`
  (`buildSaveData` / `saveModelFile` in `modelRunSupport`; the tab builds the
  meta via `getSaveMeta()`).
- `ModelData` talks to the GUI only via signals: `pointStatus(int, int)`,
  `pointMarkersChanged`, `progress`, `statusExpose/Solve/Slew/Retry`,
  `finished`. `startSlew` is a queued self-signal.
- Public config attributes still written by `Model.setupBatchData` /
  `setModelTiming`: `imageDir`, `modelName`, `numberRetries`,
  `retriesReverse`, `waitTimeExposure`, `plateSolveApp`, `modelTiming`.
- Run state attributes: `cancelBatch`, `pauseBatch`, `endBatch`,
  `passActive`, `slewPending`, `mountSlewed`, `domeSlewed`,
  `pointsInFlight`, `retries`, `runTime`, `modelRunList/Iterator/Key`.
- `modelBuildData` is still `dict[str, dict[str, Any]]` with magic string
  keys; `loadModelsFromFile`, `buildSaveData`, `writeRetrofitData`,
  `convertAngleToFloat/FloatToAngle` operate on those dicts.

Steps:
1. `modelTypes.py` (new, `src/mw4/logic/modelBuild/`):
   - `class ModelTiming(IntEnum)`: `CONSERVATIVE=0`, `NORMAL=1`,
     `PROGRESSIVE=2` (replaces the class constants on `ModelData`; update
     `tabModel.setModelTiming` and the tests that use
     `modelData.PROGRESSIVE` etc.).
   - `@dataclass(frozen=True) class ModelRunConfig`: `imageDir`,
     `modelName`, `numberRetries`, `retriesReverse`, `waitTimeExposure`,
     `modelTiming`, `plateSolveApp`.
   - `@dataclass class ModelPoint`: typed fields for the keys written in
     `prepareModelBuildData`, `addMountDataToModelBuildData`,
     `exposeImage` and the plate-solve result (`success`, `message`,
     `processed`, ...), plus `toDict()` / `fromDict()`.
2. `ModelData.runModel(config)`: tab builds the config from the UI in one
   place (merge `setupBatchData` + `setModelTiming`); drop the 7 public
   config attributes.
3. Group the run flags into one small state object or keep them as they
   are if that is simpler (decide when implementing; no behaviour change).
4. `modelBuildData: dict[str, ModelPoint]`. Adapt `startNewSlew`,
   `exposeImage`, `collectPlateSolveResult`, `buildProgModel`,
   `checkRetryNeeded`, `generateRunIterator`, `sendModelProgress`.
   At the file boundaries convert with `toDict()` / `fromDict()` so
   `modelRunSupport` and the JSON format stay unchanged.
5. Tests: update fixtures (`buildRunData`, `solveResult`) and add
   round-trip tests (`fromDict(toDict(x)) == x`, and a saved model file
   from `testData` loads and saves identically).

Risk: widest change, touches almost every method of `ModelData`. Do it in
its own commit; verify the saved `.model` JSON is byte-identical for the
same input.

## Phase 5 – Move business logic out of the GUI (DONE)

| # | Change |
|---|--------|
| 5.1 | Pure functions `buildSaveData(buildData, meta, mountModel)` and `saveModelFile(path, data)` in `modelRunSupport`. `ModelData` no longer holds save data or `version/profile/firmware/latitude`; the tab builds the meta via `getSaveMeta()`. |
| 5.2 | `ModelData.loadFromFiles(paths) -> str` (stateful part). `runFileModel` stays in the tab (dialog, naming, operation state). |
| 5.3 | `ModelData` emits `pointStatus(index, status)` and `pointMarkersChanged`; the tab forwards them to `app.buildPoint` and `app.updatePointMarker`. `ModelData` no longer touches `app.buildPoint` / `app.updatePointMarker`. |

## Phase 6 – Finalisation (DONE for phases 1, 2, 5; repeat after Phase 4)

1. `uv run ruff format` / `uv run ruff check` on all touched files,
   fix all findings; verify line length from `pyproject.toml`.
2. Run the touched test modules with coverage (100 % for the changed
   modules).
3. Run the complete test suite as the last step.

## Order and dependencies

Phase 1 -> 2 -> (3 skipped) -> 4 -> 5 -> 6 (after each).

## Open questions

- Desired semantics of "End" (finish in-flight points vs. stop now)?
