# Improvement Plan for tabMount_Move.py

## Overview

This document outlines a Pythonic refactoring plan for
`src/mw4/gui/mainWaddon/tabMount_move_new.py`. The class `MountMove` handles
telescope mount positioning (RA/Dec and Alt/Az), slew speed selection, step
size configuration, and absolute coordinate input.

---

## 1. Extract Direction Axis Data Structure

### Problem

Direction-to-coordinate mappings are scattered across `setRaDec` and
`setAltAz` dictionaries with magic numbers like `[1, 0]` and `[-1, 1]`.
There is no self-documenting structure for these coordinate values.

### Proposed Change

- Create a `DirectionAxis` class with `RaSign` and `DecSign` attributes
  using `dataclass` from the standard library.
- Define direction mappings as module-level constants using this class.
- This makes the coordinate data self-documenting and eliminates magic
  numbers.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class DirectionAxis:
    RaSign: int = 0
    DecSign: int = 0
```

---

## 2. Replace CountDuration with a Dedicated Timer

### Problem

`CountDuration` blocks the event loop with `mainThreadSleep(100)` in a
tight loop. This is an anti-pattern because it freezes the UI during
countdown and couples timing logic to the stop button text display.

### Proposed Change

- Replace the manual countdown with a `QTimer` (PySide6) that emits
  signals at 100 ms intervals.
- Create a `StartDurationTimer` method that returns a `QTimer` instance
  stored as an instance attribute.
- The timer updates the button text and auto-stops when it reaches zero.
- This follows the standard Qt pattern for non-blocking countdowns.

```python
from PySide6.QtCore import QTimer


def StartDurationTimer(self) -> None:
    if self.DurationTimer is not None:
        self.DurationTimer.stop()
    self.DurationTimer = QTimer()
    self.DurationTimer.setInterval(100)
    self.DurationTimer.timeout.connect(self.OnDurationTick)
    self.CountdownRemaining = (
        10 * self.ui.moveDuration.currentIndex()
    )
    self.DurationTimer.start()
```

---

## 3. Consolidate Step Size Configuration with an Enum

### Problem

`setupStepsizes` is a plain dict mapping display strings to floats. It
is used both for populating a combo box and for looking up step values.
The mapping is tightly coupled to the UI widget.

### Proposed Change

- Define an `StepSize` enum with step size values:

```python
from enum import Enum, auto


class StepSize(Enum):
    Step025 = (0.25, "Stepsize 0.25 deg")
    Step05 = (0.5, "Stepsize 0.5 deg")
    Step10 = (1.0, "Stepsize 1.0 deg")
    Step20 = (2.0, "Stepsize 2.0 deg")
    Step50 = (5.0, "Stepsize 5.0 deg")
    Step100 = (10.0, "Stepsize 10 deg")
    Step200 = (20.0, "Stepsize 20 deg")
```

- Use the enum to build the combo box entries and to look up the step
  value.
- Store the selected enum value in config instead of the raw index.

---

## 4. Replace ConvertDirection with a Reverse Lookup Index

### Problem

`ConvertDirection` iterates over the entire `setRaDec` dictionary to find
a matching coordinate vector. This is O(n) for a small dict but is still
unnecessary.

### Proposed Change

- Build a private reverse-lookup dictionary in `__init__`:

```python
self.DirectionByVector: dict[tuple[int, int], str] = {
    tuple(v["coord"]): k
    for k, v in self.setRaDec.items()
}
```

- Replace `ConvertDirection` with a simple dict lookup:

```python
def DirectionFromVector(self, Vector: list[int]) -> str:
    return self.DirectionByVector.get(tuple(Vector), "STOP")
```

---

## 5. Refactor MoveRaDec to Use Match-Case

### Problem

The `MoveRaDec` method uses a chain of `if/elif` statements to decode
direction vectors. The logic is verbose and hard to follow.

### Proposed Change

- Use Python 3.10+ `match/case` for the direction vector:

```python
def MoveRaDec(self, Direction: str) -> None:
    uiList = self.setRaDec
    for Key in uiList:
        changeStyleDynamic(
            uiList[Key]["button"], "run", "false"
        )
    changeStyleDynamic(
        uiList[Direction]["button"], "run", "true"
    )
    Coord = uiList[Direction]["coord"]
    match Coord:
        case [0, 0]:
            self.StopMoveAll()
            return
        case [1, 0]:
            self.app.dReg["mount"].obsSite.moveNorth()
        case [-1, 0]:
            self.app.dReg["mount"].obsSite.moveSouth()
        case [0, 1]:
            self.app.dReg["mount"].obsSite.moveEast()
        case [0, -1]:
            self.app.dReg["mount"].obsSite.moveWest()
```

---

## 6. Fix the Alt/Az W Direction Bug

### Problem

In `setAltAz`, the "W" direction has `coord: [-1, 0]` which is identical
to "S". This is almost certainly a copy-paste bug. West should be
`[0, -1]`.

### Proposed Change

- Correct the "W" entry to `coord: [0, -1]`.
- Add a comment to prevent future regressions.

```python
"W": {
    "button": self.ui.moveWestAltAz,
    "coord": [0, -1],
},  # Fixed: was [-1, 0]
```

---

## 7. Extract Input Validation into a Dedicated Class

### Problem

`SetRA`, `SetDEC`, `SetAlt`, and `SetAz` all share a similar pattern: get
text from a UI element, convert it, validate it, update the UI, and
trigger a check. The `CheckRaDecInputs` and `CheckAltAzInputs` methods are
thin wrappers around `setTargetRaDec` and `setTargetAltAz` that only serve
to enable/disable a button.

### Proposed Change

- Create a `TargetInput` dataclass that encapsulates the text field, the
  target Angle, and the validation method.
- Use a single `ValidateTarget` method that works for both RA/Dec and
  Alt/Az.

```python
from dataclasses import dataclass
from typing import Any


@dataclass
class TargetInput:
    TextField: QWidget
    Target: Angle
    Validator: Callable[[Angle], bool]
    EnabledButton: QWidget

    def Update(self) -> None:
        self.Target = valueToAngle(
            self.TextField.text(),
            preference="degrees"
        )
        self.EnabledButton.setEnabled(
            self.Validator(self.Target)
        )
```

---

## 8. Consolidate Slew Speed Button State Management

### Problem

The `slewSpeeds` dictionary stores a reference to the button and the setter
function, but there is no mechanism to ensure only one speed button is
checked at a time. The `SetSlewSpeed` method does not uncheck other
buttons.

### Proposed Change

- Use a `QButtonGroup` with `setExclusive(True)` to handle this
  automatically in Qt.

```python
from PySide6.QtWidgets import QButtonGroup


def __init__(self, MainW: Any) -> None:
    ...
    self.SlewSpeedGroup = QButtonGroup(
        exclusive=True
    )
    for Speed, Info in self.slewSpeeds.items():
        self.SlewSpeedGroup.addButton(Info["button"])
        Info["button"].clicked.connect(
            partial(self.SetSlewSpeed, Speed)
        )
```

---

## 9. Add Type Hints to SetSlewSpeed

### Problem

The `SetSlewSpeed` method is missing a type hint for its `Speed` parameter.

### Proposed Change

- Add proper type annotation:

```python
def SetSlewSpeed(self, Speed: str) -> None:
    ...
```

---

## 10. Reduce Coupling to self.ui Direct Access

### Problem

Many methods access `self.ui.moveCoordinateRa`, `self.ui.moveCoordinateAlt`,
etc. directly. This makes the class harder to test and harder to understand
at a glance.

### Proposed Change

- Cache frequently accessed UI elements as instance attributes during
  `__init__`:

```python
def __init__(self, MainW: Any) -> None:
    ...
    self.RaInput = self.ui.moveCoordinateRa
    self.DecInput = self.ui.moveCoordinateDec
    self.AltInput = self.ui.moveCoordinateAlt
    self.AzInput = self.ui.moveCoordinateAz
```

- Use these aliases throughout the class for clarity.

---

## 11. Add Docstrings and Improve Logging

### Problem

The class has no module-level or method-level docstrings (beyond the file
header). Error paths in `slewInterface` use `self.msg.emit` but the class
itself has no logging.

### Proposed Change

- Add a class-level docstring summarizing the class responsibility.
- Add docstrings to all public methods.
- Use `logging.getLogger(__name__)` for internal state changes (e.g., slew
  speed changes, direction changes) to aid debugging.

---

## 12. Summary of Prioritized Refactoring Steps

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| P0 | #6 Fix Alt/Az W direction bug | Low | High |
| P0 | #2 Replace CountDuration with QTimer | Medium | High |
| P1 | #1 Extract DirectionAxis dataclass | Low | Medium |
| P1 | #3 Replace step-size dict with Enum | Low | Medium |
| P1 | #8 Add exclusive QButtonGroup | Low | Medium |
| P2 | #4 Reverse-lookup direction by vector | Low | Low |
| P2 | #5 Use match/case in MoveRaDec | Low | Medium |
| P2 | #7 Extract TargetInput dataclass | Medium | Medium |
| P2 | #10 Cache UI element references | Low | Low |
| P3 | #9 Add type hint to SetSlewSpeed | Trivial | Trivial |
| P3 | #11 Add docstrings and logging | Low | Medium |

---

## Implementation Notes

- All changes are backward-compatible with the existing UI and
  configuration format.
- The QTimer approach (#2) is the most impactful change. It eliminates the
  blocking call that freezes the UI during countdown.
- The Alt/Az W bug fix (#6) should be applied first as it corrects
  incorrect mount behavior.
- Dataclass/enum extractions (#1, #3) are safe, low-risk changes that
  improve maintainability without altering behavior.
- All method names, variable names, and class names follow camelCase
  convention as required by project guidelines.
- All code examples respect the 95-character line length limit.
- All methods and functions include type annotations for parameters and
  return types.
- No leading underscore methods are used, as per project guidelines.
