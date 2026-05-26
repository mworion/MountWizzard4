# Plan: Update Unit Tests for Code Changes

## Affected Source Files

| File | Change Summary |
|------|----------------|
| `src/mw4/base/loggerMW.py` | New `setTrace` function; `setCustomLoggingLevel` no longer sets `app.mount.loggingTrace` in TRACE branch – calls `setTrace` instead |
| `src/mw4/base/alpacaAscomCommon.py` | `getDeviceProp`, `setDeviceProp`, `callDeviceMethod` now have concrete implementations with `loggingTrace` support |
| `src/mw4/gui/mainWaddon/tabSett_Update.py` | Import of `setTrace` added (no behavioural change for tests) |

---

## Changes to `tests/unit_tests/base/test_loggerMW.py`

### Fix existing test
- `test_setCustomLoggingLevel_trace`: Remove wrong assertion
  `assert app.mount.loggingTrace is False` (new code no longer sets this
  attribute in the TRACE branch). Verify instead that `setTrace` is called
  with `enable=True`.

### New tests for `setTrace`
- `test_setTrace_noDrivers`: empty driver dict → no iteration, no error
- `test_setTrace_ascomFramework_enable`: "ascom" key → `loggingTrace=True`
- `test_setTrace_alpacaFramework_enable`: "alpaca" key → `loggingTrace=True`
- `test_setTrace_indiFramework`: "indi" key → just `pass`, no attribute set
- `test_setTrace_disable`: "ascom" key with `enable=False` → `loggingTrace=False`

---

## Changes to `tests/unit_tests/base/test_alpacaAscomCommon.py`

### New tests for base-class methods (loggingTrace paths)
- `test_getDeviceProp_inPropertyExceptions`: prop already in exceptions →
  immediate `None` return (early-exit branch)
- `test_getDeviceProp_withLoggingTrace`: device set, `loggingTrace=True` →
  value returned and trace logged
- `test_setDeviceProp_inPropertyExceptions`: prop already in exceptions →
  early return, no setattr
- `test_setDeviceProp_withLoggingTrace`: device set, `loggingTrace=True` →
  value written and trace logged
- `test_callDeviceMethod_inPropertyExceptions`: prop already in exceptions →
  `None` returned
- `test_callDeviceMethod_withLoggingTrace`: device set, `loggingTrace=True` →
  method called, return value forwarded, trace logged

---

## Execution Steps

1. Create this plan file ✓
2. Update `test_loggerMW.py`
3. Update `test_alpacaAscomCommon.py`
4. Run pytest with coverage on the three affected test files
5. Run Ruff (lint + format) and fix any findings
6. Run overall package tests

