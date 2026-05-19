# Plan: Refactoring von CameraAlpaca und CameraAscom

## Datum: 2026-05-19

---

## Problem-Analyse

Die beiden Klassen `CameraAlpaca` (`cameraAlpaca.py`) und `CameraAscom`
(`cameraAscom.py`) sind nahezu identisch. Der einzige strukturelle
Unterschied ist ihre jeweilige Basisklasse:

| Klasse          | Basisklasse    |
|-----------------|----------------|
| `CameraAlpaca`  | `AlpacaClass`  |
| `CameraAscom`   | `AscomClass`   |

Beide `AlpacaClass` und `AscomClass` leiten von `AlpacaAscomCommon` ab,
welche das gemeinsame Kommunikationsprotokoll (Kommando-Queue,
Verbindungsaufbau, Poll-Loop) implementiert.

### Duplizierter Code (vollständig identisch oder nahezu identisch)

| Methode / Attribut      | Unterschied          |
|-------------------------|----------------------|
| `CAMERA_STATES`         | keiner               |
| `__init__`              | keiner               |
| `getInitialConfig`      | keiner               |
| `setExposureState`      | fehlende Rückgabe-Typ-Annotation in `CameraAscom` |
| `pollData`              | keiner               |
| `sendDownloadMode`      | keiner               |
| `expose`                | minimaler Formatierungsunterschied |
| `abort`                 | keiner               |
| `sendCoolerSwitch`      | keiner               |
| `sendCoolerTemp`        | keiner               |
| `sendOffset`            | keiner               |
| `sendGain`              | keiner               |

---

## Lösungsansatz: Mixin-Klasse

Extraktion der gemeinsamen Logik in eine **Mixin-Klasse**
`CameraAlpacaAscomBase`, die beide protokollspezifischen Klassen
einbinden.

### Vererbungsstruktur (nach Refactoring)

```
AlpacaAscomCommon
    ├── AlpacaClass
    │       └── CameraAlpaca(CameraAlpacaAscomBase, AlpacaClass)
    └── AscomClass
            └── CameraAscom(CameraAlpacaAscomBase, AscomClass)

CameraAlpacaAscomBase  (Mixin – enthält gesamte gemeinsame Logik)
```

### Python MRO (Method Resolution Order)

- `CameraAlpaca.__mro__`:
  `CameraAlpaca → CameraAlpacaAscomBase → AlpacaClass → AlpacaAscomCommon`
- `CameraAscom.__mro__`:
  `CameraAscom → CameraAlpacaAscomBase → AscomClass → AlpacaAscomCommon`

`super().__init__(parent=parent)` im Mixin delegiert korrekt an die
jeweilige Protokollklasse.

---

## Implementierungsschritte

### Schritt 1 – Neue Datei `cameraAlpacaAscomBase.py` anlegen

Pfad: `src/mw4/logic/camera/cameraAlpacaAscomBase.py`

Enthält die Klasse `CameraAlpacaAscomBase` mit allen aktuell duplizierten
Methoden und Attributen:

- `CAMERA_STATES: list[str]`
- `__init__`
- `getInitialConfig`
- `setExposureState` (inkl. fehlender `-> None` Annotation)
- `pollData`
- `sendDownloadMode`
- `expose`
- `abort`
- `sendCoolerSwitch`
- `sendCoolerTemp`
- `sendOffset`
- `sendGain`

#### Schritt 1a – `super().__init__()` an den Anfang von `__init__` verschieben

**Analyse der aktuellen Initialisierungsreihenfolge:**

Im bisherigen Code der Kameraklassen wird `super().__init__(parent=parent)` ans
Ende gesetzt, obwohl die Basisklassen-Initialisierung keine vorab gesetzten
`self`-Attribute benötigt. Konkret:

- `AlpacaAscomCommon.__init__` liest alle benötigten Werte aus dem `parent`-
  Parameter direkt (`parent.app`, `parent.data`, `parent.signals`,
  `parent.deviceType`) – nicht aus `self`.
- Die manuell gesetzten Zuweisungen `self.app = parent.app`,
  `self.data = parent.data`, `self.signals = parent.signals`
  im Kamera-`__init__` sind daher **redundant**, denn
  `AlpacaAscomCommon.__init__` setzt diese Attribute selbst.

**Ergebnis:** `super().__init__(parent=parent)` kann und soll an den **Anfang**
von `__init__` verschoben werden. Im Mixin-`__init__` verbleiben danach nur
noch die Attribute, die die Basisklasse **nicht** setzt:

```python
def __init__(self, parent: Any) -> None:
    super().__init__(parent=parent)
    self.parent = parent
    self.startTimeExposure: float = 0
    self.exposing: bool = False
```

Die bisher redundanten Zuweisungen `self.app`, `self.data`, `self.signals`
werden entfernt, da sie durch `AlpacaAscomCommon.__init__` bereits gesetzt
werden.

### Schritt 2 – `cameraAlpaca.py` vereinfachen

`CameraAlpaca` erbt von `(CameraAlpacaAscomBase, AlpacaClass)`.
Der gesamte duplizierte Code wird entfernt. Die Datei enthält nur noch
die Klassendefinition mit der Mehrfachvererbung.

```python
class CameraAlpaca(CameraAlpacaAscomBase, AlpacaClass):
    pass
```

### Schritt 3 – `cameraAscom.py` vereinfachen

`CameraAscom` erbt von `(CameraAlpacaAscomBase, AscomClass)`.
Gleiche Vereinfachung wie in Schritt 2.

```python
class CameraAscom(CameraAlpacaAscomBase, AscomClass):
    pass
```

### Schritt 4 – Bestehende Tests anpassen

- `test_cameraAlpaca.py`: Import-Pfad und ggf. Fixture auf die
  neue Struktur anpassen
- `test_cameraAscom.py`: entsprechend anpassen
- Neue Testdatei `test_cameraAlpacaAscomBase.py` anlegen mit 100 %
  Coverage für die gemeinsame Basislogik

### Schritt 5 – Qualitätssicherung

1. `pytest tests/unit_tests/logic/camera/` mit 100 % Coverage
2. `ruff check src/mw4/logic/camera/` – alle Findings beheben
3. `ruff format src/mw4/logic/camera/`
4. Gesamtpaket-Test: `pytest tests/unit_tests/`

---

## Dateienübersicht nach Refactoring

| Datei                                  | Status       |
|----------------------------------------|--------------|
| `src/mw4/logic/camera/cameraAlpacaAscomBase.py` | **neu** |
| `src/mw4/logic/camera/cameraAlpaca.py` | vereinfacht  |
| `src/mw4/logic/camera/cameraAscom.py`  | vereinfacht  |
| `tests/unit_tests/logic/camera/test_cameraAlpacaAscomBase.py` | **neu** |
| `tests/unit_tests/logic/camera/test_cameraAlpaca.py` | angepasst |
| `tests/unit_tests/logic/camera/test_cameraAscom.py`  | angepasst |

---

## Risiken und Hinweise

- Die **MRO muss korrekt sein**: Mixin zuerst, dann Protokollklasse –
  `(CameraAlpacaAscomBase, AlpacaClass)`.
- `super().__init__(parent=parent)` im Mixin muss **ohne** direkten
  Klassenaufruf erfolgen, damit die MRO-Kette korrekt durchlaufen wird.
- `AscomClass` enthält plattformspezifischen Code (`Windows`-Guard).
  Der Mixin selbst hat keine Plattformabhängigkeit, daher ist kein Guard
  im Mixin erforderlich.
- Da `CameraAscom` nur unter Windows genutzt wird, bleibt der
  bedingte Import in `camera.py` unverändert.

