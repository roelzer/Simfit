# Simfit Backend

FastAPI + SQLModel (SQLite per Default, Postgres über `DATABASE_URL`). API-Vertrag: [`../docs/API.md`](../docs/API.md).

```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload        # http://localhost:8000/docs
pytest
```

## Datenquellen (`SIMFIT_SOURCE`)

- `demo` (Default): deterministische Fake-Daten, kein Garmin-Konto nötig.
- `garmin`: Garmin-Connect-Cloud über die inoffizielle Bibliothek `garminconnect`.
  Einmalig einloggen (inkl. MFA), danach nutzt der Server nur die gespeicherten Tokens:

  ```bash
  python -m app.garmin_login
  SIMFIT_SOURCE=garmin uvicorn app.main:app
  ```

Neue Quellen implementieren das Protokoll in `app/sources/base.py`.

Hinweis: Die Garmin-Anbindung ist gegen die Bibliothek geschrieben, aber noch nicht mit einem echten Konto getestet.
