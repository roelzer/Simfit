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
REINE_MODULE = ("app/core/*.py", "app/garmin/normalize.py", "app/nutrition/calc.py", "app/training/matching.py")  # AE-3
VERBOTEN_IN_REINEN = ("fastapi", "starlette", "sqlalchemy", "sqlmodel", "httpx", "requests", "urllib", "socket",
                      "garminconnect", "curl_cffi", "os", "subprocess", "app.db", "app.settings", "app.token_vault")
NETZ_BIBLIOTHEKEN = ("httpx", "requests", "urllib.request", "aiohttp", "socket", "curl_cffi")
NETZ_ERLAUBT = {"app/nutrition/off_client.py"}  # AE-9
GARMIN_ZIEL = "app/garmin/connection.py"  # AE-8
GARMIN_BESTAND = {"app/sources/garmin.py", "app/garmin_login.py"}  # Prototyp, gilt nur bis connection.py existiert
EINHEITEN = ("_m", "_s", "_ms", "_kcal", "_g", "_kg", "_bpm", "_s_per_km", "_per_100g", "_days")  # AE-5
EINHEITENLOS = {"id", "steps", "sleep_score", "stress_avg", "body_battery_high", "body_battery_low",
                "weeks_count", "sort_order", "consecutive_rate_limits"}
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
