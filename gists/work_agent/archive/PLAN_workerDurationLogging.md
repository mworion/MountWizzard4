# Plan: log duration of pollSetting / pollPointing when they hang

**Status:** implemented in `src/mw4/base/tpool.py` (checked 2026-10-08). The
plan stays active only for the optional follow-up at the end: the logging is
in place, so the next step is to evaluate it in the field.

## Goal
Find out why `Worker pollSetting busy, skipped` repeats for ~40 s. Log how long
a worker has been running when it is skipped, and how long it took once it
finishes. Nothing else changes.

## Analysis
- `startWorker` (`../../../src/mw4/base/tpool.py`) skips a call when `tryAcquire()` fails.
  The skip log has no information about the running call.
- `Worker.run` does not measure the runtime.
- `cycleSetting` / `cyclePointing` (`../../../src/mw4/mountcontrol/mount.py`) use
  `startWorker`, so a generic change in `tpool.py` covers both and every other
  worker.

## Changes (only `../../../src/mw4/base/tpool.py`)
1. Constants
   - `SLOW_WORKER_THRESHOLD = 5.0` (seconds). A finished run longer than this
     is logged at warning level.
2. `Worker.__init__`
   - Add `self.startTime: float | None = None` (`time.monotonic()`).
3. `Worker.tryAcquire`
   - On success set `self.startTime = time.monotonic()` (start of the busy
     period, including the pool queue wait).
4. `Worker.release`
   - Compute `duration = time.monotonic() - self.startTime` before releasing,
     reset `startTime` to `None`, and return the duration (`float | None`).
5. `Worker.run` (finally block)
   - Use the duration returned by `release()`. If it is greater than
     `SLOW_WORKER_THRESHOLD`, log
     `Worker {fnName} finished after {duration:.1f}s (slow)` at warning level.
     Otherwise log nothing, to avoid log noise.
6. `startWorker` skip branch
   - Extend the message to
     `Worker {fnName} busy, skipped (running for {elapsed:.1f}s)`, with
     `elapsed = worker.elapsed()`. Deviation: a new helper `Worker.elapsed()`
     returns `0.0` when `startTime` is `None`; `release` uses it too.
   - Keep it at debug level.

## Tests (done, `../../../tests/unit_tests/base/test_tpool.py`, module scope, 100 % coverage)
- `tryAcquire` sets `startTime`; `release` returns a duration and resets it.
- `release` without a prior acquire returns `None`.
- `run` with a patched `time.monotonic` (and a lowered threshold) logs the
  slow warning (`caplog`); a fast run logs nothing.
- `startWorker` on a busy worker logs `busy, skipped (running for ...)`.
- Existing tests keep passing.

## Finish (done)
- `uv run ruff format` and `uv run ruff check`, resolve all findings.
- `uv run pytest tests/unit_tests/base/test_tpool.py --cov=mw4.base.tpool`
  (100 %), then the whole package.

## Optional follow-up (open, not part of this task)
Log which mount command was running inside `pollSetting` when it hangs
(`mountcontrol/connection.py`). Only do this if the new logging shows the
hang is inside the mount communication.

