"""Architekturtests Frontend (Simfit). Lesen nur Dateien (Textmuster), führen nichts aus.

Regeln und Begründung: docs/ARCHITEKTUR.md (AE-Nummern). Ändern nur der Architekt.
"""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "frontend" / "src"
CLIENT_ZIEL = "lib/api/client.ts"  # AE-11
CLIENT_BESTAND = "lib/api.ts"  # Prototyp, gilt nur bis lib/api/client.ts existiert
ERLAUBTE_ENV = {"NEXT_PUBLIC_API_URL", "NODE_ENV"}
ERLAUBTE_HOSTS = ("localhost", "127.0.0.1", "openfoodfacts.org", "opendatacommons.org")  # AE-12


def quellen():
    """Produktiv-Quelltexte (ohne Tests)."""
    return sorted(p for p in SRC.rglob("*") if p.suffix in (".ts", ".tsx")
                  and not re.search(r"\.(test|spec)\.tsx?$", p.name) and "__tests__" not in p.parts)


def rel(p: Path) -> str:
    return p.relative_to(SRC).as_posix()


def test_a10_netzwerkaufrufe_nur_im_api_client():
    # Übergang: Solange der Prototyp-Client lib/api.ts existiert (bis P1b ihn löscht), ist er zusätzlich erlaubt.
    erlaubt = {c for c in (CLIENT_ZIEL, CLIENT_BESTAND) if (SRC / c).exists()} or {CLIENT_ZIEL}
    nutzer = {rel(p) for p in quellen() if re.search(r"(?<![\w.])fetch\s*\(|XMLHttpRequest|new\s+WebSocket|axios",
                                                    p.read_text(encoding="utf-8"))}
    assert nutzer <= erlaubt, f"Netzwerkaufrufe außerhalb von {sorted(erlaubt)}: {sorted(nutzer - erlaubt)}"


def test_a9_keine_geheimnisse_im_browser_code():
    verstoesse = []
    for p in quellen():
        for name in re.findall(r"process\.env\.([A-Z0-9_]+)", p.read_text(encoding="utf-8")):
            if name not in ERLAUBTE_ENV:
                verstoesse.append(f"{rel(p)}: process.env.{name}")
    assert verstoesse == [], "\n".join(verstoesse)


def test_a10_keine_externen_ressourcen_im_browser():
    verstoesse = []
    for p in quellen():
        text = p.read_text(encoding="utf-8")
        if re.search(r"""from\s+["']next/font/google["']""", text):
            verstoesse.append(f"{rel(p)}: next/font/google (Schrift selbst hosten)")
        for host in re.findall(r"https?://([A-Za-z0-9.-]+)", text):
            if not any(host == h or host.endswith("." + h) for h in ERLAUBTE_HOSTS):
                verstoesse.append(f"{rel(p)}: externe Adresse {host}")
    assert verstoesse == [], "\n".join(verstoesse)


def test_seiten_und_bausteine_importieren_keine_backend_interna():
    verstoesse = [rel(p) for p in quellen()
                  if re.search(r"""from\s+["'][./]*(\.\./)+backend""", p.read_text(encoding="utf-8"))]
    assert verstoesse == [], f"Frontend greift auf Backend-Dateien zu: {verstoesse}"


# ---------------------------------------------------------------------------
# Regeln aus der Planprüfung (B5, S2, DESIGN 10.3), siehe ARCHITEKTUR.md Abschnitt 11.
# ---------------------------------------------------------------------------
BACKEND_ERRORS = ROOT / "backend" / "app" / "errors.py"
NUR_IM_CLIENT = {"network_error"}  # Fehler ohne Serverantwort, erzeugt nur client.ts
FARBE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(rgb|rgba|hsl|hsla)\(")


def _backend_kennungen():
    if not BACKEND_ERRORS.exists():
        return None
    for k in ast.walk(ast.parse(BACKEND_ERRORS.read_text(encoding="utf-8"))):
        ziel = k.targets[0] if isinstance(k, ast.Assign) else k.target if isinstance(k, ast.AnnAssign) else None
        if isinstance(ziel, ast.Name) and ziel.id == "ERROR_CATALOG" and isinstance(k.value, ast.Dict):
            return {s.value for s in k.value.keys if isinstance(s, ast.Constant)}
    return None


def test_b5_fehlerkennungen_backend_und_frontend_gleich():
    """AE-11/AE-13: ApiErrorCode in client.ts = ERROR_CATALOG im Backend (+ network_error). Scharf, wenn beide existieren."""
    backend = _backend_kennungen()
    client = SRC / CLIENT_ZIEL
    if backend is None or not client.exists():
        return
    treffer = re.search(r"export\s+type\s+ApiErrorCode\s*=([^;]*);", client.read_text(encoding="utf-8"))
    assert treffer, "client.ts ohne 'export type ApiErrorCode = ...;'"
    frontend = set(re.findall(r"""["']([a-z_]+)["']""", treffer.group(1)))
    assert frontend - NUR_IM_CLIENT == backend, (
        f"nur im Backend: {sorted(backend - frontend)}; nur im Frontend: {sorted(frontend - NUR_IM_CLIENT - backend)}")


def test_s2_fehlerdetail_nie_als_json_anzeigen():
    """AE-13/S2: JSON.stringify nur für Anfrage-Körper – nie, um eine Fehlerantwort anzuzeigen. Scharf ab lib/api/client.ts."""
    if not (SRC / CLIENT_ZIEL).exists():
        return
    verstoesse = []
    for p in quellen():
        for nr, zeile in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for m in re.finditer(r"JSON\.stringify\s*\(", zeile):
                if not re.search(r"\bbody\s*[:=]\s*$", zeile[: m.start()]):
                    verstoesse.append(f"{rel(p)}:{nr} JSON.stringify außerhalb eines Anfrage-Körpers")
    assert verstoesse == [], "\n".join(verstoesse)


def test_keine_html_injektion():
    """Fremdtexte (Aktivitätsnamen, OFF-Produktnamen) nur als Text: kein dangerouslySetInnerHTML/innerHTML/eval."""
    verstoesse = [f"{rel(p)}: {m.group(0)}" for p in quellen() for m in re.finditer(
        r"dangerouslySetInnerHTML|\.(inner|outer)HTML\s*=|\beval\s*\(|new\s+Function\s*\(", p.read_text(encoding="utf-8"))]
    assert verstoesse == [], "\n".join(verstoesse)


def test_design_keine_festen_farben():
    """DESIGN 10.3: Farben nur über Tokens (CSS-Variablen in globals.css). Scharf, sobald components/ui existiert (P2).
    components/ui ist generiert (shadcn) und ausgenommen."""
    if not (SRC / "components" / "ui").is_dir():
        return
    verstoesse = []
    for p in quellen():
        r = rel(p)
        if r.startswith("components/ui/") or not r.startswith(("components/", "app/")):
            continue
        for nr, zeile in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if FARBE.search(zeile):
                verstoesse.append(f"{r}:{nr} feste Farbe – var(--…) bzw. Token-Klasse verwenden")
    assert verstoesse == [], "\n".join(verstoesse)
