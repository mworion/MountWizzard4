# Plan A4 / roadmap 12 – layering contracts (import-linter) in CI

Source: `../2026-10-20_review_copilot_open.md`, finding A4; roadmap item 12.
Status: **implemented 2026-10-22** (7 contracts, `deviceRegistry` moved, ruff TID251, docs; `test_deviceEntry.py` stays in `tests/unit_tests/base` because `base/deviceEntry.py` still exists).

## Findings (measured 2026-10-22 with probe configs, not committed)

Today there is one contract in `../pyproject.toml`: *`base`, `logic`, `mountcontrol` do not import
`gui`*. It is run by the `lint` job of `.github/workflows/unit_ubuntu.yml` (`uv run
lint-imports`). Everything else about the layering is unprotected.

Probe of the intended architecture `gui → logic → mountcontrol → base`
(`exclude_type_checking_imports = true`, 336 files, 1228 dependencies):

| Candidate contract | Result |
|--------------------|--------|
| `base` ↛ `logic` | **broken** – only `base/deviceRegistry.py` (16 driver imports) |
| `base` ↛ `mountcontrol` | **broken** – only `base/deviceRegistry.py` (`mountcontrol.mount`, plus transitive via drivers) |
| `mountcontrol` ↛ `logic` | kept |
| `layers: gui > logic > mountcontrol > base` | broken by the same module only |
| `logic.controllers` ↛ `logic.drivers` and the reverse | kept |
| controller areas independent (`image`, `imageWindow`, `model`, `mount`, `satellites`) | kept |
| `fits`, `profiles`, `file`, `databaseProcessing` ↛ `drivers`/`controllers` | kept |
| `fits`, `profiles`, `databaseProcessing` have no PySide6 | kept |
| `logic.controllers` have no PySide6 | broken by 2 QObject workers: `imageWindow.photometry`, `model.modelRun` |

So the "`base` ↔ `logic` is circular" note in the review boils down to **one module**:
`base/deviceRegistry.py` is really the composition root (it instantiates every driver and the
mount). Its users are `mainApp.py`, the type-only import in `base/appProtocol.py` and tests.

Qt in the lower layers (current): `base` 10 files, `logic` 15, `mountcontrol` 4, all
`QtCore` (`QObject`, `Signal`, `QThreadPool`, `QTimer`, `QMutex`), `QtNetwork` (sockets,
`mountcontrol/connection.py`, `remote`) and `QtMultimedia` (`audioManager`). **No** `QtWidgets`
or `QtGui` import exists outside `gui`. That is the acceptable boundary; it is just not
enforced. import-linter cannot forbid a Qt *submodule* (external packages are squashed to
`PySide6`), so that part goes into ruff.

## Goal

Encode the architecture so a violation fails CI:

```
gui  →  logic  →  mountcontrol  →  base          (top-level modules mainApp, loader,
         ├─ controllers   (no drivers, Qt only in 2 workers)        deviceRegistry = composition root)
         ├─ drivers       (no controllers)
         └─ fits / profiles / file / databaseProcessing   (foundations)
```

## Rules

- No behaviour change; the only code move is `deviceRegistry` (pure move + import rewrite).
- Contracts must pass on every OS (static analysis; Windows-only modules are analysed too).
- Every `ignore_imports` entry needs a one-line reason in the TOML.
- Tests keep the mirrored layout; `test_testMapping.py` stays green.

## Steps

### 1. Move the composition root out of `base`

1. `git mv src/mw4/base/deviceRegistry.py src/mw4/deviceRegistry.py` (next to `mainApp.py`;
   it is neither base infrastructure nor logic).
2. Rewrite imports and dotted strings with a script over `src` and `tests`:
   `mw4.base.deviceRegistry` → `mw4.deviceRegistry` (`mainApp`, `appProtocol` under
   `TYPE_CHECKING`, `baseTestApp`, `test_measure`, `test_mainWindow`,
   `mock.patch("mw4.base.deviceRegistry.MeasureData", …)`).
3. Mirror the tests: `tests/unit_tests/base/test_deviceRegistry.py` →
   `../tests/unit_tests/test_deviceRegistry.py`; `test_deviceEntry.py` moves next to it
   (it tests `DeviceEntry` from the same module).
4. Check path-bound config for the old path: `../pyproject.toml` (coverage, pyrefly sub-configs,
   ruff per-file-ignores) and `doc/`.
5. Verify: `uv run pytest tests/unit_tests -n auto` (5226 passed, 100 %), `ruff`, `pyrefly`.

### 2. Replace the single contract by the full set

`../pyproject.toml` (all of these passed in the probe except the layers/base contracts, which
pass once step 1 is done):

```toml
[tool.importlinter]
root_package = "mw4"
include_external_packages = true
exclude_type_checking_imports = true

[[tool.importlinter.contracts]]
name = "Layers: gui > logic > mountcontrol > base"
type = "layers"
layers = ["mw4.gui", "mw4.logic", "mw4.mountcontrol", "mw4.base"]

[[tool.importlinter.contracts]]
name = "Controllers do not import drivers"
type = "forbidden"
source_modules = ["mw4.logic.controllers"]
forbidden_modules = ["mw4.logic.drivers"]

[[tool.importlinter.contracts]]
name = "Drivers do not import controllers"
type = "forbidden"
source_modules = ["mw4.logic.drivers"]
forbidden_modules = ["mw4.logic.controllers"]

[[tool.importlinter.contracts]]
name = "Controller areas are independent"
type = "independence"
modules = [
    "mw4.logic.controllers.image",
    "mw4.logic.controllers.imageWindow",
    "mw4.logic.controllers.model",
    "mw4.logic.controllers.mount",
    "mw4.logic.controllers.satellites",
]

[[tool.importlinter.contracts]]
name = "Foundations do not import drivers or controllers"
type = "forbidden"
source_modules = [
    "mw4.logic.fits", "mw4.logic.profiles", "mw4.logic.file", "mw4.logic.databaseProcessing",
]
forbidden_modules = ["mw4.logic.drivers", "mw4.logic.controllers"]

[[tool.importlinter.contracts]]
name = "Foundations are Qt free"
type = "forbidden"
source_modules = ["mw4.logic.fits", "mw4.logic.profiles", "mw4.logic.databaseProcessing"]
forbidden_modules = ["PySide6"]
allow_indirect_imports = true

[[tool.importlinter.contracts]]
name = "Controllers are Qt free except workers"
type = "forbidden"
source_modules = ["mw4.logic.controllers"]
forbidden_modules = ["PySide6"]
allow_indirect_imports = true
ignore_imports = [
    # QObject workers with signals, not GUI code
    "mw4.logic.controllers.imageWindow.photometry -> PySide6",
    "mw4.logic.controllers.model.modelRun -> PySide6",
]
```

The old "Lower layers do not import gui" contract is covered by `layers` and is removed.
`logic.file` is intentionally not in the Qt-free list (`fileHandler` is a `QObject`).

### 3. Keep the Qt GUI stack out of the lower layers (ruff)

`TID251` is already enabled (it bans `platform.system`). Extend
`[tool.ruff.lint.flake8-tidy-imports.banned-api]`:

```toml
"PySide6.QtWidgets".msg = "Widgets belong in mw4.gui."
"PySide6.QtGui".msg = "GUI types belong in mw4.gui."
"PySide6.QtCharts".msg = "Charts belong in mw4.gui."
```

and add `"src/mw4/gui/**" = ["TID251"]` and `"tests/**" = ["TID251"]` to the
per-file-ignores. Before enabling, check top-level modules (`mainApp`, `loader`, …) with
`grep -rn "QtWidgets\|QtGui" src/mw4 --include='*.py' | grep -v "src/mw4/gui/"`; add a
narrow ignore only where unavoidable. Known gap: attribute access like
`PySide6.QtCore.QTimer()` after a bare `import PySide6` (4 files: `bootstrap`, `dome`,
`measureCSV`, `measureRaw`) is not caught – harmless, QtCore only.

### 4. CI and developer workflow

- CI already runs `uv run lint-imports` in the ubuntu `lint` job; nothing to add there except
  keeping the job required for merges.
- `../tasks.py`: make sure the local lint task runs `lint-imports` next to ruff/pyrefly.
- Docs: add a short "Architecture rules" section (layer diagram above and the contract
  list) to `../doc/architecture/index.rst`; mention the rules in
  `.github/copilot-instructions.md` ("logic never imports gui; controllers never import
  drivers").
- Proof the gate works: on a scratch branch add `from mw4.gui.utilities.qtHelpers import
  clickable` to a `base` module and `from mw4.logic.drivers.dome.dome import Dome` to a
  controller; `lint-imports` must fail for both.

### 5. Optional follow-ups (not part of this plan)

- GUI tab independence (`mainWaddon/tab*` only import `TabAddon`/`SatData`): import-linter
  wildcards cannot match partial module names (`tab*`), so this needs either an explicit module
  list in the TOML or a small meta-test. Decide after steps 1–4.
- Move the type-only import of `DeviceRegistry` in `base/appProtocol.py` behind a protocol
  (`HasDevices` exists) so `base` has no upward reference even under `TYPE_CHECKING`.

## Verification

- `uv run lint-imports` → all contracts kept (7 instead of 1), `Analyzed … files`.
- `uv run ruff check src tests`, `uv run ruff format --check src tests`,
  `uv run pyrefly check` → clean.
- `uv run pytest tests/unit_tests -n auto` → 5226 passed, 100 % line and branch coverage;
  `test_testMapping.py` green after the test move.
- Update `../2026-10-20_review_copilot_open.md` (A4 done, roadmap items 3 and 12) and
  `2026-10-20_review_copilot.md`; the "22 `logic` + 8 `mountcontrol` files import PySide6"
  note becomes "QtCore/QtNetwork/QtMultimedia only, enforced".

## Risks

- Moving `deviceRegistry` touches many test imports and `mock.patch` strings; a missed dotted
  string fails at test time, not at import time → grep for `base.deviceRegistry` after the
  rewrite (must be 0).
- `ruff` `TID251` on `PySide6.QtGui` also flags `from PySide6.QtGui import …` in
  test helpers; hence the `tests/**` ignore.
- Stricter contracts can block quick fixes later; that is the intent, and the escape hatch
  is an `ignore_imports` entry with a reason.

## Out of scope

- Removing Qt `QObject`/`Signal` from `logic` and `mountcontrol` (accepted by design).
- Typed configuration (A3).

