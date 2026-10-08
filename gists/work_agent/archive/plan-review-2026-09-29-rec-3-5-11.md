# Plan – Review 2026-09-29, Recommendations 3, 5, 11

Source: `2026-09-29-review.md`

## Rec 3 – Remove dead Alpaca-server code
- `gui/extWindows/devicePopupW.py`: delete `setAlpacaServer()` and the
  `elif framework == "alpacaServer":` branch in `discoverDevices`.

## Rec 5 – Platform-conditional coverage
- Add dev dependency `coverage-conditional-plugin`.
- `../../pyproject.toml`:
  - `plugins = ["coverage_conditional_plugin"]`
  - rule: exclude `if platform.system() == "Windows":` blocks when not on
    Windows (regex rule, no pragmas in source).
  - omit `base/ascomClass.py` and `logic/camera/cameraAscom.py` when not on
    Windows.

## Rec 11 – Small cleanups
- `base/alpacaAscomCommon.py`: remove `ImageArray` no-op branch.
- `gui/mainWaddon/tabSat_Search.py`: catch only expected exceptions in
  `runnerCalcSatList`, log at `warning`, no unbound `sat`.
- `logic/plateSolve/plateSolve.py`: drop unused `stdout` in timeout branch.
- `../../tests/unit_tests/base/test_indiClass.py`: test for `discoverMutex`
  contention (`tryLock()` fails).

## Finish
- Update tests, run full suite with coverage (100 % on macOS), Ruff.
- Update the review document with the status.
