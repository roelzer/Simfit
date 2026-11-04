# Simfit – Anforderungen und Kontext (Stand 2026-11-04)

Diese Datei ist als Übergabe an einen Entwickler oder KI-Chat gedacht. Sie enthält Ziel, Entscheidungen, Anforderungen, Architekturvorschlag und offene Punkte.

## 1. Ziel

Simfit ist eine Fitness-App, die Daten von einer Garmin-Uhr holt und als Dashboard darstellt. Zusätzlich soll sie Kalorien-/Ernährungstracking und Trainingsplanung enthalten.

- **Phase 1 (MVP):** Nur für den Eigenbedarf des Auftraggebers (ein Nutzer, ein Garmin-Konto).
- **Später:** Optional Mehrnutzerbetrieb. Dafür ist ein anderer Garmin-Zugang nötig (siehe 3.).

## 2. Entscheidungen bisher

| Thema | Entscheidung |
|---|---|
| Datenquelle Phase 1 | Garmin Connect **Cloud**, per inoffizieller Bibliothek (`garminconnect` / `garth`, Python). Kein Garmin-Antrag nötig. |
| Garmin-Zugriff | Hinter einem **austauschbaren Interface** kapseln (siehe 5.), damit andere Quellen später ergänzt werden können. |
| Plattform | Web-App (Entscheidung Web vs. Mobile noch nicht bestätigt, siehe 8.) |
| Repo | `roelzer/simfit`, noch leer, Entwicklungsbranch `claude/lucid-gates-69jllu` |

## 3. Garmin-Datenzugang: Optionen und Einschränkungen

Es gibt keine lokale API in der Garmin-Connect-App. Datenfluss: Uhr → Bluetooth → Garmin Connect App → Garmin Cloud.

1. **Inoffizielle Bibliothek (Phase 1).** Login mit Garmin-Zugangsdaten, Abruf aus der Cloud. Alle Metriken verfügbar. Risiken: nicht offiziell erlaubt, kann bei Garmin-Änderungen brechen, aggressives Rate Limiting (HTTP 429, Sperre 1–24 h bei vielen Login-Versuchen), MFA-Handling nötig.
2. **Offizielle Garmin Connect Developer API** (Health, Activity, Training). Zugang nur nach Prüfung durch Garmin. Das Antragsformular war laut Drittquelle zuletzt pausiert (nicht verifiziert, im Developer Portal prüfen). Stufen: „Personal" (nur eigene Daten, pull) und Business „Starter" (push-only, begrenzte Nutzer). Pflicht für eine öffentliche App.
3. **Health Connect (Android) / Apple Health (iOS).** Garmin Connect schreibt dort einen Teil der Daten hinein (u. a. Schritte, Puls, Schlaf, Workouts; Umfang am Gerät testen). Braucht eine native Mobile App. Weniger Daten: Body Battery, Training Readiness, Training Load, HRV-Details fehlen meist.
4. **Aggregatoren** (z. B. Terra, Open Wearables): schnell, aber laufende Kosten und Abhängigkeit.

**Konsequenz:** Phase 1 über Option 1. Für Mehrnutzerbetrieb später Option 2 und/oder 3 ergänzen.

## 4. Funktionale Anforderungen

### 4.1 Garmin-Sync und Dashboard (MVP-Kern)
- Anbindung an Garmin Connect mit Login inklusive MFA. Tokens persistent speichern und wiederverwenden, um Logins zu minimieren.
- Regelmäßiger Sync (Cron/Job) und manueller Sync-Button, mit Backoff bei 429.
- Daten: Aktivitäten, Schlaf, Ruhepuls und Puls, HRV, Schritte, Stress, Body Battery, Gewicht (falls vorhanden).
- Daten in eigener Datenbank speichern, damit Dashboard und Historie nicht von Live-Abrufen abhängen.
- Dashboard: Tages-, Wochen-, Monatsansicht, Trendcharts.
- Aktivitätsdetails: Karte (GPS), Pace, Puls und Pulszonen, Dauer, Distanz, Höhenmeter.

### 4.2 Ernährung / Kalorien
- Mahlzeiten und Lebensmittel loggen (Frühstück, Mittag, Abend, Snacks), Kalorien und Makros (Kohlenhydrate, Eiweiß, Fett).
- Lebensmittelsuche, Favoriten, zuletzt verwendete, eigene Lebensmittel und Rezepte.
- Barcode-Scan (bei Web-App eingeschränkt, ggf. später).
- Tagesbilanz: Kalorienbedarf (Grundumsatz plus Garmin-Aktivkalorien) gegen Aufnahme.
- Gewichtsverlauf und Kalorienziel (abnehmen / halten / zunehmen).
- Lebensmitteldaten: **Open Food Facts** (Barcodes, Packungsprodukte; ODbL mit Attribution und Share-alike, eigener User-Agent, Rate Limits) und **USDA FoodData Central** (generische Lebensmittel; Lizenz und API-Bedingungen vor Einsatz prüfen). Für deutsche Grundnahrungsmittel ggf. BLS prüfen (Lizenz ungeprüft). Quellen-Lizenzen getrennt halten.

### 4.3 Training
- Trainingsplan erstellen: manuell und regelbasiert nach Ziel, Wochenumfang und Level.
- Plan gegen tatsächlich absolvierte Garmin-Aktivitäten abgleichen (geplant vs. absolviert).
- Belastung und Erholung (Training Load, Readiness aus HRV und Schlaf).

### 4.4 Spätere Funktionen (nicht im MVP)
- Ziele, Streaks, Wochenberichte.
- KI-Coach, der Plan und Ernährung anhand der Daten anpasst.
- Export von Trainings auf die Uhr (nur mit offizieller API möglich).
- Mehrnutzer-Betrieb, Mobile App.

## 5. Architekturvorschlag

- **Backend:** Python (FastAPI) wegen `garminconnect`/`garth`.
- **Frontend:** Next.js oder SvelteKit.
- **Datenbank:** PostgreSQL.
- **Job-Runner:** Cron oder Worker für den periodischen Sync.
- **Datenquellen-Interface:** z. B. `DataSource` mit Implementierungen `GarminCloudSource` (jetzt), später `GarminOfficialSource`, `HealthConnectSource`. Rohdaten und normalisiertes Modell trennen.
- **Secrets:** Garmin-Zugangsdaten und Tokens verschlüsselt speichern, niemals ins Repo.
- Hosting möglichst in der EU.

## 6. Nicht-funktionale Anforderungen

- **Datenschutz:** Gesundheitsdaten sind nach DSGVO Art. 9 besonders geschützt. Bei Eigenbedarf reicht eine saubere private Absicherung. Für Mehrnutzerbetrieb: Einwilligung, Löschkonzept, Datenexport, EU-Hosting.
- **Robustheit:** Sync muss Fehler und Rate Limits tolerieren (Retry mit Backoff, keine Login-Schleifen).
- **Wartbarkeit:** Garmin-Anbindung gekapselt, weil die inoffizielle API brechen kann.
- **Lizenzen:** Attribution für Open Food Facts auf jeder Ansicht, die diese Daten zeigt.

## 7. Grobe Aufwandsschätzung (ein Entwickler)

| Baustein | Aufwand |
|---|---|
| Setup, Backend, Auth, DB | 1 Woche |
| Garmin-Sync und Datenmodell | 1–2 Wochen |
| Dashboard mit Charts | 2 Wochen |
| Kalorientracker | 3–4 Wochen |
| Trainingsplan und Abgleich | 3–4 Wochen |
| **MVP gesamt** | **ca. 10–13 Wochen** |
| Nur Sync + Dashboard | 3–4 Wochen |
| Offizieller Garmin-Zugang | Antragsdauer ungewiss, plus 2–4 Wochen |
| Mobile App zusätzlich | plus 6–10 Wochen |

## 8. Offene Punkte

- Nur Eigenbedarf oder später für andere Nutzer? (Bestimmt den Garmin-Weg.)
- Web-App, Mobile App oder beides? (Annahme bisher: Web.)
- Stack bestätigen (Vorschlag in 5.).
- Alleinstellungsmerkmal gegenüber MyFitnessPal, Garmin Connect, Runalyze, Intervals.icu klären. Vorschlag: Ernährung, Training und Erholung auf einer Oberfläche.
- Aktuellen Status des Garmin Developer Program prüfen.
- Unterstützte Garmin-Geräte und Metriken des Auftraggebers festlegen.

## 9. Quellen

- Garmin Developer Program: https://developer.garmin.com/gc-developer-program/overview
- Terra zur Pausierung des Programms: https://tryterra.co/blog/garmin-connect-developer-program-pause
- garmin-auth (Rate Limits, MFA): https://pypi.org/project/garmin-auth/
- Open Food Facts Lizenz: https://openfoodfacts.github.io/openfoodfacts-server/api/tutorials/license-be-on-the-legal-side
