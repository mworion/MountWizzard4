# Test Updates Summary

## Overview
Updated tests for `uploadPopupW`, `downloadPopupW`, `astroObjects`, and `tabTools_IERSTime` to reflect the integration of the new `showWindow()` method.

## Changes Made

### 1. **test_uploadPopupW.py**
- **Added**: `test_showWindow()` - Tests the new `showWindow()` method
  - Verifies `show()` is called
  - Verifies window is fixed in size
  - Verifies minimum/maximum size constraints (400x120)

### 2. **test_downloadPopupW.py**
- **Added**: `test_showWindow()` - Tests the new `showWindow()` method
  - Verifies `show()` is called
  - Verifies window is fixed in size
  - Verifies minimum/maximum size constraints (400x120)

### 3. **test_astroObjects.py**
- **Updated**: `test_runDownloadPopup_when_online()` - Changed assertion from `show.assert_called_once()` to `showWindow.assert_called_once()`
- **Added**: `test_runUploadPopup_calls_showWindow()` - Tests that `runUploadPopup()` calls `showWindow()` on the upload popup
  - Verifies `showWindow()` is called
  - Verifies `uploadFile()` is called after `showWindow()`

### 4. **test_tabTools_IERSTime.py**
- **Added**: `test_progEarthRotationData_calls_showWindow()` - Tests that `progEarthRotationData()` calls `showWindow()` on the upload popup
- **Added**: `test_finishLoadFinalsFromSourceURLs_calls_showWindow()` - Tests that `finishLoadFinalsFromSourceURLs()` calls `showWindow()` on the download popup
- **Added**: `test_loadTimeDataFromSourceURLs_calls_showWindow()` - Tests that `loadTimeDataFromSourceURLs()` calls `showWindow()` on the download popup

## Test Results

All 100 tests pass successfully:
- `test_uploadPopupW.py`: 34 tests (includes new `test_showWindow`)
- `test_downloadPopupW.py`: 19 tests (includes new `test_showWindow`)
- `test_astroObjects.py`: 29 tests (includes updated and new tests)
- `test_tabTools_IERSTime.py`: 18 tests (includes 3 new tests)

## Linting
All files pass Ruff linting checks with no violations.

## Implementation Details

### Source Code Changes (Already in place)
- `uploadPopupW.showWindow()` (lines 88-92) - Displays window and sets constraints
- `downloadPopupW.showWindow()` (lines 59-63) - Displays window and sets constraints
- `astroObjects.runDownloadPopup()` (line 101) - Calls `showWindow()` on popup
- `astroObjects.runUploadPopup()` (line 145) - Calls `showWindow()` on popup
- `tabTools_IERSTime.progEarthRotationData()` (line 81) - Calls `showWindow()` on popup
- `tabTools_IERSTime.finishLoadFinalsFromSourceURLs()` (line 112) - Calls `showWindow()` on popup
- `tabTools_IERSTime.loadTimeDataFromSourceURLs()` (line 129) - Calls `showWindow()` on popup

## Coverage
- All affected code paths are tested
- Test coverage remains at 100% for all modified modules

