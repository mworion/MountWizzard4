# Plan: Adjust Unit Tests to Match Class Changes

## Date: 2026-05-23

## Summary of Findings

Running coverage analysis on the four changed source files reveals the
following issues in the unit tests:

### `test_camera.py` — 6 failing tests (methods removed from Camera class)

The following methods no longer exist in `camera.py`:
- `waitExposed`
- `waitStart`
- `waitDownload`
- `waitSave`
- `waitFinish`

**Actions required:**
- Remove tests: `test_waitExposed_1`, `test_waitExposed_2`,
  `test_waitStart_1`, `test_waitDownload`, `test_waitSave_1`,
  `test_waitFinish`
- Remove the `mocked_sleepAndEvents` fixture (no longer needed)
- Add a test to cover line 152 (`return False` in `Camera.abort()` when
  the framework's `abort()` returns `False`)

### `test_cameraAlpacaAscomBase.py` — 1 failing test + 1 missing line

- `test_abort_cannotAbort`: asserts `suc is True` but
  `CameraAlpacaAscomBase.abort()` now returns `False` when
  `CAN_ABORT = False`. Fix: change `assert suc` → `assert not suc`.
- Line 68 of `cameraAlpacaAscomBase.py` (`return` inside
  `setExposureState`) is not covered. This path is reached when
  `state != 0`, `state != 2`, and `self.exposing is False`.
  Add: `test_setExposureState_stateNot0Not2NotExposing`

### `imageW.py` and `tabImage_Manage.py`

Both files already have 100 % coverage — no changes needed.

## Files to Change

| File | Change |
|------|--------|
| `tests/unit_tests/logic/camera/test_camera.py` | Remove obsolete tests,<br>remove unused fixture, add `test_abort_1` |
| `tests/unit_tests/logic/camera/test_cameraAlpacaAscomBase.py` | Fix assertion in `test_abort_cannotAbort`,<br>add `test_setExposureState_stateNot0Not2NotExposing` |

## Verification

After changes run:
```
uv run pytest tests/unit_tests/logic/camera/test_camera.py \
              tests/unit_tests/logic/camera/test_cameraAlpacaAscomBase.py \
              tests/unit_tests/gui/extWindows/image/test_imageW.py \
              tests/unit_tests/gui/mainWaddon/test_tabImage_Manage.py \
              --cov=mw4.logic.camera.camera \
              --cov=mw4.logic.camera.cameraAlpacaAscomBase \
              --cov=mw4.gui.extWindows.image.imageW \
              --cov=mw4.gui.mainWaddon.tabImage_Manage \
              --cov-report=term-missing
```

Expected: 0 failures, 100 % coverage on all four modules.

