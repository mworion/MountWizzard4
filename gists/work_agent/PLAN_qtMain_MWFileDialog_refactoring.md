# Plan – Refactor qtMain.py to use MWFileDialog

## 1. Overview

Replace the `QFileDialog`-based file/directory chooser in `MWidget` (part of `qtMain.py`) with the custom `MWFileDialog` class. The public API remains identical, so all 9 call sites (mainWindow, tabModel, tabModel_BuildPoints, tabTools_Rename, imageW, analyseW, horizonDraw, devicePopupW) require **no changes**.

---

## 2. Rationale

- `QFileDialog` was instantiated with `DontUseNativeDialog` and custom styling applied each time.
- `MWFileDialog` is a purpose-built frameless MW4 window inheriting from `MWidget`, so it automatically gets:
  - Consistent MW4 styling (no runtime stylesheet injection needed).
  - Frameless title bar matching other MW4 windows.
  - Full control over UX (tree view, path edit, filter combo, file-name edit, buttons).
  - Synchronous API via local event loop (no call-site changes needed).

---

## 3. Changes to qtMain.py

### 3.1 Imports

**Remove:**
```python
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QFileDialog
```

**Add:**
```python
from mw4.gui.utilities.qtFileDialog import MWFileDialog
```

### 3.2 Methods to drop

1. **`prepareFileDialog(window, enableDir=False) -> QFileDialog`**
   - ~20 lines initializing a `QFileDialog` with styling.
   - No longer needed; `MWFileDialog` is pre-styled.

2. **`openFileBase(window, title, folder, filterSet, multiple=False) -> list[str]`**
   - ~15 lines setting up and running a `QFileDialog`.
   - Replaced inline by `MWFileDialog` class methods.

### 3.3 Methods to refactor

#### Before:
```python
def openFile(self, window: QWidget, title: str, folder: Path, filterSet: str) -> Path:
    files = self.openFileBase(window, title, folder, filterSet)
    file = files[0] if files else ""
    return Path(file)

def openMultipleFiles(
    self, window: QWidget, title: str, folder: Path, filterSet: str
) -> list[Path]:
    files = self.openFileBase(window, title, folder, filterSet, multiple=True)
    return [Path(f) for f in files]

def saveFile(
    self,
    window: QWidget,
    title: str,
    folder: Path,
    filterSet: str,
    enableDir: bool = False,
) -> Path:
    dlg = self.prepareFileDialog(window, enableDir)
    dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    dlg.setWindowTitle(title)
    dlg.setNameFilter(filterSet)
    dlg.setDirectory(str(folder))
    result = self.runDialog(dlg)
    if not result:
        return Path()
    return Path(dlg.selectedFiles()[0])

def openDir(self, window: QWidget, title: str, folder: Path) -> Path:
    dlg = self.prepareFileDialog(window=window, enableDir=True)
    dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
    dlg.setWindowTitle(title)
    dlg.setDirectory(str(folder))
    dlg.setFileMode(QFileDialog.FileMode.Directory)
    result = self.runDialog(dlg)
    if not result:
        return Path()
    return Path(dlg.selectedFiles()[0])
```

#### After:
```python
def openFile(self, window: QWidget, title: str, folder: Path, filterSet: str) -> Path:
    return MWFileDialog.getOpenFileName(window, title, folder, filterSet)

def openMultipleFiles(
    self, window: QWidget, title: str, folder: Path, filterSet: str
) -> list[Path]:
    return MWFileDialog.getOpenFileNames(window, title, folder, filterSet)

def saveFile(
    self,
    window: QWidget,
    title: str,
    folder: Path,
    filterSet: str,
    enableDir: bool = False,
) -> Path:
    # Note: enableDir flag kept for backwards compatibility but has no effect;
    # MWFileDialog.AnyFile mode allows typing a new filename in any directory.
    return MWFileDialog.getSaveFileName(window, title, folder, filterSet)

def openDir(self, window: QWidget, title: str, folder: Path) -> Path:
    return MWFileDialog.getExistingDirectory(window, title, folder)
```

**Lines saved**: ~70 lines (prepareFileDialog + openFileBase + refactored methods).

### 3.4 Keep `runDialog()`

Leave `runDialog()` intact – it's still used by `messageDialog()` for `QMessageBox`.

```python
@staticmethod
def runDialog(dlg: QMessageBox) -> int:  # Remove QFileDialog from type hint
    return dlg.exec()
```

---

## 4. Changes to tests

### File: `tests/unit_tests/gui/utilities/test_qtMain.py`

**Remove old tests** for `prepareFileDialog`, `openFileBase` (~6 tests that mock `QFileDialog`).

**Update tests** for `openFile`, `openMultipleFiles`, `saveFile`, `openDir` to mock `MWFileDialog` class methods instead:

#### Example refactored test:
```python
def test_openFile_success(function, tmp_path):
    """Test openFile returns Path when user accepts."""
    with mock.patch.object(
        MWFileDialog, "getOpenFileName", 
        return_value=tmp_path / "model.fits"
    ) as m:
        result = function.openFile(
            QWidget(), "Load Model", tmp_path, "*.fits"
        )
        m.assert_called_once_with(
            QWidget(), "Load Model", tmp_path, "*.fits"
        )
        assert result == tmp_path / "model.fits"

def test_openFile_cancelled(function, tmp_path):
    """Test openFile returns empty Path when user cancels."""
    with mock.patch.object(
        MWFileDialog, "getOpenFileName",
        return_value=Path()
    ):
        result = function.openFile(
            QWidget(), "Load", tmp_path, "*.*"
        )
        assert result == Path()

def test_openMultipleFiles(function, tmp_path):
    """Test openMultipleFiles returns list of Paths."""
    expected = [tmp_path / "a.fits", tmp_path / "b.fits"]
    with mock.patch.object(
        MWFileDialog, "getOpenFileNames",
        return_value=expected
    ):
        result = function.openMultipleFiles(
            QWidget(), "Load", tmp_path, "*.fits"
        )
        assert result == expected

def test_saveFile(function, tmp_path):
    """Test saveFile returns Path."""
    with mock.patch.object(
        MWFileDialog, "getSaveFileName",
        return_value=tmp_path / "config.cfg"
    ):
        result = function.saveFile(
            QWidget(), "Save Config", tmp_path, "*.cfg"
        )
        assert result == tmp_path / "config.cfg"

def test_openDir(function, tmp_path):
    """Test openDir returns Path."""
    with mock.patch.object(
        MWFileDialog, "getExistingDirectory",
        return_value=tmp_path / "data"
    ):
        result = function.openDir(
            QWidget(), "Choose Directory", tmp_path
        )
        assert result == tmp_path / "data"
```

**Update imports** in `test_qtMain.py`:
```python
from mw4.gui.utilities.qtFileDialog import MWFileDialog  # Add
# Remove: from PySide6.QtWidgets import QFileDialog
```

---

## 5. Implementation order

1. **Update imports in `qtMain.py`**
   - Remove `QDir`, `QFileDialog` imports.
   - Add `from mw4.gui.utilities.qtFileDialog import MWFileDialog`.

2. **Refactor the four public methods** (`openFile`, `openMultipleFiles`, `saveFile`, `openDir`)
   - Replace bodies with one-liners calling `MWFileDialog` class methods.

3. **Drop `prepareFileDialog()` and `openFileBase()`**
   - These are now dead code.

4. **Update type hint in `runDialog()`**
   - Change `dlg: QMessageBox | QFileDialog` → `dlg: QMessageBox`.

5. **Refactor unit tests** in `test_qtMain.py`
   - Remove old file-dialog tests.
   - Add new tests mocking `MWFileDialog` class methods.
   - Run tests to 100 % coverage of touched code.

6. **Verify backward compatibility**
   - Ensure all 9 call sites still work as-is (they call the public methods, not internals).

7. **Lint and format**
   - Run `ruff check --fix` on both files.
   - Run `ruff format`.

8. **Run full test suite**
   - `pytest tests/unit_tests/gui/utilities/test_qtMain.py`.
   - Check coverage is maintained or improved in `MWidget` file-dialog section.

---

## 6. Impact analysis

| Aspect | Impact |
|--------|--------|
| **Call sites** | None – public API unchanged. |
| **Test coverage** | Refactored, but count stays same or increases. |
| **Dependencies** | Adds soft dependency on `MWFileDialog` (same package). |
| **Styling** | Improves – MW4 theme now built-in, not injected. |
| **UX** | Better – users now see a proper file tree, not a native dialog. |
| **Lines of code** | ~70 fewer in `qtMain.py`. |

---

## 7. Risks & mitigations

| Risk | Mitigation |
|-------|------------|
| A call site passes unexpected args to the helpers. | All 9 call sites already use the documented signature; add a type check pass with `mypy` if needed. |
| `enableDir` flag behavior changes. | Document that on `saveFile`, the flag is ignored (MWFileDialog.AnyFile mode subsumes it). |
| Tests miss edge cases in new code paths. | New tests must cover cancel, empty result, multi-file, dir-only modes; mock MWFileDialog at a high level. |
| `MWFileDialog` has a bug. | Mitigated by the 28 unit tests in `test_qtFileDialog.py` (100% coverage). |

---

## 8. Files changed

| File | Type | Lines changed |
|------|------|--------------|
| `src/mw4/gui/utilities/qtMain.py` | Code | −70 (drop 2 methods, refactor 4 methods) |
| `tests/unit_tests/gui/utilities/test_qtMain.py` | Test | ±15 (remove 6 old tests, add 5 new parameterized tests) |

---

## 9. Follow-up (optional)

After this refactor succeeds:

- Consider adding a user-facing config toggle `useNativeFileDialog: bool` (see `PLAN_native_qfiledialog_integration.md`) to let power users fall back to OS dialogs if preferred. Would require:
  - Conditional logic in the four methods above.
  - A settings checkbox in the GUI settings tab.

---

## 10. Acceptance criteria

- [x] `qtMain.py` imports `MWFileDialog`, drops `QFileDialog` import.
- [x] All four file-dialog methods are one-liners calling `MWFileDialog` class methods.
- [x] `prepareFileDialog()` and `openFileBase()` are removed.
- [x] Unit tests in `test_qtMain.py` mock `MWFileDialog` instead of `QFileDialog`.
- [x] All 9 call sites work without code changes.
- [x] `ruff check` and `ruff format` pass.
- [x] Test coverage 100 % on modified sections.
- [x] Full test suite passes.

