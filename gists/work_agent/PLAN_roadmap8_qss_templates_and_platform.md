# Plan – Roadmap item 8: QSS templates (M5) and central platform handling (P8)

Source: `../../2026-10-20_review_copilot.md`, findings **M5** and **P8**, roadmap *Medium* item 8.
Status: **implemented.** Decisions: 7.1 shared Windows back-end registration helper only (no factory); 7.2 templates in `src/mw4/assets/styles/`; 7.3 constants read at import; 7.4 both parts in one go. Golden-hash test guards the rendered output; `TID251` bans `platform.system` outside `base/platformInfo.py`.
in either order and shipped separately (WP 8.A = styles, WP 8.B = platform).

## 1. Problem (measured)

### M5 – styles
- `gui/styles/styleSheets.py` is 691 lines of Python strings (`MAC_STYLE`, `NON_MAC_STYLE`,
  `BASIC_STYLE`), no code. It is only consumed by `styles.py` (`STYLE` class attribute,
  chosen at import time by `platform.system() == "Darwin"`) and one trivial test
  (`isinstance(..., str)`).
- Placeholders already exist (`$M_BACK$`, `$imageName$`) and are resolved line by line in
  `Styles.renderStyle` (`replaceColor`, `replaceImage`). So the template mechanism is there;
  only the storage as Python strings is the problem (no QSS syntax highlighting, no linting,
  diffs inside string literals, 691-line module in every size metric).
- `Styles.STYLE` is evaluated at **import time**, so the platform choice cannot be tested
  without reloading the module.

### P8 – platform checks
- 35 `platform.system()` checks in 22 modules of `src`, 60 in `tests`. Three patterns:
  1. **Import guard + back-end registration** (10 device modules: `camera`, `dome`, `focuser`,
     `telescope`, `filter`, `cover`, `lightPanel`, `sensorWeather`, `pegasusUPB`,
     `ascomClass`): `if platform.system() == "Windows": from … import XAscom` and later
     `if platform.system() == "Windows": self.run["ascom"] = …`.
  2. **Per-OS lookup** (`astap`, `astrometry`, `watney`): `apps[platform.system()]`,
     `Darwin or Linux` branches, `.exe` suffix.
  3. **GUI/bootstrap** (`bootstrap`, `cli`, `qtMain`, `tabSettGui`, `styles`).
- Critical coupling: `../../pyproject.toml` configures the coverage plugin with the **literal source
  text** `if platform\.system\(\) == "Windows":` (rule) and omits `ascomClass.py` and
  `cameraAscom.py` on non-Windows. Any rewrite of the guard must update that rule, otherwise
  coverage on Linux/macOS drops below 100 %.

## 2. Goals

1. QSS lives in `.qss` template files, loaded through `importlib.resources`, rendered with the
   existing placeholder mechanism; the platform choice becomes testable.
2. One module `base/platformInfo.py` is the only place that calls `platform.system()`;
   everything else uses its constants/helpers.
3. Device back-end registration for Windows-only drivers becomes uniform (no inline branching
   repeated in 10 files).
4. 100 % coverage on all three OS, no change in rendered stylesheet or runtime behaviour.

Non-goals: restyling, changing colour sets, new platforms, converting plate-solver
configuration to a different structure beyond the OS lookup.

## 3. Design

### 3.A Styles (M5)

- New files: `src/mw4/assets/styles/{mac,nonMac,basic}.qss` (content = the three strings,
  byte-identical, placeholders unchanged).
- `styleSheets.py` is **deleted**; `Styles` gets
  `loadTemplate(name: str) -> str` (`files("mw4").joinpath("assets/styles/<name>.qss").read_text`)
  and a method `styleTemplate() -> str` that returns `mac + basic` on Darwin and
  `nonMac + basic` otherwise, using the platform helper from 8.B (or `platform.system()` until
  that lands). `STYLE` stops being a class attribute; `mw4Style` calls `styleTemplate()`.
- Template text is cached (`functools.cache`) – it never changes at runtime.
- Packaging: `uv_build` ships everything under `../../src/mw4`, but verify the wheel contains the
  `.qss` files (the `package-data` entry in `pyproject.toml` currently only names `data/**`).
- Tests: the old `isinstance` tests are replaced by
  - a **golden test**: rendered output for each colour set × platform equals a stored
    snapshot generated *before* the move (same technique as WP 2 materials);
  - a test that every `$key$` in each template is a known colour or image key (catches typos,
    which today fail silently because `replaceColor` skips unknown keys);
  - tests that `styleTemplate()` picks the right files per platform (monkeypatch the helper).

### 3.B Platform (P8)

New module `base/platformInfo.py` (type: plain constants + tiny functions, no Qt):

```python
SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_MAC = SYSTEM == "Darwin"
IS_LINUX = SYSTEM == "Linux"
```

- Constants are read once at import. Tests that today `mock.patch("platform.system", …)`
  (≈ 8 sites) patch `mw4.base.platformInfo.IS_WINDOWS` (or the consumer's reference)
  instead – cleaner, but all these tests must be migrated.
- **Pattern 1 (device back-ends):** keep the conditional *import* where it is (the import must
  not execute off Windows) but replace the second inline check by a tiny shared helper
  on the device side:
  `registerWindowsBackends(run, {"ascom": CameraAscom, "sgpro": CameraSGPro}, owner)` in
  `base/platformInfo.py` or `logic/deviceBackends.py`. This removes the duplicated branching
  but still needs the guarded import, so complete removal of the guard is **not** promised.
  Decision needed, see §7.
- **Pattern 2 (solver paths):** replace `apps[platform.system()]` and the `Darwin or Linux`
  branches by `IS_WINDOWS` / a `POSIX = not IS_WINDOWS` constant; `.exe` suffix becomes
  `EXE_SUFFIX`.
- **Pattern 3:** straight replacement with the constants; `qtMain`'s
  `not in ["Linux","Windows"]` becomes `IS_MAC`.
- Coverage plugin rule is updated to match the new guard text, e.g.
  `'if IS_WINDOWS:' = "platform_system != 'Windows'"`, and the omit list stays. Check the same
  on a Windows runner (CI `unit_win.yml` already runs per folder with `--cov-fail-under=0`;
  full-tree 100 % remains a local/Linux/macOS criterion).
- A ruff `banned-api`/`TID251` rule forbids `platform.system` outside
  `base/platformInfo.py`, so it cannot regrow (replaces the review's "enforce" bullet).

## 4. Work packages

| WP | Content | Effort | Risk |
|----|---------|--------|------|
| 8.A1 | Golden snapshot of rendered stylesheet (2 platforms × 3 colour sets × transparency 1.0/0.5) taken **before** any change | 0.25 d | low |
| 8.A2 | Move strings to `.qss` files, loader + `styleTemplate()`, drop `styleSheets.py`, wheel check, tests (golden, key validation, platform choice) | 0.5 d | low |
| 8.B1 | `base/platformInfo.py` + tests; migrate pattern 3 and 2 (bootstrap, cli, qtMain, tabSettGui, styles, solvers) | 0.5 d | low |
| 8.B2 | Device back-ends (pattern 1): shared registration helper, migrate 10 modules, update coverage plugin rule and omit list, verify coverage on Linux/macOS locally and Windows in CI | 1 d | med |
| 8.B3 | Migrate tests off `mock.patch("platform.system")` to the new constants; enable `TID251` for `platform.system`; update review (M5, P8 done, metrics) | 0.5 d | low |

Total ≈ 2.75 days. 8.A (1–2) and 8.B (1–3) are independent; 8.A2 can use the new helper once
8.B1 exists but does not need it.

## 5. Verification

- 8.A: rendered output byte-identical to the 8.A1 snapshot for all combinations; app starts and
  both macOS-style and non-mac look are checked visually once (light/dark colour sets).
- 8.B: full suite at 100 % line + branch on macOS/Linux locally (Windows-only code is omitted
  by the plugin), the Windows CI jobs green, pyrefly 0 errors, ruff clean incl. the new
  `TID251` rule.
- Wheel check: `uv build` and list the wheel; confirm `assets/styles/*.qss` are included and
  the app starts from the built wheel (or at least `files("mw4")` resolves the templates).

## 6. Risks

| Risk | Mitigation |
|------|------------|
| Coverage plugin no longer recognises the Windows guard → coverage < 100 % on Linux/macOS | Change rule and guards in the same commit; run full coverage locally right after; keep the rule text as a one-line constant in one place |
| `.qss` files missing from the wheel / PyInstaller-style bundles | Wheel check in 8.A2; same loader pattern as the existing `assets/icon` access (`importlib.resources`) |
| Import-time constants break tests that rely on patching at call time | Use module attribute access (`platformInfo.IS_WINDOWS`) in consumers where tests patch it; migrate those tests in 8.B3 |
| Windows-only paths cannot be exercised locally | Windows CI job is the check; changes there are mechanical and kept minimal |
| Hidden behavioural difference in `renderStyle` when templates move | Golden snapshot from 8.A1 |

## 7. Open decisions

1. **Device back-ends (pattern 1):** only a shared registration helper (recommended, low
   risk) or a full back-end factory/plugin registry that removes the guarded imports too?
   The review proposes the factory; it is larger (touches `AppProtocol`-independent logic
   in 10 modules plus the coverage config) and gains little because the conditional import
   cannot disappear.
2. **Template location:** `../../src/mw4/assets/styles` (recommended, next to icons) or beside the
   Python in `gui/styles/`?
3. Constants read at import (recommended) or functions called at use time (easier to patch,
   marginally slower and more verbose)?
4. Do 8.A and 8.B in one go, or ship 8.A first (smaller, visible benefit)?
