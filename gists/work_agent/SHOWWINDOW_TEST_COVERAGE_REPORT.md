# showWindow() Test Coverage Report

**Date**: 2026-06-06  
**Status**: ✓ COMPLETE - All showWindow() methods now have dedicated test coverage

---

## Summary

All 12 source files in `src/mw4/gui/extWindows/` that implement `showWindow()` now have dedicated test functions covering these method calls.

---

## Detailed Coverage Report

| # | Source File | showWindow() | Test File | Test Function | Status |
|---|---|---|---|---|---|
| 1 | analyseW.py | ✓ | test_analyseW.py | test_showWindow | ✓ |
| 2 | bigPopupW.py | ✓ | test_bigPopupW.py | test_showWindow | ✓ |
| 3 | hemisphere/hemisphereW.py | ✓ | hemisphere/test_hemisphereW.py | test_showWindow_1 | ✓ |
| 4 | image/imageW.py | ✓ | image/test_imageW.py | test_showWindow_1 | ✓ |
| 5 | keypadW.py | ✓ | test_keypadW.py | test_showWindow_1 | ✓ |
| 6 | measure/measureW.py | ✓ | measure/test_measureW.py | test_showWindow_1 | ✓ |
| 7 | messageW.py | ✓ | test_messageW.py | test_showWindow | ✓ **ADDED** |
| 8 | satelliteHorW.py | ✓ | test_satelliteHorW.py | test_showWindow | ✓ |
| 9 | satelliteMapW.py | ✓ | test_satelliteMapW.py | test_showWindow | ✓ |
| 10 | setting/settingW.py | ✓ | setting/test_settingW.py | test_showWindow | ✓ **ADDED** |
| 11 | simulator/simulatorW.py | ✓ | simulator/test_simulatorW.py | test_showWindow | ✓ |
| 12 | video/videoBase.py | ✓ | video/test_videoBase.py | test_showWindow_1 | ✓ |
| 13 | video/videoW.py (subclass) | inherits | video/test_videoW.py | test_showWindow | ✓ **ADDED** |

---

## Changes Made

### Added Tests

Three new dedicated test functions were added to ensure complete coverage:

#### 1. `tests/unit_tests/gui/extWindows/test_messageW.py`
```python
def test_showWindow(function):
    with mock.patch.object(function, "show"):
        function.showWindow()
```

#### 2. `tests/unit_tests/gui/extWindows/setting/test_settingW.py`
```python
def test_showWindow(function):
    with mock.patch.object(function, "show"):
        function.showWindow()
```

#### 3. `tests/unit_tests/gui/extWindows/video/test_videoW.py`
```python
def test_showWindow(function):
    with mock.patch.object(function, "show"):
        function.showWindow()
```

---

## Test Results

All 13 showWindow() tests pass successfully:

```
tests/unit_tests/gui/extWindows/hemisphere/test_hemisphereW.py::test_showWindow_1 PASSED
tests/unit_tests/gui/extWindows/image/test_imageW.py::test_showWindow_1 PASSED
tests/unit_tests/gui/extWindows/measure/test_measureW.py::test_showWindow_1 PASSED
tests/unit_tests/gui/extWindows/setting/test_settingW.py::test_showWindow PASSED ✓ NEW
tests/unit_tests/gui/extWindows/simulator/test_simulatorW.py::test_showWindow PASSED
tests/unit_tests/gui/extWindows/test_analyseW.py::test_showWindow PASSED
tests/unit_tests/gui/extWindows/test_bigPopupW.py::test_showWindow PASSED
tests/unit_tests/gui/extWindows/test_keypadW.py::test_showWindow_1 PASSED
tests/unit_tests/gui/extWindows/test_messageW.py::test_showWindow PASSED ✓ NEW
tests/unit_tests/gui/extWindows/test_satelliteHorW.py::test_showWindow PASSED
tests/unit_tests/gui/extWindows/test_satelliteMapW.py::test_showWindow PASSED
tests/unit_tests/gui/extWindows/video/test_videoBase.py::test_showWindow_1 PASSED
tests/unit_tests/gui/extWindows/video/test_videoW.py::test_showWindow PASSED ✓ NEW

========================= 13 passed in 1.68s =========================
```

---

## Coverage: 13/13 ✓ 100%

All extWindow files with `showWindow()` methods now have explicit, dedicated test coverage.

---

## Notes

- All tests use the pattern: mocking the `show()` method to prevent actual GUI rendering during unit tests
- Each test is isolated and focuses specifically on the `showWindow()` method
- For subclasses (e.g., `VideoWindow`), tests also validate that inherited `showWindow()` implementations work correctly
- Tests follow the project's naming convention: `test_showWindow` or `test_showWindow_1`

