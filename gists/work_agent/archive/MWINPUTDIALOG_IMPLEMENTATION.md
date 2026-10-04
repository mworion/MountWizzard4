# MWInputDialog - Themed Input Dialog Pattern

## Overview

Created `MWInputDialog`, a lightweight, themed input dialog following the same pattern as `MWFileDialog`. It wraps Qt's input functionality with a consistent look and feel matching MW4's design.

## Files Created

1. **`src/mw4/gui/utilities/qtInputDialog.py`** - 266 lines
2. **`tests/unit_tests/gui/utilities/test_qtInputDialog.py`** - 323 lines

## Key Features

### Input Modes
- **Text** - Accept any text input
- **Integer** - Accept and validate integer input
- **Double** - Accept and validate floating-point input

### Architecture

#### Instance Methods
- `validateInput(text)` - Validate input based on input mode
- `onAccept()` - Handle OK button click
- `onReject()` - Handle Cancel button click
- `exec()` - Execute dialog modally
- `getValue()` - Get the input value
- `wasAccepted()` - Check if dialog was accepted

#### Class Methods (Convenience API)
- `getText(parent, title, label, defaultValue)` - Get text input
- `getInt(parent, title, label, defaultValue)` - Get integer input
- `getDouble(parent, title, label, defaultValue)` - Get float input

## Usage Examples

### Direct Instantiation (Advanced)
```python
dlg = MWInputDialog(
    parent=self,
    title="Enter Your Name",
    label="Name:",
    defaultValue="John",
    inputMode="text",
)
dlg.exec()
if dlg.wasAccepted():
    name = dlg.getValue()
```

### Convenience Methods (Simple)
```python
# Get text input
text, ok = MWInputDialog.getText(self, "Input", "Enter text:")

# Get integer input
value, ok = MWInputDialog.getInt(self, "Input", "Enter number:", 0)

# Get float input
value, ok = MWInputDialog.getDouble(self, "Input", "Enter decimal:", 0.0)
```

## Design Patterns

### Same as MWFileDialog & MWMessageDialog
- ✓ Frameless themed dialog (extends MWidget)
- ✓ Local QEventLoop for synchronous execution
- ✓ Input validation
- ✓ Modal dialog behavior
- ✓ Both direct instantiation and convenience class methods
- ✓ Proper centering over parent widget
- ✓ Default button (OK) focus
- ✓ Input field auto-focus on exec()

### Architecture Consistency
| Feature | MWFileDialog | MWMessageDialog | MWInputDialog |
|---------|:----------:|:-------------:|:-------------:|
| Extends MWidget | ✓ | ✓ | ✓ |
| Local QEventLoop | ✓ | ✓ | ✓ |
| Convenience Methods | ✓ | ✓ | ✓ |
| Direct Instantiation | ✓ | ✓ | ✓ |
| Input Validation | - | - | ✓ |
| Modal Behavior | ✓ | ✓ | ✓ |
| Parent Centering | ✓ | ✓ | ✓ |

## Validation

### Text Mode
- Accepts any non-empty string

### Integer Mode
- Validates integer format
- Accepts negative numbers
- Rejects floats and non-numeric input

### Double Mode
- Validates floating-point format
- Accepts integers or decimals
- Accepts negative numbers
- Rejects non-numeric input

## Test Coverage

### Total Tests: 34
- Initialization tests (6)
- Validation tests (3)
- Acceptance/Rejection tests (6)
- Event loop tests (2)
- GUI element tests (3)
- Class method tests (6)
- Direct instantiation tests (3)
- Miscellaneous tests (5)

All tests passing ✓

## Code Quality

- ✓ All 34 tests pass in 0.31s
- ✓ Ruff linting: All checks passed
- ✓ No code style issues
- ✓ Type annotations throughout
- ✓ Comprehensive docstrings
- ✓ Follows MountWizzard4 coding conventions

## Integration with MW4 Utilities

Now MW4 has a consistent pattern for all three main dialog types:

```python
# File Operations
file = MWFileDialog.getOpenFileName(parent, "title", Path("."), "*.txt")

# Message Dialogs
ok = MWMessageDialog.question(parent, "title", "question?")

# Input Dialogs
text, ok = MWInputDialog.getText(parent, "title", "Enter value:")
```

## Future Extensions

Could be extended with:
- Item selection (like QInputDialog.getItem())
- Multi-line text input
- Custom validators
- Input masks for phone numbers, dates, etc.
- Color picker
- Font selector

## Compliance with MW4 Standards

✓ Source code in `src/mw4/gui/utilities/`
✓ Unit tests in `tests/unit_tests/gui/utilities/`
✓ 100% test coverage
✓ No `_` prefixed methods
✓ Full type annotations
✓ Ruff compliant
✓ camelCase naming
✓ Comprehensive docstrings
✓ Follows MWFileDialog pattern exactly
✓ Python 3.11+ compatible


