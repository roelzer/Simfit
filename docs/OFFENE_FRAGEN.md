# Offene Fragen

## Antworten von Simon (2026-11-04)
- E-1 Datenbank: „keine Ahnung“ → Empfehlung des Teams gilt. E-2 Betriebssystem des Freundes: **iOS** (iPhone) → lokaler Betrieb mit Docker entfällt, Web-App auf einem Server. E-3: **mit Benutzer**, gern Apple-ID oder Google-Konto. E-4: „keine Ahnung“ → Empfehlung (Einrichtungsseite) gilt. E-5: Updates unwichtig, „daten dürfen auf keinen fall verloren gehen“. E-6: **alles deutsch**.
- Offen aus der Startfreigabe, ohne Antwort: Bilanz, Umfang, Zeitraum, Kontakt, Merge nach main, Freigabe `dev-team.json`, „Freigabe zum Bauen“ (noch nicht erteilt).
- Folge: Plan wird neu gedacht (Hosting, Benutzerkonten, Anmeldung, Sicherung, deutsche Namen). Siehe neue Fragen H1–H4 unten.

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

- **F-Zeitraum:** Einstellung „Daten holen: 1 Jahr“ streichen, höchstens 90 Tage je Abruf? – Empfehlung: ja (1 Jahr = rund 1.500 Garmin-Aufrufe, Sperr-Risiko unbekannt). Ohne Antwort: 90 Tage.
- **F-Kontakt:** Welche E-Mail-Adresse von dir geht im User-Agent an Open Food Facts (Pflicht dort)? Ohne Adresse bleibt die Online-Suche aus.

## Fachliche Bestätigungen für Simon
(keine)

## Nur Simon
- [ ] Garmin-Zugangsdaten am Ende selbst eingeben, über die Einrichtungsseite der App (Anleitung kommt mit der Übergabe, Paket P15).
- [ ] BLS-Lizenz lesen (blsdb.de oder mri.bund.de, Nutzungsbedingungen); bis dahin Basis-Lebensmittel aus USDA (CC0).
- [ ] Optional: in den Netzwerk-Einstellungen der Cloud-Umgebung freigeben (eur-lex.europa.eu, mri.bund.de, blsdb.de, fdc.nal.usda.gov, openfoodfacts.github.io, forums.garmin.com), damit Recherche und OFF-Prüfung gegen Primärquellen laufen.
- [ ] Probelauf auf einem frischen Rechner (Startskript bis „Heute zeigt Beispieldaten“) – A6 braucht einen Menschen.
