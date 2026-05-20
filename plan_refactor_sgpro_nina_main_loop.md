# Plan: Refactor `SgproNinaCommon` – Main-Loop, Queued Calls, No Timers

## Ziel

`sgproNinaCommon.py` soll strukturell an `alpacaAscomCommon.py` angeglichen werden:

- **Kein `QTimer`** mehr für das periodische Polling
- **Kein `QMutex`** mehr für die Absicherung des Poll-Workers
- **Kein `RemoteDeviceShutdown`-Signal** mehr
- **Kein separater `Worker`** für den Status-Poll (da der Loop selbst im ThreadPool läuft)
- Stattdessen: **blocking `runnerCommunicationLoop`** auf einem `Worker` im ThreadPool
- **`queue.Queue`** für asynchrone HTTP-Anfragen (fire-and-forget)
- **`threading.Event`** (`stopEvent`) zum sauberen Beenden des Loops

---

## Analyse der Unterschiede

| Aspekt                  | `alpacaAscomCommon`                        | `sgproNinaCommon` (aktuell)                   |
|-------------------------|--------------------------------------------|-----------------------------------------------|
| Polling-Mechanismus     | blocking loop + `stopEvent.wait(timeout)`  | `QTimer` + `QMutex` + Worker je Tick          |
| Beenden                 | `stopEvent.set()`                          | `cycleDevice.stop()` + Mutex                  |
| Queued Commands         | `commandQueue` (queue.Queue)               | nicht vorhanden                               |
| Initial Config          | direkt in `handleDeviceConnect`            | via separatem `Worker` + `workerGetConfig`    |
| Loop-Einstieg           | `runnerCommunicationLoop`                  | `startCommunication` startet Timer            |
| Loop-Start              | Worker mit `runnerCommunicationLoop`        | `startCommunication` startet `QTimer`         |

---

## Änderungen in `src/mw4/base/sgproNinaCommon.py`

### Entfernen

- Import: `RemoteDeviceShutdown` aus `driverDataClass`
- Import: `Worker` aus `tpool`
- Import: `QMutex`, `QTimer` aus `PySide6.QtCore`
- Attribute: `workerGetConfig`, `workerStatus`, `mutexPollStatus`,
  `cycleDevice`, `signalRS`
- Methoden: `startTimer`, `stopTimer`, `clearPollStatus`,
  `pollStatus` (timer-basiert)

### Hinzufügen

- Import: `queue`, `threading`, `time`
- Attribute: `stopEvent: threading.Event`
- Attribute: `commandQueue: queue.Queue`
- Methode: `requestPropertyQueued(valueProp, params)` – legt einen
  HTTP-Request in die `commandQueue` (fire-and-forget)
- Methode: `processCommandQueue()` – verarbeitet alle ausstehenden
  Einträge der `commandQueue` (analog `alpacaAscomCommon`)
- Methode: `pollData()` – ersetzt `workerPollStatus`; wird direkt im
  Loop aufgerufen (kein Worker, da Loop bereits im ThreadPool läuft)
- Methode: `handleDeviceConnect()` – kapselt Verbindungsaufbau inkl.
  `connectDevice`, Signale, `getInitialConfig` (direkt, kein Worker)
- Methode: `handleDeviceDisconnect()` – kapselt Verbindungsabbau inkl.
  Signale und Nachricht
- Methode: `runnerCommunicationLoop()` – blocking loop analog zu
  `alpacaAscomCommon.runnerCommunicationLoop`

### Anpassen

- `workerGetInitialConfig()` – bleibt als überschreibbarer Hook, wird
  aber jetzt **direkt** aus dem Loop-Thread aufgerufen (kein separater
  Worker)
- `getInitialConfig()` – ruft `workerGetInitialConfig()` direkt auf
  (da bereits im richtigen Thread)
- `startCommunication()` – startet keinen Timer mehr, sondern
  setzt `stopEvent` zurück und startet einen `Worker` mit
  `runnerCommunicationLoop` im `threadPool`
- `stopCommunication()` – setzt `stopEvent.set()` statt Timer zu
  stoppen; Rest bleibt identisch

---

## Neue Struktur von `runnerCommunicationLoop`

```python
def runnerCommunicationLoop(self) -> None:
    while not self.stopEvent.is_set():
        if not self.deviceConnected:
            self.handleDeviceConnect()
        else:
            state = self.pollData()
            if not state:
                self.handleDeviceDisconnect()
            else:
                self.processCommandQueue()
        self.stopEvent.wait(timeout=self.UPDATE_RATE / 1000)
```

> `UPDATE_RATE` wird auf `float` (Sekunden) umgestellt, analog zu
> `alpacaAscomCommon` (war bisher `int` in Millisekunden für `QTimer`).

---

## Änderungen in `src/mw4/base/ninaClass.py` und `sgproClass.py`

Keine inhaltlichen Änderungen nötig; beide erben nur `PROTOCOL_NAME`.

---

## Änderungen in `src/mw4/logic/camera/cameraSgproNinaBase.py`

- `workerGetInitialConfig` bleibt unverändert (Override-Hook)
- `expose` / `abort` etc. bleiben unverändert
- Prüfen, ob `requestProperty` für fire-and-forget-Calls (z. B.
  `abortImage`) durch `requestPropertyQueued` ersetzt werden soll;
  nur wenn im Kontext des Loop-Threads sinnvoll

---

## Änderungen in `tests/unit_tests/base/test_sgproNinaCommon.py`

- Alle Tests zu `startTimer`, `stopTimer`, `clearPollStatus`,
  `pollStatus`, `workerStatus`, `mutexPollStatus` entfernen
- Neue Tests für:
  - `requestPropertyQueued` (Eintrag in Queue)
  - `processCommandQueue` (leere Queue, GET, POST)
  - `pollData` (Connected / Disconnected / kein Response)
  - `handleDeviceConnect` (Erfolg, Fehler)
  - `handleDeviceDisconnect`
  - `runnerCommunicationLoop`
    (Loop läuft durch, stopEvent beendet Loop, Connect-Pfad,
    Disconnect-Pfad)
  - `startCommunication` (Worker wird gestartet, stopEvent wird
    resettet)
  - `stopCommunication` (stopEvent gesetzt, Signale ausgelöst)
- `getInitialConfig` wird direkt (kein Worker-Mock mehr) getestet
- Test-Fixture: `mock.patch.object(QTimer, "start")` entfällt

---

## Reihenfolge der Umsetzung

1. `sgproNinaCommon.py` refaktorieren
2. `test_sgproNinaCommon.py` auf 100 % Coverage bringen
3. `cameraSgproNinaBase.py` prüfen und ggf. anpassen
4. Ruff – Formatter und Linter ausführen, Befunde beheben
5. Gesamttest des Pakets

---

## Risiken / Hinweise

- `QTimer` läuft im Qt-Haupt-Thread; der neue Loop läuft im
  ThreadPool-Thread. Signale (`emit`) sind thread-safe in Qt/PySide6,
  also kein Problem.
- `requestProperty` ist ein blocking HTTP-Call – im Loop-Thread
  ohne Qt-Event-Loop ist das kein Problem.
- `processCommandQueue` für fire-and-forget HTTP-Calls: falls ein
  Consumer des Queued-Calls ein Ergebnis benötigt, müssen Callbacks
  oder Futures hinzugefügt werden (out-of-scope für diesen Plan).
- `UPDATE_RATE` Einheitenwechsel (ms → s) muss in allen Subklassen
  geprüft werden (`CameraSgproNinaBase`, `NINAClass`, `SGProClass`).

