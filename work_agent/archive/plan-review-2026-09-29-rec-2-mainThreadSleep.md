# Plan – Review 2026-09-29, Recommendation 2

**Status:** implemented (GUI sites A–E; site F deferred to recommendation 1)

Replace the remaining **GUI** `mainThreadSleep` calls with event-driven
`QTimer.singleShot` continuations (or remove them), so the GUI no longer runs a
nested `QEventLoop` to "sleep".

Source: `2026-09-29-review.md`, section 3.1 and section 8 (#2).

Scope note: the two `mainThreadSleep(500)` calls in
`logic/modelBuild/modelRun.py` (211, 307) belong to **recommendation 1**
(make `ModelRun` event-driven) and are **out of scope** here. This plan only
covers the GUI call sites.

---

## 1. Current State

`base/threadUtils.py`:

```python
def mainThreadSleep(value: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(value, loop.quit)
    loop.exec()
```

Every call spins a nested event loop on the GUI thread. Any re-entrant signal
(close window, switch profile, start another action) runs on top of that stack.

GUI call sites in scope:

| # | File                                     | Line(s) | Context / caller                                   | Purpose of the wait                                  |
|---|------------------------------------------|---------|----------------------------------------------------|------------------------------------------------------|
| A | `gui/extWindows/analyseW.py`             | 464     | `drawAll` (GUI thread, `clicked` + direct calls)   | `mainThreadSleep(0)` = one event pass between charts  |
| B | `gui/extWindows/video/videoBase.py`      | 142     | `restartVideo` (GUI thread, `currentIndexChanged`) | Let the capture worker stop before `startVideo`       |
| C | `gui/mainWindow/externalWindows.py`      | 180     | `closeExtendedWindows` (called on profile load and in `closeEvent`) | 50 ms stagger between window closes  |
| D | `gui/extWindows/downloadPopupW.py`       | 156     | `closePopup` (worker `result` callback, GUI thread) | 500 ms so the final status is visible before `close`  |
| E | `gui/extWindows/uploadPopupW.py`         | 202     | `closePopup` (worker `result` callback)            | Poll-wait: `while pollStatusRunState: sleep(100)`     |
| E | `gui/extWindows/uploadPopupW.py`         | 209     | `closePopup`                                       | 500 ms cosmetic delay before `close`                  |
| F | `gui/mainWaddon/tabModel.py`             | 196     | `clearAlignAndBackup` (called inside synchronous `runBatch` / `runFileModel`) | 1 s so the mount processes `clearModel` |

Difficulty tiers:

- **Trivial:** A
- **Easy:** B, D
- **Medium:** C, E
- **Coupled to rec 1:** F

---

## 2. Target Design (per site)

### A. `analyseW.drawAll` – remove the event pass (Trivial)

`mainThreadSleep(0)` only yields once so the charts appear progressively.
pyqtgraph repaints on the next natural event-loop pass anyway.

```python
def drawAll(self) -> None:
    for chart in self.charts:
        chart()
    self.linkViewsAltAz()
    self.linkViewsRa()
    self.linkViewsDec()
```

Just delete the `mainThreadSleep(0)` call. If progressive painting is desired,
wrap the loop in `setUpdatesEnabled(False)`/`True` instead (no functional need).
Remove the now-unused `mainThreadSleep` import.

### B. `videoBase.restartVideo` – timer continuation (Easy)

```python
def restartVideo(self) -> None:
    self.stopVideo()
    QTimer.singleShot(1000, self.startVideo)
```

`restartVideo` no longer blocks; the 1 s gap that lets the capture worker stop
is preserved. Remove the `mainThreadSleep` import (add `QTimer` import).

### C. `externalWindows.closeExtendedWindows` – drop the stagger (Medium)

The 50 ms between `close()` calls exists to let each window's `closeEvent`
be processed. Two callers:

- `mainWindow.py:170` (profile change / rebuild) – GUI thread, safe.
- `mainWindow.py:319` (`closeEvent`, application shutdown) – **must stay
  synchronous**; deferring closes with a timer during shutdown is unsafe because
  the app is quitting.

Target: close all windows in the loop **without** sleeping. `QWidget.close()`
is synchronous; it posts a deferred delete but does not need a 50 ms gap. If a
gap is genuinely required for repaint, replace the whole per-window sleep with a
single `QApplication.processEvents()` **after** the loop (not per window), or
nothing:

```python
def closeExtendedWindows(self) -> None:
    for window in self.uiWindows:
        classObj = self.uiWindows[window]["classObj"]
        if not classObj:
            continue
        self.log.debug(f"Closing window: {window}")
        classObj.close()
```

Verify visually and in tests that windows still close on profile switch and on
app exit. This is the one site where a timer-based continuation is the wrong
tool (shutdown path), so the fix is removal, not deferral.

### D. `downloadPopupW.closePopup` – timer close (Easy)

`closePopup` is the worker `result` callback; `finishedMethod=self.loop.quit`
fires separately, so `exec()` returns independently of the 500 ms delay. Set the
return value immediately and defer only the visual `close`:

```python
def closePopup(self, result: bool) -> None:
    self.signalProgress.emit(100)
    if result:
        self.signalProgressBarColor.emit("green")
        self.signalStatus.emit("Download successful")
    else:
        self.signalProgressBarColor.emit("red")
        self.signalStatus.emit("Download failed")
    self.returnValues["success"] = result
    QTimer.singleShot(500, self.close)
```

Note: `returnValues["success"]` is now set before the delay (previously after
the sleep). Since `exec()` only returns after `loop.quit` (the worker `finished`
signal, which fires after `result`), the value is still set before `exec()`
returns. Confirm ordering with a test.

### E. `uploadPopupW.closePopup` – signal-driven finalization (Medium)

Two waits:

1. `while self.pollStatusRunState: mainThreadSleep(100)` – waits for
   `runnerPollStatus` (a worker loop) to set `pollStatusRunState = False`.
2. `mainThreadSleep(500)` – cosmetic delay before `close`.

Target: replace the poll-wait with the poll worker's `finished` signal instead
of busy-waiting.

- `startWorker(self.workerPollStatus, …)` already produces a `finished` signal.
  Connect it to a new `finishPollStatus` slot, or split `closePopup` into
  `closePopup` (from `workerUploadFile.result`) and a finalizer that runs once
  the poll worker is done.
- Flow on success:
  - `closePopup(result=True)` stores `returnValues["success"]` and, if the poll
    worker is still running, waits for its `finished` signal; if it already
    finished, finalize immediately.
  - The finalizer sets the bar colour / message from
    `returnValues["successMount"]`, then `QTimer.singleShot(500, self.close)`.
- On `result=False`, set `pollStatusRunState = False`, red bar, and
  `QTimer.singleShot(500, self.close)` as today.

This removes both nested loops. Keep `exec()`'s own `self.loop` (that is the
public blocking API of the popup and is acceptable; only the *inner* sleeps are
removed). Guard against double-close (result path + finished path both firing).

### F. `tabModel.clearAlignAndBackup` – handle with recommendation 1 (Coupled)

`clearAlignAndBackup` returns `bool` and is called **synchronously** inside
`runBatch` (line 279) and `runFileModel` (line 311). Those flows also call
`self.modelData.runModel()`, which itself busy-waits via `mainThreadSleep`
(recommendation 1). Converting only this 1 s wait to a timer while the caller
stays synchronous does not fit the control flow (the caller expects the mount to
be cleared before it continues).

Decision: **defer site F to recommendation 1**, where `runBatch` /
`runFileModel` become a state machine. At that point the 1 s "waiting for clear"
becomes a `QTimer.singleShot(1000, <next state>)` transition. Doing it here in
isolation would require restructuring `runBatch` twice.

If rec 1 is not scheduled soon and this site must be closed now, the fallback is
to move the clear+backup sequence into a dedicated worker
(`runnerClearAlignAndBackup`) with a `result` continuation — but that is
effectively part of the rec 1 rewrite and is **not** recommended as a standalone
change.

---

## 3. Steps

1. `analyseW.py`: remove `mainThreadSleep(0)` in `drawAll`; drop the import (A).
2. `videoBase.py`: timer continuation in `restartVideo`; swap import to
   `QTimer` (B).
3. `externalWindows.py`: remove the per-window 50 ms sleep; drop the import;
   verify the `closeEvent` shutdown path (C).
4. `downloadPopupW.py`: set `returnValues` first, `QTimer.singleShot(500,
   self.close)`; adjust imports (D).
5. `uploadPopupW.py`: add a poll-worker `finished` continuation, split/guard
   `closePopup`, replace both inner sleeps; adjust imports (E).
6. Leave `tabModel.py` site F for recommendation 1 (document in the review).
7. Once no GUI call site remains, `mainThreadSleep` is used only by
   `modelRun.py`. Do **not** delete `base/threadUtils.py` yet (rec 1 still uses
   it); its removal happens with rec 1.
8. Tests (`tests/unit_tests/gui/...` mirroring the source):
   - `test_analyseW.py`: `drawAll` calls every chart and the three `linkViews*`
     once; no sleep.
   - `test_videoBase.py`: `restartVideo` calls `stopVideo` and schedules
     `startVideo` (patch `QTimer.singleShot` to call immediately / assert the
     ms + callback).
   - `test_externalWindows.py`: `closeExtendedWindows` closes every built
     window and skips `None` entries; works when called twice (profile + close).
   - `test_downloadPopupW.py`: `closePopup` sets `returnValues["success"]` and
     schedules `close`; both success and failure branches; `exec` still returns
     the right value.
   - `test_uploadPopupW.py`: success path finalizes only after the poll worker
     `finished`; failure path closes; no busy-wait remains; double-close guard;
     `successMount` True/False message/colour.
   - Patch `QTimer.singleShot` in tests so the deferred callback runs
     synchronously (or assert the `(ms, callback)` arguments) to keep tests
     deterministic and cover the callback body.
9. Update `2026-09-29-review.md` section 10: mark rec 2 as partially done
   (A–E), note site F folded into rec 1, and update section 3.1's table.
10. Ruff format/check, then `pytest tests/unit_tests --cov` → 100 %.

---

## 4. Risks

| Risk                                                              | Mitigation                                                                 |
|------------------------------------------------------------------|----------------------------------------------------------------------------|
| `exec()` in download/upload popups returns before `returnValues` is set | `returnValues` is set synchronously in `closePopup`, before `loop.quit`; covered by a test |
| Upload double-close (result path + poll `finished` both finalize) | A `closed`/`finalized` guard flag; test both orderings                     |
| `closeExtendedWindows` during shutdown must not defer            | Keep it fully synchronous; only remove the sleep, no `QTimer`              |
| Removing the 50 ms stagger leaves a window visually half-closed  | Verify on profile switch and app exit; add a single post-loop `processEvents` only if needed |
| `restartVideo` timer fires after the window/worker is gone       | `startVideo` already checks `self.running`/source; safe if window closed    |
| Deferred `QTimer` callbacks are hard to cover 100 %             | Patch `QTimer.singleShot` in tests to invoke the callback immediately       |
| Site F touched in isolation destabilizes the model flow          | Defer F to rec 1; do not restructure `runBatch` twice                      |

---

## 5. Out of Scope

- `logic/modelBuild/modelRun.py` (`mainThreadSleep` 211, 307) → recommendation 1.
- `tabModel.clearAlignAndBackup` (site F) → recommendation 1.
- Deleting `base/threadUtils.mainThreadSleep` → with recommendation 1, once the
  last caller is gone.
- `gPlotBase.py:154` and `splashScreen.py:31` `processEvents()` (already noted
  as acceptable in the review).
