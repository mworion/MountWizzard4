# Plan: Refactor `UploadPopup.prepareFiles` to Use a Context Manager

**File:** `src/mw4/gui/extWindows/uploadPopupW.py`
**Date:** 2026-05-04

---

## Problem

`prepareFiles()` calls `open(fullDataFilePath)` inside a loop, collects the
raw file handles into a `dict`, and returns them. Those handles are passed
to `requests.post()` in `postHostData()` and are **never explicitly closed**
— a resource leak.

```python
# current (resource leak)
files[self.dataNames[dataType]["attr"]] = (
    self.dataNames[dataType]["file"],
    open(fullDataFilePath),          # handle never closed
)
```

---

## Proposed Solution

Read each file's bytes inside a `with` block and store `(filename, bytes)`
instead of `(filename, file_handle)`. `requests.post(url, files=...)` accepts
`(filename, bytes)` tuples natively, so no other method needs to change.

```python
# after refactoring (context manager, no resource leak)
with open(fullDataFilePath, "rb") as fh:
    files[self.dataNames[dataType]["attr"]] = (
        self.dataNames[dataType]["file"],
        fh.read(),
    )
```

---

## Steps

### 1 – Rewrite `prepareFiles()` in `uploadPopupW.py`

- Replace `open(fullDataFilePath)` with a `with open(fullDataFilePath, "rb")
  as fh:` block.
- Store `(filename, fh.read())` as the tuple value.
- Return type stays `dict`; method signature is unchanged.

### 2 – Verify call-flow requires no further changes

- `postHostData()` passes `files` dict to `requests.post()` — no change
  needed.
- `uploadFileWorker()` calls `prepareFiles()` then `postHostData()` — no
  change needed.

### 3 – Update unit tests in `test_uploadPopupW.py`

- Replace `mock.patch.object(builtins, "open")` with
  `mock.patch("builtins.open", mock.mock_open(read_data=b""))` in all
  `test_prepareFiles_*` tests so the mock correctly supports the context
  manager protocol (`__enter__` / `__exit__`) and `.read()`.

### 4 – Run Ruff (lint + format)

```bash
ruff check --fix src/mw4/gui/extWindows/uploadPopupW.py \
    tests/unit_tests/gui/extWindows/test_uploadPopupW.py
ruff format src/mw4/gui/extWindows/uploadPopupW.py \
    tests/unit_tests/gui/extWindows/test_uploadPopupW.py
```

### 5 – Run test suite with coverage

```bash
pytest tests/unit_tests/gui/extWindows/test_uploadPopupW.py \
    --cov=mw4.gui.extWindows.uploadPopupW \
    --cov-report=term-missing
```

Confirm 100 % coverage is maintained.

### 6 – Run overall package tests

```bash
pytest tests/unit_tests/
```

---

## Further Considerations

1. **Binary vs. text mode:** Switching to `"rb"` is safer for cross-platform
   consistency and required for non-text files such as `satellites.tle`.
   The mount API accepts raw bytes — `requests` sends them verbatim.
2. **Early-return path:** If `dataType not in self.dataNames` triggers after
   one or more files have already been opened, those handles are closed
   automatically when the `with` block exits — no extra cleanup needed.
3. **Stricter typing (out of scope):** `dict[str, tuple[str, bytes]]` could
   be used as the return type annotation in a future task.

