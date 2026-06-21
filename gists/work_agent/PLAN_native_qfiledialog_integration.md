# Plan – Integrating the native `QFileDialog` into the custom (frameless) window

## 1. Motivation

The current `MWidget` in `src/mw4/gui/utilities/qtMain.py` builds every file
dialog with `QFileDialog.Option.DontUseNativeDialog`, applies the MW4
stylesheet, sets `QDir` filters and manually centers the dialog over the
parent window. Reasons were visual consistency with the custom
`FramelessWindowHint` + `WA_TranslucentBackground` main window
(`CustomTitleBar`) and the dark MW4 theme.

Drawbacks of the non-native dialog:

- No access to OS-level features (favorites, recent locations, network
  shares, iCloud, Quick Look on macOS, file tags, jump lists on Windows,
  GTK/KDE bookmarks on Linux).
- Inconsistent behavior with the rest of the OS the user works in.
- Manual positioning logic that ignores DPI/multi-monitor.
- The Qt non-native dialog drags in extra widgets that are styled by our
  custom QSS, sometimes producing visual glitches inside frameless windows.

Goal: allow the **native** `QFileDialog` to be used while keeping the
custom-framed MW4 windows intact, with a single switch to fall back to the
themed non-native dialog when needed.

---

## 2. Constraints from the current architecture

- `MWidget` is `QMainWindow` with `Qt.WindowType.FramelessWindowHint` and
  `WA_TranslucentBackground`. Native dialogs are *separate* top-level OS
  windows; they cannot be embedded into the custom title bar layout. They
  must remain modal child dialogs of the MW4 window.
- A frameless top-level still has a real native window handle, so
  `QFileDialog.getOpenFileName(parent=self, ...)` works correctly: the OS
  positions and parents the native dialog to the MW4 window.
- The native dialog ignores `setStyleSheet`, `setWindowIcon`, manual
  `move()` and the `QDir.Filter.AllDirs` flag. Code that sets these must be
  skipped on the native path.
- All call sites currently consume `MWidget.openFile / openMultipleFiles /
  saveFile / openDir` – there are 9 call sites (mainWindow, tabModel,
  tabTools_Rename, tabModel_BuildPoints, imageW, analyseW, horizonDraw,
  devicePopupW). The public API of these helpers must stay stable.

---

## 3. Design

### 3.1 Configuration switch

Add a single global preference (default `True` = native):

- Key: `useNativeFileDialog: bool`
- Stored in the existing app config dict (alongside other GUI settings),
  loaded in `initConfig` of the main window mixin that already manages
  global GUI preferences.
- Exposed in the GUI settings tab (checkbox: *"Use native OS file dialog"*).
- Read by `MWidget` through `self.app.config` (consistent with how
  `MWidget` already accesses `app.mwGlob`).

The switch can be overridden per-call via an optional `useNative` keyword
argument on the helper methods, defaulting to the configured value. This
keeps backwards-compatibility for all existing call sites.

### 3.2 Refactor of `MWidget` helpers (`qtMain.py`)

Touch only the file-dialog section. Two parallel code paths:

1. **Native path** – uses `QFileDialog` static convenience methods
   (`getOpenFileName`, `getOpenFileNames`, `getSaveFileName`,
   `getExistingDirectory`). Parent = the calling MW4 window so the OS
   parents the dialog. No styling, no manual positioning, no
   `DontUseNativeDialog` option, no `QDir` filter mangling.
2. **Themed path** – the existing `prepareFileDialog` / `openFileBase`
   logic, kept as the fallback. Renamed internals stay private to
   `MWidget` (no leading underscore per project rules; instead a clear
   name like `prepareThemedFileDialog`).

New helper signatures (public API additions are optional kwargs only):

```python
def openFile(self, window, title, folder, filterSet,
             useNative: bool | None = None) -> Path: ...
def openMultipleFiles(self, window, title, folder, filterSet,
                      useNative: bool | None = None) -> list[Path]: ...
def saveFile(self, window, title, folder, filterSet,
             enableDir: bool = False,
             useNative: bool | None = None) -> Path: ...
def openDir(self, window, title, folder,
            useNative: bool | None = None) -> Path: ...
```

`useNative is None` ⇒ resolve through `self.resolveUseNativeDialog()`
which reads the config flag, with a safe default of `True` if the config
is unavailable (e.g. unit tests using a bare `MWidget`).

### 3.3 Behavioural details per platform

- **macOS**: `getExistingDirectory` shows the proper Finder folder picker.
  `enableDir=True` on `saveFile` (currently sets `QDir.Filter.AllDirs`)
  has no effect on native and is dropped on the native path; documented
  in the docstring.
- **Windows**: native dialogs follow the dark/light system theme. We do
  **not** try to repaint them. Add a Windows guard only if a future bug
  requires it (`platform_system == 'Windows'`).
- **Linux**: GTK/KDE portal dialogs are used by Qt automatically.

### 3.4 Interaction with the custom frameless window

- The native dialog is application-modal (`QFileDialog` static methods
  block on the parent). The custom title bar's drag handlers do not
  interfere because input is blocked while the native dialog is open.
- `CustomTitleBar` does not need any change.
- `WA_TranslucentBackground` on the parent is irrelevant for native
  child dialogs – the OS draws them with their own chrome.
- Screenshots (`F5`/`F6` → `saveWindowAsPNG`) keep working: the native
  dialog is a separate OS window and is not part of the MW4 grab.

---

## 4. Affected files

| File | Change |
|------|--------|
| `src/mw4/gui/utilities/qtMain.py` | Refactor file-dialog helpers, add `useNative` path, keep themed fallback. |
| `src/mw4/gui/mainWaddon/tabSettMisc.py` *(or the tab where global GUI settings already live – to be confirmed during implementation)* | Add checkbox + `initConfig`/`storeConfig` for `useNativeFileDialog`. |
| `src_add/widgets/<settingsTab>.ui` | Add the checkbox widget. |
| `src/mw4/gui/mainWindow/mainWindow.py` | Ensure default for `useNativeFileDialog` exists in `initConfig`. |
| Documentation: `doc/config/gui/` | Add a short section describing the new option. |

No changes to existing call sites are required (backwards compatible).

---

## 5. Test strategy (target: 100 % coverage)

Located under `tests/unit_tests/gui/utilities/test_qtMain.py`.

1. **Native path** – patch `QFileDialog.getOpenFileName`,
   `getOpenFileNames`, `getSaveFileName`, `getExistingDirectory` with
   `unittest.mock.patch` and assert:
   - they are called with the expected `parent`, `caption`, `dir`,
     `filter` arguments,
   - the returned `Path` objects are correct,
   - cancellation (empty string return) yields `Path()` for save/open
     and an empty list for multi-open.
2. **Themed path** – existing tests stay valid; add tests that force
   `useNative=False` to keep the themed branch covered.
3. **Resolver** – tests for `resolveUseNativeDialog`: explicit `True` /
   `False` arguments win over config, missing config defaults to `True`.
4. **Settings tab** – pytest-qt tests for the new checkbox: `initConfig`
   restores the value, `storeConfig` writes it.
5. Windows-specific behavior (if any branch is added) is guarded by
   `platform_system == 'Windows'` and excluded from non-Windows coverage
   tracking, per project rules.

---

## 6. Step-by-step implementation order

1. Create this plan (done).
2. Refactor `qtMain.py`:
   - Extract themed prep logic into `prepareThemedFileDialog`.
   - Add `resolveUseNativeDialog`.
   - Implement native branches in `openFile`, `openMultipleFiles`,
     `saveFile`, `openDir`.
3. Update / add unit tests in `test_qtMain.py`; run the file to 100 %.
4. Add the config flag default in the main window `initConfig`.
5. Add the GUI checkbox (logic mixin + `.ui` file) and tests for it.
6. Update user documentation under `doc/config/gui/`.
7. Run Ruff (format + lint), fix all findings.
8. Run the full test suite with coverage; ensure 100 %.

---

## 7. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Native dialog visually clashes with dark MW4 theme. | The flag lets the user fall back to the themed dialog. |
| Some platforms ignore `directory` argument when it does not exist. | Resolve `folder` to an existing parent path before the call. |
| `enableDir` flag (used in `saveFile`) is non-native. | Documented; if user enables it the call automatically falls back to the themed dialog. |
| Existing tests rely on `QFileDialog()` being instantiated. | Keep the themed path; add new mocks for the static methods. |
| Native macOS dialog can be slow on first open. | Cosmetic only – no action. |

---

## 8. Out of scope

- Re-skinning the native dialog (impossible without OS hooks).
- Embedding a file browser into the custom title-bar window.
- Replacing other `QMessageBox` / `QInputDialog` usages.

