# HID Controller Reconnection Implementation Plan

## Objective
Add connection state tracking and auto-reconnection capability to the HID controller, allowing it to detect device disconnection and automatically reconnect when the device becomes available again.

## Current Issues
1. **No connection state tracking**: The current `runnerHidController` doesn't track whether the device is actually connected
2. **No reconnection logic**: If the device disconnects during operation, the worker thread exits
3. **Early failure**: If device not found at startup, the thread immediately exits without retry capability
4. **No connection verification**: No way to check if the device is still responsive during the polling loop

## Proposed Solution

### 1. Add Three New Methods to `HidController` Class

#### `isConnected(hidpad: hid.device) -> bool`
- **Purpose**: Verify device is still available and responsive
- **Implementation**: Attempt a non-blocking read with zero timeout
- **Return**: `True` if device responsive, `False` on exception
- **Handles graceful connection state checking without disrupting normal polling**

#### `handleConnect() -> tuple[hid.device | None, int, int]`
- **Purpose**: Encapsulate device enumeration and connection logic
- **Implementation**:
  - Enumerate HID devices
  - Find device matching `self.config.deviceName`
  - Extract vendor and product IDs
  - Open device and set non-blocking mode
  - Return tuple of (device, vendorId, productId)
  - Return (None, 0, 0) on failure
- **Benefits**: Reusable logic for initial connection and reconnection attempts
- **Error handling**: Catches exceptions during open, logs warnings

#### `handleDisconnect(hidpad: hid.device) -> None`
- **Purpose**: Safely close device connection
- **Implementation**:
  - Attempt to close device
  - Catch and log any exceptions
- **Benefits**: Centralized cleanup logic, prevents resource leaks

### 2. Refactor `runnerHidController()` Method

**Current flow:**
```
1. Try to enumerate device once
2. If not found, exit with signal
3. Open device
4. Poll in loop until running=False
5. Close device
```

**New flow:**
```
1. Initialize: hidControllerDevice=None, deviceConnected=False
2. Loop while running:
   a. If not connected:
      - Call handleConnect()
      - If successful: emit deviceConnected signal, set deviceConnected=True
      - If failed: emit deviceDisconnected signal, sleep 0.5s, retry
   b. If connected:
      - Check if device still responsive (isConnected())
      - If not responsive: cleanup, set deviceConnected=False, retry
      - If responsive: read and process data as normal
3. On exit: cleanup device connection
```

**Key improvements:**
- Connection state explicitly tracked with `deviceConnected` flag
- Polling loop doesn't exit on device disconnection
- Automatic retry with backoff (0.5s) when device unavailable
- Connection state verified in each polling iteration
- Signals emitted on state transitions (disconnected→connected, connected→disconnected)

### 3. Update `startCommunication()` Method

**Current behavior:**
- Sets `running = True`
- Starts worker
- Immediately emits `deviceConnected` signal

**New behavior:**
- Sets `running = True`
- Starts worker
- **Remove immediate `deviceConnected` signal** (let worker emit it when actually connected)

**Rationale**: Signal should only be emitted when device truly connected, not before verification

### 4. Update `readHidController()` Method

**Consideration:**
- Current implementation catches exceptions and sets `running = False`
- This causes immediate exit from worker loop
- With new reconnection logic, we should let caller handle disconnection

**Decision:**
- Keep as-is for now (handles transport-level errors)
- The `isConnected()` check in main loop provides connection verification
- Exceptions here represent hard device errors, not just temporary disconnection

## Implementation Details

### Type Annotations
```python
def isConnected(self, hidpad: hid.device) -> bool: ...
def handleConnect(self) -> tuple[hid.device | None, int, int]: ...
def handleDisconnect(self, hidpad: hid.device) -> None: ...
```

### Error Handling
- `handleConnect()`: Returns (None, 0, 0) on any enumeration/open failure
- `handleDisconnect()`: Catches and logs exceptions, continues
- `isConnected()`: Catches exceptions, returns False

### Logging
- Initial connection attempt: debug level with device info
- Connection failure: warning level with device name
- Reconnection attempts: debug level
- Disconnection detected: warning level

### Signal Emission
- `deviceConnected`: Emitted when successfully connected (first time or after reconnection)
- `deviceDisconnected`: Emitted when disconnection detected during polling

## Files to Modify
- `/Users/Q115346/PycharmProjects/MountWizzard4/src/mw4/logic/hidController/hidController.py`

## Testing Strategy

### Unit Tests Location
- `/Users/Q115346/PycharmProjects/MountWizzard4/tests/unit_tests/logic/hidController/test_hidController.py`

### Test Cases Required
1. **test_isConnected_returns_true_when_device_responsive**
   - Mock device read with valid data
   - Verify returns True

2. **test_isConnected_returns_false_on_exception**
   - Mock device read to raise exception
   - Verify returns False

3. **test_handleConnect_success**
   - Mock hid.enumerate to return device
   - Verify returns (device, vendorId, productId)
   - Verify device opened and set_nonblocking called

4. **test_handleConnect_device_not_found**
   - Mock hid.enumerate to not contain device
   - Verify returns (None, 0, 0)

5. **test_handleConnect_exception_on_open**
   - Mock hid.enumerate to return device
   - Mock open to raise exception
   - Verify returns (None, 0, 0) and logs warning

6. **test_handleDisconnect_closes_device**
   - Mock device close
   - Verify close called without exception

7. **test_handleDisconnect_catches_exception**
   - Mock device close to raise exception
   - Verify exception caught and logged

8. **test_runnerHidController_initial_connection_success**
   - Mock handleConnect to return valid device
   - Verify deviceConnected signal emitted
   - Verify polling loop enters

9. **test_runnerHidController_initial_connection_failure_retry**
   - Mock handleConnect to fail initially, then succeed
   - Verify retries with sleep
   - Verify eventual connection

10. **test_runnerHidController_reconnection_on_disconnect**
    - Mock isConnected to return False after initial connection
    - Verify handleDisconnect called
    - Verify reconnection attempt
    - Verify deviceDisconnected signal emitted

11. **test_runnerHidController_polling_loop**
    - Mock successful connection and data reading
    - Verify polling continues
    - Verify data processing

12. **test_startCommunication_no_early_signal**
    - Verify deviceConnected signal NOT emitted in startCommunication
    - Verify signal emitted by worker when connected

## Expected Behavior After Implementation

1. **User starts communication**:
   - If device connected: Worker connects immediately, emits signal, begins polling
   - If device not connected: Worker retries every 0.5s, waits for device

2. **User plugs in device during operation**:
   - Worker detects availability on next retry
   - Connects and emits deviceConnected signal
   - GUI updates to show device connected

3. **User unplugs device during operation**:
   - Worker detects disconnection during isConnected() check
   - Emits deviceDisconnected signal
   - Waits for reconnection

4. **User stops communication**:
   - Worker exits loop gracefully
   - Device properly closed

## Coverage Requirements
- All three new methods must have 100% coverage
- runnerHidController refactored logic must have 100% coverage
- All error paths must be tested
- Windows-specific tests (if any) only tracked on Windows

## Completion Checklist
- [ ] Three new methods implemented with type annotations
- [ ] runnerHidController refactored with new flow
- [ ] startCommunication updated
- [ ] All unit tests written and passing
- [ ] 100% code coverage achieved
- [ ] Ruff linting passes
- [ ] Integration tested with real device (manual)

