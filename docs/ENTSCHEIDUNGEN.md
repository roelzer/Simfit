# Entscheidungen des Projektleiters

`- Datum | was entschieden | warum | was es kostet, wenn es falsch ist`

## Auftrag: Simfit weiterbauen
- 2026-11-04 | Stufe Groß, Profil web | Gesundheitsdaten, Datenbank, Schnittstellen nach außen, Geheimnisse (Tokens), neue Abhängigkeiten | zu viel Prüfaufwand
- 2026-11-04 | Bestehender Prototyp wird nicht weggeworfen, sondern vom Architekten bewertet | Backend/Frontend laufen und sind geprüft angesehen, aber ohne Test-Schranke gebaut | Umbau, falls der Architekt das Rückgrat ändert
- 2026-11-04 | M4: Die Oberfläche startet den ersten Abruf nach dem Verbinden, nicht das Backend (so in ARCHITEKTUR AE-16, P6, P8, DESIGN) | Eine Stelle, kein doppeltes Holen; mein Auftrag an den Designer war ein Versehen | Bei Abbruch der Seite nach dem Verbinden startet der erste Abruf erst beim nächsten Öffnen oder Knopfdruck
- 2026-11-04 | „Alles löschen“: ganz oder gar nicht nur für die Datenbank; Anmeldung und Sicherungen werden danach gelöscht, bei Fehlschlag meldet die App `delete_incomplete` mit dem Rest | technisch nicht in einer Transaktion möglich | Rest-Dateien bleiben bis zum nächsten Versuch
- 2026-11-04 | Besetzung Kunde, E-1…E-6 und F-Fragen gelten als Annahme nach Empfehlung, bis Simon antwortet | Antwort steht in der Startfreigabe aus | Umbau einzelner Pakete (z. B. Startweg, Datenbank)
