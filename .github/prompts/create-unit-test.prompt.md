# Unit-Test erstellen

Erstelle einen vollständigen pytest Unit-Test für die angegebene Datei.

## Regeln
- Platziere den Test unter `tests/unit_tests/` mit derselben Ordnerstruktur wie `src/mw4/`
- Verwende `pytest` und `unittest.mock`
- Verwende `pytest-qt` für GUI-Tests (Fixture: `qtbot`)
- Strukturiere jeden Test nach **arrange / act / assert**
- Teste sowohl den Erfolgsfall als auch Fehlerfälle
- Mocke externe Abhängigkeiten (Hardware, Netzwerk, Dateisystem)
- Verwende aussagekräftige Testnamen: `test_<methodenname>_<szenario>`

## Datei
${file}

