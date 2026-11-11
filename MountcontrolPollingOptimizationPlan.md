# Mountcontrol Connection and Polling Optimization Plan

## 1. Current state

Every command batch creates a new `Connection` object, which opens a new `QTcpSocket`,
sends, reads, and closes (`connection.py`: `buildClient` -> `sendData` -> `receiveData` ->
`closeClientHard`).

| Cyclic task | Period | Code | Commands | Connections |
|---|---|---|---|---|
| pointing | 0.5 s | `obsSite.pollPointing` | `:GS# :GDUT# :TLESCK# :Ginfo# :GaE#` | 1 |
| settings | 3 s | `setting.pollSetting` | 27-30 commands in one batch (`cs1+cs2+cs3`) | 1 |
| mount up | 1 s | `mountTimeConn.runnerMountUp` | ping + raw TCP connect/shutdown | 1 (no data) |
| clock diff | 1 s | `mountTimeConn.runnerPollSyncClock` | `:GJD1#` | 1 |
| collect | 1 s | `mountData.collect` | local only | 0 |
| clock sync | 30 s | `syncClock` | `:NUtim`/`:SUDT` | 1 |

Total: about 4.3 connections/s (about 15,000/h), plus one-off connections for each setter, `getFW`,
`getLocation`, model and satellite commands.

### Redundancies found

| Item | Problem | Action |
|---|---|---|
| `:GJD1#` every 1 s | JD is already in `:Ginfo#` field 6 (every 0.5 s) | Remove the poll. Compute `timeDiff` from the Ginfo JD plus the measured round-trip time of that batch |
| `runnerMountUp` TCP connect every 1 s | Extra connection that only checks reachability | Derive `mountIsUp` from the persistent connection state and the Ginfo success. Keep ping only while disconnected (reconnect probe) |
| `:GS#` (sidereal time) at 0.5 s | Derivable from JD and longitude, otherwise slow-changing | Move to the 3 s set, or compute locally (decide in phase 3) |
| `:GDUT#` (UT1-UTC) at 0.5 s | Changes about once per day | Move to the 3 s set, next to `:GDUTV#` |
| `:TLESCK#` at 0.5 s | Satellite-data status, slow-changing | Move to the 3 s set |
| `:Ginfo#` status field vs `:Gstat#` | Status is in Ginfo already | No separate status query; ensure none exists |
| `:Gdat#`/`:GDUTV#` etc. in the 27+ command 3 s batch | Single oversized batch, above the about 5 commands/round guideline | Split into 3 independent sub-batches at command boundaries, phase-staggered |
| `:Gtg#`, `:GMAC#`, `:GWOL#`, `:GINQ#`, `:GT#`, `:Gh#`, `:Go#` | Static or near-static | Candidate for a slow set (30 s or on demand). Confirm per command with the user before removal |

The pointing result must stay unchanged for consumers; `parsePointing` takes its values from Ginfo
plus the slow cache.

## 2. Target architecture

### 2.1 `connection.py`: persistent link and single communication worker

- New class `MountLink(QObject)`, owned by `MountContext` and thus shared by all mountcontrol modules.
  - One persistent `QTcpSocket` with `LowDelayOption=1`, living in a dedicated thread. This is a worker per the repo rule: the variable is `workerLink`, the method `runnerLink`.
  - One outstanding batch at a time.
  - Priority queue with three levels: `interactive` (setters, slews, `communicateRaw`), `fast` (0.5 s poll), `slow` (3 s sets, setting polls).
  - Coalescing: a poll is never queued twice. A missed cycle is skipped (monotonic clock).
  - Whole-batch deadline (default 2 s for telemetry, configurable), not a per-read restart.
- Public API stays compatible: `Connection(parent).communicate(cmd, responseCheck)` and `communicateRaw(cmd)` remain. They become thin facades that submit to `MountLink` and block for the result, so `setting`, `obsSite`, `model`, `satellite`, `firmware` and `tabMount_Command` need only minimal edits.
- Connection states: `disconnected`, `connecting`, `ready`, `failed`. A signal `connectionChanged(bool)` drives `mountIsUp`.
- On every (re)connect:
  1. send `:U2#` once (high precision is per session, so `obsSite.setHighPrecision` at startup is removed);
  2. reset the parser;
  3. mark the telemetry cache stale.
- On timeout, EOF or framing error:
  1. fail the pending transaction;
  2. close the socket and discard parser state;
  3. reconnect with bounded backoff (1, 2, 4, 8 s, max 10 s).
  - No command is ever retried or resent. A timeout or error is reported as failed; cyclic polls simply run again in the next cycle.

### 2.2 Streaming reply parser

- Replace the current chunk counting (`numberOfChunks`, `minBytes`) with a per-command reply spec built from the existing tables:
  - `COMMAND_A` / `COMMAND_P`: no reply;
  - `COMMAND_B`: fixed-length reply without `#`, consumed exactly;
  - default: `#`-terminated.
- Leftover bytes stay in the buffer for the next transaction.
- The `(suc, response, numberOfChunks)` return contract is kept, so the parsers keep working.
- Add `:Gstat#` (exact case) to `COMMANDS` if used; do not use `:GSTAT#`.
- Keep the `\xdf` -> `*` replacement.

### 2.3 Cyclic schedule (in `mount.py`, timers stay, targets change)

| Set | Period | Content |
|---|---|---|
| fast | 0.5 s | `:Ginfo#` and `:GaE#` (batch of 2) |
| slow A | 3 s, phase 0 | `:GS# :GDUT# :TLESCK# :GDUTV# :Gdat#` and the former settings, part 1 (at most 5 per batch) |
| slow B | 3 s, phase 1.5 s | settings, part 2 |
| slow C | 3 s, phase 0.75 s | weather and config, part 3 |
| event | on connect | `:U2#`, firmware, location |
| 30 s | `syncClock` | unchanged, but through `MountLink` |

- A telemetry cache in `MountContext` keeps the latest parsed result with a timestamp; consumers read it.
- `Setting.parseSetting` is split into per-sub-batch parsers. `validateSetting` and `WATCHED_FIELDS` change-detection are kept and applied per sub-batch.
- Clock diff: `mountTimeConn` consumes the Ginfo JD plus the RTT reported by `MountLink` (same 25-sample moving average).
- Remove `runnerMountUp` TCP connect. Keep ping only while disconnected.

### 2.4 Inventory of all non-cyclic mount traffic

Every user of `Connection` was checked (`plateSolve.py` and `remote.py` do not talk to the mount; they only match on `communicate`/`Connection` names).

| Caller | Commands | Trigger | Reply type | Link class |
|---|---|---|---|---|
| `satellite.getTLE/setTLE` | `:TLEG#` (multi-chunk), `:TLEL0..2#` (`responseCheck="V"`) | user / startup | chunked, 1-char | bulk |
| `satellite.calcTLE` | `:TLEGAZ{jd}#:TLEGEQ{jd}#:TLEP{jd},{dur}#` | user, track calc | multi-chunk | bulk |
| `satellite.slewTLE` | `:TLES#` | user | `#`-terminated | interactive |
| `satellite.statTLE` | `:TLESCK#` | user and in cyclic batch today | `#`-terminated | slow set |
| `satellite.startProgTrajectory`, `addTrajectoryPoint`, `preCalcTrajectory` | `:TRNEW…#` (`"V"`), many `:TRADD{az},{alt}#` in one batch, `:TRP#` / `:TRREPLAY#` | user, track calc | N one-char replies, one chunked reply | bulk |
| `satellite.getTrackingOffsets` | `:TROFFGET1..4#` | user and GUI refresh | 4 replies | interactive |
| `satellite.set/add/clearTrackingOffset` | `:TROFFSET`, `:TROFFADD`, `:TROFFCLR#` (`"V"`) | user | 1-char | interactive |
| `model` | `:getalst#`, `:getain#`, `:getalp{n}#`, `:modelnamN#`, `:modelnam{n}#` (multi-chunk reads); `:delalig#`, `:delalst{n}#`, `:modelsv/ld/del{name}#` (`"1"`); `:newalig#:newalpt…#:endalig#` (`"V"`, large batch) | user | chunked / 1-char | bulk (reads, programming) or interactive |
| `firmware.poll` | `:GVD# :GVN# :GVP# :GVT# :GVZ#` | startup | 5 `#` replies | slow, once |
| `obsSite` setters and commands | slew, stop, park, unpark, track, flip, `:Sd/Sr/Sa/Sz#`, location, `:Sdat#`, … | user | 1-char or `#` | interactive |
| `setting` setters | tracking, limits, refraction, UDP, WOL, … | user | 1-char | interactive |
| `mountTimeConn.syncClock` | `:SCV…#`, `:SC…#` (clock set) | 30 s / user | 1-char | interactive |
| `tabMount_Command` | free text via `communicateRaw` | user | any | interactive |

Handling rules:

- Three link classes with strict priority: **interactive** > **bulk** > **cyclic** (fast, then slow).
- A bulk transaction (e.g. `:TRADD` batches, `:newalpt` programming, `:TLEG#`) owns the link for its duration. The cyclic scheduler pauses, coalesces the missed polls, and does not queue them. The per-transaction deadline is scaled by the number of commands and chunks, not the 2 s telemetry limit.
- Replies for bulk reads that end in an unknown number of chunks are described by a reply spec (`#`-terminated chunks, expected count, or one-char `responseCheck`). The streaming parser keeps leftover bytes between transactions.
- Interactive commands (slew, stop, park) preempt queued cyclic batches but never abort a transaction already on the wire.
- Failure in a bulk transaction closes and reconnects the link. No command is retried; the transaction is reported as failed.
- `:TLESCK#` is polled only in the slow set. `satellite.statTLE` reads the cache unless the user forces a refresh.
- No cached or polled data replaces an explicit user-triggered read (e.g. `getTrackingOffsets` after a set).

### 2.5 Timing constants (no fast/slow mode)

No global mode. Precision comes from `:U2#` and the `:Ginfo#` fields, not from poll speed. All periods are module constants in one place (`mountcontrol/connection.py` or a small `mountcontrol/timing.py`):

| Constant | Value | Use |
|---|---|---|
| `POLL_FAST_S` | 0.5 | `:Ginfo#` |
| `POLL_MEDIUM_S` | 3 | settings sub-batches (staggered) |
| `POLL_SLOW_S` | 30 | near-static data, clock sync |
| `BATCH_DEADLINE_S` | 2 | whole-batch deadline for telemetry |
| `RECONNECT_BACKOFF_S` | tbd | reconnect backoff |
| `BULK_CHUNK_SIZE` | 20-50, measured | commands per bulk chunk |

### 2.6 Debug logging of polling issues

Via the `logging` module at DEBUG level (no overhead when off). Per transaction: link class, command count, duration, deadline overruns, timeouts, partial replies, parser resyncs, reconnects, polls skipped or coalesced. Per bulk chunk: chunk number, size and duration.

### 2.7 Chunked bulk transactions with progress signals

- Bulk batches are split into chunks of `BULK_CHUNK_SIZE` commands: `:TRADD` (`satellite.startProgTrajectory`), `:newalpt` (`model.programModelFromStarList`), and the model name/star reads.
- Chunk boundaries sit only between independent commands. Chunks are pipelined on the persistent link, so each boundary costs one LAN round trip. The size is validated in phase 5 (no measurable slowdown against one big batch).
- The link stays owned between chunks, so cyclic polls cannot interleave.
- Progress: `pyqtSignal(int, int)` `progress(done, total)` emitted after each chunk by the satellite and model classes. The GUI connects to the signal; no tab coupling.
- A chunk failure or timeout aborts the whole transaction, with no retry. For trajectories, `:TRP#` is sent only after all chunks succeed. For `:newalpt`, `:endalig#` is sent only after all chunks succeed, and the failure is reported with the number of completed chunks.
- `parseSetting`-style index-based parsing is replaced by per-chunk parsers.

## 3. Rollout phases

1. **Parser and link core**: per-command reply spec, `MountLink` (persistent socket, queue, deadline, reconnect, `:U2#`). The `Connection` facade gets identical behavior. No schedule change.
2. **Migrate callers** (see 2.4): setters, firmware, model, satellite (TLE, track calc, offsets), `communicateRaw` use the facade or `MountLink` directly; bulk transactions get a link class and a scaled deadline. Remove the per-call socket code.
3. **Redundancy removal**: remove `:GJD1#` polling, fold in `checkMountUp`, move slow commands out of the 0.5 s batch, split the 3 s batch with phase offsets.
4. **Cache and priority**: telemetry cache with stale flags, interactive priority, coalescing metrics.
5. **Measurement**: log queue/send/first-byte/last-byte timestamps, p50/p95/p99, coalesced cycles, reconnects. Compare baseline, persistent link and the final schedule. Acceptance: p99 below 250 ms on the 0.5 s cycle at 2 Hz, no queue growth, at most 1 connection on 3490 for MW4. Also measure bulk throughput for several `BULK_CHUNK_SIZE` values against one big batch and choose the constant.

## 4. Constraints

- camelCase everywhere, no leading-underscore methods, full type annotations, Python 3.12+.
- Layering: `mountcontrol` imports only `base`. Qt only via `QObject`/`QTcpSocket` (QtNetwork, not Widgets or Gui). `uv run lint-imports` must stay green.
- Long-running work is in thread-pool workers named `worker{Name}` / `runner{Name}`.
- No GUI-tab coupling. Signals and slots only.

## 5. Tests (100% coverage, module scope)

- `tests/unit_tests/mountcontrol/test_connection.py`: fake `QTcpSocket`/local test server for:
  - framing (`#`, fixed-length, no-reply, split packets, leftover bytes);
  - deadline;
  - reconnect and backoff;
  - `:U2#` on connect;
  - queue priority and coalescing;
  - no retry or resend after timeout or error;
  - chunk splitting, progress signal values (`done`, `total`), abort on chunk failure without the final command;
  - debug log records for timeouts, resyncs, reconnects and skipped polls (`caplog`).
- Update `test_mount.py`, `test_mountTimeConn.py`, `test_obsSite.py`, `test_setting.py`, `test_firmware.py`, `test_model.py`, `test_satellite.py` for the new schedule and the removed `:GJD1#` and connect probe.
- Windows-only paths are guarded and only tracked on Windows.
- Final steps: Ruff format and lint, `uv run lint-imports`, full test suite with coverage.

## 6. Risks and open questions

- The `:Ginfo#` JD precision is sufficient for the clock diff (to be validated against the current `:GJD1#`).
- Whether `:GS#` can be computed locally with the required accuracy.
- Which near-static commands may be moved to the event-driven or 30 s set.
- Firmware versions without `:Ginfo#` extra fields: parsing tolerates trailing fields (already `>= 8`).
- Blocking facade calls from the GUI thread must not deadlock with the link thread (calls are only allowed from workers or a timeout-bound wait).

## Phase 3 leftovers (done)
- Static settings `:GINQ#:GMAC#:GWOL#` are polled once and then every 30 s (`pollStaticSetting`, `cycleStaticSetting`).
- `:GT#`, `:Gh#`, `:Go#`, `:gtg#` stay cyclic: they change at runtime.
- The three settings sub-batches run sequentially, so no extra phase offset is needed.
- A link-state accessor on `LinkWorker` was not added; no caller needs it yet.
