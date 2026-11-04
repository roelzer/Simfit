# Plan: Simfit weiterbauen (Trainingsplan, Lebensmittelsuche, Sicherheit, Übergabe an Freund)

**Stand:** 2026-11-04 · **Stufe:** Groß · **Profil:** web · **Besetzung:** Kunde (Empfehlung, wartet auf Simon) · **Status:** Entwurf

## 1. Ziel
Aus dem Prototyp wird eine übergabefertige App für den Freund: Garmin-Daten holen und zeigen (zuerst mit Demo-Daten), Kalorien tracken mit Open-Food-Facts-Suche, Trainingspläne erstellen und mit den Aktivitäten abgleichen, Gesundheitsdaten und Garmin-Tokens sicher halten, dazu Anleitung zur Inbetriebnahme. Echte Garmin-Zugangsdaten kommen erst am Ende, der Freund trägt sie selbst ein.

## 2. Anforderungen
Siehe `docs/lastenheft.md` (A1–A11). Zuordnung zu Paketen legt der Architekt fest.

## 3. Ausgangslage im Code
Prototyp: `backend/` (FastAPI, SQLModel, SQLite, Demo- und Garmin-Quelle, Sync im Hintergrund, Ernährungs-API, 1 Integrationstest), `frontend/` (Next.js, Recharts, eigenes CSS, 4 Seiten). Keine Test-Schranke, kein Testbefehl in `.claude/dev-team.json`. Garmin-Quelle gegen echtes Konto ungetestet. Tokens liegen unverschlüsselt in `~/.simfit/garmin`. Frontend weicht vom Oberflächen-Standard ab (eigenes CSS statt Tailwind/shadcn). Spalten heißen teils nicht nach der Einheiten-Regel (`weight_kg` ja, `steps` ohne Einheit ok).

## 4. Lösung
Details: `docs/ARCHITEKTUR.md`. Der Prototyp bleibt und wird umgebaut.
- Fachbereiche `garmin`, `nutrition`, `training`, `privacy` mit reinen Rechenmodulen; Datenmodell nur in `backend/app/models/`; Adapter am Rand (`garmin/connection.py` einziger Ort mit `garminconnect`, `nutrition/off_client.py` einziger Ort mit Netzwerk zu Open Food Facts).
- Schema über Alembic-Migrationen, Einheiten in Feldnamen (Englisch, z. B. `resting_hr_bpm`), Rohdaten getrennt gespeichert, „leer überschreibt nie“, Tokens verschlüsselt (Fernet), Zeitzone der Instanz statt UTC.
- Fertiger Zustand: ein Prozess liefert API und statisch exportierte Oberfläche unter `127.0.0.1:8000`.
- **ANNAHME:** Garmin-Beispieldaten sind nachgebaut (nicht aufgezeichnet); ob sie zur echten Struktur passen, zeigt erst der erste echte Sync. **ANNAHME:** OFF-Grenzen (10 Suchen/min, 100 Abrufe/min) stammen aus einer Websuche, Doku nicht erreichbar.

## 5. Arbeitspakete
| Nr | Was | Abhängig von | Parallel mit |
|---|---|---|---|
| **M1** | | | |
| P1 | Backend-Fundament (Modell, Migration, Fehlerformat, API v1) | V0 | P2, P3 |
| P2 | Oberflächen-Grundlage (Tailwind, shadcn/ui, Tokens) | V0, Designer | P1, P3 |
| P3 | Open-Food-Facts-Adapter | V0 | P1, P2 |
| **M2** | | | |
| P4 | Garmin-Normalisierung und Beispieldaten | P1 | P5, P6, P8 |
| P5 | Sync-Dienst (Backoff, Doppelungen, Abbruch) | P1 | P4, P6, P8 |
| P6 | Verbindung, Token-Tresor, Einrichtung im Browser | P1 | P4, P5, P8 |
| P7 | Garmin-Cloud-Quelle und Verdrahtung | P4, P5, P6 | P8 |
| P8 | Oberfläche Dashboard, Aktivitäten, Einstellungen | P1, P2 | P4–P7 |
| **M3** | | | |
| P9 | Lebensmittelsuche Backend | P1, P3 | P10–P12 |
| P10 | Ernährung-Oberfläche | P2, P8 | P9, P11, P12 |
| P11 | Trainingsplan Backend | P1 | P9, P10, P12 |
| P12 | Trainingsplan-Oberfläche | P2, P8 | P9–P11 |
| **M4** | | | |
| P13 | Datenschutz: Export und Löschen | M3 | P14 |
| P14 | Betrieb und Auslieferung (Docker, Sicherung, Header) | M3 | P13 |
| P15 | Übergabe-Anleitung | P14 | – |

Vorarbeit V0 (Tester, vor M1): `pytest.ini`, `conftest.py` mit Netzsperre, `tests/run_all.py`, Vitest-Konfiguration. Baupläne je Paket: Bericht des Architekten (`docs/pruefberichte/`), vollständige Fassung nach der Kritiker-Runde.
Mapping: A1 → P1,P4,P5,P7 · A2 → P2,P8 · A3 → P3,P9,P10 · A4 → P11,P12 · A5 → P1,P5,P7 · A6 → P14,P15 · A7 → P1,P6,P14 · A9 → P5,P6,P7 · A10 → P3,P9,P13,P14.

## 6. Absicherung
- Testgetrieben, verdeckte Abnahmetests (Tester), Architekturtests (Architekt).
- Garmin nie echt in Tests: nur aufgezeichnete Beispieldaten.
- **Einsatz:** Instanz des Freundes, voraussichtlich lokal bei ihm (Q1); falls gehostet: öffentlich erreichbar mit Passwortschutz.

**Auslöser-Checkliste**
| Risiko-Auslöser | ja/nein | Begründung |
|---|---|---|
| Anmeldung/Rechte | ja | App nimmt Garmin-Passwort und MFA-Code über die eigene Oberfläche an, begrenzt Anmeldeversuche (Kritiker-Befund) |
| personenbezogene/vertrauliche Daten | ja | Gesundheitsdaten (Art. 9) |
| Datenbank/Migration | ja | Schema wächst (Trainingsplan), Änderungen an bestehender SQLite |
| Serverbetrieb | ja | Dauerprozess mit Hintergrund-Sync, täglicher Sicherung, Docker, Migration beim Start (Kritiker-Befund) |
| Netzwerk/Schnittstellen | ja | Garmin Connect, Open Food Facts |
| Updates/Signierung/Release | ja | Übergabe an Freund, Updatepfad |
| Geheimnisse/Schlüssel | ja | Garmin-Tokens und -Zugang |
| Löschen/Überschreiben | ja | Sync überschreibt Tageswerte, Löschen von Einträgen/Plänen |
| Desktop-Berechtigungen | nein | Web-App; Startskripte schreiben `.env` und öffnen den Browser (knapp, vom Sicherheitsprüfer mitgeprüft) |
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
