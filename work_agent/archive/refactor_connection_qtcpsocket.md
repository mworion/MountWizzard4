# Refactoring Plan: `Connection` from `socket` to `QTcpSocket`

## 1. Goal

Replace the low-level Python `socket` implementation in
`src/mw4/mountcontrol/connection.py` with Qt's `QTcpSocket`
(`PySide6.QtNetwork`) **without changing any public interface** used by
the rest of the code base. All callers (`obsSite`, `setting`, `model`,
`satellite`, `firmware`, `mountTime`, `tabMount_Command`) must continue
to work unchanged.

## 2. Interface Contract (MUST stay stable)

The following surface is consumed externally and must remain
byte-for-byte compatible in signature and return semantics:

| Member | Signature | Returns |
|--------|-----------|---------|
| `Connection(parent)` | `parent.config.hostAddress`, `parent.config.port`, `parent.loggingTrace` | instance |
| `communicate(commandString, responseCheck="")` | | `tuple[bool, list[str], int]` |
| `communicateRaw(commandString)` | | `tuple[bool, bool, str]` |
| `validCommand(command)` | | `bool` |
| `validCommandSet(commandString)` | | `bool` |
| `analyseCommand(commandString)` | | `tuple[int, bool, int]` |

Class constants stay unchanged:
`COMMANDS`, `COMMAND_A`, `COMMAND_P`, `COMMAND_B`, `SOCKET_TIMEOUT`.

`analyseCommand`, `validCommand`, `validCommandSet` contain **no socket
code** and are not touched (pure string logic).

## 3. Internal Methods (implementation detail – will change)

These helpers are currently `socket`-typed and are unit-tested directly.
They will be reimplemented on top of `QTcpSocket`. Their names and
call-shape are preserved so `communicate` / `communicateRaw` stay simple,
but the `client` type changes from `socket.socket` to `QTcpSocket`:

- `buildClient() -> QTcpSocket | None`
- `sendData(client, commandString) -> bool`
- `receiveData(client, numberOfChunks, minBytes) -> tuple[bool, list[str]]`
- `closeClientHard(client) -> None`

## 4. socket → QTcpSocket Mapping

| Current (`socket`) | New (`QTcpSocket`) |
|--------------------|--------------------|
| `socket.socket(AF_INET, SOCK_STREAM)` | `QTcpSocket()` |
| `client.settimeout(10)` | pass `10*1000` ms to each `waitFor*` |
| `setsockopt(TCP_NODELAY, True)` | `setSocketOption(QAbstractSocket.SocketOption.LowDelayOption, 1)` |
| `client.connect(host)` | `connectToHost(addr, port)` + `waitForConnected(ms)` |
| `client.sendall(bytes)` | `write(bytes)` + `waitForBytesWritten(ms)` |
| `client.recv(2048)` | `waitForReadyRead(ms)` + `readAll()` → `bytes(qba)` |
| `TimeoutError` | `waitFor*()` returns `False` → treat as timeout |
| `client.shutdown()/close()` | `abort()` / `close()` |
| connection error text | `client.errorString()` |

### Timeout semantics
Python's `settimeout` applies per blocking op. Mirror this by passing
`SOCKET_TIMEOUT * 1000` ms to `waitForConnected`, `waitForBytesWritten`
and `waitForReadyRead`. A `False` return replaces the `TimeoutError`
branch (same log messages, same `False`/`[]` returns).

## 5. Threading Note
`Connection` objects are created and used synchronously inside mount
worker threads (`runWorker` / `threadPool`). `QTcpSocket` blocking
`waitFor*` calls work **without** a running event loop, so no event loop
is required. The socket is created, used and destroyed within one call —
no cross-thread signal wiring, no parent QObject needed.

## 6. Step-by-step Implementation

1. **Imports**: remove `import socket`; add
   `from PySide6.QtNetwork import QAbstractSocket, QTcpSocket`.
   Keep `host` as `(hostAddress, port)` tuple to preserve the existing
   malformed-host guard logic and internal tests' `conn.host = ...`
   overrides.
2. **`closeClientHard`**: guard `if not client: return`; wrap
   `client.abort()` / `client.close()` in try/except with the same
   warning log. (`abort()` == immediate RST, closest to `SHUT_RDWR`.)
3. **`buildClient`**:
   - keep `if not self.host` and `if not isinstance(self.host, tuple)`
     guards + identical log lines.
   - create `QTcpSocket`, set `LowDelayOption`.
   - `connectToHost(self.host[0], int(self.host[1]))`.
   - `if not waitForConnected(SOCKET_TIMEOUT*1000)` → log timeout,
     `closeClientHard`, return `None`.
   - wrap unexpected exceptions the same way (general error branch).
4. **`sendData`**: `write(commandString.encode())` then
   `waitForBytesWritten(...)`. On `False`/exception → same log + `False`.
5. **`receiveData`**: loop while receiving:
   - `if not client.waitForReadyRead(ms)` → timeout branch (`False, []`).
   - `chunkRaw = bytes(client.readAll())`; empty → break.
   - keep the identical chunk/minBytes accumulation + decode logic,
     including the `ASCII` decode exception branch.
6. **`communicate`**: unchanged flow (build → analyse → send → receive →
   close), unchanged returns.
7. **`communicateRaw`**: build client, `sendData`, then one
   `waitForReadyRead` + `readAll()` decode; keep timeout/exception text
   values (`"Timeout"`, `"Exception"`, `"Socket error"`) and the
   `(sucSend, sucRec, val)` shape.

## 7. Test Refactoring (`tests/unit_tests/mountcontrol/test_connection.py`)

Interface-level tests stay; socket-mock tests are re-pointed at
`QTcpSocket`. Concretely:

- Replace `import socket` mocks with a mocked
  `mw4.mountcontrol.connection.QTcpSocket`.
- `m_socket.return_value.connect` → mock `connectToHost` +
  `waitForConnected(return_value=True)`.
- `.sendall(...)` → `write(...)` + `waitForBytesWritten(True)`.
- `.recv(...) = b"...#"` → `waitForReadyRead(True)` +
  `readAll(return_value=QByteArray(b"...#"))`.
- Timeout tests: set `waitForConnected` / `waitForBytesWritten` /
  `waitForReadyRead` `return_value=False` (instead of
  `side_effect=TimeoutError`).
- `test_closeClientHard_*`, `test_buildClient_*`, `test_receiveData_*`
  updated to construct/mocked `QTcpSocket` and its `abort`/`close`.
- Keep all `analyseCommand` / `validCommand*` tests unchanged.
- Preserve `loggingTrace` coverage tests (rewired to QTcpSocket mocks).

Target: **100 % coverage** of `connection.py`, no `# pragma: no cover`.

## 8. Verification

1. `pytest tests/unit_tests/mountcontrol/test_connection.py` – all pass.
2. `pytest tests/unit_tests/mountcontrol/` – callers still green
   (they mock `Connection`, so should be unaffected).
3. Full suite: `pytest tests/unit_tests/`.
4. `ruff check` + `ruff format` on `connection.py` and the test file.
5. Confirm coverage of `connection.py` == 100 %.

## 9. Risks / Notes

- `QAbstractSocket.SocketOption.LowDelayOption` is the Qt6 enum path
  (scoped enum under PySide6).
- `readAll()` returns `QByteArray`; wrap with `bytes(...)` before
  `.decode("ASCII")` to keep existing decode-exception handling working.
- `abort()` vs `disconnectFromHost()`: use `abort()` to match the
  immediate hard-close semantics of the old `shutdown(SHUT_RDWR)`.
- No change to `SOCKET_TIMEOUT` value (10 s) to keep behaviour identical.
- Scope is limited to `connection.py` + its test file. No caller edits.
