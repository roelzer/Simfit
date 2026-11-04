# Bericht architekt – 2026-11-04 13:47

🟡 Architekt, Modus entwurf, Schritt 2 Teil C: **4 von 6 Bauplänen fertig. P12 und der Prüf-Schwerpunkt fehlen noch (Status BLOCKIERT, Grund: Kontext voll).** Fertig sind die Baupläne P8, P9, P10, P14 und P15. Jeder hat Dateien und Besitz, exakte Signaturen, Tests mit Anforderungsnummer und erwartetem Wert, Randfälle, Eskalation und eine Antwortzeile je Kritiker-Rückfrage. Die Namen aus P1b und P2 habe ich nachgelesen und wörtlich übernommen. Architekturtests habe ich nicht geändert und nicht ausgeführt (nicht geprüft).

1. **Was fehlt, nächster Schritt:** ein frischer Architekt schreibt
   - `docs/bauplaene/P12.md` (Trainingsplan-Oberfläche): im Stil von P10, gebaut gegen `training.ts` aus P1b. Die Fehlerfälle stehen in `P11.md` Zeile 33–56: 422 für `start_date` bzw. `date`, 409 `conflict`, wenn Einheiten aus dem Zeitraum fallen. Die drei Kritiker-Rückfragen sind ungefähr so zu beantworten:
     - `training.ts` legt P1b an.
     - Vorauswahl: der laufende Plan, sonst der neueste.
     - Dauer in Stunden und Minuten wird zu Sekunden umgerechnet (ganzzahlig), km zu Metern (gerundet auf 1 m).
   - `docs/bauplaene/PRUEFSCHWERPUNKT.md` (bis 5 Fälle je Meilenstein M1–M4). Als Ausgangspunkt eignet sich der alte Prüf-Schwerpunkt in `docs/pruefberichte/20261104-123834-architekt-ac3282c008d26e6b1.md`, Zeile 332–337.

2. **Ein Punkt, der zwei Pakete verbindet (bitte prüfen und in ARCHITEKTUR §6 nachtragen lassen):**
   - Tagebucheinträge (`GET`/`POST /food-log`) liefern zusätzlich die vier fertig gerechneten Werte `kcal`, `protein_g`, `carbs_g`, `fat_g`. Grund: Sonst müsste die Oberfläche die Nährwertrechnung ein zweites Mal bauen.
   - Das Backend dafür baut P9. P10 ergänzt dazu genau den Typ `FoodLogEntry` in `nutrition.ts` (Besitz P1b, erlaubt nach AE-11).
   - Die Schwester, die ARCHITEKTUR.md nachzieht, sollte das in §6 aufnehmen.

3. **Entscheidungen, die vom bisherigen Stand abweichen:**
   - **P9:** Die USDA-Basis-Lebensmittel kommen ohne Migration und ohne Änderung an `main.py` in die Datenbank. Sie werden bei der lokalen Suche nachgelegt, falls sie fehlen (doppelte Einfügungen werden still übersprungen). So sind sie nach „Alles löschen“ automatisch wieder da, ohne dass P13 auf den Ernährungsbereich zugreifen muss.
   - **P10:** Untergrenze der Menge ist 0,5 g, nicht 1 g. DESIGN 6.4 muss der Designer angleichen. Die USDA-Quelle steht als Text ohne Link da, weil der Architekturtest nur die Links zu Open Food Facts erlaubt.
   - **P8:**
     - Im Zeitraum für „Daten holen“ entfällt die Auswahl „1 Jahr“ (höchstens 90 Tage).
     - Die Zeile „Als Nächstes …“ bei „Training heute“ entfällt (Annahme), weil `/training/today` nur den heutigen Tag liefert.
     - Ob ein Ziel festgelegt ist, erkennt die Willkommenskarte an `goal !== null`.
   - **P14:**
     - Die CSP (Sicherheitsregel, welche Skripte der Browser ausführen darf) wird je Seite aus Prüfsummen der eingebetteten Skripte berechnet. So bleibt die Kopfzeile klein.
     - Der Sicherungsstatus kommt über einen neuen Endpunkt `GET /api/backup/status`. `/health` bleibt unverändert, damit der Test aus P1a nicht angepasst werden muss.
     - Die Schlüsseldatei liegt außerhalb des Projektordners. Docker Compose findet sie über die Variable `SIMFIT_ENV_FILE`, die das Startskript setzt.
     - Der Port ist mit `SIMFIT_PORT` änderbar; die Host-Prüfung nutzt dann den äußeren Port.
   - **P14 ändert in M4** Dateien, die P1a gehören (`settings.py`, `context.py`, `db.py`, Header-Teil von `security.py`), außerdem `system.ts` und eine Zeile in der Einstellungsseite. Das ist erlaubt, weil P14 in M4 allein läuft.

4. **Offene Annahmen für Simon:**
   - E-2 (Betriebssystem des Freundes): P14 baut beide Varianten, Windows `.bat`/`.ps1` und Mac/Linux `.command`/`.sh`. Die nicht benötigte Variante entfernt der Projektleiter nach Simons Antwort.
   - Docker-Mindestversion: beim Sicherheitsprüfer nur mit Sicherheit 65. P15 prüft sie per Websuche nach.
   - Höchstens 90 Tage bei „Daten holen“.
   - Kein eigener Text für „nächste Einheit“ bei „Training heute“.

5. **Bitten an den Projektleiter:**
   - Vor P9 die USDA-Liste in genau dem Format liefern, das in `P9.md` beschrieben ist.
   - Den neuen Text für die „Nur Simon“-Zeile zum A6-Probelauf aus `P15.md` in `docs/OFFENE_FRAGEN.md` eintragen.
   - Die geschriebenen Dateien unter `docs/bauplaene/` liegen außerhalb meines normalen Schreibbereichs. Ich habe sie auf deine ausdrückliche Anweisung angelegt; bitte im Diff so verbuchen.

**Geänderte Dateien:**
- /home/user/Simfit/docs/bauplaene/P8.md
- /home/user/Simfit/docs/bauplaene/P9.md
- /home/user/Simfit/docs/bauplaene/P10.md
- /home/user/Simfit/docs/bauplaene/P14.md
- /home/user/Simfit/docs/bauplaene/P15.md

Kein Commit (meine Rolle committet nicht).
