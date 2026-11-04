# Simfit

Gilt nur für dieses Projekt. Allgemeine Regeln stehen im Grundgesetz des Dev-Teams.

## Worum geht es
Fitness-App für den Eigenbedarf von Simon: holt die Daten seiner Garmin-Uhr aus Garmin Connect und zeigt sie als Dashboard, dazu Ernährungs-/Kalorientracking und Trainingsplanung. Vollständige Anforderungen, Entscheidungen und offene Punkte: `docs/ANFORDERUNGEN.md` (vor jedem Auftrag lesen).

## Besetzung
**Solo** (Eigenbedarf, ein Nutzer). Für Garmin-Sync und Datenmodell zusätzlich verdeckte Abnahmetests durch den `tester` (Datenverlust, Doppelungen, Zeitzonen, Sperre durch zu viele Logins). Gesundheitsdaten (DSGVO Art. 9): vor der ersten echten Nutzung einmal `sicherheitspruefer` mit Angriffsversuchen. Wird die App für andere Nutzer geöffnet: Besetzung **Kunde**.

## Fachgebiet
Sport und Gesundheit: Trainingssteuerung (Belastung, Erholung, HRV, Pulszonen), Ernährung (Kalorien, Makros, Grundumsatz). Keine medizinischen Aussagen.

## Technik
- Typ: Web-App (Entscheidung Web gegen Mobile noch offen, siehe `docs/ANFORDERUNGEN.md`, Abschnitt 8)
- Vorschlag: Backend Python (FastAPI, wegen garminconnect/garth), Frontend Next.js mit Tailwind + shadcn/ui (Oberflächen-Standard des Dev-Teams), PostgreSQL, Sync-Job
- Setup-, Test- und Zusatzbefehle stehen **nur** in `.claude/dev-team.json` (legt der Projektleiter beim ersten Auftrag fest).

## Architekturregeln
- Datenquellen hinter einer Schnittstelle (`DataSource`; jetzt `GarminCloudSource`, später offizielle API oder Health Connect). Rohdaten und normalisiertes Modell getrennt.
- Garmin schonen: Tokens wiederverwenden, keine Login-Schleifen, Backoff bei HTTP 429. In Tests nie echt bei Garmin anfragen – nur aufgezeichnete Beispieldaten.
- Garmin-Zugangsdaten und Tokens verschlüsselt, nie im Repo, nie im Browser-Code. Simon trägt sie selbst in `.env` ein.
- Datenmodell an genau einer Stelle; Größen mit Einheit im Namen (`distanz_m`, `dauer_s`, `energie_kcal`).
- Lebensmitteldaten: Quellen und Lizenzen getrennt halten; Open-Food-Facts-Attribution auf jeder Ansicht, die diese Daten zeigt.

## Wichtige Dateien
- `docs/ANFORDERUNGEN.md` – Anforderungen und Kontext von Simon (Stand 2026-11-04)
- `docs/lastenheft.md` – Anforderungen A1 … mit Abnahmekriterien (entsteht beim ersten Auftrag)
- `docs/STATUS.md` – Stand beim eigenständigen Bauen
- `docs/OFFENE_FRAGEN.md` – Fragen an Simon und „Nur Simon“-Liste
- `docs/ENTSCHEIDUNGEN.md` – Entscheidungen des Projektleiters
- `.claude/freigaben.md` – Freigaben: technische trägt der Projektleiter nach Kritiker-Prüfung ein, fachliche nur Simon

## Entscheidungslog
Format: `Datum – Entscheidung – Grund`
- 2026-11-04 – Dev-Team eingerichtet, Besetzung Solo – Eigenbedarf, ein Nutzer (Simon)

## Projekt-Lektionen
<!-- Nur was speziell für dieses Projekt gilt. Allgemeines gehört in die Lessons des Dev-Teams. -->
