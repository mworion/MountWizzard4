# Plan: Fix Unit Tests for Main Application Classes

## Files to Fix

### 1. test_mainApp.py (111 lines)
- ✓ Fixture naming is OK ("app")
- Need to verify assertions and config keys
- Tests appear well-structured

### 2. test_tabAlmanac.py (184 lines)
- ✗ Fixture named "function" → rename to "almanac"
- ✗ Test names have numeric suffixes (test_plotTwilightData_1)
- Need config key verification

### 3. test_tabSat_Track.py (853 lines - LARGE)
- ✗ Fixture named "function" → rename to "satTrack"
- ✗ Extensive numeric test suffixes
- ✗ Likely poor assertions

### 4. test_mainWindow.py (470 lines)
- ✓ Fixture named "window" (OK)
- ✗ Test names have numeric suffixes (test_initConfig_1)
- Need to rename and improve

### 5. test_mainWindowAddons.py (62 lines)
- Need to check structure

## Implementation Strategy

1. Fix test_mainApp.py (small, check for any issues)
2. Fix test_tabAlmanac.py (rename fixture, rename tests)
3. Fix test_tabSat_Track.py (large - systematic approach)
4. Fix test_mainWindow.py (rename tests with descriptive suffixes)
5. Fix test_mainWindowAddons.py (check and fix if needed)

All following the same pattern as setting classes.

