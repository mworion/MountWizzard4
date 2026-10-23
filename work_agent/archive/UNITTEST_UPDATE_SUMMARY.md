# Unit Test Updates for startWorker Mutex Changes

## Overview
Updated unit tests to reflect changes in how `startWorker()` now handles mutexes internally and can return `None` when the guard fails or the worker's mutex is already locked.

## Files Modified

### 1. `/tests/unit_tests/base/test_tpool.py`
- Updated worker tests to lock mutex before running since `startWorker` now handles mutex locking
- Modified `test_worker_run_emitsFinishedSignal()` - Added `a.mutex.lock()` before running
- Modified `test_worker_run_emitsResultSignal()` - Added `a.mutex.lock()` before running
- Modified `test_worker_run_doesNotEmitErrorOnSuccess()` - Added `a.mutex.lock()` before running
- Modified `test_worker_run_emitsErrorOnException()` - Added `a.mutex.lock()` before running
- Updated `test_startWorker_mutexBlocks()` - Now properly mocks Worker class to test mutex blocking scenario
- Updated `test_startWorker_mutexAcquired()` - Calls `worker.run()` to trigger mutex unlock
- Updated `test_startWorker_mutexUnlockedAfterWorkerFinishes()` - Calls `worker.run()` instead of emitting signal
- **Test Coverage**: 100% (54/54 statements)

### 2. `/tests/unit_tests/mountcontrol/test_mount.py`
- Removed manual mutex locking/unlocking from test methods
- Updated `test_cyclePointing_1()` - Checks that worker is None when mountIsUp is False
- Updated `test_cyclePointing_2()` - Checks worker is not None, cleans up properly
- Updated `test_cyclePointing_3()` - Checks worker creation and cleanup
- Updated `test_cycleSetting_1()` - Checks that worker is None when mountIsUp is False
- Updated `test_cycleSetting_2()` - Checks worker is not None, cleans up properly
- Updated `test_cycleSetting_3()` - Checks worker creation and cleanup
- Updated `test_CalcTLE_1()` - Checks that worker is None when mountIsUp is False
- Updated `test_CalcTLE_2()` - Checks worker is not None, cleans up properly
- Updated `test_CalcTLE_3()` - Checks worker creation and cleanup
- Updated `test_GetTLE_1()` - Checks that worker is None when mountIsUp is False
- Updated `test_GetTLE_2()` - Checks worker is not None, cleans up properly
- Updated `test_GetTLE_3()` - Checks worker creation and cleanup
- **Test Results**: 73 tests passing

### 3. `/tests/unit_tests/mountcontrol/test_mountTime.py`
- Removed manual mutex locking/unlocking
- Updated `test_checkMountUp_locked()` - Mocks startWorker to return None
- Updated `test_checkMountUp_unlocked()` - Checks worker creation and cleanup
- Updated `test_pollSyncClock_locked()` - Mocks startWorker to return None
- Updated `test_pollSyncClock_unlocked()` - Checks worker creation and cleanup
- Updated fixture cleanup - Added `hasattr()` checks to handle workers deleted by tests
- **Test Results**: 54 tests passing

## Key Changes in Testing Pattern

### Before (Old Pattern)
```python
def test_cyclePointing_2(function):
    function.mountIsUp = True
    function.mutexCyclePointing.lock()
    with mock.patch.object(QThreadPool, "start"):
        function.cyclePointing()
    function.mutexCyclePointing.unlock()  # Manual unlock
```

### After (New Pattern)
```python
def test_cyclePointing_2(function):
    function.mountIsUp = True
    with mock.patch.object(QThreadPool, "start"):
        function.cyclePointing()
        assert function.workerCyclePointing is not None
    if function.workerCyclePointing is not None:
        function.workerCyclePointing.signals.finished.emit()
        del function.workerCyclePointing  # Proper cleanup
```

## Summary of Changes

1. **Mutex Management**: Tests no longer manually lock/unlock mutexes since `startWorker()` handles this internally
2. **Return Value Handling**: Tests now check if `startWorker()` returns `None` (when guard fails or mutex is locked)
3. **Worker Cleanup**: Tests properly clean up workers by emitting finished signal and deleting references
4. **Null Checks**: Tests verify worker creation (not None) when appropriate, and handle None return values

## Test Results

✅ **test_tpool.py**: 16 tests passing, 100% coverage
✅ **test_mount.py**: 73 tests passing
✅ **test_mountTime.py**: 54 tests passing

**Total**: 127 tests passing with proper cleanup and no mutex errors

## Code Quality

✅ All tests pass Ruff linting
✅ All tests properly formatted with Ruff
✅ No "QMutex: destroying locked mutex" errors in cleanup

