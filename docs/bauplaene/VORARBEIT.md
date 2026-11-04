# Vorarbeit vor und zwischen den Paketen

## V0 – Tester (vor M1, ein Lauf)
- Root-`pytest.ini`: `testpaths = backend/tests tests/architektur`, `pythonpath = backend`, `addopts = --import-mode=importlib -p no:cacheprovider`, `norecursedirs = .claude .dev-team node_modules .venv`.
- `backend/tests/__init__.py`, `backend/tests/fakes/__init__.py`, `backend/tests/conftest.py` mit **Netzsperre**: `socket.socket.connect`/`connect_ex` und `socket.create_connection` für `AF_INET`/`AF_INET6` → `RuntimeError("Netzzugriff im Test")`; `AF_UNIX` erlaubt (Antwort auf Kritiker V0-1).
- `tests/run_all.py`: Backend-pytest (inkl. Architekturtests) und `npm --prefix frontend run test`; fehlt `frontend/node_modules` oder `backend/.venv` → klare Meldung, Exit 1, nie Schein-Grün (V0-2). Gegenprobe: ein absichtlich roter Test macht den Lauf rot.
- Vitest: `frontend/vitest.config.ts` (happy-dom, `include: ["tests/**/*.test.{ts,tsx}"]`, `testTimeout: 30000`), `frontend/tests/setup.ts` (jest-dom), devDependencies `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `happy-dom`, `@vitejs/plugin-react`, Skript `"test": "vitest run"`. **Frontend-Tests liegen in `frontend/tests/`, nicht in `src/`** (sonst greifen die `src`-Architekturregeln, z. B. `fetch` nur in `client.ts`).
- V0-3 (`format.test.ts`): Es gibt keinen solchen Test im Bestand; P2 schreibt `frontend/tests/lib/format.test.ts` selbst neu. **Tester-Vorarbeit P2 entfällt.**

## Tester-Vorarbeit P1a
- `backend/tests/test_api.py` löschen (testet Prototyp-Endpunkte, die P1a entfernt). Eigener Commit vor P1a.

## Tester-Vorarbeit vor M2: Garmin-Ersatz `backend/tests/fakes/garmin_lib.py` (B2)
Klasse `FakeGarmin` (nie `Garmin` nennen – Architekturtest A9) mit derselben Oberfläche wie `garminconnect.Garmin` 0.3.20, gelesen im Quelltext (`api/base.py`, `client/transport.py`, `api/_common.py`, `client/sso.py`, `client/tokens.py`):
`__init__(email=None, password=None, is_cn=False, prompt_mfa=None, return_on_mfa=False, **kw)`, `login(tokenstore=None) -> tuple[str | None, Any]` (`("needs_mfa", client_state)` bzw. `(None, None)`), `resume_login(client_state, mfa_code) -> tuple`, `client.dumps() -> str` (JSON mit `di_token`, `di_refresh_token`, `di_client_id`), `client.di_token`, `get_user_timezone() -> str | None` (wirft nie, liefert `None` bei Fehler), `get_stats(cdate)`, `get_sleep_data(cdate)`, `get_hrv_data(cdate)`, `get_body_composition(startdate, enddate=None)`, `get_activities_by_date(startdate, enddate=None, activitytype=None, sortorder=None)`. Verhalten per Klassen-Fabrik `make_fake_garmin(script: dict) -> type[FakeGarmin]`; jeder Aufruf landet in `calls: list[str]` (Klassenattribut, je Fabrik neu).

**Echte Ausnahmeklassen** (aus `garminconnect.exceptions`, Import im Test erlaubt): `GarminConnectConnectionError` (Attribut `response`), `GarminConnectNotFoundError` (Unterklasse von ConnectionError), `GarminConnectTooManyRequestsError`, `GarminConnectAuthenticationError`. Antwort-Ersatz: Objekt mit `status_code`.

Ketten-Bausteine (Funktionen, die die fertige Ausnahme liefern), je mit Quelle:
| Funktion | außen | `__cause__` | Quelle |
|---|---|---|---|
| `profile_429_after_token_login()` | `GarminConnectAuthenticationError("Failed to retrieve social profile")` | `GarminConnectConnectionError("API Error 429")`, `response.status_code=429` | `base.py:636-657`, `transport.py:246-279` |
| `login_429()` / `login_427()` | `GarminConnectTooManyRequestsError("Too many login attempts. …")` | `GarminConnectConnectionError("Login failed: API Error 429/427")`, Status 429/427 | `base.py:590-600` |
| `login_bad_credentials()` | `GarminConnectAuthenticationError("Authentication failed (401 Unauthorized). …")` | ConnectionError, Status 401 | `base.py:602-611` |
| `token_unloadable()` (kaputtes JSON, ohne Passwort) | `GarminConnectAuthenticationError("Username and password are required")` | – | `base.py:500-516` |
| `data_429()` | `GarminConnectTooManyRequestsError("Rate limit exceeded: API Error 429")` | ConnectionError, Status 429 | `_common.py:539-542` |
| `data_401()` | `GarminConnectAuthenticationError("Authentication failed: API Error 401")` | ConnectionError, Status 401 | `_common.py:535-538` |
| `data_404()` | `GarminConnectNotFoundError("… client error (404): API Error 404")` | ConnectionError, Status 404 | `_common.py:543-550` |
| `data_403()` | `GarminConnectConnectionError("… client error (403): API Error 403")` | ConnectionError, Status 403 | `_common.py:551-558` |
| `data_503()` | `GarminConnectConnectionError("… HTTP error: API Error 503")` | ConnectionError, Status 503 | `_common.py:579-585` |
| `network_down()` | `GarminConnectConnectionError("… HTTP error: …")` | eingebautes `ConnectionError` | `_common.py:586ff.` |
| `mfa_wrong_code()` | `GarminConnectAuthenticationError("Widget MFA failed: …")` | – | `sso.py:765` |
| `mfa_429()` | `GarminConnectTooManyRequestsError("… returned 429")` | – | `sso.py:104-106` |

Zusätzliche Eigenheiten, die der Ersatz nachbildet: (1) Mit `return_on_mfa=True` und ohne MFA liefert `login()` `(None, None)`, lädt **kein** Profil und behält das Passwort im Objekt (`base.py:517-524`). (2) Mit gespeicherten Tokens **und** Passwort im Objekt löst ein abgelehntes Profil einen Voll-Login aus (`base.py:548-568`) – darum Token-Client immer ohne Passwort. (3) Der Profilabruf wird bei jeder Ausnahme 3-mal versucht (zählt 3 Aufrufe in `calls`). (4) `dumps()` speichert nur DI-Tokens; JWT_WEB-Notweg → `di_token=None` (Baustein `jwt_web_only()`).
Eigentest des Ersatzes: `backend/tests/fakes/test_garmin_lib.py` prüft jede Kette (`type(exc)`, `type(exc.__cause__)`, `exc.__cause__.response.status_code`).

## Projektleiter-Aufgaben
- **Vor P3:** einen echten Aufruf an OFF (Barcode `3017620422003`) über v3 `/api/v3/product/{code}` und v2; Feldnamen (`product_name`, `product_name_de`, `brands`, `nutriments.energy-kcal_100g`, `energy-kj_100g`, `proteins_100g`, `carbohydrates_100g`, `fat_100g`) und den Suchweg (`/cgi/search.pl?search_terms=…&search_simple=1&json=1`) bestätigen; Ergebnis als Abschnitt „PL-Ergebnis“ in `P3.md` eintragen. Ohne Bestätigung: v2.
- **Vor P9:** Rechercheur besorgt eine USDA-FDC-Liste (~30 Basis-Lebensmittel, FDC-ID, kcal/Eiweiß/KH/Fett je 100 g, deutscher Anzeigename) als Datei für `backend/app/nutrition/data/usda_basis.json`. Ohne belegte Liste: keine Basis-Lebensmittel.
- **Vor M1:** `testbefehl` (`backend/.venv/bin/python tests/run_all.py`), `testzahl_muster`, `zusatzbefehle` (`bandit -r backend/app -ll`, `npm --prefix frontend run lint` mit `eslint-plugin-security`), `sicherheitsbefehl` (`pip-audit -r backend/requirements.lock` und `npm audit --omit=dev --audit-level=high`) in `.claude/dev-team.json` – nur mit Simons Freigabe.
- **Vor P14:** Antwort Simons zu E-2 (Betriebssystem des Freundes) einholen.
