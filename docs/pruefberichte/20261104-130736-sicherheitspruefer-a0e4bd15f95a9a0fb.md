# Bericht sicherheitspruefer – 2026-11-04 13:07

🔴 **Sicherheitsprüfer, Modus plan: Den Plan bitte noch nicht so freigeben. Zwei Lücken müssen vorher ins Rückgrat (P1). Beide sind am Prototyp getestet, und beide lassen sich ohne Umbau beheben.**

Wichtig vorweg: Das war eine Prüfung des Plans und des Prototyps. Es war kein Penetrationstest. Angriffe gegen eine laufende App gab es nicht. Die Versuche unten liefen lokal im Testclient gegen den Prototyp bzw. gegen eine kleine Nachbildung, nur mit Testdaten.

## Das Wichtigste für Simon
1. **Jede Webseite, die dein Freund besucht, kann an seine Gesundheitsdaten kommen (DNS-Rebinding).** Der Plan verlässt sich darauf, dass die App nur unter 127.0.0.1 erreichbar ist. Das reicht nicht. Eine fremde Webseite kann den Browser dazu bringen, mit der App wie mit sich selbst zu sprechen. Dann kann sie den Export lesen, „Alles löschen“ auslösen und die Garmin-Verbindung ändern. Die App prüft nicht, unter welchem Namen sie aufgerufen wird. **Getestet:** Eine Anfrage mit fremdem Namen bekommt die Daten (Antwort 200).
2. **Das Garmin-Passwort kann im Klartext auf dem Bildschirm erscheinen.** Bei einer zu langen oder falschen Eingabe schickt der Server das Passwort in seiner Fehlerantwort zurück. **Getestet** (Werkzeugstandard von FastAPI). Die Oberfläche des Prototyps zeigt diese Fehlerantwort als Text an. Macht der Freund davon einen Screenshot für dich, ist das Passwort darauf.
3. **Fremde Webseiten können Garmin-Abrufe starten.** Dafür reicht ein unsichtbares Formular, eine Anmeldung braucht es nicht. Viele Abrufe führen zu einer Garmin-Sperre. **Getestet.**
4. **„Alles löschen“ löscht nicht wirklich alles.** Gelöschte Daten bleiben in der Datenbankdatei lesbar, außerdem in den Docker-Protokollen und im Zwischenspeicher des Browsers. Neue Sicherungen kopieren die alten Reste wieder mit.
5. **Die Python-Bibliotheken sind nicht auf feste Versionen festgelegt.** Beim Freund würde jeweils die neueste Version installiert, auch die der inoffiziellen Garmin-Bibliothek, und zwar ungeprüft.

Die Punkte des Kritikers bestätige ich (Bewertung unten). Den DNS-Rebinding-Punkt stufe ich von 70 auf 90 hoch, weil ich ihn getestet habe.

---

## Befunde (Sicherheit ≥ 80), nach Schwere

**S1 – DNS-Rebinding: Eine fremde Webseite liest alle Daten und kann alles löschen.** Hoch, Sicherheit 90, **getestet** am Prototyp.
- *Angriffsweg:* Der Freund öffnet eine präparierte Seite `evil.example`. Deren Name zeigt nach kurzer Zeit auf 127.0.0.1. Für den Browser gilt dann `evil.example:8000` als „dieselbe Herkunft“. Die Seite kann JSON senden und Antworten lesen: `GET /api/privacy/export` (alle Gesundheitsdaten), `POST /api/privacy/delete-all` mit `{"confirm":"ALLES LÖSCHEN"}`, `POST /garmin/connection` (die App mit dem Garmin-Konto des Angreifers verbinden) und den MFA-Code durchprobieren. Ein Teil der Chrome-Versionen fragt bei Zugriffen aufs lokale Netz um Erlaubnis. Firefox und Safari tun das nicht.
- *Beleg:* Prototyp im Testclient mit `Host: rebind.angreifer.example:8000` → `GET /api/daily` 200, `POST /api/sync` 200. ARCHITEKTUR §8 „Berechtigung“ nennt als Schutz nur die Bindung an 127.0.0.1. In keinem Paket ist eine Prüfung von Host oder Origin geplant.
- *Abhilfe (Rückgrat, P1):* In `create_app` eine Middleware, die **jede** Anfrage ablehnt, deren `Host` nicht `127.0.0.1:<port>` oder `localhost:<port>` ist (Starlette `TrustedHostMiddleware` mit genau diesen Werten). Zusätzlich lehnt sie jede schreibende Anfrage (POST/PUT/DELETE) ab, die ein `Origin` außerhalb dieser Liste mitschickt oder `Sec-Fetch-Site: cross-site` hat. Als Architekturregel festhalten. Tests: `test_a10_fremder_host_abgelehnt` (GET mit fremdem Host → 400, Export und delete-all eingeschlossen), `test_a10_fremder_origin_bei_schreiben_abgelehnt`. In P14 ein Angriffsversuch per `curl -H "Host: …"` gegen den Container.

**S2 – Das Passwort steht in der Fehlerantwort und auf dem Bildschirm.** Mittel, Sicherheit 90, **getestet** (Backend) und **gelesen** (Frontend).
- *Angriffsweg / Ablauf:* Das Passwort ist länger als die Längengrenze, oder ein zusätzliches Feld verletzt `extra="forbid"`. Dann antwortet FastAPI mit 422 und `"input":"GEHEIMES-PASSWORT-123"`. Die Oberfläche macht daraus mit `JSON.stringify(d)` die angezeigte Fehlermeldung (`frontend/src/lib/api.ts:136`). Schreibt ein Fehler-Handler `exc.errors()` ins Protokoll, landet das Passwort auch dort.
- *Beleg:* Nachbildung mit FastAPI 0.162 / Pydantic 2.14 aus dem venv: `{"type":"string_too_long","loc":["body","password"],…,"input":"GEHEIMES-PASSWORT-123"}`. Bei einem zusätzlichen Feld ebenso.
- *Abhilfe (P1, AE-13):* Ein eigener Handler für `RequestValidationError` gibt nur `{detail, code, field}` zurück, nie `input` und nie `ctx`. Er protokolliert nur Feldnamen. Oberfläche (P1/P8): `detail` nur anzeigen, wenn es ein String ist, sonst einen festen deutschen Text. Tests: `test_a9_passwort_nicht_in_422_antwort` und `test_a9_passwort_nicht_im_log` (caplog), je mit zu langem Passwort und mit Zusatzfeld.

**S3 – Fremde Webseiten können Abrufe starten (CSRF über „einfache“ Anfragen).** Mittel, Sicherheit 90, **getestet**.
- *Angriffsweg:* `<form method=post action="http://127.0.0.1:8000/api/sync" enctype="text/plain">` oder `fetch(…, {mode:"no-cors", method:"POST"})` von irgendeiner Webseite. Endpunkte mit Pflicht-JSON-Körper lehnt FastAPI 0.162 ab (getestet: text/plain, ohne Content-Type und form-urlencoded → 422). Endpunkte **ohne Pflicht-Körper** werden aber ausgeführt (getestet: `POST /sync` ohne Körper mit text/plain → 200 `started`).
- *Auswirkung:* Garmin-Abrufe auf Knopfdruck einer fremden Seite → 429 bzw. Sperre des Garmin-Kontos (Verfügbarkeit). Das gilt auch für jeden künftigen POST ohne Körper (z. B. „Abruf abbrechen“, „Sicherung jetzt“).
- *Abhilfe (P1):* Die Origin-Prüfung aus S1. Dazu: Jede schreibende Anfrage braucht `Content-Type: application/json`, sonst 415. `POST /sync` bekommt einen Pflicht-Körper. Test `test_a10_schreiben_ohne_json_abgelehnt` für alle schreibenden Routen, aufgezählt über `app.routes`, damit neue Routen automatisch mitgeprüft werden.

**S4 – „Alles löschen“ hinterlässt lesbare Reste.** Mittel, Sicherheit 85, **gelesen** (Plan) und **bekanntes SQLite-Verhalten** (nicht ausprobiert).
- *Ablauf:* SQLite überschreibt gelöschte Zeilen nicht (`secure_delete` ist standardmäßig aus), und die WAL-Datei hält alte Seiten. Die Backup-API kopiert die Datei seitenweise, mit den freien Seiten. Dazu kommen: Das uvicorn-Zugriffsprotokoll schreibt Adressen mit Suchbegriffen (`/foods/search?q=…`) und Datumswerten in die Docker-Protokolle. API-Antworten ohne `Cache-Control` können im Browser-Zwischenspeicher liegen. P13 löscht laut Bauplan nur Tabellen, Tokens und Sicherungen.
- *Auswirkung:* Das Löschversprechen (A10, Art. 17 DSGVO) stimmt technisch nicht. Wer Zugriff auf die Datei oder die Sicherung hat, kann Reste lesen.
- *Abhilfe (P13/P14):* `PRAGMA secure_delete=ON` bei jeder Verbindung (P1, `db.py`). Nach delete-all `PRAGMA wal_checkpoint(TRUNCATE)` und `VACUUM`. Zugriffsprotokoll ohne Query-String (oder `--no-access-log`). Docker-Logging begrenzen (`max-size`). `Cache-Control: no-store` auf allen `/api`-Antworten. Test: Ein Merkwort in einem Lebensmittel und in einer Notiz speichern, alles löschen, dann die Bytes von DB-Datei, `-wal` und `backups/` durchsuchen → nicht gefunden. Der Löschtext nennt ehrlich, was außerhalb der App liegt: heruntergeladene Exporte im Download-Ordner und Daten bei Garmin.

**S5 – Backend-Abhängigkeiten nicht festgeschrieben (Lieferkette).** Mittel, Sicherheit 95, **gelesen und durch die Schranke bestätigt**.
- *Ablauf:* `backend/requirements.txt` hat nur `>=`. Der Docker-Build beim Freund holt die jeweils neueste Version, auch die von `garminconnect`, das Passwort, MFA und Tokens sieht. Ein kompromittiertes oder kaputtes Release ginge ungeprüft in Betrieb. `pytest` steht zudem in den Laufzeitpaketen.
- *Abhilfe (V0/P1, P14):* Eine Lock-Datei mit Hashes (`pip-compile --generate-hashes` oder `uv lock`), Installation im Dockerfile mit `--require-hashes`. Laufzeit- und Entwicklungspakete trennen. Basis-Images per Digest festlegen. Frontend mit `npm ci`. `sicherheitsbefehl` in `.claude/dev-team.json` eintragen (`pip-audit -r <lock>` und `npm audit --omit=dev --audit-level=high`). Die neue Abhängigkeit `cryptography` (Fernet) über die Abhängigkeits-Schranke.

**S6 – Passwort und MFA-Zwischenstand im Speicher: Ort und Laufzeit nicht festgelegt.** Mittel, Sicherheit 80, **gelesen** (Bibliothek).
- *Ablauf:* `garminconnect` behält `self.password` und löscht es erst nach erfolgreicher Anmeldung (`api/base.py:573`). Bei `return_on_mfa` muss das Objekt mit Passwort und Sitzungs-Cookies zwischen zwei Anfragen leben. Der Zwischenstand lässt sich serialisieren (`client/sso.py:302`). Der Plan sagt nicht, wo er liegt und wann er verfällt (Kritiker P6-1/P6-6, unbeantwortet). Landet er in DB oder Datei, steckt er in Sicherung und Export.
- *Abhilfe (P6):* Nur im Arbeitsspeicher, höchstens ein offener Vorgang, Verfall nach 10 Minuten. Verwerfen bei Erfolg, Fehler, Abbruch, Trennen und delete-all. Nie in DB, Datei oder Log, kein `repr` in Fehlermeldungen. Tests: Nach Erfolg und nach Ablauf ist der Speicher leer. Nach einer Einrichtung mit Merk-Passwort enthalten DB, Datenordner und caplog das Passwort nicht. Der Sync-Client entsteht ohne Zugangsdaten, wie geplant. Das ist wichtig, weil die Bibliothek sonst bei abgelehnten Tokens selbst mit Passwort neu anmeldet (`api/base.py:548-565`, gelesen).

**S7 – Schlüssel und Datenvolume beim Update bzw. Neustart (Kritiker-Punkt).** Mittel, Sicherheit 85, **gelesen**.
- *Ablauf:* Ohne `name:` in Compose leitet Docker den Projektnamen und damit das Volume vom Ordnernamen ab. Ein Update in einen neuen Ordner sieht eine leere Datenbank. Erzeugt das Startskript dann einen neuen `SIMFIT_SECRET_KEY`, sind die Tokens unlesbar. Sicherheitsseitig kommt dazu: Der Plan legt nicht fest, dass es **nie** einen eingebauten Ersatzschlüssel gibt. Der Test `test_a7_demo_runs_without_secret_key` lädt zu genau so einem Rückfallwert ein.
- *Abhilfe (P14, P6):* Compose mit festem `name: simfit` und benanntem Volume. Das Skript überschreibt eine vorhandene `.env` nie. Den Schlüssel erzeugt `Fernet.generate_key()` im Container, nicht `$RANDOM` oder Ähnliches, und die `.env` bekommt Rechte 0600. Ohne Schlüssel: Demo läuft, Garmin-Speichern wird mit klarer Meldung verweigert, kein Standardwert. Ist der Schlüssel falsch, zeigt die App „Garmin neu verbinden“ statt abzustürzen. Arch-Test: kein Fernet-Schlüssel als Literal im Code.

**S8 – Wiederherstellung und Migration ohne Sicherheitsnetz.** Mittel, Sicherheit 85, **gelesen**.
- *Ablauf:* Laut §8 heißt Wiederherstellung „Datei zurückkopieren“. Bei laufender App und WAL beschädigt das die DB, oder die `-wal` spielt alte Stände ein. Migrationen laufen beim Start automatisch. Eine Sicherung vorher ist nur im Update-Skript vorgesehen, nicht beim Start. Laut Checkliste ist eine einmal ausprobierte Wiederherstellung Pflicht.
- *Abhilfe (P14/P15):* Vor jeder Migration beim Start eine Sicherung über die Backup-API. Bei Fehlschlag startet die App nicht und zeigt eine deutsche Meldung. Wiederherstellung als Skript (Container stoppen, `-wal`/`-shm` entfernen, Datei einsetzen, Integritätsprüfung). Abnahme: einmal ausprobiert und das Datum festgehalten.

**S9 – Gleichzeitigkeit von Löschen, Trennen, Abruf und Sicherung (Kritiker B3, ergänzt).** Hoch, Sicherheit 85, **gelesen**.
- Ich bestätige B3. Dazu: Der **Sicherungsjob** und die **Migration** gehören in dieselbe Sperre. Sonst schreibt eine Sicherung mitten im Löschen die Daten neu nach `backups/`. Die Prozess-Sperre funktioniert nur mit genau einem Worker.
- *Abhilfe (P5/P6/P13/P14):* Eine gemeinsame Sperre mit Abbruch-Signal. Tokens nur mit passender Generationsnummer zurückschreiben. Uvicorn fest mit `--workers 1`. Tests wie vom Kritiker vorgeschlagen, plus „Sicherung während delete-all“.

**S10 – Die Auslöser-Checkliste im Plan ist falsch ausgefüllt.** Niedrig (Prozess), Sicherheit 90, **gelesen**.
- „Anmeldung/Rechte“ und „Serverbetrieb“ müssen „ja“ heißen (wie beim Kritiker). „Updates/Signierung“ steht auf ja, es gibt aber kein Konzept zur Echtheit: Woher holt „Simfit aktualisieren“ den neuen Stand, und wie prüft es ihn? Abhilfe (Plan, P14/P15): feste Quelle per HTTPS mit festem Tag/Commit, Prüfsumme des ZIPs in der Anleitung.

**S11 – Standard-CORS des Prototyps und Swagger-Seite in der Auslieferung.** Niedrig, Sicherheit 85, **getestet**.
- Der Prototyp erlaubt standardmäßig `http://localhost:3000` mit allen Methoden (getestet: Preflight für DELETE → erlaubt). Jedes andere Programm auf Port 3000 könnte dann alles lesen. `/docs` ist erreichbar und lädt Skripte von `cdn.jsdelivr` (getestet). Der Prototyp sendet keinen einzigen Sicherheits-Header (getestet).
- *Abhilfe (P1/P14):* `CORS_ORIGINS` ohne Standardwert. In der Auslieferung kein CORS, `docs_url=None`, `openapi_url=None`. Test: Produktiv-Settings → keine `access-control-allow-origin`-Antwort, `/docs` 404.

**S12 – Open-Food-Facts-Kennung ungeprüft in der Adresse, Kontakt im User-Agent.** Niedrig, Sicherheit 80, **gelesen**.
- §8 prüft nur den Barcode (8–14 Ziffern). `POST /foods/import {origin_id}` baut ebenfalls eine OFF-Adresse. Mit `../`, `?` oder `#` lässt sich der Pfad auf dem OFF-Server verbiegen. Der Host bleibt fest, deshalb ist die Wirkung gering. `SIMFIT_OFF_CONTACT` im User-Agent schickt bei jeder Anfrage eine E-Mail-Adresse an OFF. A10 erlaubt nur Suchbegriff und Barcode.
- *Abhilfe (P3/P9):* `origin_id` mit derselben Regel wie den Barcode prüfen, die Adresse über `httpx` mit Pfad-Escaping bauen. Als Kontakt eine Projektadresse von Simon verwenden, nicht die des Freundes, und das in der Anleitung nennen. Die Online-Suche nur auf ausdrücklichen Knopfdruck, nicht bei jeder Tipppause. Sonst gehen auch halb getippte Begriffe raus. Ernährungsbegriffe können Gesundheitsschlüsse erlauben, z. B. „glutenfrei“.

**S13 – Übergabe-ZIP kann lokale Daten enthalten.** Niedrig, Sicherheit 80, **gelesen**.
- Im Arbeitsordner liegen unversioniert `backend/simfit.db`, `backend/.venv` und `.env`-Dateien. Ein ZIP oder `COPY` ohne `.dockerignore` nimmt sie mit.
- *Abhilfe (P14/P15):* ZIP nur über `git archive` bauen. `.dockerignore` schließt `*.db`, `.env*`, `.venv`, `data/`, `backups/` und `node_modules` aus. Test: Liste im Image bzw. ZIP gegen die Ausschlussliste prüfen.

**S14 – Der Prototyp zeigt interne Fehlertexte an.** Niedrig, Sicherheit 90, **gelesen**.
- `backend/app/sync.py` speichert `f"{type(e).__name__}: {e}"` als Meldung, und die Oberfläche zeigt sie an. AE-13 regelt das bereits, aber kein Test erzwingt es. *Abhilfe (P5):* Meldungen nur aus einem festen Katalog. Test: Der Text einer ausgelösten Ausnahme taucht nicht in `sync_run.message` auf.

## Unsichere Beobachtungen (unter 80)
- **NaN/Unendlich aus Fremddaten (70):** `float("nan")` bzw. `float("inf")` lassen sich aus Text erzeugen (getestet). Eine Antwort mit NaN führt in FastAPI zu 500 (getestet). Ob OFF oder Garmin solche Werte je liefern, ist nicht geprüft. Ein so gespeichertes Lebensmittel würde den betroffenen Tag dauerhaft unlesbar machen. Empfehlung P3/P4: `math.isfinite`, Wertegrenzen (0–900 kcal/100 g, Makros 0–100 g), Textlängen kürzen (Name ≤ 200), Größe der Antwort begrenzen.
- **Docker unter Linux (65):** Ältere Docker-Versionen ließen Rechner im selben Netz an Ports, die nur auf 127.0.0.1 veröffentlicht waren. Ich meine, das ist ab Docker 28 behoben. Version nicht verifiziert. Empfehlung P15: Mindestversion in der Anleitung.
- **CSP (Kritiker, 85 als Funktionsfehler, 60 als Sicherheitsrisiko):** Der statische Next-Export braucht Inline-Skripte. Die Gefahr ist, dass jemand unter Zeitdruck `'unsafe-inline' 'unsafe-eval'` setzt. Vorschlag P14: Hashes der Inline-Skripte beim Start aus den exportierten HTML-Dateien berechnen, `script-src 'self' 'sha256-…'`. Für Recharts `style-src 'self' 'unsafe-inline'` (begründet). Dazu `object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; connect-src 'self'; img-src 'self' data:`. Die Telemetrie von Next beim Build abschalten.
- **Andere Benutzer am selben Rechner (Restrisiko, keine Zahl):** Ohne Anmeldung kann jedes Programm und jedes Benutzerkonto auf dem Rechner alle Daten über 127.0.0.1 lesen. Bei einem Familienrechner ist das real. Das ist eine Entscheidung für Simon (E-3, Option „einfache Passwortabfrage“).

## Bewertung der Kritiker-Punkte
- **B1 Demo überschreibt echte Daten:** bestätigt (AE-6 b gelesen), Datenintegrität, hoch. Gehört in P5 als Regel „Demo schreibt nie über `source="garmin"`“.
- **B2 429 → „Anmeldung nötig“:** bestätigt durch eigenes Nachlesen (`api/base.py:636-657`, jede Ausnahme → AuthError). Verfügbarkeit des Garmin-Kontos, hoch. P6 muss die Ursachenkette auswerten.
- **B3 Trennen/Löschen während eines Abrufs:** bestätigt und erweitert (S9).
- **Host-Header/DNS-Rebinding:** bestätigt, getestet (S1), hoch.
- **Update in neuen Ordner:** bestätigt (S7).
- **CSP mit Inline-Skripten:** bestätigt als Funktionsfrage, sicherheitlich niedrig (siehe oben).

---

## Pflichtfragen
1. **Bedrohungsmodell ⚠️** (gelesen). Schützenswert sind Gesundheitsdaten (Art. 9), das Garmin-Passwort und der MFA-Code (nur kurz im Speicher), die Garmin-Tokens (verschlüsselte Datei), der Fernet-Schlüssel (`.env`), die Sicherungen und der Export. Mögliche Angreifer: fremde Webseiten im Browser des Freundes (S1, S3), andere Programme oder Benutzer am selben Rechner (Restrisiko), eine kompromittierte Abhängigkeit (S5), manipulierte Fremddaten von OFF bzw. Garmin. Vertrauensgrenzen: Browser ↔ App (ohne Anmeldung, nur durch Host/Origin schützbar), App ↔ Garmin, App ↔ OFF, Host ↔ Container. Der Plan beschreibt die Grenze Browser ↔ App nicht.
2. **Anmeldung und Rechte ⚠️.** Fremde ID: entfällt. Es gibt nur einen Nutzer, alle Datensätze gehören ihm, also gibt es keinen „fremden“ Datensatz (Lastenheft §3, §6). Schutz der Instanz selbst: Er beruht nur auf 127.0.0.1, und das hält nicht (S1, S3, getestet). Andere lokale Benutzer: nicht geschützt, Entscheidung Simon (E-3).
3. **Eingaben ⚠️.** SQL läuft über SQLModel und ist parametrisiert (gelesen: `api.py`, auch `ilike` mit Parameter). Eine Injection ist dort nicht zu sehen. XSS: React maskiert. Im Frontend gibt es kein `dangerouslySetInnerHTML`/`innerHTML`/`eval` (gelesen per Suche). Aktivitätsnamen von Garmin und Produktnamen von OFF erscheinen als Text. Ein Test mit `<img src=x onerror=…>` als Aktivitäts- und Produktname fehlt im Plan, das gehört in P8/P10. CSRF: S3. Uploads: entfallen, es gibt keinen Upload. Die Fremddaten von OFF/Garmin brauchen Typ-, Längen- und Wertegrenzen (unsichere Beobachtung NaN, S12).
4. **Geheimnisse ⚠️.** Git-Historie: Die Schranke mit `--historie` und eine Stichprobe mit `git log -p` fanden keinen echten Schlüssel. In der Historie gibt es keine `.db`- oder `.env`-Datei außer den Beispielen. Die zwei Schranken-Fehler sind Fehlalarme (siehe 9), die Schranke ist aber rot. Offen sind das Passwort in der 422-Antwort (S2), der MFA-Speicher (S6), ein möglicher Ersatzschlüssel (S7) und das Übergabe-ZIP (S13). Der Schlüssel liegt getrennt von DB und Token-Datei (`.env` auf dem Host, Daten im Volume), das ist gut so. Er darf weder in Export noch Sicherung (geplant, Test in P13 nötig). `backend/.env.example` konnte ich nicht lesen (Leseregel verweigert): **nicht geprüft**.
5. **Abhängigkeiten ⚠️.** Siehe „Werkzeuge“. Backend nicht festgeschrieben (S5). `sicherheitsbefehl` ist leer.
6. **Datenschutz ⚠️.** Die Daten liegen lokal beim Freund. Externe Datenflüsse: Garmin (vom Freund gewollt), OFF (Suchbegriff, Barcode, IP-Adresse, dazu laut Plan die Kontaktadresse im User-Agent, S12). Es gibt keine KI-Dienste und keine Telemetrie im Browser (Arch-Test geplant), die Next-Telemetrie beim Build ist noch offen. Export ist geplant (ZIP, ohne Tokens). Löschen ist geplant, aber unvollständig (S4). Der Export im Download-Ordner ist unverschlüsselt. Hinweis für die Anleitung: Festplattenverschlüsselung des Rechners empfehlen.
7. **Betrieb ⚠️.** Sicherung täglich geplant, Wiederherstellung nicht ausprobiert und unsicher beschrieben (S8). Updates ohne Echtheitsprüfung (S10). Logging: Das Zugriffsprotokoll enthält Suchbegriffe (S4). Fehlermeldungen: AE-13 ist gut, im Prototyp aber verletzt (S14), und 422 verrät Eingaben (S2).
8. **Typische KI-Schwächen ⚠️.** Debug und Doku-Seite offen (S11, getestet). CORS-Standard zu weit (S11, getestet). Zertifikatsprüfung: In `garminconnect` gibt es kein `verify=False` (gelesen per Suche), ✅. Selbstgebaute Kryptografie: keine, Fernet ist geplant ✅ (Beleg ARCHITEKTUR §7). Risiko eines festen Ersatzschlüssels: S7.
9. **Werkzeuge ohne KI ⚠️.** Siehe unten. `--build` wurde **nicht geprüft**, weil es noch keinen Build gibt. Stellen mit „dev-team: sicher“: keine gefunden.
10. **Browser-Code ⚠️.** Der Prototyp nutzt nur `NEXT_PUBLIC_API_URL` (localhost-Standard, kein Geheimnis). Der Arch-Test `test_a9_keine_geheimnisse_im_browser_code` ist geplant. Ausgelieferte Dateien sind **nicht geprüft** (kein Build).
11. **Gleichzeitigkeit, Fehler, Backup ❌.** Siehe S9 (Sperre fehlt für Löschen, Trennen, Sicherung und Migration) und S8 (Rückweg nicht getestet). „Gespeichert, obwohl es fehlschlug“: Die Löschzeile in der Ernährung verschwindet sofort (DESIGN §6.4). P10 braucht einen Test „DELETE schlägt fehl → Zeile kommt zurück, Meldung“.
12. **Angriffsversuche:** entfällt in diesem Modus (plan). Es läuft noch keine App. Die lokalen Testclient-Versuche oben (Host, text/plain, 422, Preflight, `/docs`, NaN) sind keine Angriffe gegen eine laufende Instanz. Der Modus `angriff` ist vor der ersten echten Nutzung Pflicht (CLAUDE.md).
13. **Gegenfrage:** Die ✅ in diesem Bericht stehen bei Zertifikatsprüfung (Angriff Mitlesen; scheitert, weil kein `verify=False`; Beleg Suche in der Bibliothek), bei Kryptografie (eigene Krypto; scheitert, weil Fernet; Beleg ARCHITEKTUR) und bei SQL (Injection über `q`; scheitert, weil parametrisiert; Beleg `api.py` `ilike`, gelesen, nicht angegriffen). „Entfällt“ steht bei der fremden ID: Es gibt keinen zweiten Nutzer. Bei Uploads: Es gibt keinen Upload-Endpunkt laut §6. Alles andere ist ⚠️/❌ oder „nicht geprüft“. Gegen „nur intern“ habe ich gezielt gefragt, wer die Daten beeinflusst: Aktivitätsnamen kommen aus dem Garmin-Konto, auch aus verknüpften Apps. Produktnamen kommen aus der offenen OFF-Datenbank, die jeder bearbeiten kann. Beide sind fremde Eingaben.

## Tatsächlich ausgeführte Werkzeuge
- `python3 …/scripts/pruefe_sicherheit.py --alles --historie` → wörtlich:
  `FEHLER: Geheimwert als Rückfallwert in backend/app/config.py …` / `FEHLER: Geheimwert als Rückfallwert in frontend/src/lib/api.ts …` / `WARNUNG: Fehler wird ohne Meldung übergangen in frontend/src/lib/api.ts: catch { /* kein JSON */ } …` / `SICHERHEIT: NICHT OK (2 Fehler)`.
  Meine Bewertung: Beide Fehler sind **Fehlalarme**. Es handelt sich um den SQLite-Pfad `sqlite:///./simfit.db` bzw. `http://localhost:8000`, kein Geheimnis. Beide Dateien ersetzt P1. Die Schranke bleibt bis dahin rot, deshalb in P1 Standardwerte ohne URL-Muster oder mit `dev-team: sicher – <Grund>` zur Einzelbewertung. Die Warnung zum `catch` ist harmlos: Bei einer Fehlerantwort ohne JSON fällt der Code auf „Fehler <Status>“ zurück (`api.ts:137-140`, gelesen). Es wird nichts als gespeichert gemeldet.
- `npm audit --audit-level=high` (frontend): 16 Lücken, alle mittel, alle über `minimatch` in den eslint-Plugins (nur für die Entwicklung). `npm audit --omit=dev`: `found 0 vulnerabilities`.
- `pip-audit` (in einer eigenen venv im Scratchpad) gegen `pip freeze` des Backend-venv (38 Pakete): `No known vulnerabilities found`. Einschränkung: Geprüft wurde der installierte Stand, nicht eine Lock-Datei, weil es keine gibt (S5).
- `pruefe-abhaengigkeiten.sh --basis b3c077a` → `ERGEBNIS: NICHT OK`. Die PyPI-Pakete existieren und sind etabliert. Die npm-Downloadzahlen waren über den Proxy nicht abrufbar (**nicht geprüft**). 6 Python-Pakete sind ohne `==`.
- Testclient-Versuche (Scratchpad, Testdaten): Ergebnisse wie bei S1, S2, S3 und S11 und in der unsicheren Beobachtung zu NaN.

## Was in welches Paket gehört
- **P1 (Rückgrat, vor allem anderen):** Host- und Origin-Middleware und JSON-Pflicht für schreibende Anfragen (S1, S3), eigener 422-Handler ohne `input` (S2), `CORS_ORIGINS` ohne Standard, `/docs` aus (S11), `secure_delete=ON` und `Cache-Control: no-store` (S4), Fehlertext-Katalog, Standardwerte ohne Schranken-Fehlalarm. Dazu die Architekturregeln „jede schreibende Route wird auf Origin/JSON getestet“ und „kein Schlüssel-Literal“.
- **V0/P1:** Lock-Datei mit Hashes, Entwicklungspakete getrennt, `sicherheitsbefehl` setzen (S5, Freigabe Simon für `dev-team.json`).
- **P3/P9:** `origin_id` prüfen, Fremddaten begrenzen (`isfinite`, Längen, Wertebereiche, Größe der Antwort), Kontakt im User-Agent klären (S12, NaN).
- **P4:** dieselben Wertegrenzen für Garmin-Felder.
- **P5:** gemeinsame Sperre mit Abbruch-Signal, ein Worker, Meldungskatalog (S9, S14, B1).
- **P6:** MFA-Speicher nur im RAM mit Verfall, Passwort-Tests für 422, Log und Dateien, Ursachenkette bei 429, Tokens mit Generationsnummer (S6, S2, B2, B3).
- **P8/P10:** XSS-Test mit Aktivitäts- und Produktnamen, Fehlertext nie als JSON anzeigen, Löschen mit Fehlschlag zurückrollen.
- **P13:** Löschen mit VACUUM/Checkpoint, Merkwort-Test über DB, WAL und Sicherungen, Export-Test ohne Tokens, Schlüssel und MFA-Zustand (S4).
- **P14:** Compose `name: simfit`, benanntes Volume, `.env` nie überschreiben und 0600, Schlüssel per `Fernet.generate_key()`, Container gehärtet (nicht-root, `cap_drop: [ALL]`, `security_opt: no-new-privileges`, `read_only` mit tmpfs, kein docker.sock, Log-Rotation), `.dockerignore`, Images per Digest, Next-Telemetrie aus, CSP mit Hashes, Sicherung vor Migration, Wiederherstellungs-Skript, Angriffstest Host/Origin per curl (S1, S3, S7, S8, S13).
- **P15:** ZIP per `git archive` mit Prüfsumme, Wiederherstellung einmal ausprobiert, Hinweise zu Datenflüssen an OFF und Garmin, Festplattenverschlüsselung, Docker-Mindestversion, ehrlicher Löschtext (S4, S10, S13).
- **Plan §6:** „Anmeldung/Rechte“ und „Serverbetrieb“ auf „ja“ setzen, Update-Herkunft festlegen (S10).

## Bitten an den Projektleiter
- Simon entscheiden lassen (E-3): Läuft die App auf einem Rechner, den auch andere Personen benutzen? Wenn ja, eine einfache Passwortabfrage einplanen.
- Den Architekten S1–S3 als Architekturregeln mit Tests in P1 aufnehmen lassen, bevor P1 startet.
- Vor der ersten echten Nutzung den Modus `angriff` gegen den gebauten Container einplanen (CLAUDE.md verlangt ihn). Für Gesundheitsdaten eines Dritten empfehle ich Simon zusätzlich, über einen externen Test nachzudenken. Dieses Team ersetzt ihn nicht.

**Wichtige Dateien**
- /home/user/Simfit/docs/ARCHITEKTUR.md (§6, §7, §8, AE-6, AE-8)
- /home/user/Simfit/docs/plan.md (§6 Auslöser-Checkliste)
- /home/user/Simfit/docs/pruefberichte/20261104-123834-architekt-ac3282c008d26e6b1.md (Baupläne P6, P13, P14)
- /home/user/Simfit/backend/requirements.txt (S5)
- /home/user/Simfit/backend/app/main.py, /home/user/Simfit/backend/app/config.py, /home/user/Simfit/backend/app/sync.py (S1, S11, S14)
- /home/user/Simfit/frontend/src/lib/api.ts (Zeile 136, S2)
- /home/user/Simfit/backend/.venv/lib/python3.13/site-packages/garminconnect/api/base.py (Zeilen 548-573, 636-657)
- Prüfskripte: /tmp/claude-0/-home-user-Simfit/4a258c46-2b2d-542f-bbd8-c428f0922ded/scratchpad/probe.py und /tmp/claude-0/-home-user-Simfit/4a258c46-2b2d-542f-bbd8-c428f0922ded/scratchpad/probe2.py
