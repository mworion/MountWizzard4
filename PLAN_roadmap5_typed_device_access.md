# Plan – Roadmap item 5: typed device access on `DeviceRegistry` (A2)

Source: `2026-10-20_review_copilot.md`, finding **A2**, roadmap *Medium* item 5.
Status: **plan only, nothing implemented yet.**

## 1. Problem (measured)

- `dReg["<name>"]` string lookups in `src`: **~500** literal keys. A typo is a runtime
  `KeyError`; there is no completion and no type for the result.
- Distribution: `mount` 312, `camera` 53, `dome` 45, `hidController` 17, `plateSolve` 14,
  `power` 8, `lightPanel` 8, the rest ≤ 6 each. 195 further uses in `tests`.
- `DeviceEntry.instance` is `Any`, so everything behind it is untyped. What is accessed after
  the entry: `.instance` 114, `.signals` 105, `.obsSite` 96, `.data` 57, `.setting` 39,
  `.stat` 30, `.model` 18, others < 10.
- Dynamic keys (variable or loop name) exist and must keep working: `tabEnviron_Weather`,
  `mainWindow`, `tabSettDevice`, `devicePopupW` (about 25 sites).
- `DeviceEntry` has 12 near-identical forwarding properties, each repeating the same
  `if self.instance is None: raise` block (≈ 90 lines of boilerplate).

## 2. Goals

1. `dReg.mount`, `dReg.camera`, … return a **typed** `DeviceEntry[<DeviceClass>]`, so
   `dReg.mount.instance.obsSite` is checked by pyrefly and completed by the IDE.
2. String lookups stay for the genuinely dynamic cases only.
3. Remove the `DeviceEntry` boilerplate.
4. No behaviour change; config keys (`SettingDevice`, device names) unchanged.

Non-goals: changing how devices are created, renaming device keys, touching the
`signalsToName` mechanism, splitting `AppProtocol` (that is plan 6).

## 3. Design

### 3.1 Generic entry
`DeviceEntry` becomes `Generic[T]` (Python 3.12 syntax: `class DeviceEntry[T]`).
`instance: T | None`. The forwarding properties stay (they are used 400+ times) but are
generated from one helper `requireInstance()` that raises the same `AttributeError` as today,
so each property is one line and the message text is unchanged.

### 3.2 Typed attributes on the registry
`DeviceRegistry` gets one typed attribute per spec entry, filled by `addDevices`:

```python
class DeviceRegistry(QObject):
    mount: DeviceEntry[MountDevice]
    camera: DeviceEntry[Camera]
    dome: DeviceEntry[Dome]
    ...
```

- The internal `self.d: dict[str, DeviceEntry[Any]]` stays for iteration (`configurable()`,
  `realDrivers()`, config collect/write); the attributes point at the same objects.
- `deviceSpec` stays the single source of truth; a test asserts that every spec name has a
  matching attribute and vice versa (prevents drift).
- `"refraction"` has `instance=None` today → `DeviceEntry[None]`.
- `onlineWeather` is added by the test stub only → test-side concern, see WP 5.4.

### 3.3 Keep `__getitem__` for dynamic keys
Add `@overload __getitem__(self, name: Literal["mount"]) -> DeviceEntry[MountDevice]` etc.,
plus the fallback `__getitem__(self, name: str) -> DeviceEntry[Any]`. Result: old literal
call sites become typed for free, and dynamic ones still work. The overload list is generated
by hand once (20 devices) and guarded by the same drift test.

Decision: **attributes are the preferred form for new/migrated code; the `Literal`
overloads remain as a safety net** so migration can be incremental and no shim is needed.

## 4. Work packages

| WP | Content | Effort | Risk |
|----|---------|--------|------|
| 5.1 | `DeviceEntry[T]` + `requireInstance`, shorter properties; tests for every property incl. the `None` and "no framework" error paths | 0.5 d | low |
| 5.2 | Typed attributes + `Literal` overloads on `DeviceRegistry`, drift test | 0.5 d | low |
| 5.3 | Migrate `src`: literal `dReg["x"]` → `dReg.x` (mechanical codemod, AST-based, per package: `mountcontrol`/`logic`/`base` first, then `gui`). Dynamic lookups untouched | 1 d | low/med |
| 5.4 | Migrate `tests` (195 uses) + `baseTestApp` stub (it builds the registry itself and adds `onlineWeather`) | 0.5 d | low |
| 5.5 | Fix pyrefly findings that the new types reveal (expected: some `Optional` narrowing and attribute errors that were hidden behind `Any`); lower suppressions where possible | 1 d | med |
| 5.6 | Enforcement: ruff `custom` is not available, so add a small test that greps `src` for `dReg\["literal"\]` and fails on literals (dynamic keys allowed). Update review (A2 done, metrics) | 0.25 d | low |

Total ≈ 3.5–4 days. 5.1 and 5.2 are independent of each other; 5.3 depends on 5.2.

## 5. Verification (per WP)

- Codemod runs produce a diff that is purely `dReg["x"]` → `dReg.x`; reviewed by
  regenerating with `git diff --stat` and re-running the codemod (idempotent).
- Full suite at 100 % line + branch, ruff clean, **pyrefly: 0 errors** and the suppression
  count (54) must not rise.
- Tests that patch `app.dReg["mount"]…` keep working because the attribute and the dict
  entry are the same object; add one test that proves this identity.
- Manual smoke test: start app, open device settings, connect/disconnect a simulated device,
  open mount tabs.

## 6. Risks

| Risk | Mitigation |
|------|------------|
| Tests replace `dReg.d[...]` entries after creation → attribute points to the old object | Make the typed names read-only properties backed by `self.d` instead of copied attributes (small cost, no drift); decide in 5.2 |
| Typing the instance reveals many latent pyrefly errors | WP 5.5 is explicitly budgeted; fix or narrow, do not add `type: ignore` |
| Circular imports (registry already imports every device class) | Types come from the existing imports; no new imports needed |
| Merge conflicts with plan 6 (both touch `self.app.…` lines) | Do plan 5 first; the codemod is cheap to re-run on top of other changes |

## 7. Open decisions

1. Attributes as **properties backed by `self.d`** (recommended, no drift) or plain
   attributes set in `addDevices`?
2. Keep the `Literal` overloads permanently, or remove them once all literal sites are
   migrated (recommended: keep, they are harmless and protect third-party/dynamic code)?
3. Rename `DeviceEntry.instance` to something shorter? (Recommended: **no**, 114 uses, no gain.)
