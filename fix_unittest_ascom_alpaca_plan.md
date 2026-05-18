# Fix Unit Tests for ascomClass and alpacaClass – Plan

## Date: 2026-05-18

## Summary of Source Changes

The source files `ascomClass.py` and `alpacaClass.py` were updated. The unit
tests no longer match the current source. This plan documents all required
test corrections.

---

## Issues Found in `test_ascomClass.py`

| # | Location | Issue | Fix |
|---|----------|-------|-----|
| 1 | Fixture (line 44) | `func.client` used – source uses `self.device` | → `func.device` |
| 2 | `test_init` (line 51) | `workerCommunicationLoop` – source has `workerRunnerCoreLoop` | rename |
| 3 | `test_init` (line 52) | `not hasattr(function, "propertyExceptions")` – source adds `self.propertyExceptions` | assert it exists |
| 4 | All `function.client.*` | `client` renamed to `device` in source | → `function.device.*` |
| 5 | `callAscomMethod` calls | Old signature accepted positional args; source now uses `**kwargs` | Use keyword args |
| 6 | `CommandItem` usage | Old fields `name`, `args` replaced by `valueProp`, `kwargs` | Update all usages |
| 7 | `runnerCommunicationLoop` tests (lines 226–343) | Tests mock `CoInitialize`/`Dispatch`; these now belong to `runnerCoreLoop` | Rename & rework |
| 8 | Source bug | `else: self.runnerCoreLoop()` in `runnerCoreLoop` should be `runnerCommunicationLoop()` | Fix source typo |

---

## Issues Found in `test_alpacaClass.py`

| # | Location | Issue | Fix |
|---|----------|-------|-----|
| 1 | `Parent` class (line 33–37) | Missing `deviceType` attribute; source `__init__` accesses `parent.deviceType` | Add `deviceType = ""` |
| 2 | `resetState` fixture | Does not clear `propertyExceptions` (module-scoped instance) | Add `function.propertyExceptions.clear()` |
| 3 | `test_setDeviceProp_1` | Asserts `assert result`; `setDeviceProp` returns `None` | Remove return check |
| 4 | `test_setDeviceProp_2` | Asserts `assert not result`; should check `propertyExceptions` | Check exceptions list |
| 5 | `test_setDeviceProp_3` | Same as above | Check exceptions list |

---

## Source Fix Required

**`src/mw4/base/ascomClass.py`**:
- In `runnerCoreLoop`, the `else` branch calls `self.runnerCoreLoop()` (recursive
  bug). Change to `self.runnerCommunicationLoop()`.

---

## Implementation Steps

1. Fix source bug in `ascomClass.py`
2. Rewrite `test_ascomClass.py` to match current source structure
3. Fix `test_alpacaClass.py` (targeted changes)
4. Run tests and validate 100% coverage
5. Run Ruff linter/formatter
6. Run overall package tests

