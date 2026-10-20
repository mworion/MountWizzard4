# Plan – Roadmap item 6: split `AppProtocol` and group signals (A1)

Source: `../../2026-10-20_review_copilot.md`, finding **A1**, roadmap *Medium* item 6.
Status: **WP 6.1–6.6 implemented.** Decisions: 8 roles, signal grouping as in §3.2
(the `HasSignals` role is folded into `HasMessaging`: `signals`, `messageQueue`).

How to add a signal: declare it in the matching group class in `base/appSignals.py`
(`UiSignals`, `HemisphereSignals`, `ModelSignals`, `SystemSignals`) and use it as
`app.signals.<group>.<name>`. `MountWizzard4` and the test stub need no change.

Metrics after: `AppProtocol` lists 17 members (was 38) via 8 role protocols; 0 flat
signals on the app classes. Consumers narrowed to a single role where the whole class
hierarchy needs only that role: 15 modules (`HasThreadPool` 9, `HasDevices` 5,
`HasBuildPoints` 1, `HasMessaging` 1); the rest use several roles and keep `AppProtocol`.

## 1. Problem (measured)

- `AppProtocol` (`base/appProtocol.py`) lists 13 state members, 23 signals and 2 config
  methods. 106 modules type their `app` parameter with it, so every tab/device appears to
  depend on everything.
- Real usage in `src` (`app.<member>`):

  | Member | Uses | | Member | Uses |
  |---|---:|---|---|---:|
  | `config` | 94 | | `msg` (signal) | 42 |
  | `timeMgr` | 69 | | `operationRunning` | 21 |
  | `buildPoint` | 58 | | `colorChange` | 17 |
  | `mwGlob` | 47 | | `redrawHorizon` | 11 |
  | `threadPool` | 33 | | 17 other signals | 2–7 each |
  | `isOnline` | 11 | | `hipparcos`, `ephemeris`, `mainW`, … | ≤ 6 |

- Signals are a flat list on `MountWizzard4` (`mainApp.py`) and again on the test stub
  (`../../tests/unit_tests/unitTestAddOns/baseTestApp.py`), so a new signal needs three edits.
- `drawHorizonPoints` exists on both app classes but is **not** in the protocol (drift the
  protocol contract test does not catch because it only checks listed members).

## 2. Goals

1. Narrow role protocols so each consumer declares only what it needs.
2. Group the 23 signals into 4 sub-objects, mirroring the existing `MountSignals`.
3. Keep `AppProtocol` as the **composition** of the role protocols (so `MountWizzard4` and the
   test stub still satisfy it and the existing contract test keeps its meaning).
4. No behaviour change.

Non-goals: removing `app` as the injection point, changing the device-registry typing
(plan 5), changing widgets or the thread model.

## 3. Design

### 3.1 Role protocols (type-only, in `base/appProtocol.py`)

| Protocol | Members |
|---|---|
| `HasConfig` | `config`, `initConfig`, `storeConfig` |
| `HasThreadPool` | `threadPool`, `MAX_THREAD_COUNT` |
| `HasDevices` | `dReg` |
| `HasMessaging` | `msg`, `messageQueue`, `playSound` |
| `HasTime` | `timeMgr`, `ephemeris`, `hipparcos` |
| `HasMountState` | `isOnline`, `statusOperationRunning`, `operationRunning`, `mwGlob` |
| `HasBuildPoints` | `buildPoint` + build-point signals |
| `HasMainWindow` | `mainW` |

`class AppProtocol(HasConfig, HasThreadPool, …, Protocol)` – unchanged public name; consumers
migrate to the smallest protocol opportunistically. Names are provisional (see §7).

### 3.2 Signal groups
Plain `QObject` classes holding the signals, owned by the app as sub-objects:

| Group | Signals |
|---|---|
| `app.signals.ui` | `msg`, `colorChange`, `playSound`, `showImage`, `showAnalyse`, `operationRunning`, `remoteCommand` |
| `app.signals.hemisphere` | `redrawHemisphere`, `redrawHorizon`, `updatePointMarker`, `drawBuildPoints`, `drawHorizonPoints`, `buildPointsChanged` |
| `app.signals.model` | `refreshModel`, `refreshName`, `sendSatelliteData`, `updateSatellite`, `showSatellite`, `updateDomeSettings` |
| `app.signals.system` | `timebaseChanged`, `onlineModeChanged`, `hidModeChanged`, `relayChanged`, `parkChanged` |

Final grouping to be confirmed (`updateDomeSettings` and the satellite signals are the
borderline cases).

**Migration decision:** as with the dialog options in plan 7, this is a **full replacement**,
no compatibility shim (`__getattr__` forwarding would hide exactly the coupling we want to
expose). Consequence: ~190 `self.app.<signal>` sites in `src` plus the matching sites in
`tests` and the test stub change in one mechanical pass.

## 4. Work packages

| WP | Content | Effort | Risk |
|----|---------|--------|------|
| 6.1 | Add role protocols; make `AppProtocol` their composition; add `drawHorizonPoints`; extend contract test to assert `AppProtocol` members == union of role protocols and that both `MountWizzard4` and the stub satisfy **each** role protocol | 0.5 d | low |
| 6.2 | Narrow consumer annotations: low-level consumers first (`logic/*`, `base/*`, `mountcontrol`: mostly only `HasConfig`/`HasThreadPool`/`HasMessaging`), then `gui`. AST codemod proposes the minimal protocol from the members a class really uses; reviewer confirms | 1.5 d | low |
| 6.3 | Signal groups: new `base/appSignals.py` with the 4 group classes, owned by `MountWizzard4` and the test stub; `AppProtocol.signals: AppSignals` | 0.5 d | med |
| 6.4 | Codemod `app.<signal>` → `app.signals.<group>.<signal>` in `src`, then `tests` + stub; update `.connect`/`.emit` sites and `mock.patch.object(app, "msg")` style patches | 1.5 d | med |
| 6.5 | Remove the old flat signals from `MountWizzard4` and the protocol; add a drift test (every signal lives in exactly one group; protocol lists none flat) | 0.25 d | low |
| 6.6 | Enforcement + docs: update review A1 and metrics (members on `AppProtocol`, consumers per role protocol); add a short "how to add a signal" note to the docs | 0.25 d | low |

Total ≈ 4.5 days. 6.1–6.2 are safe to ship independently of 6.3–6.5; if the signal move
turns out too noisy, stop after 6.2 and the main benefit (narrow dependencies) is already won.

## 5. Verification (per WP)

- Full suite at 100 % line + branch, ruff clean, pyrefly 0 errors, suppressions not rising.
- 6.2: after narrowing, pyrefly proves each consumer only uses members of its protocol; this
  is the main safety net and the reason to do it before the signal move.
- 6.4: signal connections are not type-checked at runtime, so add a smoke test that builds
  the real `MountWizzard4` object (existing `mainApp` tests) and a test that each group
  signal can be connected and emitted once. Manual smoke test: start app, change colour
  scheme (`colorChange`), run a message (`msg`), open hemisphere (redraw signals), load a
  satellite.
- Qt quirk to remember: signals cannot be patched with `mock.patch.object(signal, "connect")`;
  tests patch the slot instead.

## 6. Risks

| Risk | Mitigation |
|------|------------|
| Large mechanical diff in 6.4 hides a real change | Pure AST codemod, idempotent, one commit; reviewer checks `git diff --stat` and a regexp-normalised diff is empty |
| Test stub and real app diverge on signal groups | Both use the same `AppSignals` class; contract test covers both |
| Signals consumed through other objects (`self.mainW.app.msg`, window `app` copies) | Codemod matches any `….<signal>.(emit\|connect)` attribute chain, not only `self.app` |
| Over-narrow protocols force constant edits when a tab needs one more member | Start coarse (8 roles); tabs that need more simply use `AppProtocol` |
| Overlap with plan 5 (`HasDevices` vs typed registry) | `HasDevices` just exposes `dReg: DeviceRegistry`; independent of how the registry is typed |

## 7. Open decisions

1. Final role-protocol names and the member split (§3.1) – is 8 roles the right granularity?
2. Final signal grouping (§3.2), especially where the satellite and dome signals belong.
3. Do 6.1–6.2 only (low risk, most of the value) or also the signal move 6.3–6.5?
   Recommendation: ship 6.1–6.2 first, decide on the signal move afterwards.
4. Order relative to plan 5: recommended **plan 5 first** (self-contained, type safety
   immediately visible), then plan 6.
