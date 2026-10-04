# Plan – Rec 12 (C2): Atomic `storeConfig` for Config Sections

**Date:** 2026-09-30
**Source:** [2026-09-29-status-review.md](2026-09-29-status-review.md), rec 12,
finding C2 (from [2026-09-26-review.md](2026-09-26-review.md))
**Scope:** the `storeConfig` methods that empty a config section before they
fill it again. `tabSettUpdate.py` is already done (rec 5).

---

## 1. Finding

> `storeConfig` pattern `config[x] = {}` then refill: an exception half way
> leaves an empty section that is then saved. Build the dict locally and
> assign once.

Most of these methods are also connected to widget signals (`textChanged`,
`clicked`, `valueChanged`). So one exception in a slot can leave an empty or
half-filled section in `app.config`, and the next profile save writes it to
disk.

---

## 2. Inventory (`src/mw4`, excluding `gui/widgets`)

| # | File / method | Section | Pattern | Other writers | Kept references |
|---|---------------|---------|---------|---------------|-----------------|
| 1 | `gui/mainWaddon/tabMount_Park.py:43` `storeConfig` | `MountPark` | `= {}` then fill | none | none (`get` per call) |
| 2 | `gui/extWindows/setting/tabSettRelay.py:42` `storeConfig` | `SettingRelay` | `= {}` then fill | none (`tabRelay` only reads) | none |
| 3 | `gui/extWindows/setting/tabSettAudio.py:48` `storeConfig` | `SettingAudio` | `= {}` then fill | none (`audioManager` only reads) | none |
| 4 | `gui/extWindows/setting/tabSettMount.py:71` `storeConfig` | `SettingRack` | `= {}` then fill | none | none |
| 5 | `gui/extWindows/setting/tabSettGui.py:59` `storeConfig` | `SettingGui` | `= {}` then fill | none (`mainWindow.initConfig` only reads) | none |
| 6 | `gui/extWindows/setting/tabSettPark.py:49` `storeConfig` | `SettingPark` | `= {}` then fill | none (`tabMount_Park` only reads) | none |
| 7 | `gui/mainWindow/mainWindow.py:126` `storeConfig` | `WindowMain` | `.clear()` then refill | **~18 main tabs** write into `app.config["WindowMain"]` in their `storeConfig` (called through `mainWindowAddons.storeConfig()`) | none |

Checked and **not** part of C2:

- `mountcontrol/geometry.py:69-71` only creates `SettingDome` if it is missing
  and never empties it. `Geometry.cfg` and `Dome.cfg` keep a **reference** to
  this dict, so `SettingDome` must never be replaced. `tabSettDome.storeConfig`
  already updates it in place. No change.
- `mainWindow.initConfig:109-110` only creates `WindowMain` if it is missing.
  No change needed, but it is changed to `setdefault` together with #7 for
  symmetry.

---

## 3. Solution

Two rules, depending on who owns the section:

**Rule A – one owner (#1–#6): build locally, assign once.**

```python
def storeConfig(self) -> None:
    config = {
        "ParkMountAfterSlew": self.mainW.ui.parkMountAfterSlew.isChecked(),
    }
    self.app.config["MountPark"] = config
```

For loops, fill a local `config: dict[str, Any] = {}` and assign it at the
end. If a widget read raises, the old section is unchanged. This keeps the
current behaviour of dropping old keys, because the section is still replaced
as a whole (`test_storeConfig_overwrites_previous_config` in
`test_tabSettRelay` stays valid). This is safe because no one keeps a
reference to these dicts.

In `tabSettGui` and `tabSettMount`, the method also writes device configs
(`hidController`, `mount`). Only the dict part changes; the assignment goes
right after the dict is built, **before** the device config writes, so the
order of side effects (`hidModeChanged.emit()` last) is kept.

**Rule B – shared section (#7 `WindowMain`): update in place, never clear.**

"Build locally" does not work for `WindowMain`, because the main tabs write
into `self.app.config["WindowMain"]` after `MainWindow.storeConfig` prepared
it. Change:

```python
def storeConfig(self) -> None:
    config = self.app.config
    config["profileName"] = self.ui.profileName.text()
    config = config.setdefault("WindowMain", {})
    self.getPositionWindow(config)
    ...
```

- The `.clear()` goes away: an exception in any tab leaves the other keys at
  their last saved value instead of losing them.
- Trade-off: keys of tabs that no longer exist stay in the profile. All readers
  use explicit keys (`get` / `setTabAndIndex`), so old keys are harmless.
- `initConfig` uses `setdefault("WindowMain", {})` in the same way.

Rejected alternative for #7: take a copy before `clear()` and restore it in an
`except` block. It adds error handling to one method only, and it catches
exceptions that should reach the worker / Qt log. Rule B is simpler.

---

## 4. Steps

1. **Rule A** in `tabMount_Park.py`, `tabSettRelay.py`, `tabSettAudio.py`,
   `tabSettMount.py`, `tabSettGui.py`, `tabSettPark.py` (type the local dict
   as `dict[str, Any]` where it is filled in a loop).
2. **Rule B** in `mainWindow.py` (`storeConfig`, `initConfig`).
3. **Tests** (in the mirrored `tests/unit_tests/...` modules):
   - For each Rule A module, one new test: pre-fill the section with a
     sentinel dict, make one widget read raise (`mock.patch.object(...,
     side_effect=RuntimeError)`), call `storeConfig` inside
     `pytest.raises(RuntimeError)`, and assert that the section is still the
     sentinel (atomicity).
   - Existing tests that assert the section is created or overwritten stay as
     they are.
   - `test_mainWindow`: the two existing `storeConfig` tests stay (with and
     without `WindowMain`). New test: a key written before is still present
     after `storeConfig` (no clear). New test: an exception in
     `mainWindowAddons.storeConfig` leaves the earlier `WindowMain` keys in
     place.
4. **Verification:**
   - `grep -rnE 'config\[[^]]+\]\s*=\s*\{\}|WindowMain"\]\.clear' src/mw4`
     → only `geometry.py:70` (create if missing) is left.
   - `uv run ruff format src tests`, `uv run ruff check src tests` → clean.
   - `uv run pytest tests/unit_tests -n auto --cov=mw4` → all passed, 100 %.
5. **Status review:** C2 → ✅ Fixed, rec 12 → ✅ Done; add a row to section 7.

---

## 5. Risks

| Risk | Mitigation |
|------|------------|
| A reader keeps a reference to a Rule A section and misses the new dict | The grep in section 2 shows only `get(...)` per call for sections #1–#6. `SettingDome` (which is referenced) is not changed. |
| Old `WindowMain` keys pile up in profiles | Harmless (explicit key lookups); the section is small. |
| Behaviour change in the `hidController` / mount config writes | Not touched; only the dict part of `tabSettGui` / `tabSettMount` changes. |

---

## 6. Effort

Small (S): 7 source files, a few lines each; about 8 new tests.

