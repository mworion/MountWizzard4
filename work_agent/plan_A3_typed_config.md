# Plan A3 – typed, versioned configuration dataclasses with migration

Source: `2026-10-20_review_copilot_open.md`, finding A3 (roadmap item 2).
Status: **schema complete, call-site migration open (2026-10-23)**.
Done: infrastructure, migration hook, `AppProtocol.config: ProfileConfig`, typed top-level keys and
typed sections `MountPark`, `Setting{Update,Gui,Audio,Dome,Rack}`, `Window{Main,Analyse,Hemisphere,
Image,Simulator}` (defaults extracted from the former inline `config.get(key, default)` calls,
numbers are interchangeable int/float). `mainApp` uses attributes.
Left in `ProfileConfig.extra` (dynamic or call-site defaults): window geometry keys, tab order
dicts, `Setting{Park,Relay,Device,DeviceMount}`, `Window{Keypad,Message,Measure,Setting,...}`,
and `WindowMain` filter texts / `renameDir`.
Open: convert GUI call sites + their dict-based tests to attributes (step 2 rest), remove the dict
shim (step 4), developer docs (step 5).

## Findings (measured 2026-10-23)

- `app.config` is a plain `dict` created by `logic/profiles/profile.py::loadProfileStart`.
  `defaultConfig()` only contains `profileName` and `version` (`profileVersion = "5.0"`).
- ~438 `config[...]` / `config.get(...)` accesses in `src/mw4` (gui ≈ 400: `mainWaddon` 39 files,
  `extWindows` ≈ 40, `mainWindow` 8; `mainApp`, `profile`, `deviceRegistry`, `mountcontrol`, dome
  driver the rest).
- Every tab reads/writes its own section in `initConfig` / `storeConfig`, defaults are inline
  literals (`config.get("ParkMountAfterSlew", False)`), so defaults are scattered and the same key
  may carry different defaults in different places.
- Top-level sections: `WindowMain` (≈ 30 uses), `Window*` (Hemisphere, Simulator, Setting,
  SatelliteMap, SatelliteHor, Message, Measure, Keypad, Image, Analyse), `Setting*` (Dome, Relay,
  Park, Update, Gui, Audio, Rack, Device, DeviceMount), `MountPark`, tab sections, plus loose
  top-level keys (`topoLat`, `topoLon`, `topoElev`, `unitTimeUTC`).
- Version handling: a version mismatch **discards the whole profile** (`loadConfig` returns
  `defaultConfig()`); there is no migration.
- Device configs are already dataclasses (`driver.config`, `collectConfigFromSingleDevice` in
  `deviceRegistry.py` uses `dataclasses.fields`). This is the pattern to follow.

## Goal

One place per section that defines keys, types and defaults; one version field and one migration
hook; `app.config` accessors become typed. Persisted YAML format stays compatible (same keys), so
existing profiles load unchanged.

## Rules

- No behaviour change for existing profiles; YAML keys and nesting stay identical.
- `logic/profiles` stays Qt-free and does not import `gui` (import-linter contracts).
- Unknown keys in a profile are preserved on save (no silent data loss).
- Invalid value types fall back to the dataclass default and log a warning.
- Migrate section by section; each step keeps the suite green at 100 % coverage.
- camelCase naming, full type annotations, no leading-underscore helpers.

## Design

New module `src/mw4/logic/profiles/config.py` (Qt-free):

```python
@dataclass
class SectionBase:                      # shared helpers
    @classmethod
    def fromDict(cls, data: dict[str, Any] | None) -> Self: ...   # defaults + type coercion
    def toDict(self) -> dict[str, Any]: ...                        # asdict

@dataclass
class MountParkConfig(SectionBase):
    ParkMountAfterSlew: bool = False
...
@dataclass
class ProfileConfig:
    profileName: str = "config"
    version: str = profileVersion
    topoLat: float = 51.47
    topoLon: float = 0.0
    topoElev: float = 46.0
    unitTimeUTC: bool = True
    MountPark: MountParkConfig = field(default_factory=MountParkConfig)
    WindowMain: WindowMainConfig = field(default_factory=WindowMainConfig)
    ...
    extra: dict[str, Any] = field(default_factory=dict)   # unknown keys, round-tripped
    @classmethod
    def fromDict(cls, data: dict[str, Any]) -> Self: ...
    def toDict(self) -> dict[str, Any]: ...
```

- Field names equal the existing YAML keys (keeps files compatible; camelCase rule applies to new
  Python identifiers, persisted keys are kept as is and documented as such).
- Migration hook: `migrateConfig(data: dict, fromVersion: str) -> dict` in
  `profiles/migration.py`, a table `{ "5.0": migrate5to6, ... }` applied in order. Replaces the
  "discard on mismatch" logic in `loadConfig`; unknown/too-new versions still fall back to
  defaults.
- `profileVersion` bumps only when a migration is added; the first step introduces the
  infrastructure with an identity `5.0 → 5.0` check so behaviour is unchanged.

## Steps

### 1. Infrastructure (no consumers yet)

1. Add `profiles/config.py` with `SectionBase`, `ProfileConfig` (only `profileName`, `version`,
   `topo*`, `unitTimeUTC`, `extra`) and `profiles/migration.py`.
2. `profile.py`: `loadConfig` / `loadProfileStart` build `ProfileConfig.fromDict(migrate(...))`;
   `saveConfig` writes `config.toDict()`.
3. Compatibility shim: `ProfileConfig` implements `__getitem__`, `__setitem__`, `get`, `pop`,
   `__contains__` backed by sections + `extra`, so the ~438 existing accesses keep working while
   being migrated. Shim is removed in step 4.
4. Tests: `tests/unit_tests/logic/profiles/test_config.py`, `test_migration.py`, extend
   `test_profile.py` (round trip, unknown keys kept, wrong types → default, old/new version).

### 2. Convert sections to dataclasses (one commit per group, shim keeps rest working)

Order, smallest blast radius first:

1. `MountPark`, tab sections of `mainWaddon` (one dataclass per tab, defaults moved out of the
   `config.get(..., default)` calls).
2. `Setting*` (Dome, Relay, Park, Update, Gui, Audio, Rack) – `Setting*` consumers outside the GUI
   (`mainApp`, dome driver, `mountcontrol`) switch to attribute access.
3. `Window*` geometry sections (`WindowMain`, `WindowHemisphere`, ...) – a shared
   `WindowGeometryConfig` base where keys coincide.
4. `SettingDevice*` – keep existing device dataclasses; `ProfileConfig` holds them as
   `dict[str, dict]` validated by `deviceRegistry` (no duplicate schema).

For each group: replace `initConfig` / `storeConfig` bodies with attribute reads/writes
(`self.app.config.MountPark.ParkMountAfterSlew`), update the matching tab test, remove inline
defaults.

### 3. Type the access point

1. `AppProtocol.config` (`base/appProtocol.py`) becomes `ProfileConfig`.
2. Update `makeApp` test helpers / fixtures to build `ProfileConfig()` instead of `{}`.

### 4. Remove the shim

1. Delete dict-style methods from `ProfileConfig`; grep for remaining `config[` / `config.get(`
   in `src/mw4` (expected 0 outside `profiles/`).
2. Add a ruff/CI grep check or test (`test_noDictConfigAccess`) to keep it that way.

### 5. Docs and validation

- Update `doc/` developer docs (config structure, how to add a key, how to add a migration) and
  `2026-10-20_review_copilot_open.md` (mark A3 done, grade Architecture).
- `uv run pytest tests/unit_tests --cov` → 100 %, `uv run ruff format && uv run ruff check`,
  `uv run lint-imports`.
- Manual check: load a real pre-change `profile` YAML, save, diff – only formatting-level
  differences allowed.

## Risks

| Risk | Mitigation |
|------|------------|
| 438 call sites in ~100 files | shim + per-group migration; each step green on its own |
| Silent default drift (same key, different inline defaults today) | collect all defaults per key first (grep), resolve explicitly, note in commit |
| Profile files from users with stray types | `fromDict` coerces / falls back, logs warning |
| Future version bump loses user data | migration table, covered by tests per step |

## Out of scope

- Changing YAML key names or file layout.
- Per-device driver configs (already dataclasses).
- GUI widget `.ui` files.
