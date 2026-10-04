# Plan – Review 2026-09-29, Recommendation 1: Event-driven `ModelRun`

Source: `gists/work_agent/2026-09-29-review.md`, section 3.1 (worst case) and
5.1. Status: **✅ implemented** (D1 and D2: fix all). See section 6.

---

## 1. Analysis

### 1.1 What the busy loop really does

```python
def runThroughModelBuildData(self) -> None:          # modelRun.py:302
    ...
    self.startSlew.emit()
    while not self.cancelBatch and not self.endBatch and not self.checkModelFinished():
        mainThreadSleep(500)                          # nested QEventLoop
```

The model pipeline is **already event-driven**:

```
startSlew ─► startNewSlew ─► mount/dome slewed ─► startExposureAfterSlew
         ─► startNewImageExposure ─► camera exposed/downloaded/saved
              ├─► (timing) startSlew ─► next point …
              └─► saved ─► startNewPlateSolve ─► plateSolve.result
                               ─► collectPlateSolveResult (processed = True)
```

The loop does not drive anything. It only **blocks the caller** so that the
synchronous code after it can continue:

- `runThroughModelBuildDataRetries` (retry passes),
- `runModel` (`buildProgModel`, `resetSignals`),
- `Model.runBatch` in `gui/mainWaddon/tabModel.py` (program the mount, park,
  play the sound, set `STATUS_IDLE`).

So the fix is not to rewrite the pipeline. The **synchronous tail** has to become
a **continuation** that runs when the last point is processed. The second
`mainThreadSleep` (`startNewImageExposure`, l. 211) becomes a timer.

### 1.2 Findings along the way (fix in this change)

| # | Finding | Effect |
|---|---------|--------|
| F1 | `startNewImageExposure` counts `waitTime -= 1` per 500 ms (review 5.1) | The wait is half the configured seconds |
| F2 | `tabModel.setModelTiming` sets `modelData.timing`, but `ModelData` reads `modelTiming` | The timing selection is ignored. It is always `CONSERVATIVE` |
| F3 | `tabModel` sets `modelData.name`, but `prepareModelBuildData` uses `modelName` | `item["name"]` is always `""` in the saved model |

F2/F3 are one-line fixes. They are listed because the new tests would otherwise
test the wrong attribute. If you want, they can be split into their own commit.

---

## 2. Target design

### 2.1 `ModelData` (logic) – continuation instead of loop

New signal and state:

```python
class ModelData(QObject):
    finished = Signal(bool)  # payload: cancelled

    def __init__(self, app: AppProtocol) -> None:
        ...
        self.passActive: bool = False
        self.timerExposure = QTimer(self)
        self.timerExposure.setSingleShot(True)
        self.timerExposure.timeout.connect(self.checkPauseAndExpose)
```

Flow:

```python
def runModel(self) -> None:                      # starts, returns at once
    if not self.modelInputData:
        self.finished.emit(False)
        return
    self.runTime = time.time()
    self.setupSignals()
    self.prepareModelBuildData()
    self.startPass()

def startPass(self) -> None:                     # replaces the retries loop body
    if self.retries > 0:
        self.statusRetry.emit(self.retries)
    if self.cancelBatch or self.endBatch:
        self.finishModel()
        return
    self.generateRunIterator()
    for key in self.modelRunList:
        self.modelBuildData[key]["processed"] = False
    self.passActive = True
    if not self.modelRunList:                    # nothing left to do
        QTimer.singleShot(0, self.finishPass)
        return
    self.startSlew.emit()

def collectPlateSolveResult(self, result: dict[str, Any]) -> None:
    ...                                          # unchanged body
    if self.checkModelFinished():
        QTimer.singleShot(0, self.finishPass)    # queued, see 2.3

def finishPass(self) -> None:
    if not self.passActive:
        return                                   # run only once per pass
    self.passActive = False
    retry = self.checkRetryNeeded() and self.retries < self.numberRetries
    if retry and not (self.cancelBatch or self.endBatch):
        self.retries += 1
        self.startPass()
        return
    self.finishModel()

def finishModel(self) -> None:                   # tail of the old runModel
    self.timerExposure.stop()
    self.resetSignals()
    if self.cancelBatch:
        self.log.info(f"{'Cancel model':15s}: by user")
        self.finished.emit(True)
        return
    self.buildProgModel()
    ...                                          # < 3 points check, log
    self.finished.emit(False)
```

User control becomes methods (not just flags), so cancel/end finish at once, as
the old loop did:

```python
def cancelRun(self) -> None:
    self.cancelBatch = True
    self.stopRun()

def endRun(self) -> None:
    self.endBatch = True
    self.stopRun()

def stopRun(self) -> None:
    if self.passActive:
        QTimer.singleShot(0, self.finishPass)
```

Exposure wait (replaces the second `mainThreadSleep`, fixes F1):

```python
def startNewImageExposure(self) -> None:
    if self.cancelBatch or self.endBatch:
        return
    self.timerExposure.start(int(self.waitTimeExposure * 1000))

def checkPauseAndExpose(self) -> None:
    if self.cancelBatch or self.endBatch:
        return
    if self.pauseBatch:
        self.timerExposure.start(500)            # poll the pause flag
        return
    self.exposeImage()

def exposeImage(self) -> None:                   # old body after the loop
    self.addMountDataToModelBuildData()
    ...
    self.statusExpose.emit([imagePath.stem, exposureTime, binning])
```

Removed: `runThroughModelBuildData`, `runThroughModelBuildDataRetries`, and the
import of `mainThreadSleep` in the logic layer. The retry semantics stay the
same: at most `numberRetries + 1` passes, stop early when no retry is needed,
and `statusRetry` is emitted for passes ≥ 1.

### 2.2 `Model` tab (GUI) – split `runBatch`

```python
def initConfig / __init__:
    self.modelData.finished.connect(self.finishBatch)

def runBatch(self) -> None:                      # start part only
    ...                                          # checks, clear, setup unchanged
    self.setupModelInputData()
    self.modelData.runModel()                    # returns immediately

def finishBatch(self, cancelled: bool) -> None:  # old tail of runBatch
    if cancelled:
        self.msg.emit(1, "Model", "Run", "Model build cancelled by user")
    else:
        self.programModelToMount()
    if self.ui.parkMountAfterModel.isChecked():
        ...
    self.app.playSound.emit("RunFinished")
    self.app.operationRunning.emit(self.STATUS_IDLE)

def cancelBatch(self) -> None:  self.modelData.cancelRun()
def endBatch(self) -> None:     self.modelData.endRun()
```

`pauseBatch` stays a flag toggle. It is read by `checkPauseAndExpose`.
`setModelTiming` writes `modelTiming` (F2). `setupBatchData` writes
`modelName` as well as `name` (F3).

### 2.3 Why the queued `QTimer.singleShot(0, …)`

`startNewSlew` emits a failed plate-solve result **synchronously** for
"Slew not possible" and then calls `startSlew.emit()` again. If
`collectPlateSolveResult` started the next retry pass directly, that later
`startSlew.emit()` would advance the **new** pass iterator a second time and
skip a point. Queuing the pass transition (plus the `passActive` guard) makes
sure the old call stack has returned before a new pass starts. This is the
only re-entrancy rule the state machine needs.

### 2.4 Behavior that stays the same

- `endBatch` keeps its current behavior: the batch stops at once, and the points
  processed so far form the model. Results for in-flight points arrive after
  `resetSignals` and are ignored.
- Signal wiring, timing modes, slew/dome logic and saved data format are the
  same.
- The GUI is locked by `operationRunning(STATUS_MODEL_BATCH)` until
  `finishBatch`, so a second run cannot be started (same as today).

---

## 3. Files

| File | Change |
|------|--------|
| `../../src/mw4/logic/modelBuild/modelRun.py` | As in 2.1. No `mainThreadSleep` import in logic |
| `../../src/mw4/gui/mainWaddon/tabModel.py` | As in 2.2 (split `runBatch`, `finishBatch`, cancel/end calls, F2, F3) |
| `../../tests/unit_tests/logic/modelBuild/test_modelRun.py` | Replace tests for the removed loop methods. New tests for `startPass`, `finishPass` (retry / no retry / guard), `finishModel` (cancel / < 3 points / ok), `cancelRun` / `endRun` / `stopRun`, `checkPauseAndExpose` (cancel / pause / expose), queued finish in `collectPlateSolveResult`. One flow test drives a 3-point run with emitted signals through `qtbot.waitSignal(modelData.finished)` |
| `../../tests/unit_tests/gui/mainWaddon/test_tabModel.py` | `runBatch` without the tail; new `finishBatch` tests (cancelled, program, park); cancel/end delegate; `setModelTiming` asserts `modelTiming` |

About 27 existing tests touch the changed methods. Most of them only need new
method names or a `qtbot.waitSignal`.

---

## 4. Steps

1. `ModelData`: add `finished`, `passActive`, `timerExposure`, `startPass`,
   `finishPass`, `finishModel`, `cancelRun`, `endRun`, `stopRun`,
   `checkPauseAndExpose` and `exposeImage`. Remove the two loops. Fix F1.
2. `Model` tab: split `runBatch`/`finishBatch`, delegate cancel/end, fix F2/F3.
3. Tests: logic first, then GUI, then the flow test.
4. Ruff, full suite serially and with `-n auto`, coverage 100 %.
5. Update review section 10 (rec 1 ✅, 5.1 fixed, 3.1 table: `modelRun.py`
   lines removed).

## 5. Out of scope / follow-up

- `tabModel.clearAlignAndBackup` (`mainThreadSleep(1000)`, rec 2 site F). It
  can use the same pattern afterwards: `runBatch` → `QTimer.singleShot(1000,
  continueBatch)`. `runFileModel` shares the helper, so it needs the same split.
  After that, `mainThreadSleep` has no callers and `base/threadUtils.py` can be
  removed.
- Shutdown while a model is running (`closeEvent`): call `modelData.cancelRun()`
  first. This is not a regression, and the same risk exists today.

## Decisions

| #  | Question | Proposal |
|----|----------|----------|
| D1 | Fix F1–F3 in this change? | Yes (small, in the touched code) |
| D2 | Include rec 2 site F (`clearAlignAndBackup`) and delete `mainThreadSleep` in the same change? | Separate follow-up |

**Decision (user):** D1 and D2 both fixed in this change.

---

## 6. Result – ✅ Done

**`logic/modelBuild/modelRun.py`**
- New: `finished = Signal(bool)`, `PAUSE_POLL_MS`, `passActive`,
  `timerExposure` (single-shot `QTimer`), `startPass`, `finishPass`,
  `finishModel`, `stopRun`, `cancelRun`, `endRun`, `resetBatchFlags`,
  `checkPauseAndExpose` and `exposeImage`.
- `runModel` starts and returns. `collectPlateSolveResult` queues
  `finishPass` when the pass is complete.
- Removed: `runThroughModelBuildData`, `runThroughModelBuildDataRetries`, and
  both `mainThreadSleep` calls.
- F1 fixed: the exposure wait is `waitTimeExposure * 1000` ms (it was half
  of that).
- Deviation: the flags are reset by `resetBatchFlags()`, called by the GUI at
  batch start, not in `runModel`. Otherwise a cancel during the new
  non-blocking 1 s clear wait would be lost. `pauseBatch` is reset too, so a
  pause left over from an earlier run no longer blocks the next run.

**`gui/mainWaddon/tabModel.py`**
- `runBatch` → `clearAlignAndBackup(self.startBatch)` → `startBatch` →
  `modelData.runModel()`. `finishBatch(cancelled)` is connected to
  `modelData.finished`. Cancel and end call `cancelRun()` / `endRun()`.
- D2: `clearAlignAndBackup(continuation)` uses
  `QTimer.singleShot(CLEAR_WAIT_MS, partial(backupAfterClear, continuation))`.
  `runFileModel` → `programFileModel(files)` as continuation. The GUI state is
  set to `STATUS_MODEL_FILE` before the wait and back to `STATUS_IDLE` on
  failure.
- F2 fixed: `setModelTiming` writes `modelTiming`.
- F3 fixed: one attribute `modelData.modelName`. The dynamic `.name` was
  removed.
- F4 (new): with several model files, `name` was set to a `Path`, so
  `name + ".model"` would have raised `TypeError`. It now uses `.stem`.

**`base/threadUtils.py`** was deleted together with its test. There are no callers left in
`src`. The four stress tests now use `QTest.qWait` (the Qt test equivalent).

**Tests:** `test_modelRun.py` (42 → 61 tests, including a 3-point flow test
with one retry pass through `qtbot.waitSignal(finished)`) and `test_tabModel.py`
(55 → 58, with new tests for `startBatch`, `finishBatch`, `backupAfterClear` and
`programFileModel`). The module fixture now depends on `qapp`, because timers
need a running application.

**Verification:** Ruff clean. 4579 passed, 38 skipped (serial and
`-n auto`). Coverage 100 % (18,484 statements). The stress tests still
collect.

