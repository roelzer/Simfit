"""Architekturtests Frontend (Simfit). Lesen nur Dateien (Textmuster), führen nichts aus.

Regeln und Begründung: docs/ARCHITEKTUR.md (AE-Nummern). Ändern nur der Architekt.
"""
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
    erlaubt = CLIENT_ZIEL if (SRC / CLIENT_ZIEL).exists() else CLIENT_BESTAND
    nutzer = {rel(p) for p in quellen() if re.search(r"(?<![\w.])fetch\s*\(|XMLHttpRequest|new\s+WebSocket|axios",
                                                    p.read_text(encoding="utf-8"))}
    assert nutzer <= {erlaubt}, f"Netzwerkaufrufe außerhalb von src/{erlaubt}: {sorted(nutzer - {erlaubt})}"


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
