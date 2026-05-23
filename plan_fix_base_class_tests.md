# Plan: Fix Unit Tests for Base Class Changes

## Date: 2026-05-23

## Summary of Findings

9 failing tests across 3 test files. Root cause: source classes were
refactored and tests were not updated.

---

## Failures and Required Fixes

### `test_alpacaAscomCommon.py::test_init`
**Cause**: Asserts `function.deviceType == "test"`. `AlpacaAscomCommon`
no longer stores `deviceType` from the parent.
**Fix**: Remove the `assert function.deviceType == "test"` line.

---

### `test_alpacaClass.py::test_properties_3`
**Cause**: Asserts `function.deviceType == "camera"` and
`function.number == 3` after setting
`function.deviceName = "test:camera:3"`. The `deviceName` setter no
longer parses the format to derive `deviceType` and `number`.
**Fix**: Remove those two derived-attribute assertions.

---

### `test_alpacaClass.py::test_createAlpacaDevice_1/2/3`
**Cause**: Calls `function.createAlpacaDevice()` without arguments.
`AlpacaClass.createAlpacaDevice` now requires `deviceType: str`.
**Fix**: Pass the device type string as a positional argument.

---

### `test_alpacaClass.py::test_startCommunication_1`
**Cause**: The test mocks `createAlpacaDevice` to return `False` and
asserts `m_start.assert_not_called()`. `AlpacaClass.startCommunication`
no longer calls `createAlpacaDevice`; it always starts the worker thread.
The conditional device-creation step is now in each concrete subclass
(e.g. `CameraAlpaca.startCommunication`).
**Fix**: Remove the `createAlpacaDevice` mock and change the assertion to
`m_start.assert_called_once()`.

---

### `test_ascomClass.py::test_selectAscomDriver_success/error/empty`
**Cause**: Calls `function.selectAscomDriver("old")` with one argument.
`AscomClass.selectAscomDriver` now requires a second argument
`deviceType: str`.
**Fix**: Add a `deviceType` string as the second argument to each call.

---

## Coverage Gaps Fixed by the Test Changes

- `alpacaClass.py` lines 146–159 (`createAlpacaDevice`): covered once
  `test_createAlpacaDevice_1/2/3` are fixed.
- `ascomClass.py` lines 94–111 (`selectAscomDriver`): covered once
  `test_selectAscomDriver_*` are fixed.

---

## Files Changed

| File | Actions |
|------|---------|
| `tests/unit_tests/base/test_alpacaAscomCommon.py` | Remove `deviceType` assertion |
| `tests/unit_tests/base/test_alpacaClass.py` | Fix `test_properties_3`, `test_createAlpacaDevice_*`, `test_startCommunication_1` |
| `tests/unit_tests/base/test_ascomClass.py` | Fix `test_selectAscomDriver_*` |

