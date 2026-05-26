# MountWizzard4 – GitHub Copilot Instructions

## Project Description
MountWizzard4 is a Python desktop application for controlling **10micron mounts**
for astronomical observations. It provides a full GUI and supports camera, dome,
weather, and satellite workflows.

---

## Tech Stack

| Area              | Technology                                |
|-------------------|-------------------------------------------|
| Language          | Python 3.11 compatible                    |
| GUI               | PySide6 (Qt6), PyQtGraph                  |
| Astronomy         | Astropy, Skyfield, SGP4, SEP, PyERFA      |
| Data Processing   | NumPy, SciPy, OpenCV (headless)           |
| Protocols         | INDI (indipyclient), WebSocket, HID, REST |
| Image Formats     | FITS, XISF                                |
| Configuration     | PyYAML, JSON                              |
| Build             | uv / uv_build                             |
| Testing           | pytest, pytest-qt, pytest-cov             |
| Linting           | Ruff                                      |

---

## Project Structure

```
src/mw4/          → Main source code (src layout)
  gui/            → PySide6 GUI (widgets, windows, styles)
  logic/          → Device logic (camera, dome, weather, ...)
  base/           → Base classes and utilities
  mountcontrol/   → Communication with 10micron mount
tests/
  unit_tests/     → Unit tests (mirror the src/mw4/ structure)
  testData/       → Test data (FITS, WCS, JSON, ...)
src_add/
  widgets/        → Qt Designer .ui files
```

---

## Coding Conventions

- **Line length**: max. length out of pyproject.toml (Ruff)
- **Indentation**: 4 spaces
- **Imports**: sorted without sections (isort via Ruff)
- **GUI communication**: Qt Signals & Slots
- **Tests**: pytest, mocking with `unittest.mock`
- **Naming**: camelCase for classes and modules and variable
- **No** direct dependencies between GUI tabs (loose coupling)

---

## Typical Patterns

### Device Class (Logic Layer)
```python
class MyDevice:
    def __init__(self, app):
        self.app = app
        self.signals = MyDeviceSignals()
```

### GUI Mixin
```python
class TabMyFeatureMixin:
    def initConfig(self): ...
    def storeConfig(self): ...
    def setupGui(self): ...
```

### Unit Test
```python
def test_myFunction(app):
    # arrange
    ...
    # act
    result = app.myFunction()
    # assert
    assert result == expected
```

---

## Important Notes for Copilot

- Tests must always be placed under `tests/unit_tests/` mirroring the
  `src/mw4/` folder structure.
- GUI widgets are generated from `.ui` files – do **not** edit them manually.
- Astronomical calculations should preferably use **Astropy** or **Skyfield**.
- Platform-specific code (Windows) must be guarded with
  `platform_system == 'Windows'`.
- Method names, function names, variables, etc. stay in camelCase format.
- Source code is located in `src/mw4`.
- Unit tests are located in `tests/unit_tests`.
- All code must be covered by tests with a test coverage of 100%.
- if larger changes (more than one class) are needed, a plan must be created before implementing any changes.
- The plan will be saved as a Markdown file with an appropriate name in the
  root directory.
- After all changes, the package will be tested to 100% coverage.
- Ruff will be used as formatter and linter when finished. All findings will
  be resolved.
- As the last step before completion, the overall package will be tested.
- Python 3.11 language features should be used.
- There is a clear separation between business logic in `src/mw4/logic` and
  the GUI in `src/mw4/gui`.
- For the GUI, PySide6 is used.
- All longer-running calculations must be separated into workers of the main
  threadPool.
- If a worker is needed, the variable holding the worker should be named
  `worker{NameOfFunction}` and the worker method should be named
  `runner{NameOfFunction}`; full names comply with camelCase.
- Type annotations must be used for all functions and methods, including
  return types.
- Do not take `src/mw4/gui/widgets` into account, as those files are
  automatically generated.
- no local methods and functions with leading underscore (e.g., `_myFunction`) should be used
- check the line length – it must not exceed the limit, but use the line length limit as much as possible to avoid unnecessary line breaks
  defined in `pyproject.toml`; split long comments into multiple lines.
- stay close with the task description and do not add any additional features or changes that are not
  explicitly mentioned in the task description.