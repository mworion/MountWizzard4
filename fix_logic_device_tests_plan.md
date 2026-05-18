# Fix Logic Device Class Tests – Plan

## Date: 2026-05-18

## Summary

Following the `ascomClass`/`alpacaClass` API changes, multiple source files and
tests in `src/mw4/logic/` need correction.

---

## Root Causes

| Change | Impact |
|--------|--------|
| `callAscomMethodQueued` now accepts only `**kwargs` | Source files passing positional args are broken |
| `self.device` replaces `self.client` | All test fixtures use old `func.client` |
| `deviceType` added to `AlpacaClass.__init__` | Alpaca test `Parent` classes are missing this |

---

## Source Files to Fix

| File | Line(s) | Old call | New call |
|------|---------|---------|---------|
| `domeAscom.py` | 56 | `callAscomMethodQueued("SlewToAzimuth", azimuth)` | `callAscomMethodQueued("SlewToAzimuth", Azimuth=azimuth)` |
| `domeAscom.py` | 57 | `callAscomMethodQueued("SlewToAltitude", altitude)` | `callAscomMethodQueued("SlewToAltitude", Altitude=altitude)` |
| `focuserAscom.py` | 29 | `callAscomMethodQueued("move", position)` | `callAscomMethodQueued("Move", Position=position)` |
| `lightPanelAscom.py` | 40 | `callAscomMethodQueued("CalibratorOn", brightness)` | `callAscomMethodQueued("CalibratorOn", Brightness=brightness)` |
| `lightPanelAscom.py` | 46 | `callAscomMethodQueued("CalibratorOn", value)` | `callAscomMethodQueued("CalibratorOn", Brightness=int(value))` |
| `pegasusUPBAscom.py` | 72,86 | `callAscomMethodQueued("setswitch", n, v)` | `callAscomMethodQueued("SetSwitch", Id=n, State=v)` |
| `pegasusUPBAscom.py` | 94,97 | `callAscomMethodQueued("setswitch", 7/13, v)` | `callAscomMethodQueued("SetSwitch", Id=7/13, State=v)` |
| `pegasusUPBAscom.py` | 106 | `callAscomMethodQueued("setswitchvalue", n, v)` | `callAscomMethodQueued("SetSwitchValue", Id=n, Value=v)` |

---

## Test Files to Fix

| Test File | Issues |
|-----------|--------|
| `test_pegasusUPBAlpaca.py` | `Parent` missing `deviceType` |
| `test_coverAscom.py` | `func.client` → `func.device`; `("CloseCover", ())` → `("CloseCover")` |
| `test_domeAscom.py` | `func.client` → `func.device`; slew assertions with keyword args |
| `test_sensorWeatherAscom.py` | `func.client` → `func.device` |
| `test_filterAscom.py` | `func.client` → `func.device` |
| `test_focuserAscom.py` | `func.client` → `func.device`; `("move", 3)` → `("Move", Position=3)` |
| `test_lightPanelAscom.py` | `func.client` → `func.device`; fix brightness kwargs |
| `test_pegasusUPBAscom.py` | `func.client` → `func.device`; `("setswitch",…)` → new format |
| `test_cameraAscom.py` | `func.client` → `func.device`; rename `waitFunc` → `saveImage`; fix expose tests |
| `test_telescopeAscom.py` | `func.client` → `func.device` |

---

## Implementation Steps

1. Fix source files (4 files)
2. Fix all test files (10 files)
3. Run all affected tests
4. Check coverage
5. Ruff format/lint

