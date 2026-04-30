# Neues Gerät (Device) hinzufügen

Erstelle eine vollständige Geräte-Integration für MountWizzard4.

## Was zu erstellen ist

1. **Logic-Klasse** unter `src/mw4/logic/<kategorie>/<gerätename>.py`
   - Klasse mit `__init__(self, app)`
   - Signals-Klasse (QObject)
   - Verbindungs-/Trennungsmethoden
   - Gerätespezifische Methoden

2. **GUI-Mixin** unter `src/mw4/gui/` (falls nötig)
   - `initConfig()`, `storeConfig()`, `setupGui()`
   - Signal-Verbindungen

3. **Unit-Tests** unter `tests/unit_tests/logic/<kategorie>/`

## Gerät
${input:Gerätename und Kategorie (z.B. "MyCamera unter logic/camera")}

## Protokoll
${input:Kommunikationsprotokoll (INDI / WebSocket / HTTP / HID)}

