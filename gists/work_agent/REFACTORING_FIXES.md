# Refactoring Issues - Corrected ✅

## Summary
Fixed 2 test failures that were caused by overly aggressive sed replacements during the legacy API refactoring.

## Issues Fixed

### Issue 1: test_tabSett_Device.py::test_copyConfig_4
**File**: `tests/unit_tests/gui/mainWaddon/test_tabSett_Device.py` (Line 283)

**Problem**:
```python
# WRONG - sed was too aggressive
assert function.driversData["cover"].indi["test"] == 1

# CORRECT - restored original
assert function.driversData["cover"]["frameworks"]["indi"]["test"] == 1
```

**Root Cause**: The sed replacement regex `s/]\["\([^"]*\)"\]\["\([^"]*\)"\]/].\2/g` was designed to replace the legacy API pattern (`drivers["name"]["class"]` → `.instance`) but incorrectly matched and transformed legitimate multi-level dictionary access patterns.

**Impact**: This was a legitimate nested dictionary access that should NOT have been modified.

---

### Issue 2: test_cameraIndi.py::test_writeImageXisfHeader
**File**: `tests/unit_tests/logic/camera/test_cameraIndi.py` (Lines 307, 310, 313)

**Problem**:
```python
# WRONG - sed was too aggressive
assert mock_ims_meta[0].OBJECT == [...]  # Line 307
assert mock_ims_meta[0].AUTHOR == [...]  # Line 310
assert mock_ims_meta[0].FRAME == [...]   # Line 313

# CORRECT - restored original
assert mock_ims_meta[0]["FITSKeywords"]["OBJECT"] == [...]
assert mock_ims_meta[0]["FITSKeywords"]["AUTHOR"] == [...]
assert mock_ims_meta[0]["FITSKeywords"]["FRAME"] == [...]
```

**Root Cause**: The sed replacement incorrectly converted dictionary key access `["FITSKeywords"]["OBJECT"]` to attribute access `.OBJECT`, which doesn't work on dictionary objects (only on objects with attributes).

**Impact**: These were legitimate nested dictionary accesses that should NOT have been modified.

---

## Changes Applied

1. **test_tabSett_Device.py (Line 283)**:
   - Restored: `function.driversData["cover"]["frameworks"]["indi"]["test"] == 1`

2. **test_cameraIndi.py (Lines 307-314)**:
   - Restored: `mock_ims_meta[0]["FITSKeywords"]["OBJECT"]`
   - Restored: `mock_ims_meta[0]["FITSKeywords"]["AUTHOR"]`
   - Restored: `mock_ims_meta[0]["FITSKeywords"]["FRAME"]`

---

## Test Results ✅

After fixes:
- ✅ test_tabSett_Device.py: **38/38 tests passing**
- ✅ test_cameraIndi.py: **32/32 tests passing**
- ✅ test_copyConfig_4: **PASSED**
- ✅ test_writeImageXisfHeader: **PASSED**

---

## Lesson Learned

The sed-based bulk replacement was effective for the intended legacy API refactoring but had unintended side effects on legitimate dictionary access patterns. A more targeted approach or manual verification would have caught these issues before running the sed command.

**Recommendation for future refactoring**: Use AST-based tools or more precise regex patterns to avoid collateral damage.

