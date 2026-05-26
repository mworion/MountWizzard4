# Plan: Update `indiClass.py` and its Unit Tests

## Differences Between Disk and Attachment

| Area | Old (disk) | New (attachment) |
|------|-----------|-----------------|
| Imports | No `asyncio`, no `QueClient` | `import asyncio`, `QueClient` imported |
| `__init__` | No `queueClient` attribute | `self.queueClient: QueClient \| None = None` |
| `startCommunication` | `Worker(runqueclient, txQ, rxQ, ...)` | `Worker(self.runQueueClient)` |
| `runQueueClient` | Does not exist | New method: creates `QueClient`, runs `asyncio.run` |

---

## Steps

1. **Update `src/mw4/base/indiClass.py`** to match the attachment:
   - Add `import asyncio`
   - Add `QueClient` to the import from `indipyclient.queclient`
   - Add `self.queueClient: QueClient | None = None` in `__init__`
   - Add `runQueueClient` method
   - Rewrite `startCommunication` to use `Worker(self.runQueueClient)`

2. **Update `tests/unit_tests/base/test_indiClass.py`**:
   - Add `test_runQueueClient`: patch `QueClient` and `asyncio.run`,
     verify `QueClient` is created with correct args and `asyncrun` is invoked
   - Update `test_startCommunication_success`: assert the first Worker call
     receives `function.runQueueClient` as argument

3. Run `pytest` with `--cov` → must reach 100 %
4. Run `ruff check` + `ruff format` → fix all findings
5. Run the overall package tests

