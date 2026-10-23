# Qt6 QInputDialog Parameter Alignment

## Current Implementation vs Qt6 Specification

### getText() Method
**Current Parameters:**
- parent: QWidget | None
- title: str
- label: str
- defaultValue: str

**Qt6 Specification - Missing Parameters:**
- echoMode: QLineEdit.EchoMode (default: Normal)
- flags: Qt.WindowFlags (default: WindowFlags())
- inputMethodHints: Qt.InputMethodHints (default: ImhNone)

### getInt() Method
**Current Parameters:**
- parent: QWidget | None
- title: str
- label: str
- defaultValue: int

**Qt6 Specification - Missing Parameters:**
- minValue: int (default: -2147483647)
- maxValue: int (default: 2147483647)
- step: int (default: 1)

### getDouble() Method
**Current Parameters:**
- parent: QWidget | None
- title: str
- label: str
- defaultValue: float

**Qt6 Specification - Missing Parameters:**
- minValue: float (default: -2147483647.0)
- maxValue: float (default: 2147483647.0)
- decimals: int (default: 1)

## Implementation Changes

### 1. Update __init__ method
- Add minValue, maxValue parameters to support range validation
- Add step parameter for int mode
- Add decimals parameter for double mode
- Add echoMode parameter for text mode
- Store these as instance variables

### 2. Update validateInput() method
- Add range validation for int and double modes
- Consider step constraints for int mode (optional, validation only)

### 3. Update class methods
- getText(): Add echoMode, flags, inputMethodHints parameters
- getInt(): Add minValue, maxValue, step parameters
- getDouble(): Add minValue, maxValue, decimals parameters
- Apply these parameters during dialog instantiation

### 4. Update UI components
- Optionally apply echoMode to QLineEdit for text mode
- Format decimal places for double mode input field

### 5. Update tests
- Add tests for min/max validation
- Add tests for step parameter
- Add tests for decimals parameter
- Add tests for echoMode parameter
- Add tests for class methods with all new parameters

## Backward Compatibility
All new parameters have default values matching Qt6 defaults, ensuring existing code continues to work without modification.

