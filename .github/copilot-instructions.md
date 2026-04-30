# MountWizzard4 – GitHub Copilot Instructions

## Projektbeschreibung
MountWizzard4 ist eine Python-Desktop-Anwendung zur Steuerung von **10micron-Montierungen**
für astronomische Beobachtungen. Sie stellt eine vollständige GUI bereit und unterstützt
Kamera-, Kuppel-, Wetter- und Satelliten-Workflows.

---

## Tech Stack

| Bereich           | Technologie                              |
|-------------------|------------------------------------------|
| Sprache           | Python 3.11–3.13                         |
| GUI               | PySide6 (Qt6), PyQtGraph                 |
| Astronomie        | Astropy, Skyfield, SGP4, SEP, PyERFA     |
| Datenverarbeitung | NumPy, SciPy, OpenCV (headless)          |
| Protokolle        | INDI (indipyclient), WebSocket, HID, REST|
| Bildformate       | FITS, XISF                               |
| Konfiguration     | PyYAML, JSON                             |
| Build             | uv / uv_build                            |
| Testing           | pytest, pytest-qt, pytest-cov            |
| Linting           | Ruff                                     |

---

## Projektstruktur

```
src/mw4/          → Hauptquellcode (src-Layout)
  gui/            → PySide6-GUI (Widgets, Windows, Styles)
  logic/          → Gerätelogik (Kamera, Kuppel, Wetter, ...)
  base/           → Basisklassen und Utilities
  mountcontrol/   → Kommunikation mit 10micron-Montierung
tests/
  unit_tests/     → Unit-Tests (spiegeln src/mw4/ Struktur)
  testData/       → Testdaten (FITS, WCS, JSON, ...)
src_add/
  widgets/        → Qt Designer .ui-Dateien
```

---

## Coding-Konventionen

- **Zeilenlänge**: max. 95 Zeichen (Ruff)
- **Einrückung**: 4 Leerzeichen
- **Imports**: sortiert ohne Sektionen (isort via Ruff)
- **GUI-Kommunikation**: Qt Signals & Slots
- **Tests**: pytest, Mocking mit `unittest.mock`
- **Dateinamen**: camelCase für Klassen, snake_case für Module
- **Keine** direkten Abhängigkeiten zwischen GUI-Tabs (lose Kopplung)

---

## Typische Muster

### Geräte-Klasse (Logic-Layer)
```python
class MyDevice:
    def __init__(self, app):
        self.app = app
        self.signals = MyDeviceSignals()
```

### GUI-Mixin
```python
class TabMyFeatureMixin:
    def initConfig(self): ...
    def storeConfig(self): ...
    def setupGui(self): ...
```

### Unit-Test
```python
def test_myFunction(app):
    # arrange
    ...
    # act
    result = app.myFunction()
    # assert
    assert result == expected
```

---

## Wichtige Hinweise für Copilot

- Tests immer unter `tests/unit_tests/` mit gleicher Ordnerstruktur wie `src/mw4/`
- GUI-Widgets werden aus `.ui`-Dateien generiert – diese **nicht** manuell bearbeiten
- Astronomische Berechnungen bevorzugt mit **Astropy** oder **Skyfield**
- INDI-Protokoll für Hardware-Kommunikation verwenden
- Platform-spezifischer Code (Windows) mit `platform_system == 'Windows'` absichern

