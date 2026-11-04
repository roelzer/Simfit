# Architektur: Simfit

Geführt vom Agenten `architekt`. Nur er ändert diese Datei. Die prüfbaren Regeln sind als automatische Tests in `tests/architektur/` abgesichert (Python, lesen nur Dateien).

**Stand:** 2026-11-04 (Entwurf, wartet auf Simons Entscheidungen E-1 … E-6) · **Entscheidungen zuletzt geprüft:** –

## 1. Überblick
Eine Einzelnutzer-Instanz pro Person: ein Python-Prozess (FastAPI) liefert die API **und** die fertig gebaute Oberfläche (Next.js, statisch exportiert) unter einer Adresse aus, die Daten liegen in einer SQLite-Datei im Datenordner. Datenfluss Garmin: Datenquelle holt **Rohdaten** → werden unverändert gespeichert → reine Funktionen normalisieren sie → Upsert ins normalisierte Modell → API → Oberfläche. Lebensmittel: Suche lokal plus Open Food Facts über einen Server-Adapter; gewählte Produkte werden mit Quelle und Lizenz lokal gespeichert.

**Grundmuster in einem Satz:** Fachbereiche (Garmin, Ernährung, Training, Datenschutz) als getrennte Pakete mit reinen Rechenmodulen ohne Technik; Garmin-Bibliothek, Open Food Facts, Datenbank und Web sind Adapter am Rand; das Datenmodell liegt an genau einer Stelle.

## 2. Module
Alle Bezeichner im Code englisch mit Einheit im Namen (E-6), Oberfläche und Doku deutsch.

| Modul / Ordner | Zuständig für (ein Satz) | Darf benutzen |
|---|---|---|
| `backend/app/models/` | **Einziger Ort des Datenmodells** (SQLModel-Tabellen), je Fachbereich eine Datei | – |
| `backend/app/core/` | Reine Hilfslogik für alle Bereiche (lokales Datum/Zeitzone, Sportart-Gruppen) | `app.models` |
| `backend/app/settings.py` | Einstellungen aus der Umgebung lesen (`Settings`, `load_settings`) | – |
| `backend/app/db.py` | Engine, Sitzungen, Migrationen ausführen | `app.settings`, `app.models` |
| `backend/app/errors.py` | Fehlerklassen und einheitliche Fehlerantwort | – |
| `backend/app/token_vault.py` | Garmin-Tokens verschlüsselt speichern/laden/löschen | `app.errors` |
| `backend/app/garmin/` | Sync, Datenquellen (`DataSource`), Demo, Garmin-Cloud, Einrichtung, Normalisierung | Basis¹ |
| `backend/app/nutrition/` | Lebensmittel, Suche, Open-Food-Facts-Adapter, Tagebuch, Ziel, Bilanz | Basis¹ |
| `backend/app/training/` | Trainingspläne, Einheiten, Abgleich geplant/absolviert | Basis¹ |
| `backend/app/privacy/` | Export und Löschen aller Daten | Basis¹ |
| `backend/app/main.py` | App-Fabrik `create_app`, Router, Middleware, statische Oberfläche, Hintergrundjobs | alles (Zusammenbau) |
| `backend/migrations/` | Alembic-Migrationen (einziger Weg, das Schema zu ändern) | `app.models` |
| `frontend/src/lib/api/` | `client.ts` (einziger Ort mit `fetch`), je Fachbereich eine Datei mit Typen und Aufrufen | – |
| `frontend/src/components/ui/` | shadcn/ui-Bausteine (generiert, nicht von Hand umbauen) | – |
| `frontend/src/components/<bereich>/` | Bausteine je Fachbereich | `lib/`, `components/ui/` |
| `frontend/src/app/` | Seiten (Routen) | `lib/`, `components/` |

¹ Basis = `app.models`, `app.core`, `app.db`, `app.settings`, `app.errors`, `app.token_vault`.

## 3. Abhängigkeitsregeln (als Test abgesichert)
| Regel | Test |
|---|---|
| Keine Kreis-Abhängigkeiten im Backend (Modulebene) | `test_keine_kreisabhaengigkeiten_im_backend` |
| Reine Module (`app/core/*`, `garmin/normalize.py`, `nutrition/calc.py`, `training/matching.py`) importieren kein fastapi/sqlalchemy/sqlmodel/httpx/garminconnect/os/`app.db`/`app.settings` und lesen die Uhr nicht selbst (`now()`/`today()` verboten, Zeit kommt als Parameter) | `test_reine_fachlogik_kennt_keine_technik` |
| Fachbereiche importieren sich nicht gegenseitig (nur über `app.models`/`app.core`) | `test_fachbereiche_importieren_sich_nicht_gegenseitig` |
| `garminconnect` nur in `app/garmin/connection.py` | `test_a5_garmin_bibliothek_nur_im_verbindungsmodul` |
| Netzwerk-Bibliotheken nur in `app/nutrition/off_client.py` | `test_netzwerkzugriff_nur_in_adaptern` |
| Tabellen nur in `app/models/` | `test_datenmodell_an_genau_einer_stelle` |
| Zahlenfelder tragen die Einheit im Namen (Liste der einheitenlosen Felder im Test) | `test_zahlenfelder_tragen_die_einheit_im_namen` |
| Kein `create_all` im Produktivcode, Schema nur über Alembic | `test_schema_nur_ueber_migrationen` |
| Keine Passwörter/Tokens/Schlüssel in Log- oder print-Aufrufen | `test_a9_keine_geheimnisse_in_logs_oder_ausgaben` |
| Kein nacktes `except:`, kein `except …: pass` | `test_keine_verschluckten_fehler` |
| CORS nie mit `*` oder Regex | `test_a10_cors_nur_fuer_bekannte_herkuenfte` |
| Tests erzeugen nie einen echten Garmin-Client | `test_a9_tests_rufen_garmin_nie_echt_auf` |
| `.env`, Datenbank, Token-Datei, Sicherungen sind von git ausgeschlossen | `test_a7_daten_und_geheimnisse_sind_von_git_ausgeschlossen` |
| Frontend: `fetch` nur in `src/lib/api/client.ts` | `test_a10_netzwerkaufrufe_nur_im_api_client` |
| Frontend: keine `process.env` außer `NEXT_PUBLIC_API_URL`, `NODE_ENV` | `test_a9_keine_geheimnisse_im_browser_code` |
| Frontend: keine externen Adressen/Google Fonts (Ausnahme: Links zu openfoodfacts.org, opendatacommons.org) | `test_a10_keine_externen_ressourcen_im_browser` |

Mehrere Regeln schalten sich selbst scharf, sobald die Zielstruktur existiert (`app/models/`, `backend/migrations/`, `app/garmin/connection.py`, `src/lib/api/client.ts`). Bis dahin gilt der Prototyp-Bestand.

## 4. Datenmodell (AE-5)
Genau ein Ort: `backend/app/models/` (`garmin.py`, `nutrition.py`, `training.py`, `__init__.py` re-exportiert). Das **gesamte Schema dieses Auftrags** wird in P1 angelegt (eine Basis-Migration), damit parallele Pakete keine konkurrierenden Migrationen erzeugen.

| Tabelle (Klasse) | Felder |
|---|---|
| `daily_metrics` (`DailyMetrics`) | `date` PK (lokales Kalenderdatum), `source`, `steps`, `distance_m`, `resting_hr_bpm`, `avg_hr_bpm`, `sleep_s`, `sleep_score`, `hrv_ms`, `stress_avg`, `body_battery_high`, `body_battery_low`, `active_kcal`, `total_kcal`, `weight_kg`, `updated_at` |
| `activity` (`Activity`) | `id`, `source`, `source_id` (eindeutig mit `source`), `type_key`, `name`, `start_time_utc` (mit Zeitzone), `local_date` (Index), `duration_s`, `distance_m`, `avg_hr_bpm`, `max_hr_bpm`, `energy_kcal`, `elevation_gain_m`, `avg_pace_s_per_km`, `updated_at` |
| `raw_record` (`RawRecord`) | `id`, `source`, `kind` (`day`/`activity`), `key` (ISO-Datum bzw. Aktivitäts-ID), `payload_json` (Text), `fetched_at`; eindeutig (`source`,`kind`,`key`) |
| `sync_run` (`SyncRun`) | `id`, `started_at`, `finished_at`, `status` (`running`/`ok`/`error`/`rate_limited`/`auth_required`/`aborted`), `message` (deutsch, ohne Interna), `range_days`, `source`, `next_attempt_after`, `consecutive_rate_limits` |
| `food` (`Food`) | `id`, `name`, `brand`, `kcal_per_100g`, `protein_g_per_100g`, `carbs_g_per_100g`, `fat_g_per_100g`, `barcode`, `origin` (`base`/`custom`/`off`/`usda`), `origin_id`, `license` (z. B. `ODbL-1.0`), `fetched_at`; eindeutig (`origin`,`origin_id`) |
| `food_log_entry` (`FoodLogEntry`) | `id`, `date`, `meal`, `food_id` (FK, `SET NULL`), Momentaufnahme `food_name`, `food_origin`, `kcal_per_100g`, `protein_g_per_100g`, `carbs_g_per_100g`, `fat_g_per_100g`, dazu `amount_g`, `created_at` |
| `nutrition_goal` (`NutritionGoal`) | `id`=1, `target_kcal`, `protein_g`, `carbs_g`, `fat_g` |
| `training_plan` (`TrainingPlan`) | `id`, `name`, `start_date` (Montag), `weeks_count` (1–52), `created_at`, `updated_at` |
| `planned_session` (`PlannedSession`) | `id`, `plan_id` (FK, Löschweitergabe), `date`, `sport` (`running`/`cycling`/`swimming`/`strength`/`walking`/`other`), `title`, `planned_duration_s`, `planned_distance_m`, `notes`, `sort_order` |

Request-/Response-Schemas (Pydantic) liegen im jeweiligen `app/<bereich>/api.py`, nicht im Modell. Eingaben mit `extra="forbid"`.

## 5. Festlegungen
- **AE-1 [ÜBERNOMMEN] Technik:** FastAPI + SQLModel (Python 3.13), Next.js 16 + TypeScript. Bindet: alle Pakete. Verhindert: zweiter Stack. Regel: keine weiteren Web-Frameworks/ORMs.
- **AE-2 Schnitt nach Fachbereichen:** Bindet: Ordnerstruktur Abschnitt 2. Verhindert: Alles-Dateien (`api.py` mit 200 Zeilen für alles) und Kollisionen paralleler Pakete. Regel: Test „Fachbereiche importieren sich nicht“.
- **AE-3 Reine Rechenmodule:** Normalisierung, Nährwert-/Bilanzrechnung, Abgleich, Zeitumrechnung sind reine Funktionen mit Zeit als Parameter. Verhindert: Logik, die nur mit Datenbank/Netz testbar ist; Zeitzonenfehler durch `date.today()` irgendwo. Regel: Test „reine Fachlogik“.
- **AE-4 Datenquelle hinter `DataSource` [ÜBERNOMMEN aus CLAUDE.md]:** Vertrag in `app/garmin/source_base.py`:
  `RawRecord(source: str, kind: Literal["day","activity"], key: str, payload: dict)`;
  `class DataSource(Protocol): name: str; def fetch_days(self, start: date, end: date) -> list[RawRecord]; def fetch_activities(self, start: date, end: date) -> list[RawRecord]; def normalize_day(self, raw: RawRecord) -> DailyMetrics; def normalize_activity(self, raw: RawRecord) -> Activity`.
  Garmin-Tag: `payload = {"stats": dict|None, "sleep": dict|None, "hrv": dict|None, "body": dict|None}` (fehlgeschlagener Teil = `None`); Aktivität: Eintrag aus `get_activities_by_date` unverändert. Verhindert: Garmin-Formate im Rest der App. Regel: Test `garminconnect` nur in `connection.py`.
- **AE-5 Datenmodell an einer Stelle, Einheiten im Namen, Schema nur über Alembic** (Tabelle Abschnitt 4). Schemaänderung nach P1: höchstens **ein** Paket je Meilenstein mit Migration, sonst Eskalation. Regel: drei Modelltests.
- **AE-6 Upsert-Regeln beim Sync:** (a) `None` überschreibt nie einen vorhandenen Wert; (b) stammt die vorhandene Zeile aus einer anderen `source`, wird sie komplett ersetzt (keine Demo-Werte in echten Daten); (c) Aktivitäten eindeutig über (`source`,`source_id`), Tage über `date`; (d) Rohdaten über (`source`,`kind`,`key`) überschrieben. Verhindert: Datenverlust bei teilweise fehlgeschlagenem Abruf (am Prototyp nachgewiesen) und Doppelungen.
- **AE-7 Zeitzonen:** Instanz-Zeitzone `SIMFIT_TIMEZONE` (Standard `Europe/Berlin`). „Heute“ immer `core.time.local_today(now_utc, tz)`. Aktivitäten: `start_time_utc` aus `startTimeGMT`, `local_date` aus `startTimeLocal` (Garmins Ortszeit, keine eigene Umrechnung). API-Filter `from`/`to` sind **lokale** Daten und filtern auf `local_date`. Zeitstempel in der API ISO 8601 mit `Z`.
- **AE-8 Garmin schonen:** nur `connection.py` spricht mit `garminconnect`; der Sync erzeugt den Client **ohne** Zugangsdaten (nur Tokens), dadurch kann der Server kein Passwort-Login auslösen. HTTP 429 → `SourceRateLimited` → Sync bricht **sofort** ab (kein weiterer Aufruf), `next_attempt_after` = jetzt + 15 min × 2^(n−1), höchstens 24 h; vorher lehnt `POST /api/sync` mit 429 und deutscher Meldung ab. 401/abgelehnte Tokens → `SourceAuthFailed` → Status `auth_required`, kein Wiederholen. Nach jedem Lauf werden erneuerte Tokens verschlüsselt zurückgeschrieben. Einrichtung: höchstens 3 Anmeldeversuche pro Stunde.
- **AE-9 Netzwerk nur in Adaptern:** Open Food Facts nur über `app/nutrition/off_client.py` (eigener User-Agent `Simfit/<Version> (<SIMFIT_OFF_CONTACT>)`, Zeitlimit 10 s, Begrenzer 10 Suchen/min und 100 Produktabrufe/min je Prozess, nur Suchbegriff bzw. Barcode verlassen die Instanz). Garmin nur über die Bibliothek in `connection.py`. Tests nie echt im Netz (`httpx.MockTransport`, Fake-Client).
- **AE-10 Lebensmittelquellen getrennt:** jedes `Food` trägt `origin` und `license`; OFF-Daten nur mit sichtbarer Attribution „Daten von Open Food Facts (ODbL)“ mit Link, auf jeder Ansicht, die sie zeigt. USDA bekommt später einen eigenen Adapter mit `origin="usda"`, keine Vermischung. Tagebucheinträge speichern eine Momentaufnahme der Nährwerte.
- **AE-11 Frontend-API-Client:** `src/lib/api/client.ts` (`request<T>`, `ApiError`) ist der einzige Ort mit `fetch`; je Fachbereich eine Datei (`garmin.ts`, `nutrition.ts`, `training.ts`, `system.ts`). Nach der Umstellung auf eine Adresse (P14) ist die Basis-URL leer (gleiche Herkunft).
- **AE-12 Oberfläche:** Tailwind + shadcn/ui nach `wissen/oberflaeche.md` und `docs/DESIGN.md` (Designer). Schrift selbst gehostet, keine externen Ressourcen, keine Produktbilder von OFF (würden die IP des Nutzers an Dritte geben). Alle Seiten sind Client-Seiten und statisch exportierbar (keine Server Actions, keine API-Routen in Next.js, keine dynamischen Routen ohne Export – Detailseiten über `?id=`).
- **AE-13 Fehler:** Fachfehler als Klassen in `app/errors.py` (`AppError(code, message, status)`, Unterklassen `NotFound`, `InvalidInput`, `Conflict`, `SourceNotConfigured`, `SourceRateLimited`, `SourceAuthFailed`, `SourceUnavailable`). Einheitliche Antwort `{"detail": "<deutsche Meldung>", "code": "<kennung>"}`; unerwartete Fehler → 500 mit „Interner Fehler“ ohne Details, Protokoll mit Stacktrace aber ohne Inhalte. Nie verschlucken.

## 6. Öffentliche Schnittstellen (API v1, Vertrag für Pakete und Abnahmetests)
Alle unter `/api`, JSON, Datum `YYYY-MM-DD` (lokal), Zeitstempel ISO 8601 UTC mit `Z`. Felder wie im Modell (Abschnitt 4). Fehler nach AE-13.
- System: `GET /health` → `{status, source: "demo"|"garmin", garmin_connected: bool}`
- Sync: `POST /sync` `{range_days: 1–365}` → `SyncRun` (läuft schon einer: diesen zurück; Sperre aktiv: 429); `GET /sync/status` → `SyncRun|null`
- Garmin-Daten: `GET /daily?from&to` → `DailyMetrics[]` aufsteigend; `GET /activities?from&to&limit` → `Activity[]` neueste zuerst; `GET /activities/{id}`
- Garmin-Verbindung: `GET /garmin/connection` → `{connected, source}`; `POST /garmin/connection` `{email, password}` → `{status: "connected"|"mfa_required"}`; `POST /garmin/connection/mfa` `{code}` → `{status: "connected"}`; `DELETE /garmin/connection` → 204 (Tokens gelöscht, Quelle wieder Demo)
- Ernährung: `GET /foods?q` (lokal, max. 50); `POST /foods` (eigenes, `origin="custom"`); `GET /foods/search?q&online=true` → `{local: Food[], online: OffProduct[], online_error: string|null, attribution: string}`; `GET /foods/barcode/{code}` → `{local: Food|null, online: OffProduct|null}`; `POST /foods/import` `{origin: "off", origin_id}` → `Food`; `GET /food-log?date`; `POST /food-log` `{date, meal, food_id, amount_g}`; `DELETE /food-log/{id}`; `GET /nutrition/day?date` → `{date, eaten: {kcal, protein_g, carbs_g, fat_g}, burned_kcal|null, goal, balance_kcal}`; `GET|PUT /nutrition/goal`
  `OffProduct` = `{origin_id, name, brand, kcal_per_100g, protein_g_per_100g, carbs_g_per_100g, fat_g_per_100g, barcode}`
- Training: `GET|POST /training/plans`; `GET|PUT|DELETE /training/plans/{id}`; `POST /training/plans/{id}/sessions`; `PUT|DELETE /training/sessions/{id}`; `GET /training/plans/{id}/comparison` → `{weeks: [{week_no, start_date, planned_duration_s, done_duration_s, sessions: [{session, status: "done"|"missed"|"today"|"planned", activity: Activity|null}], extra_activities: Activity[]}]}`
- Datenschutz: `GET /privacy/export` → ZIP (`daten.json` je Tabelle, `LIESMICH.txt`; ohne Tokens und Schlüssel); `POST /privacy/delete-all` `{confirm: "ALLES LÖSCHEN"}` → 204

## 7. Konventionen
- **Fehler:** AE-13. Oberfläche zeigt jede Fehlermeldung verständlich mit Ausweg (erneut versuchen / Einstellungen).
- **Konfiguration:** nur Umgebungsvariablen (`SIMFIT_DATA_DIR` Standard `backend/data`, `DATABASE_URL` Standard SQLite im Datenordner, `SIMFIT_SOURCE` = `auto|demo|garmin` (auto: Garmin, wenn Tokens vorhanden), `SIMFIT_TIMEZONE`, `SIMFIT_SECRET_KEY`, `SIMFIT_OFF_CONTACT`, `SIMFIT_AUTO_SYNC_HOURS` Standard 6, 0 = aus, `CORS_ORIGINS` nur für die Entwicklung). Gelesen nur in `app/settings.py`; Tests übergeben `Settings` direkt an `create_app`.
- **Geheimnisse:** `.env` (git-ignoriert); Token-Datei `<data_dir>/secrets/garmin_tokens.enc` (Fernet); Schlüssel nur in der Umgebung, nie im Datenordner, nie im Export.
- **Logging:** Python `logging`, ohne Passwörter, Tokens, Gesundheitswerte, Suchbegriffe.
- **Benennung:** Code englisch, Einheit als Endung (`_m`, `_s`, `_ms`, `_kcal`, `_g`, `_kg`, `_bpm`, `_s_per_km`, `_per_100g`, `_days`); Tests `test_a<Nr>_<was>`.
- **Tests:** Backend pytest mit `backend/tests/helpers.py` (`make_test_app(tmp_path, **overrides)`), Frontend Vitest + Testing Library (happy-dom; Tastatur mit `fireEvent`). Keine echten Netzaufrufe.

## 8. Sicherheits-Grundgerüst
| Thema | Festlegung | Absicherung |
|---|---|---|
| Geheimnisse | Garmin-Tokens nur verschlüsselt im Datenordner, Schlüssel nur in der Umgebung; Passwort wird bei der Einrichtung einmal an Garmin weitergereicht und nie gespeichert oder protokolliert; nichts davon im Browser-Code | Arch-Tests A7/A9, Sicherheits-Schranke, Test in P6 |
| Berechtigung | Einzelnutzer ohne Anmeldung (E-3): Schutz durch Bindung an `127.0.0.1` (Port-Freigabe nur lokal). Wird die Instanz je im Netz erreichbar gemacht, ist vorher eine Anmeldung Pflicht (Eskalation) | Test in P14 (Compose/Start binden nur lokal) |
| Eingaben | Pydantic mit `extra="forbid"`, Längen- und Wertegrenzen (Gramm 0 < x ≤ 5000, Suchbegriff 2–100 Zeichen, Barcode nur Ziffern 8–14), SQL nur über SQLModel/parametrisiert | Tests je Paket |
| Fehler | AE-13 | Arch-Test „verschluckte Fehler“, Tests in P1 |
| Gleichzeitigkeit | Ein Nutzer: kein Versionsfeld. Sync: Prozess-Sperre plus Datenbankprüfung, beim Start werden hängende `running`-Läufe auf `aborted` gesetzt; Schreibvorgänge je Anfrage in einer Transaktion; SQLite im WAL-Modus | Tests in P5 |
| Anmeldung | entfällt lokal (E-3); Garmin-Anmeldeversuche begrenzt (AE-8) | Test in P6 |
| Web | Sicherheits-Header (CSP `default-src 'self'`, `frame-ancestors 'none'`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`); HSTS entfällt bei reinem `http://127.0.0.1`; CORS nur in der Entwicklung für `http://localhost:3000` | Test in P14 |
| Werkzeuge | `bandit` (Python) und `eslint-plugin-security` (Frontend) als Zusatzbefehle, `pip-audit` und `npm audit --audit-level=high` als Sicherheitsbefehl | `.claude/dev-team.json` |
| Daten | Tägliche Sicherung der SQLite-Datei (`sqlite3`-Backup-API) nach `<data_dir>/backups/`, 14 Stück aufbewahren; Wiederherstellung = Datei zurückkopieren (Anleitung); Export und Löschen durch den Nutzer | Tests in P13/P14 |

## 9. Betrieb
- **Umgebungen:** Entwicklung (Backend `uvicorn --reload`, Frontend `next dev`, CORS an) und Instanz beim Freund (ein Prozess, eine Adresse `http://127.0.0.1:8000`).
- **Start beim Freund:** ein Startweg nach E-2 (Empfehlung: Docker Compose, Doppelklick-Skript `Simfit starten`, öffnet den Browser). Beim ersten Start erzeugt das Skript `SIMFIT_SECRET_KEY` in `.env`.
- **Auslieferung:** Simon übergibt den Projektordner (bzw. ein ZIP) – kein öffentliches Image, keine laufenden Kosten.
- **Updates:** offene Frage E-5 (Empfehlung: Skript `Simfit aktualisieren` = neuen Stand holen, neu bauen, Migrationen laufen beim Start automatisch, vorher automatische Sicherung).
- **Datenort:** Docker-Volume bzw. `backend/data/` (DB, Sicherungen, verschlüsselte Tokens).

## 10. Zurückgestellt
USDA-Adapter (Lizenz/API-Schlüssel klären), BLS, Barcode-Scan per Kamera, Favoriten/Rezepte, regelbasierte Plan-Erstellung, Training Load/Readiness, Karte/Pulszonen in Aktivitätsdetails, periodischer Sync außerhalb des laufenden Programms, Mehrnutzerbetrieb und Anmeldung, Versionsfelder für gleichzeitiges Bearbeiten.

## 11. Entscheidungen
`Datum – Entscheidung – Grund – verworfene Alternativen`
- 2026-11-04 – Prototyp bleibt, wird umgebaut (Modell, Router je Fachbereich, Migrationen) – läuft, Tests grün, Garmin-Kapselung als Idee vorhanden – Neuanfang
- 2026-11-04 – Gesamtes Schema in P1 – keine konkurrierenden Alembic-Köpfe bei parallelen Paketen – Migration je Paket
- 2026-11-04 – Architekturtests in Python (ast) für Backend und Frontend – ein Testlauf, keine neuen Pakete – dependency-cruiser/import-linter
