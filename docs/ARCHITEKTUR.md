# Architektur: Simfit

Geführt vom Agenten `architekt`. Nur er ändert diese Datei. Die prüfbaren Regeln sind als automatische Tests in `tests/architektur/` abgesichert (Python, lesen nur Dateien).

**Stand:** 2026-11-04, Überarbeitung nach Kritiker (B1–B7), Sicherheitsprüfer (S1–S14) und Rechercheur (Gegenprüfung). **Entscheidungen E-1 … E-6 gelten als [ANNAHME] nach der Empfehlung des Architekten, bis Simon antwortet** (`docs/OFFENE_FRAGEN.md`). Ebenso [ANNAHME]: F-Bilanz nach Empfehlung (AE-17). · **Entscheidungen zuletzt geprüft:** – · Nachgezogen 2026-11-04 (Baupläne P1b–P4): `AppContext`, `garmin/state.py`, `failed_parts`, `choose_source` bis P7 `None`, kein Standardziel, Sync-Thread.

## 1. Überblick
Eine Einzelnutzer-Instanz pro Person: **ein** Python-Prozess (FastAPI, genau ein Worker) liefert die API **und** die statisch exportierte Oberfläche (Next.js) unter `http://127.0.0.1:8000` aus. Daten liegen in einer SQLite-Datei im Datenordner [ANNAHME E-1].
Datenfluss Garmin: Datenquelle holt **Rohdaten** (`SourceRecord`) → `garmin/store.py` führt sie je Teil mit den gespeicherten Rohdaten zusammen → reine Funktionen normalisieren → `store.py` schreibt nach festen Regeln (AE-6) ins normalisierte Modell → API → Oberfläche. Lebensmittel: lokale Suche plus Open Food Facts über einen Server-Adapter; gewählte Produkte werden mit Quelle und Lizenz lokal gespeichert.

**Grundmuster in einem Satz:** Fachbereiche (Garmin, Ernährung, Training, Datenschutz) als getrennte Pakete mit reinen Rechenmodulen ohne Technik; Garmin-Bibliothek, Open Food Facts, Datenbank und Web sind Adapter am Rand; das Datenmodell, der Fehlerkatalog und die Vorgangs-Sperre liegen je an genau einer Stelle.

## 2. Module und Besitz
Alle Bezeichner im Code englisch mit Einheit im Namen [ANNAHME E-6], Oberfläche und Doku deutsch. „Besitz“ = welches Paket die Datei anlegt bzw. ändern darf (Pakettabelle im Plan, Abschnitt 5).

| Modul / Datei | Zuständig für (ein Satz) | Darf benutzen | Besitz |
|---|---|---|---|
| `backend/app/models/` (`types.py`, `garmin.py`, `nutrition.py`, `training.py`, `__init__.py`) | **Einziger Ort des Datenmodells** (SQLModel-Tabellen) und des Spaltentyps `UTCDateTime` | – | P1a |
| `backend/app/core/time.py` | `local_today`, `instance_timezone`, Umrechnung UTC ↔ lokal (rein) | `app.models` | P1a |
| `backend/app/core/sports.py` | `SPORTS`, `sport_for_type_key(type_key) -> Sport` mit Rückfall `"other"` (rein) | – | P1a |
| `backend/app/settings.py` | Einstellungen aus der Umgebung (`Settings`, `load_settings`) – einziger Ort mit `os.environ` | – | P1a |
| `backend/app/db.py` | Engine (WAL, `secure_delete`), Sitzungen, `run_migrations` | `app.settings`, `app.models` | P1a |
| `backend/app/errors.py` | **Fehlerkatalog** `ERROR_CATALOG`, `AppError`, Fehler-Handler (auch 422 ohne Eingabewerte) | – | P1a |
| `backend/app/security.py` | `RequestGuard`: Host-/Origin-Prüfung, JSON-Pflicht, Größenlimit, `no-store` | `app.errors`, `app.settings` | P1a (Header/CSP: P14) |
| `backend/app/locking.py` | **Vorgangs-Sperre** `OperationGate` mit Abbruch-Signal (thread-basiert) | `app.errors` | P1a |
| `backend/app/context.py` | `AppContext(settings, engine, gate, source_override, pending_login)` – **ein** Objekt je Prozess in `app.state.ctx`; `get_ctx(request)`, `instance_tz(ctx, session)`, `today_local(ctx, session)` | `app.settings`, `app.locking`, `app.models`, `app.core`; `DataSource` nur unter `TYPE_CHECKING` | P1a |
| `backend/app/token_vault.py` | Garmin-Tokens verschlüsselt speichern/laden/löschen | `app.errors`, `app.settings` | P6 |
| `backend/app/backup.py` | Sicherung (SQLite-Backup-API), Aufbewahrung, Sicherung vor Migration | Basis¹ | P14 |
| `backend/app/garmin/source_base.py` | Vertrag `SourceRecord`, `DataSource` | `app.models` | P1a |
| `backend/app/garmin/state.py` | **Gemeinsamer Garmin-Zustand** für Sync (P5) und Anmeldung (P6): `load_state`, `backoff_delay`, `register_rate_limit`, `clear_rate_limit`, `active_rate_limit`, `bump_generation` – einziger Ort, der Sperre, Wartezeit und Generationsnummer in `garmin_state` ändert | Basis¹ | P1a |
| `backend/app/garmin/sources.py` | `current_source(ctx)` (P1a), `choose_source(ctx)` und `garmin_connected(ctx)` (Platzhalter in P1a: `None` bzw. `False`, gebaut in P7) | Basis¹, `garmin.*` | P1a → P7 |
| `backend/app/garmin/normalize.py` | Garmin-Rohformat → `DailyMetrics`/`Activity` (rein) | `app.models`, `app.core` | P4 |
| `backend/app/garmin/demo.py` | `DemoSource`: erzeugt Rohdaten im Garmin-Format (rein, schreibt nie selbst) | `source_base`, `normalize`, `app.core` | P4 |
| `backend/app/garmin/read_api.py` | `GET /daily`, `GET /activities`, `GET /activities/{id}` | Basis¹ | P4 |
| `backend/app/garmin/store.py` | **Einziger Schreibweg** für `DailyMetrics`, `Activity`, `RawRecord` (AE-6, B1, B4) | Basis¹, `source_base` | P5 |
| `backend/app/garmin/sync.py` | Sync-Lauf: Sperre, Abbruch, Backoff, Status, Meldungskatalog, Token-Rückschreiben | Basis¹, `store`, `source_base` | P5 |
| `backend/app/garmin/scheduler.py` | `auto_sync_tick` (nur Garmin-Quelle) | Basis¹, `sync`, `sources` | P5 |
| `backend/app/garmin/sync_api.py` | `POST /sync`, `GET /sync/status` | Basis¹, `sync`, `sources` | P5 |
| `backend/app/garmin/connection.py` | **Einziger Ort mit `garminconnect`**: Client-Erzeugung, Fehlerübersetzung (B2) | `app.errors` | P6 |
| `backend/app/garmin/setup.py` | Verbinden, MFA, Trennen, Anmeldezähler, MFA-Zwischenstand im RAM | Basis¹, `connection` | P6 |
| `backend/app/garmin/setup_api.py` | `/garmin/connection` (+ `/mfa`) | Basis¹, `setup` | P6 |
| `backend/app/garmin/garmin_cloud.py` | `GarminCloudSource` (implementiert `DataSource`) | Basis¹, `connection`, `normalize`, `source_base` | P7 |
| `backend/app/nutrition/off_client.py` | Open-Food-Facts-Adapter (einziger Ort mit HTTP zu OFF) | `app.errors` | P3 |
| `backend/app/nutrition/` (`calc.py` rein, `search.py`, `service.py`, `api.py`, `seed_usda.py`, `data/`) | Lebensmittel, Suche, Tagebuch, Ziel, Bilanz | Basis¹, `off_client` | P9 |
| `backend/app/training/` (`matching.py` rein, `service.py`, `api.py`) | Pläne, Einheiten, Abgleich, `GET /training/today` | Basis¹ | P11 |
| `backend/app/privacy/` (`service.py`, `api.py`) | Export, Alles löschen | Basis¹ | P13 |
| `backend/app/main.py` | `create_app`, Middleware, Router, `/health`, Lebenszyklus | alles (Zusammenbau) | P1a; Lebenszyklus P7; Auslieferung P14 |
| `backend/migrations/` | Alembic (einziger Weg, das Schema zu ändern) | `app.models` | P1a, danach AE-5 |
| `backend/tests/helpers.py` | `make_test_app(tmp_path, **overrides)`, `FakeSource` | – | P1a |
| `backend/requirements.in`, `requirements.lock`, `requirements-dev.txt` | Laufzeit-Abhängigkeiten (mit Hashes) und Entwicklungswerkzeuge getrennt | – | P1a |
| `frontend/src/lib/api/` (`client.ts`, `garmin.ts`, `nutrition.ts`, `training.ts`, `system.ts`) | **Frontend-Vertrag**: einziger Ort mit `fetch`, alle API-Typen, Fehlerkennungen | – | P1b |
| `frontend/src/lib/useApi.ts` | Lade-/Fehlerzustand für Seiten | `lib/api` | P1b |
| `frontend/src/lib/format.ts`, `lib/utils.ts` | Formatierer (DESIGN 3.3, Zeit als Parameter), `cn` | – | P2 |
| `frontend/src/components/ui/` | shadcn/ui (generiert, nicht von Hand umbauen) | – | P2 |
| `frontend/src/components/shell/`, `components/common/` | AppShell, SkipLink, DemoBanner, SyncStatus, EmptyState, ErrorState, Gauge, StatusBadge, MetricRow, ChartCard | `lib/`, `ui/` | P2 |
| `frontend/src/components/<bereich>/`, `src/app/<bereich>/` | Bildschirme je Fachbereich | `lib/`, `components/` | P8 (Heute, Aktivitäten, Einstellungen inkl. „Deine Daten“), P10 (Ernährung), P12 (Training) |

¹ Basis = `app.models`, `app.core`, `app.db`, `app.settings`, `app.errors`, `app.locking`, `app.context`, `app.token_vault`.

**Frontend-Übergang M1:** P1b löscht den Prototyp-Code (`lib/api.ts`, `components/{TrendChart,FoodPicker,ActivityList,SyncPanel,State,GoalForm}.tsx`, alle Seiten inkl. `activities/[id]`) und legt schlichte Platzhalter-Seiten `/`, `/activities`, `/nutrition`, `/training`, `/settings` an (P8/P10/P12 ersetzen sie). `app/layout.tsx`, `app/globals.css` und `components/Nav.tsx` gehören **P2** (P2 löscht `Nav.tsx`). `lib/format.ts` schreibt P2 neu.

## 3. Abhängigkeits- und Strukturregeln (als Test abgesichert)
| Regel | Test (`tests/architektur/…`) |
|---|---|
| Keine Kreis-Abhängigkeiten im Backend | `test_keine_kreisabhaengigkeiten_im_backend` |
| Reine Module (`core/*`, `garmin/normalize.py`, `garmin/demo.py`, `nutrition/calc.py`, `training/matching.py`) kennen keine Technik, keine Datenbank, keinen `store`/`sync`, lesen die Uhr nicht | `test_reine_fachlogik_kennt_keine_technik` |
| Fachbereiche importieren sich nicht gegenseitig | `test_fachbereiche_importieren_sich_nicht_gegenseitig` |
| `garminconnect` nur in `garmin/connection.py` | `test_a5_garmin_bibliothek_nur_im_verbindungsmodul` |
| Netzwerk-Bibliotheken nur in `nutrition/off_client.py` und `garmin/connection.py` | `test_netzwerkzugriff_nur_in_adaptern` |
| Tabellen nur in `app/models/`; Zahlenfelder mit Einheit; Schema nur über Alembic | `test_datenmodell_an_genau_einer_stelle`, `test_zahlenfelder_tragen_die_einheit_im_namen`, `test_schema_nur_ueber_migrationen` |
| Kein Passwort, kein MFA-Zwischenstand, kein Token im Datenmodell (S6) | `test_s6_kein_passwort_oder_mfa_zustand_im_datenmodell` |
| Garmin-Tabellen werden nur über `garmin/store.py` (und `privacy/` beim Löschen) geschrieben (B1, B4) | `test_b1_garmin_tabellen_nur_ueber_store_schreiben` |
| Garmin-Client mit Zugangsdaten nur in `connection.begin_password_login` (B2, S6) | `test_b2_garmin_client_mit_passwort_nur_bei_der_einrichtung` |
| Sync, Einrichtung/Trennen, Alles löschen, Sicherung und Migration nutzen die Vorgangs-Sperre (B3, S9) | `test_s9_exklusive_vorgaenge_nutzen_die_sperre` |
| Host-/Origin-Prüfung ist in `create_app` eingebaut; Tests dafür laufen über alle `app.routes` (S1, S3) | `test_s1_host_und_origin_pruefung_eingebaut`, `test_s1_sicherheitstests_ueber_alle_routen_vorhanden` |
| 422 ohne Eingabewerte (S2) | `test_s2_validierungsfehler_ohne_eingabewerte` |
| Fehlerkennungen nur aus dem Katalog; Frontend kennt genau dieselben (B5) | `test_b5_fehlerkennungen_nur_aus_dem_katalog`, `test_b5_fehlerkennungen_backend_und_frontend_gleich` |
| Kein Ausnahmetext in `message`/`detail` (S14) | `test_s14_kein_ausnahmetext_in_meldungen` |
| Kein Fernet-Schlüssel als Literal, kein Standardwert für `SIMFIT_SECRET_KEY` (S7) | `test_s7_kein_schluessel_literal_und_kein_ersatzschluessel` |
| `CORS_ORIGINS` ohne Standard, CORS nie `*`, API-Doku abschaltbar (S11) | `test_s11_cors_ohne_standardherkunft`, `test_a10_cors_nur_fuer_bekannte_herkuenfte`, `test_s11_api_doku_in_auslieferung_aus` |
| SQLite mit `secure_delete` (S4) | `test_s4_sqlite_secure_delete` |
| Lock-Datei mit Hashes, keine Testwerkzeuge zur Laufzeit, Docker installiert mit `--require-hashes` (S5) | `test_s5_abhaengigkeiten_mit_hashes` |
| Start nur mit `--workers 1` und ohne Zugriffsprotokoll (S4, S9) | `test_s9_ein_worker_ohne_zugriffsprotokoll` |
| Compose mit `name: simfit`, Ports nur `127.0.0.1`, Log-Rotation (S7) | `test_s7_compose_fester_name_und_nur_lokal` |
| `.dockerignore` schließt Daten und Geheimnisse aus (S13) | `test_s13_dockerignore_schliesst_daten_aus` |
| Keine Geheimnisse in Logs/print; keine verschluckten Fehler; Tests rufen Garmin nie echt; Daten von git ausgeschlossen | `test_a9_keine_geheimnisse_in_logs_oder_ausgaben`, `test_keine_verschluckten_fehler`, `test_a9_tests_rufen_garmin_nie_echt_auf`, `test_a7_daten_und_geheimnisse_sind_von_git_ausgeschlossen` |
| Frontend: `fetch` nur in `lib/api/client.ts`; kein `process.env` außer erlaubten; keine externen Ressourcen; keine Backend-Importe | `test_a10_netzwerkaufrufe_nur_im_api_client`, `test_a9_keine_geheimnisse_im_browser_code`, `test_a10_keine_externen_ressourcen_im_browser`, `test_seiten_und_bausteine_importieren_keine_backend_interna` |
| Frontend: Fehler-`detail` nie als JSON anzeigen (S2); kein `dangerouslySetInnerHTML`/`innerHTML`/`eval` | `test_s2_fehlerdetail_nie_als_json_anzeigen`, `test_keine_html_injektion` |
| Frontend: keine festen Farben außerhalb `globals.css` (DESIGN 10.3) | `test_design_keine_festen_farben` |

Regeln, deren Zielstruktur noch nicht existiert, **schalten sich selbst scharf**, sobald sie entsteht (z. B. `app/settings.py`, `app/garmin/store.py`, `def create_app`, `Dockerfile`, `frontend/src/components/ui/`). Bis dahin gilt der Prototyp-Bestand.

## 4. Datenmodell (AE-5)
Genau ein Ort: `backend/app/models/`. Das **gesamte Schema dieses Auftrags** entsteht in P1a als eine Basis-Migration. Alle Zeitstempel mit Spaltentyp `UTCDateTime` (`models/types.py`): schreibt UTC, liest mit `tzinfo=UTC`; API serialisiert ISO 8601 mit `Z`.

| Tabelle (Klasse) | Felder |
|---|---|
| `daily_metrics` (`DailyMetrics`) | `date` PK (lokales Kalenderdatum aus Garmins `calendarDate`), `source` (`garmin`/`demo`), `steps`, `distance_m`, `resting_hr_bpm`, `avg_hr_bpm`, `sleep_s`, `sleep_score`, `hrv_ms`, `stress_avg`, `body_battery_high`, `body_battery_low`, `active_kcal`, `total_kcal`, `weight_kg`, `updated_at` – alle Messwerte nullable |
| `activity` (`Activity`) | `id`, `source`, `source_id` (eindeutig mit `source`), `type_key` (**Originalschlüssel von Garmin**, unverändert), `name` (≤ 200), `start_time_utc`, `local_date` (Index), `duration_s`, `distance_m`, `avg_hr_bpm`, `max_hr_bpm`, `energy_kcal`, `elevation_gain_m`, `avg_pace_s_per_km`, `updated_at` |
| `raw_record` (`RawRecord`) | `id`, `source`, `kind` (`day`/`activity`), `key`, `payload_json`, `fetched_at`; eindeutig (`source`,`kind`,`key`) |
| `sync_run` (`SyncRun`) | `id`, `started_at`, `finished_at`, `status` (`running`/`ok`/`error`/`rate_limited`/`auth_required`/`aborted`), `message` (nur aus Meldungskatalog), `range_days`, `source`, `incomplete_days` |
| `garmin_state` (`GarminState`, genau eine Zeile `id=1`) | `token_generation` (int), `ever_connected` (bool), `auth_required` (bool), `rate_limited_until` (nullable), `consecutive_rate_limits` (int), `timezone` (IANA-Name aus dem Garmin-Profil, nullable), `demo_loaded_at` (nullable) |
| `garmin_login_attempt` (`GarminLoginAttempt`) | `id`, `attempted_at` |
| `food` (`Food`) | `id`, `name` (≤ 200), `brand`, `kcal_per_100g`, `protein_g_per_100g`, `carbs_g_per_100g`, `fat_g_per_100g`, `barcode`, `origin` (`usda`/`custom`/`off`), `origin_id`, `license` (`CC0-1.0`/`ODbL-1.0`/`null` bei eigenen), `fetched_at`; eindeutig (`origin`,`origin_id`) |
| `food_log_entry` (`FoodLogEntry`) | `id`, `date`, `meal` (`breakfast`/`lunch`/`dinner`/`snack`), `food_id` (FK, `SET NULL`), Momentaufnahme `food_name`, `food_origin`, `kcal_per_100g`, `protein_g_per_100g`, `carbs_g_per_100g`, `fat_g_per_100g`, `amount_g`, `created_at` |
| `nutrition_goal` (`NutritionGoal`) | `id`=1, `target_kcal`, `protein_g`, `carbs_g`, `fat_g` – **keine Zeile = kein Ziel** (kein Standardwert, entsteht beim ersten `PUT /nutrition/goal`) |
| `training_plan` (`TrainingPlan`) | `id`, `name`, `start_date` (Montag), `weeks_count` (1–52), `created_at`, `updated_at` |
| `planned_session` (`PlannedSession`) | `id`, `plan_id` (FK, Löschweitergabe), `date`, `sport` (`running`/`cycling`/`swimming`/`strength`/`walking`/`other`), `title`, `planned_duration_s`, `planned_distance_m`, `notes` (≤ 500), `sort_order` |

Request-/Response-Schemas liegen im jeweiligen `api.py`, nicht im Modell. Eingaben mit `extra="forbid"`. Fremddaten (Garmin, OFF) vor dem Speichern: `math.isfinite`, Wertebereiche, Texte gekürzt.

## 5. Festlegungen
- **AE-1 [ÜBERNOMMEN] Technik:** FastAPI + SQLModel (Python 3.13), Next.js 16 + TypeScript, SQLite [ANNAHME E-1]. *Bindet:* alle Pakete. *Verhindert:* zweiter Stack. *Regel:* keine weiteren Web-Frameworks/ORMs, neue Pakete nur über die Abhängigkeits-Schranke.
- **AE-2 Schnitt nach Fachbereichen:** *Bindet:* Abschnitt 2. *Verhindert:* Alles-Dateien und Kollisionen paralleler Pakete. Je Garmin-Teilpaket eine eigene Router-Datei (`read_api`, `sync_api`, `setup_api`); P1a legt alle Router leer an und registriert sie, später ändert niemand `main.py` außer P7 (Lebenszyklus) und P14 (Auslieferung). *Regel:* Test „Fachbereiche importieren sich nicht“.
- **AE-3 Reine Rechenmodule:** Normalisierung, Demo-Erzeugung, Nährwert-/Bilanzrechnung, Abgleich, Zeitumrechnung sind reine Funktionen; Zeit kommt als Parameter (`Settings.clock() -> datetime` mit UTC). *Regel:* Test „reine Fachlogik“.
- **AE-4 Datenquelle hinter `DataSource` [ÜBERNOMMEN aus CLAUDE.md], B5:** Vertrag in `app/garmin/source_base.py`. Die Rohdaten-Dataclass heißt **`SourceRecord`** (die Tabelle heißt `RawRecord`):
  `SourceRecord(source: str, kind: Literal["day","activity"], key: str, payload: dict, failed_parts: tuple[str, ...] = ())` (frozen)
  **`failed_parts`** unterscheidet zwei Fälle, die im `payload` beide `None` sind: Teil **fehlt** (Garmin 404 bzw. Demo erzeugt ihn nicht) → `None`, nicht in `failed_parts`; Teil **gescheitert** (Fehler außer 404) → `None` **und** Name in `failed_parts` (`"stats"|"sleep"|"hrv"|"body"`). Nutzen: `store` (P5) führt beide Fälle gleich zusammen (AE-6 e, vorhandener Teil bleibt), `sync` (P5) zählt nur gescheiterte Teile für `incomplete_days` und „alle Teile aller Tage gescheitert → `error`“ (AE-8). Normalisierung (P4) ignoriert `failed_parts`.
  `class DataSource(Protocol): name: Literal["garmin","demo"]; def fetch_day(self, day: date, cancel: CancelToken) -> SourceRecord; def fetch_activities(self, start: date, end: date, cancel: CancelToken) -> list[SourceRecord]; def normalize_day(self, rec: SourceRecord) -> DailyMetrics; def normalize_activity(self, rec: SourceRecord) -> Activity; def save_session(self) -> None`.
  Tagesformat (Garmin **und** Demo): `payload = {"stats": dict|None, "sleep": dict|None, "hrv": dict|None, "body": dict|None}`, fehlgeschlagener Teil = `None`; Aktivität = Eintrag aus `get_activities_by_date` unverändert. Die Demo-Quelle erzeugt genau dieses Format (nutzt dieselbe Normalisierung). `save_session()` sichert erneuerte Tokens (Demo: nichts). *Regel:* Test `garminconnect` nur in `connection.py`.
- **AE-5 Datenmodell an einer Stelle, Einheiten im Namen, Schema nur über Alembic** (Abschnitt 4). Nach P1a höchstens **ein** Paket je Meilenstein mit Migration, sonst Eskalation. Migration läuft beim Start im Lebenszyklus, vor allen Hintergrundjobs, unter der Vorgangs-Sperre; ab P14 mit Sicherung davor (S8).
- **AE-6 Schreibregeln Garmin-Daten (B1, B4) – nur in `garmin/store.py`:**
  (a) Gleiche Quelle: `None` überschreibt nie einen vorhandenen Wert.
  (b) **Rangfolge `garmin` vor `demo`:** Ein Garmin-Datensatz ersetzt eine Demo-Zeile vollständig. **Ein Demo-Datensatz verändert oder ergänzt nie eine Garmin-Zeile**, und ein Demo-Lauf wird abgelehnt (`demo_blocked`), sobald eine Zeile mit `source="garmin"` existiert oder `garmin_state.ever_connected` wahr ist.
  (c) Der **erste Garmin-Lauf löscht alle `source="demo"`-Zeilen** (Tage, Aktivitäten, Rohdaten) in derselben Transaktion wie den ersten Schreibvorgang – danach tauchen keine Demo-Aktivitäten im Plan-Abgleich auf.
  (d) Aktivitäten eindeutig über (`source`,`source_id`), Tage über `date`.
  (e) **Rohdaten je Teil zusammenführen:** bei `kind="day"` ersetzt ein neuer Teil `None` nie einen vorhandenen Teil; bei `kind="activity"` wird ersetzt.
  *Verhindert:* Datenverlust durch Demo (B1) und durch Teil-Lücken (B4), Doppelungen. *Regel:* Test „Garmin-Tabellen nur über store“.
- **AE-7 Zeitzonen (B7):** Instanz-Zeitzone = **Zeitzone des Garmin-Profils** (`get_user_timezone()`, garminconnect 0.3.20, beim Verbinden in `garmin_state.timezone` gespeichert), Rückfall `SIMFIT_TIMEZONE` (Standard `Europe/Berlin`), ungültiger Name → Rückfall. `core.time.instance_timezone(state_tz, settings_tz) -> ZoneInfo`; „heute“ immer `core.time.local_today(now_utc, tz)`. Aktivitäten: `start_time_utc` aus `startTimeGMT`, `local_date` aus `startTimeLocal`. API-Filter `from`/`to` sind lokale Daten. `/health` liefert `timezone`, die Oberfläche formatiert damit (nicht mit der Browser-Zeitzone). Pflicht-Testfälle für `local_today` in Europe/Berlin: `2026-03-29T22:30Z → 2026-03-30` und `2026-10-25T22:30Z → 2026-10-25` (beide scheitern bei fest UTC+1 bzw. fest UTC+2).
- **AE-8 Garmin schonen (B2, Recherche):**
  - Nur `connection.py` spricht mit `garminconnect`. Der Sync-Client entsteht mit `open_token_client(tokens_json)` **ohne E-Mail und Passwort** (`Garmin()` ohne Argumente, dann `login(tokenstore=<entschlüsselter JSON-Text>)`, nie Pfad, nie Umgebungsvariable `GARMINTOKENS`) – so kann die Bibliothek keinen Passwort-Login auslösen. Nur `begin_password_login(email, password)` erzeugt einen Client mit Zugangsdaten.
  - **Fehlerübersetzung `translate_error(exc) -> AppError`:** Die gesamte Ursachenkette (`__cause__`, `__context__`) wird durchsucht. Findet sich dort `GarminConnectTooManyRequestsError`, Status 429 oder 427 oder der Text „429“, gilt **`garmin_rate_limited`**, auch wenn außen `GarminConnectAuthenticationError` steht. Nur ein AuthError ohne 429 in der Kette → `garmin_auth_required`. Verbindungs-/Serverfehler und 403 → `garmin_unavailable`. 404 bei einem Teilabruf → Teil `None`.
  - **Backoff [Betriebsparameter, unbelegt]:** `rate_limited_until = jetzt + 1 h × 2^(n−1)`, höchstens 24 h (n = `consecutive_rate_limits`, zurück auf 0 nach einem erfolgreichen Lauf). Gilt für Sync **und** Anmeldung (ein gemeinsamer Zustand in `garmin_state`). Vorher lehnen `POST /sync` und `POST /garmin/connection` mit 429 und `retry_after` ab, ohne Garmin anzufragen.
  - 429 → Lauf bricht **sofort** ab, kein weiterer Aufruf (bekannte Ausnahme: die Bibliothek wiederholt den Profilabruf intern bis zu 3-mal – darum genau ein Token-Login je Lauf).
  - **Takt [Betriebsparameter, unbelegt]:** Pause 1 s + Zufall 0–1 s zwischen Garmin-Aufrufen (`Settings.garmin_call_pause_s`, in Tests 0); neueste Tage zuerst; je Tag eine eigene Transaktion; ein Lauf höchstens `SYNC_MAX_DAYS` = 90 Tage [ANNAHME, F-Zeitraum].
  - Alle Teile aller Tage gescheitert (laut `SourceRecord.failed_parts`, 404-Lücken zählen nicht) → Status `error`; einzelne Teile gescheitert → `ok` mit `incomplete_days`.
  - Anmeldeversuche: höchstens 3 je Stunde, gezählt in `garmin_login_attempt` (überlebt Neustarts); MFA-Codes höchstens 3 je offenem Vorgang.
  - Auto-Sync (`SIMFIT_AUTO_SYNC_HOURS`, Standard 6, 0 = aus): **nur mit Garmin-Quelle**, Zeitraum 3 Tage, übersprungen bei `rate_limited_until > jetzt`, `auth_required`, belegter Sperre oder fehlender Quelle.
- **AE-9 Netzwerk nur in Adaptern (Recherche):** OFF nur über `nutrition/off_client.py`: User-Agent `Simfit/<Version> (<SIMFIT_OFF_CONTACT>)` mit **Simons Projektadresse** (nicht der des Freundes; leer → Online-Suche aus, `off_not_configured`); Zeitlimit 10 s; Antwortgröße begrenzt; Begrenzer je Prozess **10 Suchen/min und 15 Produktabrufe/min** (Doku-Stand 26.04.2026, konfigurierbar); `origin_id`/Barcode nur Ziffern 8–14, Adresse mit Pfad-Escaping. Barcode-Abruf über API **v3**, sofern der Projektleiter es vor dem Bau von P3 mit einem echten Aufruf bestätigt (sonst v2; Ergebnis in den Bauplan). Feldnamen (`energy-kcal_100g` usw.) ebenso vorher am echten Aufruf prüfen. Garmin nur über `connection.py`. Tests nie echt im Netz.
- **AE-10 Lebensmittelquellen getrennt:** jedes `Food` trägt `origin` und `license`. Basis-Lebensmittel aus **USDA FoodData Central (CC0-1.0)**, `origin="usda"`, deutscher Anzeigename, Quellenangabe „USDA FoodData Central“ in der Ansicht – bis Simon die BLS-Lizenz bestätigt; die alten Seed-Werte des Prototyps (Herkunft unklar) entfallen. OFF-Daten nur mit sichtbarer Attribution „Daten von Open Food Facts (ODbL)“ mit Link. OFF-Suche **nur auf Knopf/Enter**, nie bei Tipppause. Tagebucheinträge speichern eine Momentaufnahme.
- **AE-11 Frontend-Vertrag (B5):** `src/lib/api/client.ts` (`request<T>`, `requestBlob`, `ApiError {status, code, detail, retryAfter, field}`, Typ `ApiErrorCode` = genau die Kennungen aus `ERROR_CATALOG` plus `network_error`) ist der einzige Ort mit `fetch`; je Fachbereich eine Datei mit allen Typen und Aufrufen (`garmin.ts`, `nutrition.ts`, `training.ts`, `system.ts`). P1b schreibt alle Dateien vollständig (dünne Aufrufe, keine Platzhalter); spätere Pakete ändern sie nur zusammen mit der passenden Backend-Änderung. Basis-URL leer (gleiche Herkunft), in der Entwicklung `NEXT_PUBLIC_API_URL`.
- **AE-12 Oberfläche:** Tailwind + shadcn/ui nach `docs/DESIGN.md`. Schrift selbst gehostet, keine externen Ressourcen, keine Produktbilder von OFF. Alle Seiten statisch exportierbar (keine Server Actions, keine Next-API-Routen, Detailseiten über `?id=`). Der Prototyp-Frontend-Code (Seiten, `components/*.tsx`, `lib/api.ts`) entfällt in P1b; die neuen Seiten bauen P8/P10/P12 nach DESIGN.
- **AE-13 Fehler (B5, S2, S14):** Genau ein Katalog `ERROR_CATALOG: dict[str, tuple[int, str]]` in `app/errors.py` (Kennung → HTTP-Status, deutsche Standardmeldung). `AppError(code, *, message=None, retry_after=None, field=None)`; unbekannte Kennung = Programmierfehler. Antwort immer `{"detail": str, "code": str, "retry_after": "…Z"|null, "field": str|null}`. 422-Handler: nur Feldname, **nie `input`/`ctx`**, Protokoll nur Feldnamen. Unerwartet → 500 `internal_error` ohne Details, Protokoll mit Stacktrace ohne Inhalte. Meldungen in `sync_run.message` nur aus einem festen Katalog in `sync.py`, nie Ausnahmetexte. Nie verschlucken.
  Katalog (Pflichtinhalt; weitere Kennungen nur mit Änderung dieser Liste):

  | Kennung | HTTP | `retry_after` |
  |---|---|---|
  | `not_found` | 404 | |
  | `invalid_input` | 422 | (`field`) |
  | `unsupported_media_type` | 415 | |
  | `payload_too_large` | 413 | |
  | `bad_host` | 400 | |
  | `forbidden_origin` | 403 | |
  | `conflict` | 409 | |
  | `operation_busy` | 409 | |
  | `confirm_mismatch` | 422 | |
  | `delete_incomplete` | 500 | |
  | `internal_error` | 500 | |
  | `demo_blocked` | 409 | |
  | `garmin_not_connected` | 409 | |
  | `garmin_auth_required` | 409 | |
  | `garmin_credentials_rejected` | 400 | |
  | `garmin_mfa_invalid` | 400 | |
  | `garmin_mfa_expired` | 409 | |
  | `garmin_login_limit` | 429 | ja |
  | `garmin_rate_limited` | 429 | ja |
  | `garmin_unavailable` | 503 | |
  | `garmin_secret_missing` | 503 | |
  | `garmin_tokens_unreadable` | 409 | |
  | `off_rate_limited` | 429 | ja |
  | `off_unavailable` | 503 | |
  | `off_not_configured` | 503 | |
- **AE-14 Vorgangs-Sperre (B3, S9):** `app/locking.py`: `OperationGate.exclusive(name: str, *, preempt: bool = False, wait_s: float = 60.0) -> ContextManager[CancelToken]`, `CancelToken.raise_if_cancelled()` → `OperationAborted`; eine Instanz je Prozess in `app.state.gate`; Prozess läuft mit genau einem Worker.
  - **Ausführung (P5):** Der Sync läuft in **einem Hintergrund-Thread** (`threading.Thread`, `daemon=True`), nicht in FastAPI-`BackgroundTasks`. `start_sync(ctx, range_days) -> SyncRun` startet den Thread und **wartet, bis der Lauf gestartet ist** (Sperre erhalten und `SyncRun` mit `running` gespeichert, oder Fehler beim Start) – erst dann antwortet `POST /sync`; ein Fehler vor dem Start (`operation_busy`, `garmin_rate_limited` …) kommt als `AppError` beim Aufrufer an. `execute_sync(ctx, source, range_days) -> SyncRun` ist derselbe Lauf **synchron** (ohne Thread) für Tests und für den Auto-Sync-Takt. Die Sperre ist thread-basiert (AE-14), Sitzungen werden je Thread neu geöffnet, nie zwischen Threads geteilt.
  - **Garmin-Zustand an einer Stelle:** Sperre bis (`rate_limited_until`), Zähler, Generationsnummer werden nur über `app/garmin/state.py` geändert (P5 und P6 nutzen dieselben Funktionen).
  - **Sync** (Hand und Auto): `preempt=False, wait_s=0`; hält die Sperre vom Anlegen des `SyncRun` bis zum Ende; prüft das Abbruch-Signal vor jedem Garmin-Aufruf und vor jedem Schreiben; Abbruch → Status `aborted`, bereits gespeicherte Tage bleiben.
  - **Verbinden, MFA, Trennen, Alles löschen:** `preempt=True` – brechen einen laufenden Sync ab und warten auf ihn (bis 60 s, sonst `operation_busy`).
  - **Sicherung und Migration:** warten (`preempt=False`).
  - **Token-Rückschreiben (Generationsnummer):** Der Sync merkt sich `token_generation` beim Start und ruft `source.save_session()` nur, wenn er **nicht** abgebrochen wurde, die Generation unverändert ist und die Token-Datei noch existiert – alles innerhalb der Sperre. Verbinden, Trennen und Alles löschen erhöhen die Generation.
- **AE-15 Demo-Betrieb (B1, A7):**
  - Quellenwahl `choose_source(ctx: AppContext) -> DataSource | None` in `garmin/sources.py`; **bis P7 Platzhalter, gibt immer `None` zurück** (dann `/health` → `source: "none"`; Tests setzen die Quelle über `ctx.source_override`). Ab P7: Tokens lesbar → Garmin. Sonst `ever_connected` oder Garmin-Zeilen vorhanden → `None` („nicht verbunden“, kein Abruf). Sonst → Demo. `SIMFIT_SOURCE=demo|garmin` erzwingt nur für die Entwicklung, AE-6 (b) gilt trotzdem.
  - Demo-Daten entstehen nur (1) **einmal beim allerersten Start** (DB ohne Tage, `ever_connected` falsch, `demo_loaded_at` leer) und (2) durch ausdrücklichen `POST /sync` im Demo-Zustand. Nie durch den Auto-Sync.
  - **Trennen:** Tokens weg, Generation +1, `ever_connected` bleibt wahr → Zustand „nicht verbunden“, keine Demo-Daten, Garmin-Tage bleiben unverändert.
  - **Alles löschen:** setzt `ever_connected` falsch, `demo_loaded_at` = jetzt (kein automatisches Neubefüllen), Generation +1; **behält** `rate_limited_until`, `consecutive_rate_limits` und die Anmeldeversuche (keine Gesundheitsdaten, schützen das Garmin-Konto).
- **AE-16 Einrichtung im Browser [ANNAHME E-4] (S6):** MFA-Zwischenstand (Bibliotheks-Objekt mit Passwort und Sitzungs-Cookies) **nur im Arbeitsspeicher** (`app.state`), höchstens ein offener Vorgang, verfällt nach **10 min**, wird verworfen bei Erfolg, Fehler, Ablauf und wenn sich die Generation geändert hat (Trennen, Alles löschen). Nie in DB, Datei, Log, `repr`. Nach Erfolg wird das Einrichtungs-Objekt verworfen; danach nur noch Token-Client. Beim Verbinden: Zeitzone aus dem Profil lesen (AE-7), Generation +1, `ever_connected` wahr. Den ersten Abruf (30 Tage) startet die Oberfläche (`POST /sync`), nicht das Backend (DESIGN M4).
- **AE-17 Kalorienbilanz (B6) [ANNAHME F-Bilanz]:** `burned_kcal` = `total_kcal` des Tages (Garmin: aktiv + Grundumsatz), sonst `null`. `balance_kcal = eaten_kcal − burned_kcal`, **`null`, wenn kein Garmin-Verbrauch vorliegt** – das Ziel wird nie als Verbrauch gerechnet. Für den laufenden Tag `burned_partial = true` (Wert wächst bis Tagesende; Oberfläche zeigt „bisher“). Energiefaktoren 4/4/9 kcal/g (EU 1169/2011, Anhang XIV) im Ziel-Dialog.
- **AE-18 Sportarten (Recherche):** `core.sports.sport_for_type_key(type_key)` ordnet Garmins `typeKey` den 6 Sportarten zu (Tabelle aus `fachwissen/recherche/simfit-grundlagen.md` Abschnitt 3 inkl. `indoor_hand_cycling`, `wheelchair_push_*`); **unbekannt → `other`**; gespeichert wird immer der Originalschlüssel (`activity.type_key`), die Gruppe wird beim Lesen berechnet.
- **AE-19 Grenze Browser ↔ App (S1, S3, S11):** `RequestGuard` (in `create_app`, vor allen Routen):
  - `Host` muss in `Settings.allowed_hosts` stehen (Standard `127.0.0.1:<port>`, `localhost:<port>`), sonst 400 `bad_host` – für **jede** Anfrage, auch GET und statische Dateien.
  - Schreibende Methoden (alles außer GET/HEAD/OPTIONS): `Origin`, falls gesendet, muss `http://<erlaubter Host>` oder eine Entwicklungs-Herkunft aus `CORS_ORIGINS` sein, sonst 403 `forbidden_origin`; `Sec-Fetch-Site: cross-site` → 403; `Content-Type` muss `application/json` sein, sonst 415 – auch ohne Körper (der Client sendet immer JSON; `POST /sync` hat einen Pflicht-Körper).
  - Körper > 1 MB → 413. Jede `/api`-Antwort mit `Cache-Control: no-store` und `X-Content-Type-Options: nosniff`.
  - CORS nur in der Entwicklung (`CORS_ORIGINS` ohne Standardwert); `docs_url`/`openapi_url` nur, wenn `Settings.api_docs` an (Standard aus).
  - Paket-Tests zählen alle schreibenden Routen über `app.routes` auf, damit neue Routen automatisch mitgeprüft werden.
- **AE-20 Löschen und Reste (S4, M2):** `PRAGMA secure_delete=ON` und WAL bei jeder Verbindung. „Alles löschen“ (unter Sperre, `preempt=True`): (1) eine DB-Transaktion löscht alle Inhaltstabellen und setzt `garmin_state` nach AE-15 – scheitert sie, ist **nichts** gelöscht; (2) Token-Datei löschen; (3) alle Sicherungen in `backups/` löschen; (4) `wal_checkpoint(TRUNCATE)` und `VACUUM`. Scheitert (2)–(4) → 500 `delete_incomplete` mit Angabe, was noch da ist. Export: ZIP mit `daten.json` je Inhaltstabelle (inkl. Rohdaten), `LIESMICH.txt` mit ODbL-Hinweis; ohne Tokens, Schlüssel, Anmeldeversuche. Zugriffsprotokoll aus (`--no-access-log`).

## 6. Öffentliche Schnittstellen (API v1 – Vertrag für Pakete, Frontend-Typen und Abnahmetests)
Alle unter `/api`, JSON, Datum `YYYY-MM-DD` (lokal), Zeitstempel ISO 8601 UTC mit `Z`, Felder wie im Modell (Abschnitt 4). Fehler nach AE-13. Bei Widerspruch gilt **dieser Abschnitt**, `docs/API.md` wird in P1a daraus neu geschrieben.
- **System:** `GET /health` → `{status: "ok", source: "demo"|"garmin"|"none", garmin_connected: bool, timezone: string}` (ohne Garmin-Aufruf; `garmin_connected` = Token-Datei mit dem Schlüssel lesbar; bis P7 immer `source: "none"`, `garmin_connected: false`).
- **Sync:** `POST /sync` `{range_days: 1–90}` → `SyncRun` (läuft schon einer: diesen zurück, 200); Fehler `garmin_rate_limited` (429, `retry_after`), `garmin_not_connected`, `garmin_auth_required`, `demo_blocked`, `operation_busy`. `GET /sync/status` → `SyncRun|null`. `SyncRun.incomplete_days` ist eine **Anzahl** (int, Tage mit mindestens einem gescheiterten Teil).
- **Garmin-Daten:** `GET /daily?from&to` (Standard: letzte 30 Tage bis `local_today`) → `DailyMetrics[]` aufsteigend; `GET /activities?from&to&sport&limit&before` → `{items: (Activity & {sport})[], next_before: int|null}` neueste zuerst nach (`start_time_utc`,`id`), `limit` 1–100 (Standard 30), `before` = `id` der letzten gezeigten Aktivität (kein Verlust am Tagesrand); `GET /activities/{id}` → `Activity & {sport}`.
- **Garmin-Verbindung:** `GET /garmin/connection` → `{connected, ever_connected, auth_required, rate_limited_until|null, login_blocked_until|null, secret_key_present}`; `POST /garmin/connection` `{email (3–254), password (1–200)}` → `{status: "connected"|"mfa_required"}`; `POST /garmin/connection/mfa` `{code: 6–8 Ziffern}` → `{status: "connected"}`; `DELETE /garmin/connection` → 204.
- **Ernährung:** `GET /foods?q` (lokal, max. 50); `POST /foods` (eigenes, `origin="custom"`); `GET /foods/search?q&online=false|true` → `{local: Food[], online: OffProduct[], online_error: {code, detail, retry_after}|null, attribution: string|null}` (`online=true` nur auf ausdrückliche Aktion); `GET /foods/barcode/{code}` → `{local: Food|null, online: OffProduct|null}`; `POST /foods/import` `{origin: "off", origin_id}` → `Food`; `GET /food-log?date`; `POST /food-log` `{date, meal, food_id, amount_g: 0,5–5000}`; `DELETE /food-log/{id}` → 204; `GET /nutrition/day?date` → `{date, eaten: {kcal, protein_g, carbs_g, fat_g}, burned_kcal: number|null, burned_partial: bool, goal: NutritionGoal|null, balance_kcal: number|null}`; `GET /nutrition/goal` → `NutritionGoal|null`; `PUT /nutrition/goal` `{target_kcal, protein_g, carbs_g, fat_g}` → `NutritionGoal` (legt die Zeile `id=1` beim ersten Mal an). **Es gibt kein Standard-Ernährungsziel**: ohne gespeichertes Ziel ist `goal` `null`, nie erfundene Werte.
  `OffProduct` = `{origin_id, name, brand, kcal_per_100g, protein_g_per_100g, carbs_g_per_100g, fat_g_per_100g, barcode}`.
- **Training:** `GET /training/plans` → `TrainingPlan[]` (neueste zuerst); `POST /training/plans` `{name, start_date, weeks_count}` → `TrainingPlan`; `GET /training/plans/{id}` → `TrainingPlan & {sessions: PlannedSession[]}` (nach `date`, `sort_order`); `PUT|DELETE /training/plans/{id}`; Einheit-Eingabe `{date, sport, title, planned_duration_s|null, planned_distance_m|null, notes|null}`; `POST /training/plans/{id}/sessions`; `PUT|DELETE /training/sessions/{id}`; `GET /training/plans/{id}/comparison` → `{weeks: [{week_no, start_date, planned_duration_s, done_duration_s, sessions: [{session, status: "done"|"missed"|"today"|"planned", activity: Activity|null}], extra_activities: Activity[]}]}`; **`GET /training/today`** → `{plan: TrainingPlan|null, sessions: [{session, status, activity}]}` (DESIGN M6; laufender Plan, bei mehreren der zuletzt angelegte).
- **Datenschutz:** `GET /privacy/export` → ZIP; `POST /privacy/delete-all` `{confirm: "ALLES LÖSCHEN"}` (Backend schneidet Leerzeichen am Rand ab) → 204 bzw. `confirm_mismatch`/`delete_incomplete`.

## 7. Konventionen
- **Fehler:** AE-13. Oberfläche zeigt `detail` nur, wenn es ein Text ist, sonst festen deutschen Text; nie `JSON.stringify` einer Fehlerantwort.
- **Konfiguration:** nur Umgebungsvariablen, gelesen nur in `app/settings.py`: `SIMFIT_DATA_DIR` (Standard `backend/data`), `DATABASE_URL` (Standard SQLite im Datenordner), `SIMFIT_SOURCE` (`auto|demo|garmin`, Standard `auto`), `SIMFIT_TIMEZONE`, `SIMFIT_SECRET_KEY` (**kein Standardwert**), `SIMFIT_OFF_CONTACT`, `SIMFIT_AUTO_SYNC_HOURS`, `SIMFIT_PORT` (8000), `SIMFIT_API_DOCS` (aus), `CORS_ORIGINS` (ohne Standard). Abgeleitete Pfade: `secrets_dir`, `backups_dir` (`<data_dir>/backups/simfit-YYYY-MM-DD.db`). Tests übergeben `Settings` direkt an `create_app` (`make_test_app`, mit `allowed_hosts` inkl. `testserver`).
- **Geheimnisse:** Token-Datei `<data_dir>/secrets/garmin_tokens.enc` (Fernet). Ohne Schlüssel: Demo läuft, Garmin-Speichern → `garmin_secret_missing`; falscher Schlüssel → `garmin_tokens_unreadable` („neu verbinden“), kein Absturz. Beim Freund liegt die Schlüsseldatei **außerhalb des Projektordners** (`~/.simfit/simfit.env`, Rechte 0600), damit ein Update in einen neuen Ordner sie nicht verliert; erzeugt einmal mit `Fernet.generate_key()`, nie überschrieben. Schlüssel nie im Datenordner, Export, Log oder Browser.
- **Logging:** Python `logging`, ohne Passwörter, Tokens, Gesundheitswerte, Suchbegriffe, Abfrageparameter.
- **Benennung:** Code englisch, Einheit als Endung (`_m`, `_s`, `_ms`, `_kcal`, `_g`, `_kg`, `_bpm`, `_s_per_km`, `_per_100g`, `_days`); Tests `test_a<Nr>_…` bzw. `test_b<Nr>_…`/`test_s<Nr>_…` für Prüfbefunde.
- **Tests:** Backend pytest mit `backend/tests/helpers.py` (`make_test_app(tmp_path, **overrides)`, `FakeSource`), Garmin-Ersatz bildet die **Ausnahmeketten der Bibliothek** nach (B2). Frontend Vitest + Testing Library (happy-dom, Tastatur mit `fireEvent`). Keine echten Netzaufrufe.

## 8. Sicherheits-Grundgerüst
| Thema | Festlegung | Absicherung |
|---|---|---|
| Geheimnisse | Tokens nur verschlüsselt; Schlüssel nur in der Umgebung, ohne Ersatzwert; Passwort nur einmal an Garmin, MFA-Zwischenstand nur im RAM (AE-16) | Arch-Tests S6, S7, A9; Paket-Tests P6 |
| Berechtigung | Einzelnutzer ohne Anmeldung [ANNAHME E-3]; Schutz = Bindung an 127.0.0.1 **plus** Host-/Origin-Prüfung (AE-19). Wird die Instanz je im Netz erreichbar oder teilen mehrere Personen den Rechner: Anmeldung Pflicht (Eskalation) | Arch-Tests S1; Paket-Tests P1a; Angriffstest P14 |
| Eingaben | Pydantic `extra="forbid"`, Grenzen je Feld, Fremddaten mit `isfinite`/Wertebereich/Länge, SQL nur parametrisiert, React maskiert | Paket-Tests; Arch-Test HTML-Injektion |
| Fehler | AE-13, 422 ohne Eingabewerte | Arch-Tests S2, S14, B5 |
| Gleichzeitigkeit | Ein Nutzer, kein Versionsfeld. Vorgangs-Sperre mit Abbruch-Signal und Generationsnummer (AE-14); ein Worker; beim Start werden hängende `running`-Läufe auf `aborted` gesetzt | Arch-Tests S9; Paket-Tests P5, P6, P13 |
| Anmeldung | entfällt lokal; Garmin-Anmeldeversuche begrenzt und gespeichert (AE-8) | Paket-Tests P6 |
| Web | AE-19; Header in P14: CSP `default-src 'self'; script-src 'self' 'sha256-…'` (Hashes der Inline-Skripte aus dem Export), `style-src 'self' 'unsafe-inline'` (Recharts, begründet), `object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; connect-src 'self'; img-src 'self' data:`, `Referrer-Policy: no-referrer`; HSTS entfällt bei `http://127.0.0.1` | Paket-Tests P14 |
| Werkzeuge | `bandit` und `eslint-plugin-security` als Zusatzbefehle; `pip-audit -r backend/requirements.lock` und `npm audit --omit=dev --audit-level=high` als Sicherheitsbefehl (Eintrag in `.claude/dev-team.json` mit Simons Freigabe) | Schranke |
| Lieferkette | `requirements.lock` mit Hashes (`uv pip compile --generate-hashes`), Dev-Pakete getrennt, Docker `--require-hashes`, Basis-Images per Digest, Frontend `npm ci`, Next-Telemetrie aus | Arch-Test S5 |
| Daten | Tägliche Sicherung (Backup-API) nach `backups/`, 14 Stück; verpasste Sicherung wird beim Start nachgeholt, Fehler sichtbar im Status; **Sicherung vor jeder Migration**, scheitert sie, startet die App nicht (deutsche Meldung); Wiederherstellung als Skript (App stoppen, `-wal`/`-shm` entfernen, Datei einsetzen, `integrity_check`), einmal ausprobiert (S8). Export/Löschen AE-20 | Paket-Tests P13, P14; Abnahme P15 |
| Updates | [ANNAHME E-5] Simon liefert ein ZIP aus `git archive` mit SHA-256-Prüfsumme in der Anleitung; Skript „Simfit aktualisieren“ sichert vorher, nutzt dasselbe Compose-Projekt `simfit` und dieselbe Schlüsseldatei (S7, S10, S13) | Paket-Tests P14; Anleitung P15 |

## 9. Betrieb
- **Umgebungen:** Entwicklung (Backend `uvicorn --reload`, Frontend `next dev`, `CORS_ORIGINS=http://localhost:3000`, `SIMFIT_API_DOCS=1`) und Instanz beim Freund (ein Prozess, `http://127.0.0.1:8000`).
- **Start beim Freund [ANNAHME E-2]:** Docker Compose (`name: simfit`, benanntes Volume `simfit-data`, Port nur `127.0.0.1:8000`, Log-Rotation, Container nicht-root, `cap_drop: [ALL]`, `no-new-privileges`, `read_only` + tmpfs), Startkommando `uvicorn … --workers 1 --no-access-log`, Doppelklick-Skript im Ordner `start/` (Betriebssystem nach Simons Antwort), öffnet den Browser. Das Skript legt die Schlüsseldatei einmal an und überschreibt sie nie.
- **Auslieferung:** ZIP per `git archive` (enthält nie lokale DB, `.env`, `.venv`, `node_modules`), `.dockerignore` entsprechend. Kein öffentliches Image, keine laufenden Kosten.
- **Updates:** siehe Abschnitt 8.
- **Datenort:** Docker-Volume `simfit-data` bzw. `backend/data/` (DB, Sicherungen, verschlüsselte Tokens); Schlüssel getrennt davon.
- **Abnahme A6 („Nur Simon“):** protokollierter Probelauf auf einem frischen Rechner bzw. einer VM, vom ZIP bis „Heute zeigt Beispieldaten“, dazu einmal Sicherung zurückspielen; Protokollvorlage `docs/abnahme/A6-probelauf.md` (P15).

## 10. Zurückgestellt
BLS als Lebensmittelquelle (Lizenzwortlaut offen), USDA-Online-Adapter, Barcode-Scan per Kamera, Portionen/ml, Favoriten/„zuletzt verwendet“/Rezepte, Kalorienziel-Modus, Gewichtsverlauf, regelbasierte Plan-Erstellung, Training Load/Readiness, Karte/Pulszonen, Erkennung „Tag ohne Uhr“ für die Bilanz (Quelle unbestätigt), Backoff über 24 h hinaus (Sperren bis 48 h berichtet – erst nach Beobachtung im Betrieb), periodischer Sync außerhalb des laufenden Programms, Instanz-Dateisperre gegen einen zweiten Prozess (bis dahin: genau ein Startweg mit `--workers 1`), Mehrnutzerbetrieb und Anmeldung, Versionsfelder.

## 11. Zuordnung der Prüfbefunde
| Befund | Festlegung | Paket(e) |
|---|---|---|
| B1 Demo überschreibt Garmin | AE-6 (b)(c), AE-15 | P5 (Regeln), P4 (Demo-Quelle), P6 (Trennen), P7 (Quellenwahl, Erststart), P13 |
| B2 429 als AuthError | AE-8 Fehlerübersetzung, Token-Client ohne Passwort | P6, P7 |
| B3/S9 Gleichzeitigkeit | AE-14 | P1a (Sperre), P5, P6, P13, P14 |
| B4 Rohdaten-Lücken | AE-6 (e), AE-4 `failed_parts` | P1a (Vertrag), P4 (Demo ohne `failed_parts`), P5, P7 (setzt `failed_parts`) |
| B5 Verträge | AE-4 (`SourceRecord`), AE-11, AE-13, Abschnitt 2 (Besitz), AE-2 | P1a, P1b |
| B6 Bilanz | AE-17 | P9, P10 |
| B7 Tests | AE-7 Testfälle, Ersatz mit Ausnahmeketten (Abschnitt 7), A6-Abnahme (Abschnitt 9) | P1a, P6, P7, P15 |
| S1/S3 Rebinding/CSRF | AE-19 | P1a, P14 |
| S2 Passwort in 422 | AE-13 | P1a, P1b |
| S4 Reste | AE-20 | P1a, P13, P14 |
| S5 Lieferkette | Abschnitt 8 | P1a, P14 |
| S6 MFA-Zwischenstand | AE-16 | P6 |
| S7 Schlüssel/Volume | Abschnitt 7 (Geheimnisse), 9 | P6, P14 |
| S8 Wiederherstellung | Abschnitt 8 (Daten) | P14, P15 |
| S10 Update-Echtheit | Abschnitt 8 (Updates) | P14, P15 |
| S11 CORS/Doku | AE-19 | P1a |
| S12 OFF-Kennung/Kontakt | AE-9, AE-10 | P3, P9, P10 |
| S13 ZIP/Image | Abschnitt 9 | P14, P15 |
| S14 Ausnahmetexte | AE-13 | P5 |
| Recherche | AE-8 (Backoff, Takt), AE-9 (OFF-Limits, v3), AE-10 (USDA, Knopf), AE-18 (typeKey), AE-7 (Profil-Zeitzone) | P3, P5, P6, P9, P10, P11 |

## 12. Entscheidungen
`Datum – Entscheidung – Grund – verworfene Alternativen`
- 2026-11-04 – Prototyp bleibt, wird umgebaut – läuft, Garmin-Kapselung als Idee vorhanden – Neuanfang
- 2026-11-04 – Gesamtes Schema in P1a – keine konkurrierenden Alembic-Köpfe – Migration je Paket
- 2026-11-04 – Architekturtests in Python (ast/Text) für Backend und Frontend – ein Testlauf, keine neuen Pakete – dependency-cruiser/import-linter
- 2026-11-04 – Schnittstelle zuerst: P1a (Backend-Vertrag) und P1b (Frontend-Vertrag) parallel in M1, danach Fachpakete parallel – Kritiker-Befund „P1 Tor für 13 Pakete“ – ein großes P1
- 2026-11-04 – Demo nie über Garmin, nach erster Verbindung bleibt die Quelle Garmin – Datenverlust B1 – „Demo ersetzt andere Quelle“ (alte AE-6 b)
- 2026-11-04 – Eine Vorgangs-Sperre mit Abbruch-Signal statt Einzelsperren – B3/S9, ein Ort – Datenbank-Sperrfelder je Vorgang
- 2026-11-04 – Garmin-Zustand (Sperre bis, Generation, Zeitzone) in einer Tabelle `garmin_state` statt in `sync_run` – Anmeldung und Sync teilen die Sperre – Felder je Lauf
- 2026-11-04 – Prototyp-Frontend wird in P1b entfernt statt umbenannt – DESIGN 10.4 ersetzt ihn ohnehin, spart Kollisionen mit P2 – Feldnamen in 8 Dateien anpassen
- 2026-11-04 – `AppContext` als ein Objekt je Prozess statt einzelner `app.state`-Felder – Router, Sync-Thread und Tests brauchen dieselben Teile (Einstellungen, Engine, Sperre, Quellen-Ersatz) – einzelne FastAPI-Abhängigkeiten je Teil
- 2026-11-04 – `garmin/state.py` als gemeinsame Stelle für Sperre/Wartezeit/Generation – P5 und P6 bauen parallel und ändern denselben Zustand – Logik doppelt in `sync.py` und `setup.py`
- 2026-11-04 – `SourceRecord.failed_parts` – „Teil fehlt (404)“ und „Teil gescheitert“ müssen für `incomplete_days`/`error` unterscheidbar sein – Sonderwert im `payload`
- 2026-11-04 – Sync im eigenen Thread, `start_sync` wartet auf den Start, `execute_sync` synchron – Fehler vor dem Start kommen als HTTP-Fehler an, Tests ohne Thread – FastAPI-`BackgroundTasks` (Fehler nicht rückmeldbar)
- 2026-11-04 – Kein Standard-Ernährungsziel, `goal` darf `null` sein – erfundene Zielwerte wären eine Gesundheitsaussage ohne Grundlage – Standard 2000 kcal
- 2026-11-04 – Schlüsseldatei außerhalb des Projektordners – Update in neuen Ordner (S7) – `.env` im Projektordner
