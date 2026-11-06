# PySide6 slots and threading implementation plan

Reviewed: 2026-11-06. The findings and recommendations below guided implementation.

Implementation status: Phases 1-3 are implemented. Phase 4 receiver coverage is implemented
for the reviewed P2/P3 surfaces; final verification remains in progress. Phase 5 documentation
is updated and full validation remains pending.

## Recommendation

Use `@Slot(...)` on application-defined signal receiver methods belonging to `QObject`
instances. First establish receiver ownership for plain Python GUI helpers, then decorate
their receivers. Prioritize worker/device-to-GUI boundaries over same-thread button handlers.

Do not decorate every method, convert the pure logic layer to Qt, or replace the existing
`QThreadPool` architecture. A decorator is not a thread switch: ordinary Python calls still
execute in the calling thread.

## Review findings

### Existing architecture

- `mainApp.py:38-39` creates the shared pool. `base/tpool.py:92-120` executes jobs and emits
  result, error and finished signals from pool threads.
- `WorkerSignals` is a `QObject`, but `Worker` is a `QRunnable`. The existing `@Slot()` on
  `Worker.run()` is the only slot decorator found outside generated widgets. It does not
  establish affinity for the functions called by `run()` or for result receivers.
- `base/tpool.py:75-90` connects callbacks using the default connection type. Worker callback
  types are deliberately generic, so slot signatures must be checked against actual signals.
- `gui/mainWaddon/tabAddon.py:4` is a plain Python base. The 22 addons constructed in
  `gui/mainWindow/mainWindowAddons.py:37-60`, including the `SatData` subclasses, therefore
  lack their own Qt receiver affinity. Their constructors generally do not initialize a base.
- `gui/extWindows/image/imageTabs.py:28` is another plain Python receiver class.
- Many windows already inherit `MWidget` and therefore have QObject affinity.
  `ModelData`, `MountDevice`, `AudioManager`, `DeviceRegistry`, `MountWizzard4` and
  `SettDevice` are also already QObjects.
- No application `moveToThread()` calls or dedicated `QThread` implementation were found.
  Pool jobs, INDI queue processing and WebSocket callbacks are relevant emission contexts.
- Static inventory found 565 `.connect(...)` call sites across 82 source files after excluding
  the two socket connections; these include generic connection helpers, loop-based connections
  and signal forwarding, not 565 distinct methods needing decoration. There are 23 application
  `resultMethod` / `finishedMethod` keyword sites across nine files, plus two in pool helpers.
  Eleven receiver expressions are lambdas and 23 are call expressions, principally partials.
  Variable-held callbacks also need inspection. Generated `gui/widgets` files were excluded.

### Confirmed worker-body violation

`gui/mainWaddon/tabSat_Track.py:185-192`:

`showSatPasses()` schedules `runnerShowSatPasses()` in the pool. That runner directly calls
`clearTrackingParameters()` (`:140-147`), which sets widget text, enabled state and styling.
This is off-thread GUI access regardless of how result callbacks are delivered.

Move the GUI reset to the accepted-start GUI path, leaving calculations in the worker.
Preserve the current behavior for absent satellites and rejected starts while a worker is busy.
Decorating `clearTrackingParameters()` would not fix its direct call from the runner.

### Worker-side graphical resource creation

`gui/extWindows/video/videoBase.py:58-71,74-96`:

`runnerVideo()` calls `sendImage()`, which constructs `QPixmap.fromImage(...)` in the pool.
Pixmap threading support is platform-dependent; this is not evidence of a crash on this Mac.
Prefer emitting a detached `QImage` or owned frame data and creating/scaling the `QPixmap`
in the GUI receiver. Preserve the existing `None` stop/clear behavior.

### Missing registration is not proof of wrong-thread execution

Qt for Python recommends decorating receiver methods and documents affinity behavior for
QObject slots with AutoConnection / QueuedConnection:

<https://doc.qt.io/qtforpython-6/tutorials/basictutorial/signals_and_slots.html>

A read-only probe using the installed PySide6 6.12.0 and the repository's `Worker` delivered
all eight tested callbacks on the application thread: decorated/undecorated QObject methods,
decorated/undecorated plain-class methods, a lambda, a partial, and explicitly queued plain
and lambda receivers. All connections were created on the application thread.

This demonstrates that existing binding-generated proxies/dynamic registration can already
queue these connections. It does not give plain classes QObject ownership, guarantee behavior
when connections are created elsewhere, or prove every application path is safe.

Treat missing decorators as explicit-registration and ownership hardening, not as a claim that
all current callbacks run in the pool. The satellite direct call is a separate confirmed bug.

## Slot and connection scheme

| Receiver / context | Scheme |
| --- | --- |
| Existing QObject or widget, application-defined receiver | Add `@Slot(...)` with the consumed signal argument types. |
| Plain GUI addon receiving worker/device notifications | Make it a GUI-owned QObject first, then decorate bound receiver methods. |
| Pure calculation, parser, FITS core, profile or database foundation | Keep Qt-free; no slot decorators. |
| Worker entry point or ordinary helper called directly | No decorator needed for threading. Keep computation in the pool. |
| Qt built-in slot such as progress-bar `setValue` or event-loop `quit` | Reuse it; no Python wrapper solely to add a decorator. |
| Signal-to-signal forwarding | Keep forwarding; verify payload and delivery at the final receiver. |
| GUI-local button lambda/partial | Keep if genuinely local; prefer a named receiver when registration/ownership matters. |
| Worker/device lambda, partial or free callback that touches GUI | Prefer a directly connected, decorated bound method on the GUI-owned receiver. |
| Receiver virtual override such as `closeEvent` / `keyPressEvent` | Do not decorate merely because Qt calls it. |

Connection policy:

- Keep AutoConnection for registered QObject receivers where same-thread synchronous behavior
  is intentional. It queues cross-thread delivery based on receiver affinity.
- Use explicit QueuedConnection for asynchronous worker-to-GUI handoffs when deferral is part
  of the contract. Do not force it globally in `Worker.rebind`: that helper also supports
  built-in slots, signal forwarding and generic callbacks.
- Retain `ModelData.startSlew`'s existing QueuedConnection
  (`logic/controllers/model/modelRun.py:56`). It also prevents synchronous re-entry.
- Do not use DirectConnection to GUI receivers or BlockingQueuedConnection for these paths.
- Create GUI receivers and establish their connections on the application thread.
- QObject affinity does not make shared dictionaries, NumPy arrays or Python flags thread-safe.
  Review publication and lifetime at changed boundaries without redesigning unrelated drivers.

Signature policy:

- Match emitted/consumed arguments, not just type annotations: `@Slot()`, `@Slot(str)`,
  `@Slot(int)`, `@Slot(bool)`, `@Slot(int, str)` and so on.
- Use `@Slot(object)` for generic `Signal(object)` payloads. Path, NumPy, Skyfield and
  application-class payloads need compatible Python-object signatures, checked at runtime.
- A zero-argument slot may intentionally discard a signal payload. Preserve this convention
  for mount result notifications and GUI refresh handlers.
- Preserve argument-dropping behavior for handlers shared by button signals, value-change
  signals and no-argument refresh notifications. Introduce overloads only if actually needed.
- `DeviceRegistry` and `SettDevice` device receivers currently accept `*args` and use
  `sender()`. Register the consumed `str` signature and preserve sender-based dispatch.
- Do not add `result=...` indiscriminately; current signal handlers generally return `None`.

## Priority worklist

Paths in the table are relative to `src/mw4`.

| Priority | Surface and evidence | Planned work |
| --- | --- | --- |
| P0 | `gui/mainWaddon/tabSat_Track.py:140-201` | Remove the worker's direct GUI reset; establish QObject ownership for SatTrack; decorate result/finished receivers. |
| P1 | `gui/mainWaddon/tabAddon.py:4`, `gui/mainWindow/mainWindowAddons.py:37-60` | Introduce GUI-owned QObject addon lifecycle and initialize all 22 concrete constructors, including SatSearch/SatTrack through SatData. |
| P1 | `gui/extWindows/image/imageTabs.py:28-65`, `logic/controllers/imageWindow/photometry.py:111-156,179-224` | Make ImageTabs a child QObject of ImageWindow. Decorate image/HFR/tilt/roundness/aberration/source/background receivers; keep photometry core computation out of GUI slots. |
| P1 | `logic/controllers/model/modelRun.py:55-65,76-108,201-205,222-234` | Decorate camera/solve/slew receivers and exposure-timer callback; retain queued slew and main-thread model state/timer ownership. |
| P1 | `mountcontrol/mount.py:88-104,143-293` | Decorate result callbacks, `startupMountData` and relevant timer receivers. Especially cover `resultCyclePointing`, which starts the settling timer. |
| P1 | `gui/mainWaddon/tabAlmanac.py:186-209`, `tabTools_Rename.py:125-165`, `tabSat_Track.py:185-201` | Register twilight result, rename result/finished, and satellite result/finished callbacks after addon ownership migration. |
| P1 | `gui/mainWindow/mainWindow.py:61-65`, `gui/extWindows/image/imageW.py:130-134,292,332` | Decorate mount/device/remote status and image/photometry/camera/solver receivers on existing widgets. |
| P1 | `gui/extWindows/keypadW.py:109-114`, `gui/mainWaddon/tabMount.py:19-24`, `tabMount_Move.py:144-146`, `tabRelay.py:28` | Register WebSocket, HID and relay GUI receivers; cover driver emissions from background loops. |
| P1 | `gui/extWindows/downloadPopupW.py:40-42,59-67`, `uploadPopupW.py:71-73,203-228` | Decorate progress/status/color/result/finished receivers; preserve modal loop and close scheduling behavior. |
| P1 | `base/audioManager.py:28-33,40-55` | Decorate `playSound`; replace five device-signal lambdas with named QObject slots so QSoundEffect creation has explicit ownership. |
| P1 | `deviceRegistry.py:86-91,334-348`, `gui/extWindows/setting/tabSettDevice.py:58-73,144-155` | Decorate device connection/disconnection receivers; preserve sender mapping and GUI/device state updates. |
| P1 | `mainApp.py:45,68,103-108` | Register message-queue and operation-state receivers without changing message ordering. |
| P1 | `gui/extWindows/video/videoBase.py:47,58-71,131-138` | Register the frame receiver and move platform-dependent pixmap creation to the GUI thread. |
| P2 | `gui/mainWaddon/tabModel*.py`, `tabMount_Sett.py`, `tabSat_Search.py`, `tabSat_Track.py`, `tabPower.py` | Register remaining device/model/data-loading receivers after shared addon migration. Include variable-held callbacks in ModelManage. |
| P2 | `gui/extWindows/hemisphere/*.py`, `satelliteHorW.py`, `satelliteMapW.py`, `simulator/*.py` | Register external display receivers; add targeted QObject ownership to plain simulator helpers receiving notifications. |
| P2 | `logic/drivers/environment/seeingWeather.py:84-111`, `sensorWeatherOnline.py:111-138` | Give weather completion receivers an explicit QObject boundary; register sendStatus and timer entry points without moving HTTP work onto GUI thread. |
| P2 | `gui/extWindows/setting/tabSettMount.py`, `tabSettDome.py`, other settings helpers | Establish QObject ownership where needed, then register firmware/device notification receivers and local settings handlers. |
| P3 | Other windows, native dialogs, timers and GUI-local callbacks | Complete the receiver-only decorator sweep; keep built-in slots and local lambdas/partials where appropriate. |

Additional boundary review, not automatic QObject conversion:

- `logic/drivers/frameworks/deviceFacade.py:13` is plain Python. Do not turn every device
  facade/backend into a QObject just to decorate a few timer handlers.
- `logic/drivers/dome/dome.py` owns a settling timer through a plain facade; identify the
  timer-facing receiver boundary separately from polling/device operations.
- Plain `Remote`, `KeyPad`, `PlateSolve`, `KMRelay`, weather drivers, `Geometry` and
  `MountTimeConn` contain Qt-facing entry points. Classify their connection context first.
  Local socket/timer callbacks are not automatically cross-thread faults.
- `measureCSV.py` and `measureRaw.py` already inherit QObject; their timer handlers can use
  decorators without ownership refactoring.
- `AstroObjects.runnerProcessSource()` invokes a supplied callable; examine that callable
  as well as the runner. `FileHandler` and `Photometry` can remain plain worker-facing
  adapters with QObject signal containers: their GUI consumers need ownership, not their
  pure computation methods.

## Implementation phases

### 1. Pin down dispatch and payload contracts

Add module-scoped pytest-qt fixtures and real-pool integration cases to the existing mirrored
unit-test modules. Establish a baseline for decorated, dynamically registered and plain
receivers, then test the actual callback families rather than relying on a generic probe.

For each changed connection record sender, emission context, payload, receiver owner,
connection type and consumed arguments. Include connect/disconnect symmetry and callbacks
installed in loops or held in variables. Do not create a new generic signal-routing framework.

### 2. Establish GUI receiver ownership

Make `TabAddon` a QObject base with optional parent initialization. Update all 22 addon
constructors to initialize it with their main window before accessing signals or widgets.
Keep the SatData inheritance chain single-QObject and preserve lifecycle hooks.

Make `ImageTabs` a QObject initialized with its image-window parent. Add parent ownership
to other Qt-facing helper classes only in the batches that need it. Extend fixtures that
currently use plain mocks so ownership tests use actual Qt parents; avoid production
fallbacks to hide invalid parents.

### 3. Fix P0 and register P1 thread boundaries

Move the satellite reset out of the runner. Add receiver decorators and deliberate queued
handoffs where needed. Address audio lambda adapters and video frame publication in this
batch. Preserve timers, model progression, cancellation, deferred closing and error recovery.

Do not replace every pool connection with QueuedConnection or move computations into slots.
Existing `Worker.run()` exception logging and finished-on-error behavior must remain intact.

### 4. Complete P2/P3 receiver coverage

Apply the same ownership/signature scheme to the remaining application-defined receivers.
Inspect variable-held callbacks, helper methods called by runners and repeated window setup.
Do not decorate unrelated helpers or modify generated files.

Keep pure controllers and foundations free of new Qt imports. Existing import-linter worker
exceptions for ModelData/Photometry do not justify widening Qt dependencies into their cores.

### 5. Verify and document the convention

Extend contributor documentation with the receiver/ownership rule, connection policy and
worker prohibition on GUI access. Finish Ruff formatting/linting and import-layer validation.
Run targeted modules for each batch, then the overall package with the configured 100%
branch-aware coverage threshold as the final implementation check.

## Acceptance criteria and regression cases

- All changed GUI/device completion receivers are registered slots on initialized QObjects.
  Inspect their metaobjects before connecting, so dynamic registration cannot conceal omissions.
- Real pool jobs execute on a non-GUI thread; selected production receivers execute on their
  QObject thread and, for GUI objects, `QApplication.instance().thread()`.
- Use event-loop-aware waits such as `qtbot.waitUntil` / `waitSignal`. Calling `worker.run()`
  synchronously or only waiting with `pool.waitForDone()` does not verify queued delivery.
- Satellite calculations never invoke the GUI reset from the worker, including empty input,
  busy-worker rejection, successful completion and failure.
- Image load and photometry emissions update views on the GUI thread with payloads intact.
  Cover repeated processing, stale queued notifications and closing the owning window.
- Mount pointing completion starts settling timers on their owning thread. Model camera/
  solver notifications preserve progressive/normal/conservative timing, pause and cancellation.
- Reused workers do not duplicate callbacks, misroute old results or lose finished-on-error
  GUI recovery. Preserve the current busy-lock contract.
- Named audio adapters retain configured sound selection and receive no foreign-thread
  QSoundEffect construction. DeviceRegistry/SettDevice retain valid `sender()` dispatch.
- Video frames are owned across the queued handoff; GUI-side pixmap creation handles normal
  frames and the `None` clear sentinel. Add Windows cases and run them on Windows.
- Open/close/reopen and object destruction do not leave live callbacks targeting deleted
  widgets. Disconnect is not assumed to cancel events that are already queued.
- Optional diagnostic run:
  `QT_LOGGING_RULES="qt.pyside.libpyside.warning=true" uv run pytest <changed modules>`.
  Investigate application receiver-registration warnings; third-party warnings are not proof
  that this project's slots are missing.
- Finish with `uv run ruff format --check src tests`, `uv run ruff check src tests`,
  `uv run lint-imports`, and `uv run pytest --cov --cov-report=term-missing`.
  Do not lower coverage thresholds, add `pragma: no cover`, or broaden Qt layer exemptions.

## Scope limits

This plan is a receiver/thread-affinity migration, not a full concurrency redesign.
It does not promise to eliminate all shared-data races, add new worker scheduling features,
change mount/device protocols, alter UI behavior, or edit generated widget modules.
Any broader synchronization issue discovered during implementation should be reported
separately unless directly required to make a changed boundary correct.
