# Plan: Refactoring von Alpaca/Ascom-Geräteklassen (überarbeitet)

## Datum: 2026-05-19

Anwendung des gleichen Musters wie bei `CameraAlpaca`/`CameraAscom`
(siehe `plan-camera-alpaca-ascom-refactoring.md`) auf alle weiteren
Gerätepaare. Dieser Plan basiert auf einer vollständigen Zeile-für-Zeile-
Prüfung der aktuellen Quelldateien (Stand 2026-05-19, letzte Revision).

---

## 1. Exakte Gegenüberstellung aller Geräteklassen

### 1.1 cover

| Methode / Attribut | `CoverAlpaca`                                               | `CoverAscom`                             |
|--------------------|-------------------------------------------------------------|------------------------------------------|
| `COVERSTATES`      | identisch                                                   | identisch                                |
| `__init__`         | `super()` + `self.parent` + `self.signals` + `self.data`    | `super()` + `self.signals` + `self.data` |
| `pollData`         | identisch                                                   | identisch                                |
| `closeCover`       | identisch                                                   | identisch                                |
| `openCover`        | identisch                                                   | identisch                                |
| `haltCover`        | identisch                                                   | identisch                                |

→ **Vollständig in Mixin extrahierbar (Gruppe A).**

---

### 1.2 dome

| Methode / Attribut  | `DomeAlpaca`                            | `DomeAscom`                             |
|---------------------|-----------------------------------------|-----------------------------------------|
| `SHUTTER_STATES`    | identisch                               | identisch                               |
| `__init__`          | `super()` + `self.signals` (redundant)  | `super()` + `self.signals` (redundant)  |
| `getInitialConfig`  | identisch                               | identisch                               |
| `pollData`          | identisch                               | identisch                               |
| `slewToAltAz`       | identisch                               | identisch                               |
| `openShutter`       | identisch                               | identisch                               |
| `closeShutter`      | identisch                               | identisch                               |
| `slewCW`            | identisch                               | identisch                               |
| `slewCCW`           | identisch                               | identisch                               |
| `abortSlew`         | identisch                               | identisch                               |

**Bug in beiden Klassen:** `pollData` referenziert `self.shutterStates[state]`,
das Klassenattribut heißt aber `SHUTTER_STATES`. Im Mixin auf
`self.SHUTTER_STATES[state]` korrigiert.
→ **Vollständig in Mixin extrahierbar (Gruppe A, mit Bug-Fix).**

---

### 1.3 focuser

| Methode / Attribut | `FocuserAlpaca`                            | `FocuserAscom`             |
|--------------------|--------------------------------------------|----------------------------|
| `__init__`         | `super()` + `self.signals` + `self.data`   | `super()` + `self.signals` |
| `pollData`         | identisch                                  | identisch                  |
| `move`             | identisch                                  | identisch                  |
| `halt`             | identisch                                  | identisch                  |

→ **Vollständig in Mixin extrahierbar (Gruppe A).**

---

### 1.4 lightPanel

| Methode / Attribut | `LightPanelAlpaca`                                          | `LightPanelAscom`                         |
|--------------------|-------------------------------------------------------------|-------------------------------------------|
| `__init__`         | `super()` + `self.parent` + `self.signals` + `self.data`    | `super()` + `self.signals` + `self.data`  |
| `pollData`         | identisch (abweichende Zeilenformatierung)                  | identisch                                 |
| `lightOn`          | identisch                                                   | identisch                                 |
| `lightOff`         | identisch                                                   | identisch                                 |
| `lightIntensity`   | identisch                                                   | identisch                                 |

→ **Vollständig in Mixin extrahierbar (Gruppe A).**

---

### 1.5 filter ✅ (identisch)

| Methode / Attribut | `FilterAlpaca`                           | `FilterAscom`                            |
|--------------------|------------------------------------------|------------------------------------------|
| `__init__`         | `super()` + `self.signals` + `self.data` | `super()` + `self.signals` + `self.data` |
| `getInitialConfig` | identisch                                | identisch                                |
| `pollData`         | identisch                                | identisch                                |
| `sendFilterNumber` | identisch                                | identisch                                |

→ **Vollständig in Mixin extrahierbar (Gruppe A).**

---

### 1.6 telescope ✅ (identisch)

| Methode / Attribut | `TelescopeAlpaca`                      | `TelescopeAscom`                       |
|--------------------|----------------------------------------|----------------------------------------|
| `__init__`         | `super()` + `self.signals` (redundant) | `super()` + `self.signals` (redundant) |
| `getInitialConfig` | identisch                              | identisch                              |

→ **Vollständig in Mixin extrahierbar (Gruppe A).**

---

### 1.7 sensorWeather ✅ (aktualisiert – jetzt identisch)

| Methode / Attribut | `SensorWeatherAlpaca`                  | `SensorWeatherAscom`                   |
|--------------------|----------------------------------------|----------------------------------------|
| `__init__`         | `super()` + `self.signals` (redundant) | `super()` + `self.signals` (redundant) |
| `pollData`         | identisch                              | identisch                              |

Beide Dateien sind **vollständig identisch** (je 33 Zeilen).
→ **Vollständig in Mixin extrahierbar (Gruppe A).**

---

### 1.8 pegasusUPB ✅ (aktualisiert – vollständig identisch, Stand 2026-05-19)

| Methode / Attribut    | `PegasusUPBAlpaca`                                           | `PegasusUPBAscom`                                            |
|-----------------------|--------------------------------------------------------------|--------------------------------------------------------------|
| `__init__`            | `super()` + `self.signals` + `self.data` (redundant)         | `super()` + `self.signals` + `self.data` (redundant)         |
| `pollData`            | identisch ✅                                                 | identisch ✅                                                 |
| `togglePowerPort`     | `callDeviceMethodQueued("SetSwitchValue", ..., Value=not val)`| `callDeviceMethodQueued("SetSwitchValue", ..., Value=not val)` ✅ |
| `togglePowerPortBoot` | `pass` – identisch ✅                                        | `pass` – identisch ✅                                        |
| `toggleHubUSB`        | `pass` – identisch ✅                                        | `pass` – identisch ✅                                        |
| `togglePortUSB`       | `callDeviceMethodQueued("SetSwitchValue", ..., Value=val)`   | `callDeviceMethodQueued("SetSwitchValue", ..., Value=val)` ✅ |
| `toggleAutoDew`       | `callDeviceMethodQueued("SetSwitch", ..., State=val)`        | `callDeviceMethodQueued("SetSwitch", ..., State=val)` ✅      |
| `sendDew`             | identisch ✅                                                 | identisch ✅                                                 |
| `sendAdjustableOutput`| `pass` – identisch ✅                                        | `pass` – identisch ✅                                        |
| `reboot`              | `pass` – identisch ✅                                        | `pass` – identisch ✅                                        |

Beide Dateien sind **vollständig identisch** (je 106/105 Zeilen, nur
der Basisklassen-Import unterscheidet sich). Früher dokumentierte
Unterschiede bei `togglePowerPort`, `togglePortUSB` und `toggleAutoDew`
existieren in den aktuellen Quelldateien nicht mehr.

→ **Vollständig in Mixin extrahierbar (Gruppe A).**

---

## 2. Gruppenklassifikation

| Gruppe | Kriterium                                       | Geräte                                                                        |
|--------|-------------------------------------------------|-------------------------------------------------------------------------------|
| **A**  | Alle Methoden identisch → vollständiges Mixin   | cover, dome, focuser, lightPanel, filter, telescope, sensorWeather, pegasusUPB |

---

## 3. Vererbungsstruktur nach Refactoring

```
AlpacaAscomCommon
    ├── AlpacaClass
    │   ├── CoverAlpaca(CoverAlpacaAscomBase, AlpacaClass)
    │   ├── DomeAlpaca(DomeAlpacaAscomBase, AlpacaClass)
    │   ├── FocuserAlpaca(FocuserAlpacaAscomBase, AlpacaClass)
    │   ├── LightPanelAlpaca(LightPanelAlpacaAscomBase, AlpacaClass)
    │   ├── FilterAlpaca(FilterAlpacaAscomBase, AlpacaClass)
    │   ├── TelescopeAlpaca(TelescopeAlpacaAscomBase, AlpacaClass)
    │   ├── SensorWeatherAlpaca(SensorWeatherAlpacaAscomBase, AlpacaClass)
    │   └── PegasusUPBAlpaca(PegasusUPBAlpacaAscomBase, AlpacaClass)
    └── AscomClass
        ├── CoverAscom(CoverAlpacaAscomBase, AscomClass)
        ├── DomeAscom(DomeAlpacaAscomBase, AscomClass)
        ├── FocuserAscom(FocuserAlpacaAscomBase, AscomClass)
        ├── LightPanelAscom(LightPanelAlpacaAscomBase, AscomClass)
        ├── FilterAscom(FilterAlpacaAscomBase, AscomClass)
        ├── TelescopeAscom(TelescopeAlpacaAscomBase, AscomClass)
        ├── SensorWeatherAscom(SensorWeatherAlpacaAscomBase, AscomClass)
        └── PegasusUPBAscom(PegasusUPBAlpacaAscomBase, AscomClass)
```

---

## 4. Implementierungsschritte

### Schritt 1 – Gruppe A: cover

**Neue Datei:** `src/mw4/logic/cover/coverAlpacaAscomBase.py`

```python
class CoverAlpacaAscomBase:
    COVERSTATES: list[str] = [
        "NotPresent", "Closed", "Moving", "Open", "Unknown", "Error"
    ]

    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None: ...
    def closeCover(self) -> None: ...
    def openCover(self) -> None: ...
    def haltCover(self) -> None: ...
```

`CoverAlpaca` und `CoverAscom` reduzieren auf `pass`-Klassen.

---

### Schritt 2 – Gruppe A: dome

**Neue Datei:** `src/mw4/logic/dome/domeAlpacaAscomBase.py`

Enthält alle Methoden. **Bug-Fix in `pollData`:**
`self.shutterStates[state]` → `self.SHUTTER_STATES[state]`.

`DomeAlpaca` und `DomeAscom` reduzieren auf `pass`-Klassen.

---

### Schritt 3 – Gruppe A: focuser

**Neue Datei:** `src/mw4/logic/focuser/focuserAlpacaAscomBase.py`

```python
class FocuserAlpacaAscomBase:
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None: ...
    def move(self, position: int) -> None: ...
    def halt(self) -> None: ...
```

`FocuserAlpaca` und `FocuserAscom` reduzieren auf `pass`-Klassen.

---

### Schritt 4 – Gruppe A: lightPanel

**Neue Datei:** `src/mw4/logic/lightPanel/lightPanelAlpacaAscomBase.py`

```python
class LightPanelAlpacaAscomBase:
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None: ...
    def lightOn(self) -> None: ...
    def lightOff(self) -> None: ...
    def lightIntensity(self, value: float) -> None: ...
```

`LightPanelAlpaca` und `LightPanelAscom` reduzieren auf `pass`-Klassen.

---

### Schritt 5 – Gruppe A: filter

**Neue Datei:** `src/mw4/logic/filter/filterAlpacaAscomBase.py`

```python
class FilterAlpacaAscomBase:
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def getInitialConfig(self) -> None: ...
    def pollData(self) -> None: ...
    def sendFilterNumber(self, filterNumber: int = 0) -> None: ...
```

`FilterAlpaca` und `FilterAscom` reduzieren auf `pass`-Klassen.

---

### Schritt 6 – Gruppe A: telescope

**Neue Datei:** `src/mw4/logic/telescope/telescopeAlpacaAscomBase.py`

```python
class TelescopeAlpacaAscomBase:
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def getInitialConfig(self) -> None: ...
```

`TelescopeAlpaca` und `TelescopeAscom` reduzieren auf `pass`-Klassen.

---

### Schritt 7 – Gruppe A: sensorWeather

**Neue Datei:** `src/mw4/logic/environment/sensorWeatherAlpacaAscomBase.py`

```python
class SensorWeatherAlpacaAscomBase:
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None: ...
```

`SensorWeatherAlpaca` und `SensorWeatherAscom` reduzieren auf `pass`-Klassen.

---

### Schritt 8 – Gruppe A: pegasusUPB (vollständiges Mixin)

**Neue Datei:** `src/mw4/logic/powerswitch/pegasusUPBAlpacaAscomBase.py`

Enthält **alle** Methoden (vollständig identisch in Alpaca und Ascom):

```python
class PegasusUPBAlpacaAscomBase:
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None: ...
    def togglePowerPort(self, port: str) -> None: ...
    def togglePowerPortBoot(self, port: str) -> None: ...
    def toggleHubUSB(self) -> None: ...
    def togglePortUSB(self, port: str) -> None: ...
    def toggleAutoDew(self) -> None: ...
    def sendDew(self, port: str, value: float) -> None: ...
    def sendAdjustableOutput(self, value: float) -> None: ...
    def reboot(self) -> None: ...
```

`PegasusUPBAlpaca` und `PegasusUPBAscom` reduzieren auf `pass`-Klassen.

---

## 5. Test-Strategie

### Gruppe A – neue Mixin-Testdateien

| Neue Testdatei                                  | Inhalt                                         |
|-------------------------------------------------|------------------------------------------------|
| `test_coverAlpacaAscomBase.py`                  | Alle Methoden des Mixins                       |
| `test_domeAlpacaAscomBase.py`                   | Alle Methoden + Bug-Fix-Verifikation           |
| `test_focuserAlpacaAscomBase.py`                | Alle Methoden des Mixins                       |
| `test_lightPanelAlpacaAscomBase.py`             | Alle Methoden des Mixins                       |
| `test_filterAlpacaAscomBase.py`                 | Alle Methoden des Mixins                       |
| `test_telescopeAlpacaAscomBase.py`              | Alle Methoden des Mixins                       |
| `test_sensorWeatherAlpacaAscomBase.py`          | Alle Methoden des Mixins                       |
| `test_pegasusUPBAlpacaAscomBase.py`             | Alle Methoden des Mixins                       |

Bestehende `test_{device}Alpaca.py` und `test_{device}Ascom.py` werden auf
minimale Vererbungsprüfung reduziert.

### Gruppe B – entfällt

Alle Geräteklassen werden vollständig in Mixins extrahiert (Gruppe A).
Es gibt keine partiellen Mixins mehr.

---

## 6. Dateienübersicht

### Neue Mixin-Dateien

| Datei                                                            | Gruppe |
|------------------------------------------------------------------|--------|
| `src/mw4/logic/cover/coverAlpacaAscomBase.py`                    | A      |
| `src/mw4/logic/dome/domeAlpacaAscomBase.py`                      | A      |
| `src/mw4/logic/focuser/focuserAlpacaAscomBase.py`                | A      |
| `src/mw4/logic/lightPanel/lightPanelAlpacaAscomBase.py`          | A      |
| `src/mw4/logic/filter/filterAlpacaAscomBase.py`                  | A      |
| `src/mw4/logic/telescope/telescopeAlpacaAscomBase.py`            | A      |
| `src/mw4/logic/environment/sensorWeatherAlpacaAscomBase.py`      | A      |
| `src/mw4/logic/powerswitch/pegasusUPBAlpacaAscomBase.py`         | A      |

### Vereinfachte / bereinigte Dateien

| Datei                                                   | Änderung                               |
|---------------------------------------------------------|----------------------------------------|
| `src/mw4/logic/cover/coverAlpaca.py`                    | `pass`-Klasse                          |
| `src/mw4/logic/cover/coverAscom.py`                     | `pass`-Klasse                          |
| `src/mw4/logic/dome/domeAlpaca.py`                      | `pass`-Klasse                          |
| `src/mw4/logic/dome/domeAscom.py`                       | `pass`-Klasse                          |
| `src/mw4/logic/focuser/focuserAlpaca.py`                | `pass`-Klasse                          |
| `src/mw4/logic/focuser/focuserAscom.py`                 | `pass`-Klasse                          |
| `src/mw4/logic/lightPanel/lightPanelAlpaca.py`          | `pass`-Klasse                          |
| `src/mw4/logic/lightPanel/lightPanelAscom.py`           | `pass`-Klasse                          |
| `src/mw4/logic/filter/filterAlpaca.py`                  | `pass`-Klasse                          |
| `src/mw4/logic/filter/filterAscom.py`                   | `pass`-Klasse                          |
| `src/mw4/logic/telescope/telescopeAlpaca.py`            | `pass`-Klasse                          |
| `src/mw4/logic/telescope/telescopeAscom.py`             | `pass`-Klasse                          |
| `src/mw4/logic/environment/sensorWeatherAlpaca.py`      | `pass`-Klasse                          |
| `src/mw4/logic/environment/sensorWeatherAscom.py`       | `pass`-Klasse                          |
| `src/mw4/logic/powerswitch/pegasusUPBAlpaca.py`         | `pass`-Klasse                          |
| `src/mw4/logic/powerswitch/pegasusUPBAscom.py`          | `pass`-Klasse                          |

---

## 7. Qualitätssicherung

```
1. pytest tests/unit_tests/logic/{device}/ (100 % Coverage) pro Gerät
2. ruff check src/mw4/logic/{device}/ → 0 Findings
3. ruff format src/mw4/logic/{device}/
4. Abschluss: pytest tests/unit_tests/ → alle Tests grün
```

---

## 8. Risiken und Hinweise

- **MRO**: Mixin immer als erstes Argument:
  `(FooAlpacaAscomBase, AlpacaClass)`.
- **`super().__init__(parent=parent)`** im Mixin ohne direkten Klassenaufruf.
- **Bug-Fix `dome`**: `self.shutterStates` → `self.SHUTTER_STATES` –
  bestehende Tests auf dieses Verhalten prüfen.
- **Windows-only**: Alle `AscomClass`-Unterklassen in Tests mit
  `pytest.skip(..., allow_module_level=True)` schützen.
