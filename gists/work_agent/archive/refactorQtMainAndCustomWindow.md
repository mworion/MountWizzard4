# Refactoring Plan: qtMain & qtCustomWindow

## Goal
Make the combination of `MWidget` (`qtMain.py`) and `CustomTitleBar`
(`qtCustomWindow.py`) more Pythonic and simpler while preserving behaviour and
keeping 100% test coverage.

## Scope
- `../../src/mw4/gui/utilities/qtCustomWindow.py` (class `CustomTitleBar`)
- `../../src/mw4/gui/utilities/qtMain.py` (class `MWidget`)
- `../../tests/unit_tests/gui/utilities/test_qtCustomWindow.py`
- `../../tests/unit_tests/gui/utilities/test_qtMain.py`

The two classes stay in separate files (loose coupling, distinct
responsibilities). No merge is performed.

## Changes

### 1. `qtCustomWindow.py` – `CustomTitleBar`
1. **Remove dead drag code**: delete the `initialPos` attribute together with
   `mouseMoveEvent` and `mouseReleaseEvent`. `mousePressEvent` already uses
   `startSystemMove`, so `initialPos` is never set and the branch is dead.
2. **Replace the `buttons` dict** with a small `dataclass` (`TitleButton`) and a
   list, removing the double `buttons[button]["widget"]` indirection.
3. **Add missing return-type annotations**: `windowStateChanged`,
   `mousePressEvent`.

### 2. `qtMain.py` – `MWidget`
1. **Flatten `eventFilter`**: compute the local position once and reuse `edges`
   for both the resize-cursor and the resize-start branches. Add `-> bool`
   return type.
2. **Dict-based `setResizeCursorShape`**: introduce a `CURSOR_MAP` class
   constant mapping edge combinations to cursor shapes; removes repeated
   branches. Add `-> None` return type.

## Constraints (from project instructions)
- camelCase for methods/variables.
- Type annotations incl. return types on every method.
- No leading-underscore local methods.
- No `# pragma: no cover`.
- Line length per `../../pyproject.toml` (Ruff).
- 100% coverage; update both test modules for removed/changed code.

## Verification Steps
1. Update unit tests for both modules (remove tests for deleted
   `mouseMoveEvent`/`mouseReleaseEvent`, adapt button-build tests, cover
   `CURSOR_MAP` branches and flattened `eventFilter`).
2. Run `pytest` for the two affected test modules with coverage → 100%.
3. Run full test suite.
4. Run Ruff (format + lint) and resolve all findings.

## Out of Scope
- Merging the two classes/files.
- Any behavioural/feature changes beyond the refactor above.

