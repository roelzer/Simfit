# Bericht designer – 2026-11-04 12:49

**Ampel: GELB.** Der Entwurf ist fertig und vollständig. Gelb, weil drei Punkte außerhalb der Oberfläche geklärt werden müssen (M1 bis M3 unten). Einer davon ist ein möglicher Datenverlust.

**Das Wichtigste in 5 Punkten**
1. **Richtung „Ruhiges Messinstrument“:** sachlich wie eine gute Sportuhr. Warmes Grau, eine Akzentfarbe Limette (im hellen Modus ein dunkles Oliv, weil Limette auf Hell zu blass ist), Schrift Geist selbst gehostet, alle Zahlen gleich breit. Begründung: Ein Laie liest Messwerte, deshalb Ruhe statt einer Kachelwand. Die App bewertet nichts als „gut“ oder „schlecht“, weil sie keine medizinischen Aussagen machen soll.
2. **Erkennungsmerkmal „Messleiste“:** Unter jeder Kennzahl zeigt eine feine Skala den heutigen Wert innerhalb der eigenen letzten 30 Tage, mit Strich für den Durchschnitt. Dasselbe Bild kommt in der Ernährung vor (gegessen gegen Ziel) und im Training (absolviert gegen geplant).
3. **Navigation:** Am Handy eine untere Tab-Leiste mit 5 Reitern (Heute, Aktivitäten, Ernährung, Training, Einstellungen). Am Desktop eine Seitenleiste links, dazwischen eine schmale Leiste. Grund (Screenshot des Prototyps bei 390 px angesehen): In der oberen Leiste rutscht „Training“ aus dem Bild, „Einstellungen“ fehlt ganz.
4. **Vollständigkeit:** 6 Bildschirme plus globale Bausteine, je mit Skizze für 1440 und 390 px und allen Zuständen: erster Start, lädt, gefüllt, viele Daten, Fehler, langer Text. Dazu 16 Abläufe mit Rückmeldung nach jedem Schritt und echte deutsche Texte, darunter:
   - Garmin verbinden in zwei Schritten (Passwort, dann Bestätigungscode)
   - Meldung mit Uhrzeit bei zu vielen Anfragen und bei zu vielen Anmeldeversuchen
   - Demo-Hinweis
   - Export
   - „ALLES LÖSCHEN“ mit exaktem Bestätigungstext
   - Trainingsstatus immer als Symbol und Text
   - Open-Food-Facts-Hinweis im Suchfenster und in der Fußzeile
5. **Merkposten an Projektleiter und Architekt** (DESIGN.md Abschnitt 9):
   - **M1, möglicher Datenverlust (Sicherheit 75):** Laut Architekturregel AE-6 (b) ersetzt eine Zeile aus einer anderen Quelle die vorhandene komplett. Ist nach „Verbindung trennen“ wieder die Demo-Quelle aktiv, würde der automatische Abruf alle 6 Stunden echte Garmin-Tage durch erfundene Werte ersetzen. Bitte festlegen: Demo-Daten überschreiben nie Garmin-Daten.
   - **M2 (Sicherheit 85):** Was „Alles löschen“ genau entfernt, ist offen: die Garmin-Anmeldung? Die Sicherungen in `backups/`? Läuft das Löschen ganz oder gar nicht?
   - **M3 (Sicherheit 85):** Für die Uhrzeit des nächsten Versuchs braucht die Oberfläche `retry_after` auch in der Fehlerantwort, wenn Garmin zu viele Anfragen meldet. Laut API-Vertrag steht der Zeitpunkt nur im Sync-Status.
   - Kleinere Punkte: M4 (startet nach dem Verbinden die Oberfläche den ersten Abruf oder das Backend?), M5 (Mengen nur in Gramm, keine ml oder Portionen; Hinweis an Simon), M6 (Endpunkt für „Training heute“).

**Angelegte Dateien** (sonst nichts geändert, laut git nur diese zwei neu)
- `/home/user/Simfit/docs/DESIGN.md`
- `/home/user/Simfit/design/tokens.json`: Farben hell und dunkel nach shadcn-Namen, Diagrammfarben 1 bis 5 mit Rollen, Schrift, Abstände, Radien, Schatten, Bewegung, Fokus. Auf gültiges JSON geprüft.
- Die Screenshots des Prototyps liegen nur im Scratchpad, z. B. `/tmp/claude-0/-home-user-Simfit/4a258c46-2b2d-542f-bbd8-c428f0922ded/scratchpad/m_.png`. Backend und Frontend sind wieder beendet (geprüft).

**Bildschirme und Zustände**

| Bildschirm | Erster Start / leer | lädt | gefüllt | viele Daten | Fehler | Handy 390 |
|---|---|---|---|---|---|---|
| Heute `/` | Willkommens-Schritte | Skeleton | ja | 30 Tage, Achsen begrenzt | je Karte einzeln, Rate-Limit, Anmeldung nötig | ja |
| Aktivitäten | ja, auch mit Filter | ja | Tabelle bzw. Liste | „Ältere laden“, Ende-Text | ja, auch beim Nachladen | ja |
| Detail `activities/detail?id=` | id fehlt, 404 | ja | ja | – | ja | ja |
| Ernährung + Suchfenster | kein Ziel, leerer Tag | ja | ja | viele Einträge | Open Food Facts nicht erreichbar oder Grenze erreicht, nichts gefunden, Barcode unbekannt, Menge ungültig | ja |
| Training | kein Plan, Plan ohne Einheiten | ja | 4 Status + „Zusätzlich“ | 52 Wochen, viele Einheiten, viele Pläne | ja | Tagesliste |
| Einstellungen | Demo | ja | verbunden | – | alle Verbindungsfehler, Anmeldesperre | ja |

**Pflichtfragen**
1. Eine Richtung mit Begründung aus Zielgruppe und Fachgebiet: ja (Abschnitt 2).
2. Jede Anforderung hat einen Ablauf (Abschnitt 7), jeder Bildschirm alle Zustände für Desktop und Handy (Abschnitt 6): ja.
3. Werte nur aus `tokens.json`: so vorgegeben, abgesichert durch die vorgeschlagenen Tests 1 und 2.
4. Kontrast nachgerechnet, nicht geschätzt (Python-Skript mit der WCAG-Formel ausgeführt): alle Textpaare mindestens 4,5:1, Grafik mindestens 3:1. Diagrammfarben 3 und 4 sind im hellen Modus nur für Grafik erlaubt. Tastatur, Fokus, Beschriftungen, mindestens 44 px Tippfläche und reduzierte Bewegung sind in Abschnitt 8 vorgegeben.
5. Echte Texte und Fehlermeldungen mit Ausweg: ja, kein Platzhaltertext.
6. Nur im Modus `treue` relevant, entfällt.

**Nicht geprüft:** ob die Schrift Geist gleich breite Ziffern (`tabular-nums`) wirklich unterstützt. Ich bin mir ziemlich sicher, habe es aber nicht nachgemessen. Prüfauftrag in P2, Ersatz ist Geist Mono für Zahlen.

**Übergabe an den Architekten** (Details in DESIGN.md Abschnitt 10)
- **P2:** Tailwind 4 und shadcn mit Tokens aus `tokens.json`, `next-themes` und `sonner` über die Abhängigkeits-Schranke, Geist über `next/font/local` samt Lizenzdatei. Eigene Bausteine: `AppShell` (Tab-Leiste, schmale Leiste, Seitenleiste), `DemoBanner`, `SyncStatus` (7 Fälle), `Gauge` (Messleiste), `MetricRow`, `StatusBadge`, `EmptyState`, `ErrorState`, `ChartCard` mit Umschalter auf Tabelle, `OffAttribution`. Dazu 18 shadcn-Bausteine.
- **P8, P10, P12:** Pflicht-Zustände je Bildschirm stehen in Tabelle 10.2.
- **Testvorschläge:**
  - Token-Treue zwischen `tokens.json` und `globals.css`, keine Hex-Farben in Komponenten
  - keine externe Schrift
  - Text je Zustand aus DESIGN.md
  - Status-Text bei Erledigt, Verpasst, Heute, Geplant
  - Bestätigungstext „ALLES LÖSCHEN“ mit Grenzfällen
  - Code-Schritt: Fokus auf dem Codefeld, Passwort danach nicht mehr vorhanden
  - Uhrzeit beim Rate-Limit mit Zeitzone und „morgen“
  - Open-Food-Facts-Hinweis sichtbar
  - Fokus in Dialogen
  - Screenshots 1440 und 390 px, hell und dunkel, mit Überlagerungen, ohne waagrechtes Scrollen

**Bitte an den Projektleiter:** M1 an den Architekten geben, bevor P5/P6 gebaut werden. M5 (nur Gramm) als Hinweis an Simon aufnehmen.
