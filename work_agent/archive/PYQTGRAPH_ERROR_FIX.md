# PyQtGraph Cleanup Error Fix

## Problem

During the Ubuntu CI runner tests in `run_tests_ubuntu_3`, a large number of exceptions were appearing in the atexit callback:

```
Exception ignored in atexit callback <built-in function __moduleShutdown>:
Traceback (most recent call last):
  ...
RuntimeError: Error calling Python override of QGraphicsWidget::sizeHint(): ...
```

While these errors didn't cause test failures (all 66 tests passed), they generated excessive noise in the CI logs and made it difficult to identify real issues.

## Root Cause

PyQtGraph 0.14.0 has known issues when used with PySide6 during interpreter shutdown. During the atexit phase, PyQtGraph attempts cleanup operations that can trigger recursion errors in several methods:
- `sizeHint()`
- `resizeEvent()`  
- `boundingRect()`
- `itemChange()`

These errors also can result in accessing already-deleted C++ objects.

## Solution

Added a stderr wrapper in the pytest configuration (`tests/unit_tests/conftest.py`) that filters out PyQtGraph atexit errors before they're printed to the console.

### Implementation Details

1. **FilteredStderr class**: A wrapper around the standard error stream that:
   - Intercepts all messages written to stderr
   - Checks if a message contains "Exception ignored in atexit"
   - If it also contains PyQtGraph-related keywords, filters it out
   - Otherwise, passes the message through to the original stderr

2. **pytest_configure hook**: Called early in the pytest startup process to install the stderr wrapper before any tests run

### Keywords Filtered

The wrapper filters atexit errors containing any of these keywords:
- `pyqtgraph`
- `sizeHint`
- `resizeEvent`
- `boundingRect`
- `itemChange`
- `already deleted`

## Benefits

- ✅ Clean CI logs without PyQtGraph noise
- ✅ All tests still pass (66 passed in ~3.8s)
- ✅ No functional changes to test behavior
- ✅ Minimal code addition

## Testing

Verified on:
- macOS local environment: 66 tests pass without errors
- Should work on Ubuntu CI runner when deployed

## Future Considerations

- Monitor for PyQtGraph version updates that may fix this issue
- If upgrading PyQtGraph in the future, verify if this workaround is still needed
- Consider this a temporary workaround; a proper fix in PyQtGraph itself would be ideal

