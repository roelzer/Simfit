# Plan: Simfit weiterbauen (Trainingsplan, Lebensmittelsuche, Sicherheit, Übergabe an Freund)

**Stand:** 2026-11-04 · **Stufe:** Groß · **Profil:** web · **Besetzung:** Kunde (Empfehlung, wartet auf Simon) · **Status:** Entwurf

## 1. Ziel
Aus dem Prototyp wird eine übergabefertige App für den Freund: Garmin-Daten holen und zeigen (zuerst mit Demo-Daten), Kalorien tracken mit Open-Food-Facts-Suche, Trainingspläne erstellen und mit den Aktivitäten abgleichen, Gesundheitsdaten und Garmin-Tokens sicher halten, dazu Anleitung zur Inbetriebnahme. Echte Garmin-Zugangsdaten kommen erst am Ende, der Freund trägt sie selbst ein.

## 2. Anforderungen
Siehe `docs/lastenheft.md` (A1–A11). Zuordnung zu Paketen legt der Architekt fest.

## 3. Ausgangslage im Code
Prototyp: `backend/` (FastAPI, SQLModel, SQLite, Demo- und Garmin-Quelle, Sync im Hintergrund, Ernährungs-API, 1 Integrationstest), `frontend/` (Next.js, Recharts, eigenes CSS, 4 Seiten). Keine Test-Schranke, kein Testbefehl in `.claude/dev-team.json`. Garmin-Quelle gegen echtes Konto ungetestet. Tokens liegen unverschlüsselt in `~/.simfit/garmin`. Frontend weicht vom Oberflächen-Standard ab (eigenes CSS statt Tailwind/shadcn). Spalten heißen teils nicht nach der Einheiten-Regel (`weight_kg` ja, `steps` ohne Einheit ok).

## 4. Lösung / 5. Arbeitspakete
Vom `architekt` (`docs/ARCHITEKTUR.md`), wird hier eingetragen.

## 6. Absicherung
- Testgetrieben, verdeckte Abnahmetests (Tester), Architekturtests (Architekt).
- Garmin nie echt in Tests: nur aufgezeichnete Beispieldaten.
- **Einsatz:** Instanz des Freundes, voraussichtlich lokal bei ihm (Q1); falls gehostet: öffentlich erreichbar mit Passwortschutz.

**Auslöser-Checkliste**
| Risiko-Auslöser | ja/nein | Begründung |
|---|---|---|
| Anmeldung/Rechte | offen | lokal nein; gehostet ja (Schutz der Instanz), hängt an Q1 |
| personenbezogene/vertrauliche Daten | ja | Gesundheitsdaten (Art. 9) |
| Datenbank/Migration | ja | Schema wächst (Trainingsplan), Änderungen an bestehender SQLite |
| Serverbetrieb | offen | hängt an Q1 |
| Netzwerk/Schnittstellen | ja | Garmin Connect, Open Food Facts |
| Updates/Signierung/Release | ja | Übergabe an Freund, Updatepfad |
| Geheimnisse/Schlüssel | ja | Garmin-Tokens und -Zugang |
| Löschen/Überschreiben | ja | Sync überschreibt Tageswerte, Löschen von Einträgen/Plänen |
| Desktop-Berechtigungen | nein | Web-App |
| neue fremde Abhängigkeiten | ja | Tailwind/shadcn, Verschlüsselungsbibliothek, ggf. Docker |
| mehrere Nutzer, dieselben Daten | nein | ein Nutzer |
| Dateien/Daten von außen (Upload/Import) | ja | Antworten von Garmin und Open Food Facts sind Fremddaten |
| Zahlungen | nein | – |
| KI-/externe Dienste | ja | Open Food Facts (Suchbegriffe/Barcodes verlassen die Instanz) |

## 7. Risiken
- Garmin-Anbindung ungetestet; Bibliothek kann brechen oder gesperrt werden (Mitigation: aufgezeichnete Beispieldaten, Backoff, Quelle austauschbar).
- Gesundheitsdaten eines Dritten (Mitigation: lokal beim Freund, Verschlüsselung, Löschen/Export).

## 8. Harte Stopps
Echte Zugangsdaten nötig; Hosting/laufende Kosten; Änderung der Datenquelle außerhalb des Plans.

## 9. Offene Fragen an Simon
Q1–Q3 in `docs/OFFENE_FRAGEN.md`.
