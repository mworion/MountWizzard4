# Type Annotation Review – `src/mw4`

> Erzeugt mit mypy 1.19.1 · 437 actionable errors (ohne `import-untyped` für externe Stubs und ohne Custom-Logger-Attribute `trace`/`header`/`ui`)

---

## Kategorie 1 – Syntax-Fehler in Annotierungen

Annotierungen, die mypy nicht parsen kann.

| Datei | Zeile | Problem | Fix |
|-------|-------|---------|-----|
| `gui/utilities/gCustomViewBox.py` | 50, 110, 111 | Syntax error in type annotation | Annotierung reparieren (vermutlich `[...]`-Schreibweise statt `list[...]`) |
| `gui/utilities/gCustomViewBox.py` | 165 | Invalid type comment or annotation | Kommentar-Annotation entfernen oder in echte Annotation umwandeln |
| `gui/utilities/gPlotBase.py` | 98, 114, 171, 172 | Bracketed expression `[...]` is not valid as a type | Durch `list[...]` ersetzen |
| `gui/mainWaddon/tabAlmanac.py` | 169, 181 | Syntax error in type annotation | Annotierung reparieren |

---

## Kategorie 2 – Falsche Typen als Annotierungen verwendet

Builtins oder Laufzeitobjekte werden als Typ-Annotation eingesetzt.

| Datei | Zeile | Problem | Fix |
|-------|-------|---------|-----|
| `gui/styles/styles.py` | 170 | `chr` (Builtin-Funktion) as type | `str` verwenden |
| `gui/utilities/gImageBar.py` | 53 | `np.array` as type | `np.ndarray` verwenden |
| `gui/extWindows/keypadW.py` | 243 | `np.array` as type | `np.ndarray` verwenden |
| `logic/photometry/photometry.py` | 47, 79, 80 | `np.array` as type | `np.ndarray` verwenden |
| `logic/dome/dome.py` | 193 | `callable` (Builtin) as type | `Callable[..., Any]` aus `collections.abc` verwenden |
| `logic/measure/measureCSV.py` | 22 | Fully qualified `PySide6.QtCore.QObject` nicht bekannt | `QObject` importieren und direkt verwenden |
| `logic/measure/measureRaw.py` | 20 | Fully qualified `PySide6.QtCore.QObject` nicht bekannt | `QObject` importieren und direkt verwenden |

---

## Kategorie 3 – Falsche Rückgabetypen

Deklarierter Return-Typ stimmt nicht mit tatsächlicher Rückgabe überein.

| Datei | Zeile | Problem | Fix |
|-------|-------|---------|-----|
| `gui/extWindows/hemisphere/hemisphereDraw.py` | 74 | `close()` → `None`, Superklasse erwartet `bool` | Return-Typ auf `-> bool` ändern und `return super().close()` aufrufen |
| `gui/utilities/gCustomViewBox.py` | 68, 81 | Gibt `None` zurück, deklariert `int` | Entweder Return-Typ auf `int \| None` oder fehlende `return`-Anweisung ergänzen |
| `gui/utilities/gPolarScatter.py` | 29 | `plot()` gibt `bool` zurück, Superklasse deklariert `None` | Rückgabetypen angleichen: entweder Superklasse auf `-> bool` oder Subklasse auf `-> None` |
| `gui/mainWaddon/tabModel.py` | 167, 171, 175 | Fehlende Return-Anweisung / `return`-Wert erwartet | Fehlende `return`-Pfade ergänzen |
| `logic/buildData/buildpoints.py` | 226, 249, 446, 464 | Falscher Return-Typ: `list[list[...]]` statt `list[tuple[...]]` | Return-Typ korrigieren auf die tatsächlich zurückgegebene Struktur |
| `logic/buildData/buildpoints.py` | 335 | Generator-Funktion mit falschem Return-Typ | Return-Typ auf `Generator[..., None, None]` setzen |
| `logic/modelBuild/modelRunSupport.py` | 62 | Gibt `list[dict]` zurück, deklariert `dict` | Return-Typ auf `list[dict[Any, Any]]` ändern |
| `logic/powerswitch/kmRelay.py` | 165, 167 | Gibt `int` zurück, deklariert `bool` | Return-Typ auf `int` ändern oder explizit `bool(...)` casten |
| `logic/satellites/satellite_calculations.py` | 205 | Gibt `list[dict]` zurück, deklariert `dict` | Return-Typ auf `list[dict[Any, Any]]` ändern |
| `logic/dome/domeIndi.py` | 130 | `return`-Wert in einer `-> None`-Funktion | `return`-Anweisung entfernen |
| `logic/environment/directWeather.py` | 59 | `return`-Wert in einer `-> None`-Funktion | `return`-Anweisung entfernen |
| `logic/powerswitch/pegasusUPBAscom.py` | 73 | `return`-Wert in einer `-> None`-Funktion | `return`-Anweisung entfernen |
| `logic/powerswitch/pegasusUPBIndi.py` | 193 | `return`-Wert in einer `-> None`-Funktion | `return`-Anweisung entfernen |
| `mountcontrol/convert.py` | 55, 59 | Gibt `str` zurück, deklariert `float` | Entweder `float(...)` casten oder Return-Typ korrigieren |

---

## Kategorie 4 – Falsche Parameter-Typ-Annotierungen

Parameter-Annotation passt nicht zum tatsächlich übergebenen Typ.

### 4a – `parse*`-Methoden im `mountcontrol`-Paket (systematisch)
Alle Aufruf-Stellen übergeben `str`, die Annotierungen erwarten `list[Any]`.

| Datei | Zeile | Methode |
|-------|-------|---------|
| `mountcontrol/dome.py` | 92 | `parse()` |
| `mountcontrol/firmware.py` | 73 | `parse()` |
| `mountcontrol/model.py` | 145, 160, 225, 243 | `parseNumberNames`, `parseNames`, `parseNumberStars`, `parseStars` |
| `mountcontrol/obsSite.py` | 459, 492 | `parseLocation`, `parsePointing` |
| `mountcontrol/satellite.py` | 76, 149, 181 | `parseGetTLE`, `parseCalcTLE`, `parseStatTLE` |
| `mountcontrol/setting.py` | 205 | `parseSetting` |

**Fix:** Parameter-Typ von `list[Any]` auf `str \| list[Any]` erweitern (oder `str` direkt, je nach tatsächlicher Verwendung).

### 4b – `updateData`, `isBetween`, `addIsoItem`, `addIsoBasic` im GUI-Utilities-Paket
Parameter als `int` annotiert, tatsächlich werden `ndarray` übergeben.

| Datei | Zeile | Methode | Fix |
|-------|-------|---------|-----|
| `gui/utilities/gCustomViewBox.py` | 64 (×3), 95 (×2), 106 (×2) | `isBetween(a,b,c: int)`, `updateData(x,y: int)` | Typen auf `int \| tuple \| np.ndarray` erweitern |
| `gui/utilities/gPlotBase.py` | 186, 196 (×3) | `addIsoBasic(…, float)`, `addIsoItem(…, int, int, int)` | Typen auf `float \| np.ndarray` bzw. `np.ndarray` erweitern |
| `gui/utilities/gNormalScatter.py` | 106 | `addIsoItemHorizon(…, int)` | Typ auf `int \| None` erweitern |

### 4c – `list2array` in `analyseW.py`
Erwartet `dtype[Any]`, bekommt `type[np.float32]` / `type[np.int64]`.

| Datei | Zeile | Fix |
|-------|-------|-----|
| `gui/extWindows/analyseW.py` | 155, 182–194 | Parameter-Typ auf `type \| np.dtype[Any]` erweitern |

### 4d – `QInputDialog`-Aufrufe
`getInt` / `getDouble` / `getItem` erwarten `QWidget \| None` als erstes Argument, bekommen die eigene Addon-Klasse.

| Datei | Zeilen | Fix |
|-------|--------|-----|
| `gui/mainWaddon/tabImage_Manage.py` | 215, 233, 240, 249, 265, 272, 281, 306, 328 | `self` durch `None` oder den echten Parent-Widget-Ausdruck ersetzen |
| `gui/mainWaddon/tabPower.py` | 181, 218 | Gleiche Fix-Strategie |

### 4e – Sonstige Parameter-Fehler

| Datei | Zeile | Problem | Fix |
|-------|-------|---------|-----|
| `base/ascomClass.py` | 135 | `storePropertyToData` erhält `str\|float\|bool\|None`, erwartet `str\|float` | Annotation auf `str \| float \| bool \| None` erweitern |
| `logic/cover/coverAscom.py` | 37, 41 | Gleich wie oben | Gleiche Fix-Strategie |
| `logic/dome/domeAscom.py` | 44 | Gleich wie oben | Gleiche Fix-Strategie |
| `logic/dome/domeAscom.py` | 52, 60 | Unbekanntes Keyword `elementInv`; vermutlich `element` gemeint | Keyword-Namen prüfen und korrigieren |
| `logic/buildData/buildpoints.py` | 242 | `sniff(delimiters=list[str])` – erwartet `str \| None` | `delimiters` als Join-String übergeben: `"".join(delimiters)` |
| `logic/buildData/buildpoints.py` | 321, 332, 401, 422, 513 | `addBuildP` erwartet `tuple[int,int,int]`, bekommt `list[float]`/`list[int]`/`int` | Parameter-Typ auf `tuple \| list` erweitern oder Aufrufe anpassen |
| `logic/camera/camera.py` | 198, 204, 210 | `in`-Operator mit `Any \| None` – guard-check fehlt | Vor dem `in` auf `None` prüfen |
| `logic/databaseProcessing/dataWriter.py` | 157, 158 | `convertDatePacked(str)` erwartet `float` | Parameter-Typ auf `float \| str` erweitern |
| `logic/environment/seeingWeather.py` | 121, 149 | `str` statt `Path` | Parameter-Typ auf `str \| Path` erweitern |
| `logic/environment/sensorWeatherOnline.py` | 142, 170 | Gleich wie oben | Gleiche Fix-Strategie |
| `logic/filter/filterAscom.py` | 35 | `enumerate(str\|float\|bool)` – erwartet `Iterable` | Guard-check oder Parameter-Typ einengen |
| `logic/keypad/keypad.py` | 206, 282, 284, 293, 295, 304, 306, 315, 317, 329, 331, 333, 335, 348, 349 | `calcChecksum(list)` annotiert als `int`; `send(list)` annotiert als `str`; `checkDispatch(list)` annotiert als `int` | Parameter-Typen auf `list[int]` / `bytes` korrigieren |
| `logic/modelBuild/modelRunSupport.py` | 182 | `findKeysSourceInDest(dict, dict)` erwartet `list[dict]` | Parameter-Typ auf `list[dict] \| dict` erweitern |
| `logic/satellites/satellite_calculations.py` | 184–204 | `list` per `str`-Key indiziert – sollte `dict` sein | Variablentyp auf `dict[str, Any]` ändern |
| `logic/satellites/satellite_calculations.py` | 225 | `sortFlipEvents(dict)` erwartet `list[dict]` | Parameter-Typ korrigieren |
| `gui/mainWaddon/tabMount_Move.py` | 190 | `moveClassic(list[int])` erwartet `str` | Entweder Annotation auf `list[int] \| str` erweitern oder Aufruf anpassen |
| `gui/mainWaddon/tabSett_Mount.py` | 134 | Default `None` für Parameter mit Typ `Setting` | Annotation auf `Setting \| None = None` |
| `gui/styles/styles.py` | 165 | `hex2rgb(list[int])` erwartet `str` | Annotation auf `str \| list[int]` erweitern |
| `gui/extWindows/measure/measureW.py` | 143 | `constructPlotItem(…, list[float]\|ndarray)` erwartet `list[float]` | Annotation auf `list[float] \| np.ndarray` erweitern |
| `mountcontrol/obsSite.py` | 659, 660 | `abs(tuple[int, float])` – nicht unterstützt | Typen auseinandernehmen: erst `int`, dann `float` |

---

## Kategorie 5 – Falsche Default-Werte (Typ ≠ Default)

Default `None`, aber Annotation schließt `None` nicht ein.

| Datei | Zeile | Parameter | Fix |
|-------|-------|-----------|-----|
| `base/ninaClass.py` | 75 | `params: dict[Any, Any] = None` | → `params: dict[Any, Any] \| None = None` |
| `base/sgproClass.py` | 73 | `params: dict[Any, Any] = None` | → `params: dict[Any, Any] \| None = None` |
| `gui/extWindows/analyseW.py` | 155 | `dtype: dtype[Any] = np.float32` | → `dtype: type \| np.dtype[Any] = np.float32` |
| `gui/utilities/toolsQtWidget.py` | 272 | `buttons: list[str] = None` | → `buttons: list[str] \| None = None` |
| `loader.py` | 79 | `mwGlob: dict[Any, Any] = None` | → `mwGlob: dict[Any, Any] \| None = None` |
| `gui/mainWaddon/tabSett_Mount.py` | 134 | `sett: Setting = None` | → `sett: Setting \| None = None` |

---

## Kategorie 6 – Falsche Variablen-Typ-Annotierungen

Annotierter Typ passt nicht zum zugewiesenen Wert.

| Datei | Zeile | Problem | Fix |
|-------|-------|---------|-----|
| `base/ethernet.py` | 26 | `var: str` ← `list[str]` | Annotation auf `list[str]` ändern |
| `base/indiClass.py` | 218 | `var: str` ← `str \| None` | Annotation auf `str \| None` ändern |
| `gui/extWindows/hemisphere/hemisphereDraw.py` | 124, 125 | `var: tuple[Any,...]` ← `ndarray` | Annotation auf `np.ndarray` ändern |
| `gui/extWindows/hemisphere/horizonDraw.py` | 168, 204, 205 | `var: list[Any]` ← `tuple`; `var: tuple` ← `ndarray` | Annotierungen anpassen |
| `gui/extWindows/satelliteHorW.py` | 121 | `var: int` ← `np.signedinteger` | Annotation auf `int` (NumPy-Integer erbt von int) oder expliziter cast |
| `gui/extWindows/satelliteMapW.py` | 111 | Gleich wie oben | Gleiche Fix-Strategie |
| `gui/mainWaddon/tabAlmanac.py` | 110 | `var: ndarray[...]` ← `list[tuple[...]]` | Annotation auf `list[tuple[float, ...]]` oder ndarray vereinheitlichen |
| `gui/mainWaddon/tabAlmanac.py` | 366 | `var: list[str]` ← `QPixmap` | Annotation auf `QPixmap` ändern |
| `gui/mainWaddon/tabImage_Manage.py` | 234, 239, 249, 266, 271, 281 | `var: str` ← `int` (Rückgabe von `getInt`/`getItem`) | Annotation auf `int` oder `str \| int` |
| `gui/mainWaddon/tabModel_Manage.py` | 258 | `var: list[dict]` ← `dict` | Annotation auf `dict[Any, Any]` oder Zuweisung in Liste einschließen |
| `gui/mainWaddon/tabSat_Track.py` | 177, 386 | `var: int` ← `float` | Annotation auf `float` |
| `gui/mainWaddon/tabSat_Track.py` | 346, 347, 357, 358 | `var: list[Any]` ← `ndarray` | Annotation auf `np.ndarray` |
| `gui/utilities/gPlotBase.py` | 127, 128, 213, 232 | `var: tuple` ← `ndarray`; `var: range` ← `ndarray`; `var: int` ← `float` | Annotierungen an tatsächliche Typen anpassen |
| `logic/buildData/buildpoints.py` | 279 | `var: str` ← `Path` | Annotation auf `Path` |
| `logic/buildData/buildpoints.py` | 295 | `var: list[list]` ← `list[tuple] \| None` | Annotation auf `list[tuple[int,int]] \| None` |
| `logic/buildData/buildpoints.py` | 323 | `var: list[int]` ← `reversed[int]` | Annotation auf `list[int]` (nach `list(reversed(...))`) oder `Iterable[int]` |
| `logic/camera/camera.py` | 145 | `imagePath: Path = ""` (leerer String als Default) | Default auf `Path()` ändern |
| `logic/keypad/keypad.py` | 236, 277, 288, 299, 310, 324 | Diverse: `int`/`str` ← falscher Typ aus Rückgabe | Annotierungen korrigieren |
| `logic/modelBuild/modelRun.py` | 127 | `var: str` ← `Any \| bool` | Annotation auf `str \| bool` |
| `logic/modelBuild/modelRun.py` | 156 | `var: list[Any]` ← `dict` | Annotation auf `dict[Any, Any]` |
| `logic/modelBuild/modelRun.py` | 297–303 | Mehrere `var: Path` ← `str`/`int`/`bool` | Annotierungen auf Union-Typen erweitern oder Zuweisungen in `Path(...)` wrappen |
| `logic/photometry/photometry.py` | 94, 95, 98, 139, 208 | Diverse `None`/`int`/`ndarray`-Mismatches | Variablentypen aus dem Init-Scope auf korrekte Defaults setzen |
| `logic/powerswitch/kmRelay.py` | 146, 149, 194 | Diverse str/list/bool-Mismatches | Annotierungen korrigieren |
| `mainApp.py` | 248 | `deviceStat["mount"] = False`, aber Dict-Wert-Typ ist `None` | `deviceStat` als `dict[str, bool \| None]` annotieren |
| `mountcontrol/connection.py` | 410 | `var: str` ← `list[str]` | Annotation auf `str \| list[str]` |
| `mountcontrol/convert.py` | 43, 46, 66, 204, 246 | `var: str` ← `list[str]`/`list[float]`/`float` | Annotierungen an tatsächliche Typen anpassen |
| `mountcontrol/model.py` | 213 | `var: int` ← `float` | Annotation auf `float` |
| `mountcontrol/setting.py` | 172 | `var: int` ← `str` | Annotation auf `str \| int` |
| `mountcontrol/setting.py` | 178 | `var: str` ← `bool` | Annotation auf `str \| bool` |
| `gui/extWindows/downloadPopupW.py` | 35 | `self.parent` ← `MWidget` (Methode überschrieben) | Typ-Annotation für `self.parent` auf `MWidget` setzen |
| `gui/extWindows/uploadPopupW.py` | 66 | Gleich wie oben | Gleiche Fix-Strategie |
| `logic/photometry/photometry.py` | 56 | `var: Worker` ← `None` | Annotation auf `Worker \| None` |

---

## Kategorie 7 – Fehlende Variablen-Typ-Annotierungen

| Datei | Zeile | Variable | Empfohlene Annotation |
|-------|-------|----------|-----------------------|
| `mainApp.py` | 54 | `messageQueue` | `messageQueue: Queue[tuple[int, str, str, str]]` |
| `gui/extWindows/analyseW.py` | 174 | `model` | `model: dict[str, Any]` |
| `logic/buildData/buildpoints.py` | 339 | `alt` | `alt: float` |
| `logic/buildData/buildpoints.py` | 428 | `celestialEquator` | `celestialEquator: list[tuple[float, float]]` |
| `logic/buildData/buildpoints.py` | 492 | `buildPs` | `buildPs: list[Any]` |
| `logic/file/fileHandler.py` | 147 | `header` | `header: dict[str, Any]` |
| `logic/keypad/keypad.py` | 339 | `result` | `result: list[int]` |
| `logic/modelBuild/modelRunSupport.py` | 97 | `model` | `model: list[dict[str, Any]]` |
| `logic/modelBuild/modelRunSupport.py` | 172, 173, 192 | `pointsIn`, `pointsOut` | `list[Any]` |

---

## Kategorie 8 – Falsche Typ-Annotierungen bei Vererbungs-Overrides

Methoden überschreiben Superklassen-Methoden mit inkompatiblen Signaturen.

| Datei | Zeile | Problem | Fix |
|-------|-------|---------|-----|
| `gui/utilities/toolsQtWidget.py` | 127 | `eventFilter(obj, event)`: Param-Typen nicht kompatibel mit `QObject.eventFilter(QObject, QEvent)` | Parameter-Typen auf `QObject` und `QEvent` anpassen |
| `gui/extWindows/hemisphere/hemisphereDraw.py` | 74 | `close() -> None` override von `QWidget.close() -> bool` | Return-Typ auf `bool` ändern |
| `gui/utilities/gPolarScatter.py` | 29 | `plot() -> bool` override von `NormalScatter.plot() -> None` | Return-Typen angleichen |

---

## Kategorie 9 – `None`-Safety-Fehler (fehlende Null-Guards)

Variablen sind als optional annotiert, werden aber ohne `None`-Prüfung dereferenziert.

| Datei | Zeilen | Typ | Fix |
|-------|--------|-----|-----|
| `logic/file/fileHandler.py` | 58–79, 85, 87, 93–96, 167, 173, 174 | Diverse `None`-Variablen werden indexiert / Methoden aufgerufen | Guard-Checks ergänzen (`if x is not None`) |
| `logic/photometry/photometry.py` | 100, 104, 105, 113–133, 139, 152, 153, 161, 169, 170, 180, 205–208, 213–238, 313, 335 | Variablen mit Typ `None` oder `np.array?` werden ohne Guard verwendet | Initialisierungstypen korrigieren + Guard-Checks |
| `gui/extWindows/hemisphere/hemisphereDraw.py` | 372, 376, 377, 408 | `Any \| None` ohne Guard verwendet | `if x is not None:` guards ergänzen |
| `gui/extWindows/hemisphere/horizonDraw.py` | 85, 87, 169, 206 | `ndarray \| None` ohne Guard indiziert | Guard-Checks ergänzen |
| `gui/extWindows/satelliteMapW.py` | 173, 194, 203, 215 | `Any \| None` – `.at()` ohne Guard | Guard-Checks ergänzen |
| `gui/mainWaddon/tabSat_Search.py` | 118, 119, 121 | `None.dest`, `None.objects` – `satellites`-Attribut ist `None` | `if self.satellites is not None:` Guard ergänzen |
| `gui/mainWaddon/tabSat_Track.py` | 246, 255, 279 | `None.objects` | Gleiche Fix-Strategie |
| `logic/remote/remote.py` | 56, 57, 79, 88, 89, 103, 104, 109 | `QTcpServer \| None` und `QTcpSocket \| None` ohne Guards | `assert`/`if`-Guards ergänzen |
| `gui/extWindows/uploadPopupW.py` | 106 | `re.match(…).group(…)` ohne None-Check | `if m := re.match(…): m.group(…)` Walrus-Operator oder Guard |
| `gui/utilities/toolsQtWidget.py` | 406, 414 | `QWidget \| None` ohne Guard übergeben bzw. aufgerufen | `if widget is not None:` Guards ergänzen |

---

## Kategorie 10 – Sonstige strukturelle Fehler

| Datei | Zeile | Problem | Fix |
|-------|-------|---------|-----|
| `mountcontrol/progStar.py` | 29, 32 | `pierside` zweimal im selben Scope definiert | Doppelte Definition entfernen |
| `logic/camera/cameraIndi.py` | 155, 158, 161 | `HDU` dreimal im selben Scope definiert | Umbenennen zu `HDU_primary`, `HDU_image`, etc. |
| `indibase/indiXML.py` | 912 | Bedingte Funktionsvarianten haben unterschiedliche Signaturen | Signaturen angleichen |
| `gui/extWindows/devicePopupW.py` | 32, 243 | `self.parent` als Methode überschrieben; `QAbstractItemModel.item()` existiert nicht | `parent` als `_parent` umbenennen; `.item()` nur bei `QStandardItemModel` |
| `logic/dome/dome.py` | 196 | `callable` als Typ-Ausdruck verwendet statt als Funktion | `Callable[[...], Any]` verwenden |
| `logic/dome/domeAscom.py` | 52, 60 | Keyword `elementInv` existiert nicht in `storePropertyToData` | `element=` prüfen oder `elementInv` als neuen Parameter hinzufügen |
| `logic/keypad/keypad.py` | 204 | `range(str)` – str statt int | Korrekte Typ-Konversion einfügen |
| `gui/mainWaddon/tabSat_Track.py` | 427 | `TLEParams.flip` existiert nicht; evtl. `_flip` | Attributname prüfen und korrigieren |
| `base/ninaClass.py` / `base/sgproClass.py` | 80/78 | `f"{bytes_var}"` gibt `b'...'` aus, nicht den Inhalt | `.decode('utf-8')` oder `f"{x!r}"` verwenden |
| `mountcontrol/connection.py` | 406 | Gleich wie oben: bytes in f-string | `.decode()` ergänzen |
| `loader.py` | 125 | `memoryview.decode()` existiert nicht | Auf `bytes` casten: `bytes(x).decode()` |
| `logic/modelBuild/modelRunSupport.py` | 146 | `Model` ist nicht iterable | Richtigen Attribut-Zugriff verwenden |
| `gui/utilities/gNormalScatter.py` | 67, 71, 84, 91 | Variable als `int` annotiert, wird aber als Sequence verwendet | Annotierungen auf `int \| Sequence` anpassen |
| `logic/satellites/satellite_calculations.py` | 118 | `Callable[[Any], Any]` hat kein `.step_days` – vermutlich skyfield-EphemerisObject | Annotation auf den konkreten Skyfield-Typ anpassen |
| `mountcontrol/obsSite.py` | 659, 660 | `abs(tuple)` – Typen falsch annotiert | Tuple entpacken oder Annotation auf Einzelwert einengen |

---

## Zusammenfassung

| Kategorie | Fehleranzahl |
|-----------|-------------|
| 1 Syntax-Fehler in Annotierungen | 6 |
| 2 Falsche Typen als Annotierungen | 7 |
| 3 Falsche Rückgabetypen | 15 |
| 4 Falsche Parameter-Typ-Annotierungen | ~90 |
| 5 Falsche Default-Werte | 6 |
| 6 Falsche Variablen-Typ-Annotierungen | ~70 |
| 7 Fehlende Variablen-Typ-Annotierungen | 9 |
| 8 Inkompatible Vererbungs-Overrides | 3 |
| 9 None-Safety ohne Guards | ~80 |
| 10 Strukturelle Fehler | ~20 |
| **Gesamt** | **~306 einzelne Fix-Stellen** |
