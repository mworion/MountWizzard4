# Plan: Fix test_imageW.py for exposeImageN Change

## Date: 2026-05-23

## Change in Source

`ImageWindow.exposeImageN` was refactored to toggle behaviour:

- **Before**: Always started continuous exposure (one code path).
- **After**: Acts as a toggle.
  - If `exposeN` is `False` → start: connect signal, set flag, call `exposeRaw`.
  - If `exposeN` is `True`  → stop:  disconnect signal, reset flag, emit
    "Continuous stopped" message and `STATUS_IDLE`.

## Coverage Gap

Lines 312–315 (the `else` / "stop" branch) are not covered by any test.

## Required Fix

Add `test_exposeImageN_2` that exercises the stop-path:
- Set `imagingDeviceStat["exposeN"] = True` (already running)
- Connect `exposeImageNDone` to the `saved` signal so the disconnect
  inside the method does not raise
- Call `exposeImageN()`
- Assert `imagingDeviceStat["exposeN"]` is `False` afterwards

## File to Change

`tests/unit_tests/gui/extWindows/image/test_imageW.py`

