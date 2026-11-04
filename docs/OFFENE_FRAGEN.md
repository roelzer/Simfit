# Offene Fragen

## Fragen an Simon
Alle mit Empfehlung; ohne Antwort gilt die Empfehlung (keine blockiert den Planabschluss).

- **Q1:** Wo läuft die App für den Freund? – Empfehlung: lokal auf seinem Rechner. Ohne Antwort: lokal.
- **Q2:** Besetzung Solo → Kunde? – Empfehlung: Kunde (`CLAUDE.md` sieht das für andere Nutzer vor). Ohne Antwort: Kunde.
- **Q3:** Testbefehl, Setup, Zusatzbefehle in `.claude/dev-team.json` eintragen (nur mit deiner Freigabe) – Vorschlag des Architekten: eigenes Startskript `tests/run_all.py`, das Backend- und Frontend-Tests zählt. Ohne Antwort: es wird nicht gebaut.
- **E-1 Datenbank:** SQLite (Empfehlung; eine Datei, Sicherung = kopieren) statt PostgreSQL (`CLAUDE.md` schlägt es vor; zweiter Dienst beim Freund). Weicht von `CLAUDE.md` ab.
- **E-2 Startweg:** Docker Compose plus Doppelklick-Skript (Empfehlung) / Python-Skript ohne Docker / gemieteter Server. Hängt am Betriebssystem des Freundes: **welches hat er (Windows, Mac)?**
- **E-3 Zugriffsschutz:** nur lokal (127.0.0.1) ohne Anmeldung (Empfehlung) / zusätzliches Passwort. Wird die App je im Netz erreichbar, ist Anmeldung Pflicht.
- **E-4 Garmin einrichten:** Einrichtungsseite im Browser mit MFA (Empfehlung; das Passwort geht einmal an Garmin und wird nie gespeichert) / Konsolen-Dialog / du richtest es beim Freund ein. Weicht von `CLAUDE.md` („Simon trägt sie selbst in `.env` ein“) ab.
- **E-5 Updates:** Skript „Simfit aktualisieren“ mit automatischer Sicherung (Empfehlung) / du bringst ein neues ZIP / keine Updates.
- **E-6 Namen im Code:** Englisch mit Einheit im Namen, z. B. `resting_hr_bpm` (Empfehlung) / Deutsch wie `distanz_m`.
- **F-Bilanz (fachlich):** Was zeigt die Kalorienbilanz an Tagen ohne Garmin-Verbrauchswert? – Empfehlung: keine Bilanz, nur „kein Verbrauch von Garmin vorhanden“ (Design). Bisher im Prototyp: Ziel als Verbrauch gerechnet.
- **F-Umfang (fachlich):** Darf folgendes für diesen Auftrag wegfallen (steht in `docs/ANFORDERUNGEN.md`, aber nicht in A1–A11)? Mengen nur in Gramm (keine ml/Portionen), Gewichtsverlauf, „zuletzt verwendet“, Kalorienziel-Modus (abnehmen/halten/zunehmen), regelbasierte Trainingspläne, Training Load/Readiness, Karte und Pulszonen in Aktivitäten. Empfehlung: ja, später als eigener Auftrag; sonst fehlen sie still.

## Fachliche Bestätigungen für Simon
(keine)

## Nur Simon
- [ ] Garmin-Zugangsdaten am Ende selbst eingeben, über die Einrichtungsseite der App (Anleitung kommt mit der Übergabe, Paket P15).
- [ ] Probelauf auf einem frischen Rechner (Startskript bis „Heute zeigt Beispieldaten“) – A6 braucht einen Menschen.
