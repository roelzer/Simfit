"""Architekturtests Backend (Simfit). Lesen nur Dateien (ast), führen keinen Produktivcode aus.

Regeln und Begründung: docs/ARCHITEKTUR.md (AE-Nummern). Ändern nur der Architekt.
Einige Regeln schalten sich selbst scharf, sobald die Zielstruktur existiert (z. B. app/models/),
damit der Prototyp-Bestand bis zum Umbau grün bleibt.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
APP = BACKEND / "app"

FACHBEREICHE = ("garmin", "nutrition", "training", "privacy")  # AE-2
REINE_MODULE = ("app/core/*.py", "app/garmin/normalize.py", "app/garmin/demo.py", "app/nutrition/calc.py",
                "app/training/matching.py")  # AE-3, AE-15 (Demo erzeugt nur Rohdaten, schreibt nie selbst)
VERBOTEN_IN_REINEN = ("fastapi", "starlette", "sqlalchemy", "sqlmodel", "httpx", "requests", "urllib", "socket",
                      "garminconnect", "curl_cffi", "os", "subprocess", "app.db", "app.settings", "app.token_vault",
                      "app.garmin.store", "app.garmin.sync")
NETZ_BIBLIOTHEKEN = ("httpx", "requests", "urllib.request", "aiohttp", "socket", "curl_cffi")
NETZ_ERLAUBT = {"app/nutrition/off_client.py", "app/garmin/connection.py"}  # AE-9 (connection: Netzfehler fangen)
GARMIN_ZIEL = "app/garmin/connection.py"  # AE-8
GARMIN_BESTAND = {"app/sources/garmin.py", "app/garmin_login.py"}  # Prototyp, gilt nur bis connection.py existiert
EINHEITEN = ("_m", "_s", "_ms", "_kcal", "_g", "_kg", "_bpm", "_s_per_km", "_per_100g", "_days")  # AE-5
EINHEITENLOS = {"id", "steps", "sleep_score", "stress_avg", "body_battery_high", "body_battery_low",
                "weeks_count", "sort_order", "consecutive_rate_limits", "token_generation"}
GEHEIM = re.compile(r"(?i)(password|passwort|secret|geheim|^token$|_token$|^tokens?_json$|refresh|dumps|api_key|mfa_code)")
LOG_METHODEN = {"debug", "info", "warning", "warn", "error", "exception", "critical", "log"}


def rel(p: Path) -> str:
    return p.relative_to(BACKEND).as_posix()


def py_dateien(basis: Path):
    return sorted(p for p in basis.rglob("*.py") if "__pycache__" not in p.parts) if basis.exists() else []


def modulname(p: Path) -> str:
    teile = list(p.relative_to(BACKEND).with_suffix("").parts)
    if teile[-1] == "__init__":
        teile = teile[:-1]
    return ".".join(teile)


def importe(p: Path, nur_oben: bool = False) -> set[str]:
    """Absolute Modulnamen aller Importe (relative aufgelöst). nur_oben: nur Modulebene, ohne TYPE_CHECKING."""
    baum = ast.parse(p.read_text(encoding="utf-8"))
    paket = modulname(p) if p.name == "__init__.py" else modulname(p).rpartition(".")[0]
    knoten = []
    if nur_oben:
        stapel = list(baum.body)
        while stapel:
            k = stapel.pop()
            if isinstance(k, ast.If) and "TYPE_CHECKING" in ast.unparse(k.test):
                continue
            if isinstance(k, (ast.If, ast.Try)):
                stapel += k.body + k.orelse + getattr(k, "handlers", []) + getattr(k, "finalbody", [])
            elif isinstance(k, ast.ExceptHandler):
                stapel += k.body
            else:
                knoten.append(k)
    else:
        knoten = list(ast.walk(baum))
    namen = set()
    for k in knoten:
        if isinstance(k, ast.Import):
            namen |= {a.name for a in k.names}
        elif isinstance(k, ast.ImportFrom):
            if k.level:
                basis = paket.split(".")
                basis = basis[: len(basis) - (k.level - 1)] if k.level > 1 else basis
                mod = ".".join(basis + ([k.module] if k.module else []))
            else:
                mod = k.module or ""
            namen.add(mod)
            namen |= {f"{mod}.{a.name}" for a in k.names}
    return namen


def trifft(name: str, praefixe) -> bool:
    return any(name == v or name.startswith(v + ".") for v in praefixe)


def test_keine_kreisabhaengigkeiten_im_backend():
    module = {modulname(p): p for p in py_dateien(APP)}
    kanten = {m: {i for i in importe(p, nur_oben=True) if i in module and i != m} for m, p in module.items()}
    zustand, kreise = {}, []

    def besuche(m, pfad):
        zustand[m] = 1
        for n in sorted(kanten[m]):
            if zustand.get(n) == 1:
                kreise.append(" -> ".join(pfad[pfad.index(n):] + [n]))
            elif n not in zustand:
                besuche(n, pfad + [n])
        zustand[m] = 2

    for m in sorted(module):
        if m not in zustand:
            besuche(m, [m])
    assert kreise == [], f"Kreis-Abhängigkeiten: {kreise}"


def test_reine_fachlogik_kennt_keine_technik():
    verstoesse = []
    for p in py_dateien(APP):
        if not any(Path(rel(p)).match(m) for m in REINE_MODULE):
            continue
        for i in importe(p):
            if trifft(i, VERBOTEN_IN_REINEN) or re.match(r"app\.\w+\.api$", i):
                verstoesse.append(f"{rel(p)} importiert {i}")
        for k in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(k, ast.Call) and isinstance(k.func, ast.Attribute) and k.func.attr in ("now", "today", "utcnow"):
                verstoesse.append(f"{rel(p)}:{k.lineno} liest die Uhr selbst ({k.func.attr}) – Zeit als Parameter übergeben")
    assert verstoesse == [], "\n".join(verstoesse)


def test_fachbereiche_importieren_sich_nicht_gegenseitig():
    verstoesse = []
    for b in FACHBEREICHE:
        andere = [f"app.{x}" for x in FACHBEREICHE if x != b]
        for p in py_dateien(APP / b):
            verstoesse += [f"{rel(p)} importiert {i}" for i in importe(p) if trifft(i, andere)]
    assert verstoesse == [], "\n".join(verstoesse)


def test_a5_garmin_bibliothek_nur_im_verbindungsmodul():
    erlaubt = {GARMIN_ZIEL} if (BACKEND / GARMIN_ZIEL).exists() else GARMIN_BESTAND
    nutzer = {rel(p) for p in py_dateien(APP) if any(trifft(i, ("garminconnect", "garth")) for i in importe(p))}
    assert nutzer <= erlaubt, f"garminconnect außerhalb von {sorted(erlaubt)}: {sorted(nutzer - erlaubt)}"


def test_netzwerkzugriff_nur_in_adaptern():
    nutzer = {rel(p) for p in py_dateien(APP) if any(trifft(i, NETZ_BIBLIOTHEKEN) for i in importe(p))}
    assert nutzer <= NETZ_ERLAUBT, f"Netzwerk-Bibliothek außerhalb der Adapter: {sorted(nutzer - NETZ_ERLAUBT)}"


def _tabellenklassen(p: Path):
    for k in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
        if isinstance(k, ast.ClassDef) and any(
                kw.arg == "table" and isinstance(kw.value, ast.Constant) and kw.value.value is True for kw in k.keywords):
            yield k


def test_datenmodell_an_genau_einer_stelle():
    orte = {rel(p) for p in py_dateien(APP) if any(True for _ in _tabellenklassen(p))}
    if (APP / "models").is_dir():
        assert not (APP / "models.py").exists(), "app/models.py und app/models/ gleichzeitig"
        fremd = {o for o in orte if not o.startswith("app/models/")}
        assert fremd == set(), f"Tabellen außerhalb von app/models/: {sorted(fremd)}"
    else:
        assert len(orte) <= 1, f"Tabellen in mehreren Dateien: {sorted(orte)}"


def test_zahlenfelder_tragen_die_einheit_im_namen():
    if not (APP / "models").is_dir():  # scharf ab dem Umbau (P1)
        return
    verstoesse = []
    for p in py_dateien(APP / "models"):
        for klasse in _tabellenklassen(p):
            for feld in klasse.body:
                if not (isinstance(feld, ast.AnnAssign) and isinstance(feld.target, ast.Name)):
                    continue
                name, typ = feld.target.id, ast.unparse(feld.annotation)
                if not re.search(r"\b(int|float|Decimal)\b", typ):
                    continue
                if name in EINHEITENLOS or name.endswith("_id") or name.endswith(EINHEITEN):
                    continue
                verstoesse.append(f"{rel(p)}: {klasse.name}.{name} ({typ}) ohne Einheit im Namen")
    assert verstoesse == [], "\n".join(verstoesse)


def test_schema_nur_ueber_migrationen():
    if not (BACKEND / "migrations").is_dir():  # scharf, sobald Alembic eingerichtet ist (P1)
        return
    treffer = [rel(p) for p in py_dateien(APP) if "create_all" in p.read_text(encoding="utf-8")]
    assert treffer == [], f"create_all im Produktivcode (Schema nur über Alembic): {treffer}"


def test_a9_keine_geheimnisse_in_logs_oder_ausgaben():
    verstoesse = []
    for p in py_dateien(APP):
        for k in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if not isinstance(k, ast.Call):
                continue
            f = k.func
            ist_log = (isinstance(f, ast.Name) and f.id == "print") or (
                isinstance(f, ast.Attribute) and f.attr in LOG_METHODEN
                and isinstance(f.value, ast.Name) and re.match(r"(?i)(log|logger|logging|_log)$", f.value.id))
            if not ist_log:
                continue
            for arg in list(k.args) + [kw.value for kw in k.keywords]:
                for n in ast.walk(arg):
                    name = n.id if isinstance(n, ast.Name) else n.attr if isinstance(n, ast.Attribute) else None
                    if name and GEHEIM.search(name):
                        verstoesse.append(f"{rel(p)}:{k.lineno} gibt '{name}' aus")
    assert verstoesse == [], "\n".join(verstoesse)


def test_keine_verschluckten_fehler():
    verstoesse = []
    for p in py_dateien(APP):
        for k in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if not isinstance(k, ast.ExceptHandler):
                continue
            if k.type is None:
                verstoesse.append(f"{rel(p)}:{k.lineno} nacktes 'except:'")
            elif all(isinstance(s, (ast.Pass, ast.Continue)) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                     for s in k.body):
                verstoesse.append(f"{rel(p)}:{k.lineno} Fehler wird still verschluckt")
    assert verstoesse == [], "\n".join(verstoesse)


def test_a10_cors_nur_fuer_bekannte_herkuenfte():
    verstoesse = []
    for p in py_dateien(APP):
        for k in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(k, ast.keyword) and k.arg == "allow_origin_regex":
                verstoesse.append(f"{rel(p)}: allow_origin_regex")
            if isinstance(k, ast.keyword) and k.arg == "allow_origins" and "'*'" in ast.unparse(k.value):
                verstoesse.append(f"{rel(p)}: allow_origins mit '*'")
    assert verstoesse == [], "\n".join(verstoesse)


def test_a9_tests_rufen_garmin_nie_echt_auf():
    verstoesse = []
    for basis in (BACKEND / "tests", ROOT / "tests"):
        for p in py_dateien(basis):
            if "architektur" in p.parts:
                continue
            baum = ast.parse(p.read_text(encoding="utf-8"))
            for k in ast.walk(baum):
                if isinstance(k, ast.ImportFrom) and (k.module or "").startswith("garminconnect") and any(
                        a.name == "Garmin" for a in k.names):
                    verstoesse.append(f"{p.relative_to(ROOT)}:{k.lineno} importiert garminconnect.Garmin")
                if isinstance(k, ast.Call) and ast.unparse(k.func) in ("garminconnect.Garmin", "Garmin"):
                    verstoesse.append(f"{p.relative_to(ROOT)}:{k.lineno} erzeugt einen echten Garmin-Client")
    assert verstoesse == [], "\n".join(verstoesse)


def test_a7_daten_und_geheimnisse_sind_von_git_ausgeschlossen():
    pfade = [".env", "backend/.env", "backend/data/simfit.db", "backend/data/secrets/garmin_tokens.enc",
             "backend/data/backups/simfit-2026-01-01.db"]
    nicht = [p for p in pfade if subprocess.run(["git", "check-ignore", "-q", p], cwd=ROOT).returncode != 0]
    assert nicht == [], f"Nicht von git ausgeschlossen: {nicht}"


# ---------------------------------------------------------------------------
# Regeln aus der Planprüfung (Kritiker B1–B7, Sicherheitsprüfer S1–S14), siehe ARCHITEKTUR.md Abschnitt 11.
# Jede Regel schaltet sich selbst scharf, sobald ihre Zielstruktur existiert.
# ---------------------------------------------------------------------------

GARMIN_TABELLEN = {"DailyMetrics", "Activity", "RawRecord"}  # AE-6
SITZUNG_SCHREIBT = {"add", "add_all", "merge", "delete", "bulk_save_objects"}
SQL_SCHREIBT = {"delete", "update", "insert"}
PFLICHT_KENNUNGEN = {  # AE-13, Katalog-Pflichtinhalt
    "not_found", "invalid_input", "unsupported_media_type", "payload_too_large", "bad_host", "forbidden_origin",
    "conflict", "operation_busy", "confirm_mismatch", "delete_incomplete", "internal_error", "demo_blocked",
    "garmin_not_connected", "garmin_auth_required", "garmin_credentials_rejected", "garmin_mfa_invalid",
    "garmin_mfa_expired", "garmin_login_limit", "garmin_rate_limited", "garmin_unavailable",
    "garmin_secret_missing", "garmin_tokens_unreadable", "off_rate_limited", "off_unavailable", "off_not_configured"}
SPERR_PFLICHT = ("app/garmin/sync.py", "app/garmin/setup.py", "app/backup.py")  # AE-14
FERNET_LITERAL = re.compile(r"(?<![A-Za-z0-9_\-])[A-Za-z0-9_\-]{43}=(?![A-Za-z0-9_\-=])")
VERBOTENE_MODELLFELDER = re.compile(r"(?i)(password|passwort|mfa|pending|cookie|secret|^tokens?$|_token$|^token_(?!generation))")


def _baum(p: Path) -> ast.AST:
    return ast.parse(p.read_text(encoding="utf-8"))


def _hat_create_app() -> bool:
    main = APP / "main.py"
    return main.exists() and "def create_app" in main.read_text(encoding="utf-8")


def _testtexte() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in py_dateien(BACKEND / "tests"))


def _aufrufname(k: ast.Call) -> str:
    f = k.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def _katalog() -> set[str] | None:
    p = APP / "errors.py"
    if not p.exists():
        return None
    for k in ast.walk(_baum(p)):
        ziel = k.targets[0] if isinstance(k, ast.Assign) else k.target if isinstance(k, ast.AnnAssign) else None
        if isinstance(ziel, ast.Name) and ziel.id == "ERROR_CATALOG" and isinstance(k.value, ast.Dict):
            return {s.value for s in k.value.keys if isinstance(s, ast.Constant)}
    return None


def test_s6_kein_passwort_oder_mfa_zustand_im_datenmodell():
    """AE-16: Passwort, MFA-Zwischenstand und Tokens nie in der Datenbank (sonst in Sicherung und Export)."""
    dateien = py_dateien(APP / "models") if (APP / "models").is_dir() else [p for p in [APP / "models.py"] if p.exists()]
    verstoesse = []
    for p in dateien:
        for klasse in (k for k in ast.walk(_baum(p)) if isinstance(k, ast.ClassDef)):
            for feld in klasse.body:
                if isinstance(feld, ast.AnnAssign) and isinstance(feld.target, ast.Name) \
                        and VERBOTENE_MODELLFELDER.search(feld.target.id):
                    verstoesse.append(f"{rel(p)}: {klasse.name}.{feld.target.id}")
    assert verstoesse == [], "Geheimnis/MFA-Zustand im Datenmodell:\n" + "\n".join(verstoesse)


def test_b1_garmin_tabellen_nur_ueber_store_schreiben():
    """AE-6: DailyMetrics/Activity/RawRecord werden nur in garmin/store.py (und beim Löschen in privacy/) geschrieben.
    Scharf, sobald app/garmin/store.py existiert."""
    if not (APP / "garmin" / "store.py").exists():
        return
    verstoesse = []
    for p in py_dateien(APP):
        r = rel(p)
        if r == "app/garmin/store.py" or r.startswith(("app/privacy/", "app/models/")):
            continue
        baum = _baum(p)
        importiert = any(isinstance(k, ast.ImportFrom) and any(a.name in GARMIN_TABELLEN for a in k.names)
                         for k in ast.walk(baum))
        for k in ast.walk(baum):
            if not isinstance(k, ast.Call):
                continue
            name = _aufrufname(k)
            if isinstance(k.func, ast.Name) and name in GARMIN_TABELLEN and r != "app/garmin/normalize.py":
                verstoesse.append(f"{r}:{k.lineno} erzeugt {name}(...) – nur normalize.py/store.py")
            if isinstance(k.func, ast.Name) and name in SQL_SCHREIBT and k.args \
                    and isinstance(k.args[0], ast.Name) and k.args[0].id in GARMIN_TABELLEN:
                verstoesse.append(f"{r}:{k.lineno} {name}({k.args[0].id}) – nur store.py")
            # Garmin-Bereich und Zusammenbau: wer die Tabellen importiert, schreibt nicht selbst über die Sitzung.
            if importiert and (r.startswith("app/garmin/") or r == "app/main.py") \
                    and isinstance(k.func, ast.Attribute) and name in SITZUNG_SCHREIBT:
                verstoesse.append(f"{r}:{k.lineno} .{name}(...) in einer Datei mit Garmin-Tabellen – über store.py schreiben")
    assert verstoesse == [], "\n".join(verstoesse)


def test_b2_garmin_client_mit_passwort_nur_bei_der_einrichtung():
    """AE-8: Der Sync-Client entsteht ohne Zugangsdaten. Garmin(...) mit Argumenten nur in begin_password_login."""
    if not (BACKEND / GARMIN_ZIEL).exists():
        return
    verstoesse = []
    for p in py_dateien(APP):
        baum = _baum(p)
        erlaubt = set()
        if rel(p) == GARMIN_ZIEL:
            for f in ast.walk(baum):
                if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name == "begin_password_login":
                    erlaubt |= {id(k) for k in ast.walk(f)}
        for k in ast.walk(baum):
            if isinstance(k, ast.Call) and _aufrufname(k) == "Garmin" and (k.args or k.keywords) and id(k) not in erlaubt:
                verstoesse.append(f"{rel(p)}:{k.lineno} Garmin(...) mit Argumenten außerhalb von begin_password_login")
    assert verstoesse == [], "\n".join(verstoesse)


def test_s9_exklusive_vorgaenge_nutzen_die_sperre():
    """AE-14: Sync, Verbinden/Trennen, Alles löschen, Sicherung und Migration laufen unter OperationGate.exclusive."""
    verstoesse = []
    for r in SPERR_PFLICHT:
        p = BACKEND / r
        if p.exists() and ".exclusive(" not in p.read_text(encoding="utf-8"):
            verstoesse.append(f"{r} nutzt die Vorgangs-Sperre nicht (.exclusive(...))")
    for p in py_dateien(APP / "privacy"):
        baum = _baum(p)
        loescht = any(isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and "delete" in f.name for f in ast.walk(baum))
        if loescht and ".exclusive(" not in p.read_text(encoding="utf-8"):
            verstoesse.append(f"{rel(p)} löscht ohne Vorgangs-Sperre")
    main = APP / "main.py"
    if main.exists():
        text = main.read_text(encoding="utf-8")
        if "run_migrations(" in text and ".exclusive(" not in text:
            verstoesse.append("app/main.py führt Migrationen ohne Vorgangs-Sperre aus")
    assert verstoesse == [], "\n".join(verstoesse)


def test_s1_host_und_origin_pruefung_eingebaut():
    """AE-19: create_app baut RequestGuard ein; der Guard prüft Host, Origin, Sec-Fetch-Site und JSON-Pflicht."""
    if not _hat_create_app():
        return
    main = (APP / "main.py").read_text(encoding="utf-8")
    assert re.search(r"add_middleware\(\s*RequestGuard", main), "create_app ohne add_middleware(RequestGuard, ...)"
    sec = APP / "security.py"
    assert sec.exists(), "app/security.py fehlt"
    text = sec.read_text(encoding="utf-8")
    assert "class RequestGuard" in text, "app/security.py ohne class RequestGuard"
    fehlend = [w for w in ("host", "origin", "sec-fetch-site", "application/json") if w not in text.lower()]
    assert fehlend == [], f"RequestGuard prüft nicht: {fehlend}"


def test_s1_sicherheitstests_ueber_alle_routen_vorhanden():
    """AE-19: Die Paket-Tests zählen alle Routen über app.routes auf (neue Routen automatisch mitgeprüft)."""
    if not (APP / "security.py").exists():
        return
    texte = _testtexte()
    fehlend = [t for t in ("app.routes", "test_a10_fremder_host_abgelehnt",
                           "test_a10_fremder_origin_bei_schreiben_abgelehnt", "test_a10_schreiben_ohne_json_abgelehnt")
               if t not in texte]
    assert fehlend == [], f"In backend/tests fehlt: {fehlend}"


def test_s2_validierungsfehler_ohne_eingabewerte():
    """AE-13: Eigener Handler für RequestValidationError, der nie input/ctx zurückgibt."""
    if not _hat_create_app():
        return
    handler = [p for p in py_dateien(APP) if re.search(r"exception_handler\(\s*RequestValidationError",
                                                       p.read_text(encoding="utf-8"))]
    assert handler, "Kein Handler für RequestValidationError registriert"
    verstoesse = []
    for p in handler:
        text = p.read_text(encoding="utf-8")
        if re.search(r"""["'](input|ctx)["']\s*:""", text):
            verstoesse.append(f"{rel(p)} gibt input/ctx zurück")
        if re.search(r"(jsonable_encoder\(\s*\w+\.errors\(\)|content\s*=\s*\w+\.errors\(\)|[\"']detail[\"']\s*:\s*\w+\.errors\(\))", text):
            verstoesse.append(f"{rel(p)} gibt exc.errors() ungefiltert zurück")
    if "test_a9_passwort_nicht_in_422_antwort" not in _testtexte():
        verstoesse.append("backend/tests ohne test_a9_passwort_nicht_in_422_antwort")
    assert verstoesse == [], "\n".join(verstoesse)


def test_b5_fehlerkennungen_nur_aus_dem_katalog():
    """AE-13: ERROR_CATALOG in app/errors.py enthält den Pflichtinhalt; AppError nur mit Kennungen aus dem Katalog."""
    katalog = _katalog()
    if katalog is None:
        return
    verstoesse = [f"Katalog ohne Pflicht-Kennung {c}" for c in sorted(PFLICHT_KENNUNGEN - katalog)]
    for p in py_dateien(APP):
        for k in ast.walk(_baum(p)):
            if isinstance(k, ast.Call) and _aufrufname(k) == "AppError" and k.args \
                    and isinstance(k.args[0], ast.Constant) and k.args[0].value not in katalog:
                verstoesse.append(f"{rel(p)}:{k.lineno} unbekannte Fehlerkennung {k.args[0].value!r}")
            ziel = k.targets[0] if isinstance(k, ast.Assign) else None
            if isinstance(ziel, ast.Name) and ziel.id == "ERROR_CATALOG" and rel(p) != "app/errors.py":
                verstoesse.append(f"{rel(p)} definiert einen zweiten ERROR_CATALOG")
    assert verstoesse == [], "\n".join(verstoesse)


def test_s14_kein_ausnahmetext_in_meldungen():
    """AE-13: In except-Blöcken landet die Ausnahme nie in message/detail (Meldungen nur aus dem Katalog).
    Scharf ab app/errors.py (P1a ersetzt den Prototyp)."""
    if not (APP / "errors.py").exists():
        return
    verstoesse = []

    def nutzt(ausdruck, name):
        return any(isinstance(n, ast.Name) and n.id == name for n in ast.walk(ausdruck))

    for p in py_dateien(APP):
        for h in ast.walk(_baum(p)):
            if not (isinstance(h, ast.ExceptHandler) and h.name):
                continue
            for k in ast.walk(ast.Module(body=h.body, type_ignores=[])):
                paare = []
                if isinstance(k, ast.Assign):
                    for ziel in k.targets:
                        if isinstance(ziel, ast.Tuple) and isinstance(k.value, ast.Tuple):
                            paare += list(zip(ziel.elts, k.value.elts))
                        else:
                            paare.append((ziel, k.value))
                for ziel, wert in paare:
                    if isinstance(ziel, ast.Attribute) and ziel.attr in ("message", "detail") and nutzt(wert, h.name):
                        verstoesse.append(f"{rel(p)}:{k.lineno} Ausnahmetext in .{ziel.attr}")
                if isinstance(k, ast.Call):
                    for kw in k.keywords:
                        if kw.arg in ("message", "detail") and nutzt(kw.value, h.name):
                            verstoesse.append(f"{rel(p)}:{k.lineno} Ausnahmetext in {kw.arg}=")
    assert verstoesse == [], "\n".join(verstoesse)


def test_s7_kein_schluessel_literal_und_kein_ersatzschluessel():
    """Kein Fernet-Schlüssel als Literal; SIMFIT_SECRET_KEY ohne Standardwert."""
    kandidaten = py_dateien(APP) + py_dateien(BACKEND / "tests")
    for extra in (ROOT / "start", ROOT / "frontend" / "src"):
        if extra.exists():
            kandidaten += [p for p in extra.rglob("*") if p.is_file() and p.suffix in ("", ".sh", ".bat", ".ps1",
                                                                                    ".command", ".ts", ".tsx", ".py")]
    kandidaten += [p for p in (ROOT / "Dockerfile", ROOT / "docker-compose.yml", BACKEND / ".env.example",
                               ROOT / ".env.example") if p.exists()]
    verstoesse = []
    for p in kandidaten:
        if "node_modules" in p.parts:
            continue
        for nr, zeile in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if FERNET_LITERAL.search(zeile):
                verstoesse.append(f"{p.relative_to(ROOT)}:{nr} sieht aus wie ein Fernet-Schlüssel")
    for p in py_dateien(APP):
        for k in ast.walk(_baum(p)):
            if isinstance(k, ast.Call) and len(k.args) >= 2 and isinstance(k.args[0], ast.Constant) \
                    and k.args[0].value == "SIMFIT_SECRET_KEY" and isinstance(k.args[1], ast.Constant) and k.args[1].value:
                verstoesse.append(f"{rel(p)}:{k.lineno} Ersatzwert für SIMFIT_SECRET_KEY")
    assert verstoesse == [], "\n".join(verstoesse)


def test_s11_cors_ohne_standardherkunft():
    """AE-19: CORS_ORIGINS hat keinen Standardwert (Auslieferung ohne CORS). Scharf ab app/settings.py."""
    if not (APP / "settings.py").exists():
        return
    verstoesse = []
    for p in py_dateien(APP):
        for k in ast.walk(_baum(p)):
            if isinstance(k, ast.Call) and len(k.args) >= 2 and isinstance(k.args[0], ast.Constant) \
                    and k.args[0].value == "CORS_ORIGINS" and isinstance(k.args[1], ast.Constant) \
                    and str(k.args[1].value).strip():
                verstoesse.append(f"{rel(p)}:{k.lineno} Standardwert für CORS_ORIGINS")
    assert verstoesse == [], "\n".join(verstoesse)


def test_s11_api_doku_in_auslieferung_aus():
    """AE-19: FastAPI(...) in create_app setzt docs_url, redoc_url und openapi_url ausdrücklich (aus, außer api_docs)."""
    if not _hat_create_app():
        return
    aufrufe = [k for k in ast.walk(_baum(APP / "main.py")) if isinstance(k, ast.Call) and _aufrufname(k) == "FastAPI"]
    assert aufrufe, "create_app ohne FastAPI(...)"
    for k in aufrufe:
        fehlend = {"docs_url", "redoc_url", "openapi_url"} - {kw.arg for kw in k.keywords}
        assert not fehlend, f"FastAPI(...) ohne {sorted(fehlend)}"


def test_s4_sqlite_secure_delete():
    """AE-20: Jede Verbindung mit PRAGMA secure_delete=ON. Scharf, sobald Alembic eingerichtet ist (P1a)."""
    if not (BACKEND / "migrations").is_dir():
        return
    db = APP / "db.py"
    assert db.exists() and "secure_delete" in db.read_text(encoding="utf-8"), "app/db.py setzt secure_delete nicht"


def test_s5_abhaengigkeiten_mit_hashes():
    """Lieferkette: requirements.lock mit Hashes, keine Testwerkzeuge zur Laufzeit, Docker mit --require-hashes."""
    lock = BACKEND / "requirements.lock"
    if not lock.exists():
        return
    verstoesse = []
    logisch = re.sub(r"\\\s*\n", " ", lock.read_text(encoding="utf-8"))
    for zeile in logisch.splitlines():
        z = zeile.strip()
        if not z or z.startswith(("#", "--")):
            continue
        if "==" not in z or "--hash=sha256:" not in z:
            verstoesse.append(f"requirements.lock ohne == und Hash: {z[:60]}")
        if re.match(r"(?i)pytest", z):
            verstoesse.append(f"Testwerkzeug in Laufzeit-Abhängigkeiten: {z[:40]}")
    if (BACKEND / "requirements.txt").exists():
        verstoesse.append("backend/requirements.txt neben requirements.lock (eine Quelle: .in → .lock)")
    docker = ROOT / "Dockerfile"
    if docker.exists() and "--require-hashes" not in docker.read_text(encoding="utf-8"):
        verstoesse.append("Dockerfile installiert ohne --require-hashes")
    assert verstoesse == [], "\n".join(verstoesse)


def _betriebsdateien():
    dateien = [p for p in (ROOT / "Dockerfile", ROOT / "docker-compose.yml") if p.exists()]
    if (ROOT / "start").is_dir():
        dateien += [p for p in (ROOT / "start").rglob("*") if p.is_file()]
    return dateien


def test_s9_ein_worker_ohne_zugriffsprotokoll():
    """AE-14/AE-20: Jeder uvicorn-Start in der Auslieferung mit --workers 1 und --no-access-log."""
    verstoesse = []
    for p in _betriebsdateien():
        text = p.read_text(encoding="utf-8", errors="ignore")
        if "uvicorn" not in text:
            continue
        flach = re.sub(r"\s+", " ", re.sub(r"""[\[\]",']""", " ", text))
        for pflicht in ("--workers 1", "--no-access-log"):
            if pflicht not in flach:
                verstoesse.append(f"{p.relative_to(ROOT)}: uvicorn ohne {pflicht}")
    assert verstoesse == [], "\n".join(verstoesse)


def test_s7_compose_fester_name_und_nur_lokal():
    """Compose: fester Projektname (Update in neuen Ordner verliert kein Volume), Ports nur 127.0.0.1, Log-Rotation."""
    p = ROOT / "docker-compose.yml"
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    verstoesse = []
    if not re.search(r"""(?m)^name:\s*["']?simfit["']?\s*$""", text):
        verstoesse.append("docker-compose.yml ohne 'name: simfit'")
    if "max-size" not in text:
        verstoesse.append("docker-compose.yml ohne Log-Rotation (max-size)")
    zeilen = text.splitlines()
    for i, z in enumerate(zeilen):
        if re.match(r"\s*ports:\s*$", z):
            einzug = len(z) - len(z.lstrip())
            for w in zeilen[i + 1:]:
                if w.strip() and len(w) - len(w.lstrip()) <= einzug:
                    break
                eintrag = w.strip().lstrip("-").strip().strip("\"'")
                if eintrag and not eintrag.startswith("127.0.0.1:"):
                    verstoesse.append(f"Port nicht nur lokal: {eintrag}")
    assert verstoesse == [], "\n".join(verstoesse)


def test_s13_dockerignore_schliesst_daten_aus():
    """Image enthält nie lokale DB, Geheimnisse, venv, Daten, Sicherungen, node_modules."""
    if not (ROOT / "Dockerfile").exists():
        return
    p = ROOT / ".dockerignore"
    assert p.exists(), ".dockerignore fehlt"
    eintraege = {z.strip().strip("/").removeprefix("**/") for z in p.read_text(encoding="utf-8").splitlines()}
    fehlend = [e for e in ("*.db", ".env", ".venv", "data", "backups", "secrets", "node_modules") if e not in eintraege]
    assert fehlend == [], f".dockerignore ohne: {fehlend}"
