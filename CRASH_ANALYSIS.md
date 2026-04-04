# Crash-Analyse: SIGSEGV (Exit Code 139) – MountWizzard4

**Datum:** 2026-04-04  
**System:** macOS 26.4 (25E246), Apple Silicon (arm64, Mac15,8)  
**Python:** 3.13.11 | **PySide6/Qt:** 6.11.0 | **shiboken6:** 6.11.0  
**numpy:** 2.4.4 | **pyqtgraph:** 0.14.0

---

## 1. Zusammenfassung

Die Applikation crasht reproduzierbar mit `SIGSEGV` (Signal 11). Alle analysierten
macOS-Crash-Reports (20+ Dateien vom 04.04.2026) zeigen ein **identisches Crash-Muster**:

```
EXC_BAD_ACCESS (SIGSEGV) – KERN_INVALID_ADDRESS
  → possible pointer authentication failure (PAC)
```

Der Crash passiert **immer im Main-Thread (Thread 0)** innerhalb der Shiboken/PySide6-
Binding-Schicht, während gleichzeitig **Worker-Threads** aktiv sind, die numpy-Berechnungen
(`np.einsum` / `np.dot`) ausführen.

---

## 2. Crash-Stack-Trace (konsistent über alle Reports)

### Faulting Thread (Main Thread / Qt Event Loop):
```
#0  libshiboken6 :: Shiboken::Conversions::cppPointer()
     oder
#0  libshiboken6 :: PepType_GetDict
#1  QtCore.abi3.so :: Sbk_QObject_getattro()        ← Python-Attribut-Zugriff auf QObject
#2  libpython3.13 :: PyObject_GetAttr
#3  libshiboken6 :: Shiboken::BindingManager::getOverride()
#4  libshiboken6 :: Sbk_GetPyOverride()
#5  QtCore.abi3.so :: QObjectWrapper::event()        ← Qt-Event wird dispatcht
#6  QtWidgets :: QApplicationPrivate::notify_helper()
#7  QtWidgets :: QApplication::notify()
#8  QtWidgets.abi3.so :: QApplicationWrapper::notify()
#9  QtCore :: QCoreApplication::sendEvent()
#10 QtCore :: QCoreApplicationPrivate::sendPostedEvents()
```

### Background Worker Threads (zum Zeitpunkt des Crashes):
```
#0  libsystem_kernel :: __psynch_cvwait
#1  libsystem_pthread :: _pthread_cond_wait
#2  libpython3.13 :: take_gil                         ← wartet auf GIL
#3  libpython3.13 :: PyEval_RestoreThread
#4  numpy :: PyArray_EinsteinSum                      ← numpy einsum
#5  numpy :: array_einsum
#6  ...
#7  QtCore.abi3.so :: QRunnableWrapper::run()         ← QThreadPool Worker
```

---

## 3. Ursachenanalyse

### 3.1 Hauptursache: Thread-Safety-Verletzung mit QObject-Zugriffen

Der Crash tritt auf, weil **Qt-Objekte (QObject) aus Worker-Threads heraus modifiziert
oder zugegriffen werden**, während der Main-Thread dieselben Objekte verarbeitet. 
Qt-Widgets und QObjects sind **nicht thread-safe** und dürfen nur vom Main-Thread aus
zugegriffen werden.

**Konkrete Problemstellen:**

#### a) `QApplication.processEvents()` im Worker-Thread (`tpool.py:72`)
```python
# src/mw4/base/tpool.py, Zeile 72
class Worker(QRunnable):
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            QApplication.processEvents()  # ← KRITISCH: Darf NICHT aus Worker-Thread!
```
`QApplication.processEvents()` darf **ausschließlich vom Main-Thread** aufgerufen werden.
Dieser Aufruf im QThreadPool-Worker ist eine schwere Thread-Safety-Verletzung und kann
direkt den beobachteten Crash verursachen: Events werden aus dem falschen Thread
dispatcht, die Qt-Event-Loop versucht QObject-Attribute zu resolven (`Sbk_QObject_getattro`),
und der Shiboken-Binding-Layer greift auf einen bereits invaliden oder korrupten Zeiger zu
→ `SIGSEGV`.

#### b) `geometry.calcTransformationMatrices()` aus Worker-Threads

Die Methode `calcTransformationMatricesActual()` in `mount.py` (Zeile 466-472) wird
sowohl von GUI-Signalhandlern (Simulator: `pointer.py`, `laser.py`, `buildPoints.py`)
als auch indirekt über `calcMountAltAzToDomeAltAz()` aus Worker-Threads aufgerufen.
Diese Methode schreibt auf geteilte Instanzvariablen:
```python
# geometry.py, Zeile 422-423
self.transMatrix = [T0, T1, T2, T3, T4, T5, T6, T7, T8, T9]
self.transVector = [P0, P1, P2, P3, ...]
```
Ohne Synchronisation entsteht eine **Race-Condition**: Der Main-Thread liest
`self.transMatrix`/`self.transVector` während ein Worker-Thread sie gleichzeitig
überschreibt.

#### c) numpy free-threading / GIL-Probleme mit Python 3.13

Python 3.13 enthält Änderungen am GIL-Verhalten. Die Crash-Reports zeigen, dass
Worker-Threads in `take_gil` (GIL-Akquise) warten, während der Main-Thread im
Shiboken-Binding crasht. Dies deutet darauf hin, dass **numpy-Operationen den GIL
freigeben** (`Py_BEGIN_ALLOW_THREADS` in `PyArray_EinsteinSum`), wodurch der Main-Thread
Code ausführen kann, der auf Python-Objekte zugreift, die gerade von numpy im 
Background-Thread modifiziert werden.

### 3.2 Sekundäre Probleme (aus dem Application-Log)

Der Application-Log (`mw4-2026-04-04.log`) zeigt **8 aufeinanderfolgende
KeyboardInterrupt-Exceptions** in den Timer-Callbacks:

```
File "mainApp.py", line 217, in sendCyclic → KeyboardInterrupt
File "mount.py", line 258, in cyclePointing → KeyboardInterrupt  
File "mount.py", line 275, in cycleSetting → KeyboardInterrupt
File "mount.py", line 224, in cycleCheckMountIsUp → KeyboardInterrupt
```

Diese `KeyboardInterrupt`-Kaskade entsteht, wenn das SIGSEGV als Interrupt in die
Python-Layer propagiert wird, bevor der Prozess endgültig terminiert. Die betroffenen
Methoden (`sendCyclic`, `cyclePointing`, `cycleSetting`, `cycleCheckMountIsUp`) 
sind die Timer-Callbacks, die zum Zeitpunkt des Crashes aktiv waren.

### 3.3 Pointer Authentication Failure (PAC)

Alle Crash-Reports enthalten den Hinweis `possible pointer authentication failure`.
Auf Apple Silicon (arm64) verwendet das System **Pointer Authentication Codes (PAC)**.
Wenn ein Zeiger durch Thread-unsichere Zugriffe korrumpiert wird, erkennt die Hardware
den ungültigen PAC und löst den `EXC_BAD_ACCESS` aus. Dies bestätigt, dass der Crash
durch **Memory Corruption infolge von Race Conditions** verursacht wird.

---

## 4. Empfehlungen zur Behebung

### 4.1 KRITISCH: `QApplication.processEvents()` aus Worker entfernen

**Datei:** `src/mw4/base/tpool.py`, Zeile 72

```python
# VORHER (fehlerhaft):
def run(self):
    try:
        result = self.fn(*self.args, **self.kwargs)
        QApplication.processEvents()  # ← ENTFERNEN

# NACHHER (korrigiert):
def run(self):
    try:
        result = self.fn(*self.args, **self.kwargs)
        # QApplication.processEvents() entfernt – nicht thread-safe
```

**Begründung:** `QApplication.processEvents()` verarbeitet Events in der Event-Queue
und darf nur im Main-Thread aufgerufen werden. In einem QRunnable-Worker hat es keinen
Zweck und verursacht den Crash.

### 4.2 KRITISCH: Shared State in Geometry schützen

**Datei:** `src/mw4/mountcontrol/geometry.py`

Option A: **QMutex** für `calcTransformationMatrices()`:
```python
from PySide6.QtCore import QMutex

class Geometry:
    def __init__(self, parent):
        # ...existing code...
        self._mutex = QMutex()
    
    def calcTransformationMatrices(self, ha, dec, lat, pierside="W"):
        self._mutex.lock()
        try:
            # ...bestehende Berechnung...
            return altDome, azDome, intersect, PB, PD
        finally:
            self._mutex.unlock()
```

Option B (besser): Die Methode **rein funktional** machen und den Shared State
(`self.transMatrix`, `self.transVector`) nur im Main-Thread setzen:
```python
def calcTransformationMatrices(self, ha, dec, lat, pierside="W"):
    # Berechnung ohne self.transMatrix/self.transVector zu setzen
    # Rückgabe aller Werte als Tuple
    return altDome, azDome, intersect, PB, PD, transMatrix, transVector
```

### 4.3 WICHTIG: Timer-Signal-Callbacks absichern

**Datei:** `src/mw4/mainApp.py`

Die `update*`-Signale werden an GUI-Elemente **und** an Worker-auslösende Methoden
verbunden. Stellen Sie sicher, dass alle Signal-Slot-Verbindungen, die Worker starten,
`Qt.ConnectionType.QueuedConnection` verwenden:

```python
self.app.update1s.connect(self.collectData, Qt.ConnectionType.QueuedConnection)
```

### 4.4 WICHTIG: ObsSite-Properties thread-safe machen

Die `ObsSite`-Klasse hat Properties wie `raJNow`, `decJNow`, `haJNow` etc., die
vom Main-Thread gelesen und aus Worker-Threads (`pollPointing`) geschrieben werden.
Diese sollten mit einem Lock geschützt oder als atomare Kopien bereitgestellt werden.

### 4.5 EMPFOHLEN: pyqtgraph auf 0.14.1+ aktualisieren

pyqtgraph 0.14.0 hat bekannte Kompatibilitätsprobleme mit PySide6 >= 6.7.
Es wird empfohlen, mindestens Version 0.14.1 oder neuer zu verwenden.

### 4.6 EMPFOHLEN: Crash-Handler verbessern

**Datei:** `src/mw4/loader.py`

```python
import signal
import faulthandler

def main(test: int = 0) -> None:
    faulthandler.enable()  # Gibt Python-Stack bei SIGSEGV aus
    # ...rest des Codes...
```

Dies ermöglicht es, bei zukünftigen Crashes den Python-Stack-Trace direkt im
Terminal zu sehen.

---

## 5. Priorisierte Umsetzungsreihenfolge

| Prio | Maßnahme | Datei | Aufwand |
|------|----------|-------|---------|
| 🔴 1 | `processEvents()` aus Worker entfernen | `tpool.py:72` | Minimal |
| 🔴 2 | Geometry Mutex oder rein funktional | `geometry.py` | Mittel |
| 🟡 3 | ObsSite Properties synchronisieren | `obsSite.py` | Mittel |
| 🟡 4 | Signal-Connections als QueuedConnection | `mount.py`, `mainApp.py` | Gering |
| 🟢 5 | faulthandler aktivieren | `loader.py` | Minimal |
| 🟢 6 | pyqtgraph aktualisieren | `pyproject.toml` | Minimal |

---

## 6. Fazit

Der SIGSEGV-Crash wird mit **hoher Wahrscheinlichkeit** durch den Aufruf von
`QApplication.processEvents()` in Worker-Threads (`tpool.py:72`) verursacht.
Dies ist der häufigste und gefährlichste Fehler, da er die Qt-Event-Loop aus dem
falschen Thread heraus manipuliert, was zu korrupten Zeigern in der Shiboken-
Binding-Schicht führt.

**Die Entfernung von `QApplication.processEvents()` aus `tpool.py` sollte den
Crash mit sehr hoher Wahrscheinlichkeit beheben.** Die weiteren Maßnahmen
(Geometry-Mutex, ObsSite-Synchronisation) sind ergänzend empfohlen, um die
allgemeine Thread-Sicherheit der Applikation zu verbessern.

