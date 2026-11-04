# Design: Simfit

Geführt vom Agenten `designer`. Werte (Farben, Schrift, Abstände, Radien, Schatten, Bewegung) stehen **nur** in `design/tokens.json`; diese Datei beschreibt, wie sie eingesetzt werden. Grundlage: Oberflächen-Standard des Dev-Teams (`wissen/oberflaeche.md`).

**Stand:** 2026-11-04 · Modus `entwurf`, nachgezogen nach der Planprüfung (kein Standardziel, Bilanz nullable/„bisher“, Abruf höchstens 90 Tage, Menge 0,5–5.000 g, „Training heute“ nur heute, USDA-Quellenangabe, OFF-Suche nur auf Knopf/Enter, Merkposten M1–M6 entschieden) · gilt für P2 (Grundlage), P8 (Heute, Aktivitäten, Einstellungen), P10 (Ernährung), P12 (Training)

---

## 1. Kontext

Ein Freund von Simon bekommt die App geschenkt. Er hat kein Technikwissen, trägt eine Garmin-Uhr und nutzt Simfit im Alltag: morgens kurz am Handy („wie habe ich geschlafen, was steht heute an“), mittags und abends am Handy zum Eintragen von Mahlzeiten, gelegentlich am Rechner zum Planen der Trainingswoche und für Einstellungen. Die App läuft lokal, ein Nutzer, alles auf Deutsch.

Wichtigste Aufgabe je Bildschirm:

| Bildschirm | Wichtigste Aufgabe |
|---|---|
| Heute | In 5 Sekunden sehen, wie der Tag steht (Erholung, Bewegung, gegessen, Training heute) |
| Aktivitäten | Eine bestimmte Einheit wiederfinden |
| Aktivität (Detail) | Die Werte einer Einheit ablesen |
| Ernährung | Eine Mahlzeit in unter 20 Sekunden eintragen |
| Training | Sehen, was diese Woche geplant und was schon erledigt ist |
| Einstellungen | Garmin verbinden, Daten sichern oder löschen |

Zuordnung zu den Anforderungen: A1/A2 → Heute, Aktivitäten, Detail, Sync-Anzeige · A3 → Ernährung · A4 → Training · A6/A7 → Erster Start, Demo-Hinweis, Garmin verbinden · A9 → Rate-Limit- und Anmeldemeldungen · A10 → Export, Alles löschen, OFF-Hinweis.

---

## 2. Gestaltungsrichtung

**„Ruhiges Messinstrument“: sachlich wie eine gute Sportuhr. Warmes Grau, eine kräftige Limetten-Akzentfarbe, die Zahlen stehen im Mittelpunkt.**

Begründung:
- **Fachgebiet:** Trainingssteuerung lebt von Messwerten und deren Einordnung, nicht von Dekoration. Eine Oberfläche wie ein Instrument (klare Skalen, gleich breite Ziffern, feine Linien) passt zu Puls, HRV und Kalorien.
- **Zielgruppe:** Ein Laie braucht Ruhe und Eindeutigkeit statt einer Kachelwand mit fünf Diagrammfarben. Deshalb gibt es eine Akzentfarbe, wenige Schriftgrößen und Werte mit Einheit und Klartext.
- **Limette statt Blau oder Lila:** Limette steht für Sport („Signalfarbe auf der Laufbahn“), ist unverwechselbar und liegt weit genug weg von Erfolg-Grün (Türkisgrün), Warnung (Bernstein) und Fehler (Rot). Im hellen Modus ist Limette als Fläche zu blass (Kontrast 1,2:1 zum Hintergrund). Dort trägt deshalb ein dunkles Oliv (`primary` #4A6B00) die Knöpfe und Links, Limette erscheint nur als Markierung (`highlight`). Im Dunkelmodus ist Limette selbst die Akzentfarbe.
- **Keine Wertung:** Die App sagt nie „gut“ oder „schlecht“ (keine medizinischen Aussagen). Sie ordnet Werte nur gegenüber den **eigenen** letzten 30 Tagen ein.

Ausdrücklich abgelehnt: Inter mit Standard-Blau, lila-blaue Verläufe, eine Wand gleich großer Kacheln (wie im Prototyp), fünf Diagramme in fünf Farben untereinander, riesige Zahlen-Helden, Emojis, zentrierte Textblöcke, Kreisdiagramme für Makros.

### 2.1 Erkennungsmerkmal: die Messleiste

Jede Kennzahl auf „Heute“ hat unter dem Wert eine feine **Messleiste**: eine 4 px hohe Skala von deinem niedrigsten bis zu deinem höchsten Wert der letzten 30 Tage, ein kurzer Strich für deinen Durchschnitt und ein Punkt für heute.

```
Ruhepuls                               51 bpm
47 ├──────────●───┼──────────────────┤ 60      Ø 53
```

- Punkt: 8 px, Füllung `highlight`, 1 px Ring in `foreground` (damit er im hellen Modus sichtbar ist).
- Skala: Linie `border`, die Spanne Min–Max in `muted-foreground` mit 40 % Deckkraft. Der Durchschnitt ist ein 1 × 8 px Strich in `muted-foreground`.
- Zahlen an den Enden: `caption`, `muted-foreground`, tabular-nums.
- Ab 5 Tagen mit Werten sichtbar. Bei weniger Tagen steht dort der Text „Zu wenig Daten für einen Vergleich“ (`caption`).
- Text für Screenreader: „Heute 51 bpm. In deinen letzten 30 Tagen zwischen 47 und 60, Durchschnitt 53.“
- Keine Farbe für gut oder schlecht, keine Pfeile mit Wertung.

Die Messleiste kommt auch in der Wochenleiste im Training vor (geplant gegen absolviert) und in der Tagesübersicht der Ernährung (gegessen gegen Ziel – **nur, wenn ein Ziel gespeichert ist**; es gibt kein Standardziel). Sie ist das durchgehende Bildelement der App.

---

## 3. Gestaltungsplan (Werte in `design/tokens.json`)

### 3.1 Farben (Rollen)

| Rolle | Hell | Dunkel | Wofür |
|---|---|---|---|
| Hintergrund `background` | #F6F6F3 warmes Hellgrau | #0F1011 | Seitenfläche |
| Fläche `card` | #FFFFFF | #18191B | Karten, Seitenleiste, Tab-Leiste |
| Text `foreground` | #17181A | #ECECE8 | Text, Zahlen |
| Nebentext `muted-foreground` | #5A5D63 | #A3A6AC | Beschriftungen, Einheiten |
| **Akzent `primary`** | #4A6B00 Oliv | #C6F24E Limette | Hauptknopf, Links, aktiver Reiter, Fokusring |
| Markierung `highlight` | #C6F24E | #C6F24E | Messleisten-Punkt, Balken des aktiven Reiters |
| Erfolg `success` | #0B7A5C | #3FD3A0 | „Erledigt“, „Verbunden“ |
| Warnung `warning` | #9A5800 | #F2B54A | Rate-Limit, Demo-Hinweis, über dem Ziel |
| Fehler `destructive` | #C12E2E | #FF7A7A | Fehler, Löschen |

Signalfarben gibt es jeweils auch als `-soft`-Fläche für Hinweisbänder. Text darauf ist immer die volle Signalfarbe.

### 3.2 Kontrast (mit WCAG-Formel nachgerechnet, nicht geschätzt)

| Paar | Hell | Dunkel |
|---|---|---|
| Text auf Hintergrund / Karte / muted | 16,4 / 17,8 / 15,4 | 16,1 / 14,9 / 13,6 |
| Nebentext auf Hintergrund / Karte / muted | 6,1 / 6,6 / 5,7 | 7,8 / 7,2 / 6,6 |
| Akzent als Text auf Hintergrund / Karte | 5,7 / 6,2 | 14,7 / 13,6 |
| Knopftext auf Akzent | 6,2 (weiß auf Oliv) | 12,6 (dunkel auf Limette) |
| Erfolg / Warnung / Fehler auf Karte | 5,3 / 5,6 / 5,7 | 9,3 / 9,6 / 7,0 |
| Signalfarbe auf eigener -soft-Fläche | 4,7 / 5,0 / 4,9 | 8,4 / 8,7 / 6,7 |
| Rahmen Eingabefeld (`input`) auf Karte | 3,3 | 3,4 |
| Diagramm 1 / 2 / 3 / 4 auf Karte | 5,1 / 5,6 / 4,1 / 4,0 | 13,6 / 7,6 / 9,0 / 5,6 |

`chart-3` und `chart-4` sind im hellen Modus nur für Linien und Flächen erlaubt (≥ 3:1), nicht für Text. Eingabefelder liegen immer auf `card`, nicht auf `muted` (dort hätte der Rahmen nur 2,9:1).

### 3.3 Schrift

- **Eine Familie: Geist** (SIL OFL), selbst gehostet über `next/font/local`, keine externe Quelle. Gegenüber Inter wirkt sie technischer und ruhiger, und sie passt zum Instrument-Charakter.
- Rollen: Seitentitel 24 (Handy 22), Abschnitt 18, Text 16, Klein 14, Beschriftung 12, Kennzahl 28 (Handy 24). **Höchstens zwei Größen je Karte.**
- Alle Zahlen mit `tabular-nums`. Einheiten stehen direkt hinter dem Wert, in Größe `small` und `muted-foreground` („51 bpm“, „5 h 48 min“).
- Zahlenformate (deutsch): `13.076` · `5 h 48 min` (Schlaf und Dauer ab 1 h) · `42:10 min` (unter 1 h) · `5:12 /km` · `8,1 km` · `2.495 kcal` · `Mi, 4. Nov.` · `14:35 Uhr`. Fehlender Wert: `–` mit Screenreader-Text „keine Daten“.

### 3.4 Abstände, Form, Bewegung

- Raster 4 / 8 / 12 / 16 / 24 / 32 px. Kartenrand innen 16 (Handy) bzw. 24 (Desktop). Zwischen Karten 16 bzw. 24, zwischen Abschnitten 32.
- Radien: Bedienelemente 8, Karten und Dialoge 12, Plaketten rund.
- Karten haben **1 px Linie und keinen Schatten**. Schatten (`float`) gibt es nur für Dialog, Sheet, Dropdown und Toast.
- Bewegung 150 ms (Hover, Reiter) bzw. 200 ms (Dialog, Sheet), weich auslaufend. Bei „reduzierte Bewegung“ entfällt jede Bewegung, auch in den Diagrammen.

### 3.5 Symbole

Nur `lucide-react`, Strichstärke 1.75, Größe 16 (im Text), 20 (Seitenleiste), 24 (Tab-Leiste am Handy). Sportarten: Laufen `Footprints`, Radfahren `Bike`, Schwimmen `Waves`, Kraft `Dumbbell`, Gehen `PersonStanding`, Sonstiges `Activity`. Ein Symbol steht nie allein für eine Bedeutung, es gibt immer Text oder eine `aria-label` dazu.

### 3.6 Diagramme (Recharts, Farben nur über `var(--chart-n)`)

- **Ein Wert pro Diagramm**, Linie 2 px in `chart-1` mit Fläche darunter (12 % Deckkraft). Punkte gibt es nur am letzten Wert, dort mit Beschriftung.
- Durchschnitt als gestrichelte Linie in `chart-4`, beschriftet „Ø 53“.
- Achsen in `chart-axis`, Schrift `caption`, höchstens 4 Werte auf der Y-Achse. Raster nur waagrecht in `chart-grid`.
- Fehlende Tage sind **Lücken**, keine verbundenen Linien (`connectNulls=false`).
- Tooltip (Fläche `popover`, Schatten `float`): Datum „Mi, 4. Nov.“, Wert mit Einheit, tabular-nums.
- Body Battery: Spanne Tagestief bis Tageshoch als Band in `chart-2`.
- Barrierefrei: Jedes Diagramm hat eine Textzusammenfassung („Schritte, letzte 14 Tage: Durchschnitt 9.840, höchster Wert 14.210 am 28. Okt.“) und einen Schalter „Als Tabelle“.

---

## 4. Navigation – Vorschlag

**Handy (< 768 px): untere Tab-Leiste mit 5 Reitern. Desktop (≥ 1024 px): Seitenleiste links.** Dazwischen (768–1023 px) eine schmale Seitenleiste mit 72 px (Symbol über kurzer Beschriftung).

Begründung: Der Prototyp hat oben eine waagrechte Leiste. Bei 390 px rutscht dort „Training“ aus dem Bild (Screenshot des Prototyps, angesehen), und „Einstellungen“ fehlt ganz. Am Handy sind 5 Reiter unten mit dem Daumen erreichbar, und jeder Reiter ist 78 × 64 px groß. Fünf Bereiche passen genau hinein, ein „Mehr“-Menü ist nicht nötig. Am Desktop ist die Seitenleiste ruhiger und hat unten Platz für den Sync-Status und den Demo-Hinweis.

| Reiter | Symbol | Pfad |
|---|---|---|
| Heute | `LayoutDashboard` | `/` |
| Aktivitäten | `Activity` | `/activities` (Detail `/activities/detail?id=`) |
| Ernährung | `Utensils` | `/nutrition` |
| Training | `CalendarCheck` | `/training` |
| Einstellungen | `Settings` | `/settings` |

- Aktiver Reiter: Text und Symbol in `primary`, Schrift `semibold`, `aria-current="page"`. Am Handy liegt ein 3 px Balken in `highlight` über dem Symbol, am Desktop ein 3 px Balken links und die Fläche `primary-soft`.
- Tab-Leiste: Fläche `card`, Linie oben `border`, Höhe 64 px plus Abstand für den Home-Balken (`env(safe-area-inset-bottom)`). Der Seiteninhalt bekommt unten denselben Abstand, damit nichts verdeckt wird.
- Die Beschriftung ist immer sichtbar (12 px), nicht nur das Symbol.
- Seitenleiste (232 px, Fläche `card`, Linie rechts): oben Wortmarke „Simfit“ (18, semibold) und bei Demo-Betrieb daneben die Plakette „Demo“. Darunter die Reiter (Höhe 40, Abstand 4). Ganz unten der **Sync-Block**: „Aktualisiert 12:40 Uhr“ und der Knopf „Aktualisieren“.
- Am Handy sitzt der Sync-Knopf im Kopf von „Heute“ (Symbol `RefreshCw` mit Text, siehe 6.1).

---

## 5. Globale Bausteine und Meldungen

### 5.1 Demo-Hinweis (A7)
Solange keine Garmin-Verbindung besteht (`/health` → `source: "demo"`), steht oben in jeder Seite ein Band (Fläche `warning-soft`, Text `warning`, Symbol `FlaskConical`, Radius 8):

> **Beispieldaten.** Du siehst erfundene Werte, damit du Simfit ausprobieren kannst. **Mit Garmin verbinden →**

- Der Link führt zu `/settings#garmin`. Mit „Ausblenden“ (Symbolknopf `X`, 44 px) verschwindet das Band für diese Sitzung. Die Plakette „Demo“ in Seitenleiste bzw. Kopf bleibt.
- Am Handy bricht der Text auf zwei Zeilen um, der Link steht in der zweiten Zeile.

### 5.2 Sync-Status (A1, A9) – Texte je Status von `SyncRun`

| Status | Anzeige (Plakette + Text) | Knopf |
|---|---|---|
| keiner | „Noch keine Daten geholt“ | „Daten holen“ |
| `running` | Plakette „Läuft“ mit Ladebalken; „Daten werden geholt …“ | gesperrt, „Wird aktualisiert …“ |
| `ok` | „Aktualisiert heute, 12:40 Uhr“ | „Aktualisieren“ |
| `error` | Plakette „Fehler“ (`destructive`): „Letzte Aktualisierung fehlgeschlagen: {message}. Deine bisherigen Daten sind unverändert.“ | „Erneut versuchen“ |
| `rate_limited` | Plakette „Pause“ (`warning`): „Garmin hat zu viele Anfragen gemeldet. Simfit wartet und versucht es ab **14:35 Uhr** wieder. Deine Daten bleiben erhalten.“ | gesperrt, „Wieder möglich ab 14:35 Uhr“ |
| `auth_required` | Plakette „Anmeldung nötig“ (`warning`): „Garmin hat die Anmeldung beendet. Bitte verbinde dein Konto neu.“ | „Neu verbinden“ → `/settings#garmin` |
| `aborted` | „Letzte Aktualisierung wurde unterbrochen (z. B. weil Simfit beendet wurde).“ | „Erneut versuchen“ |

- Uhrzeit aus `next_attempt_after` in Ortszeit. Liegt sie nicht am selben Tag, steht dort „morgen, 08:10 Uhr“ bzw. „am Do, 6. Nov., 08:10 Uhr“.
- Antwortet `POST /sync` (oder `POST /garmin/connection`) mit 429, erscheint derselbe Text wie bei `rate_limited` mit der Uhrzeit aus `retry_after` der Fehlerantwort (M3). Fehlt die Uhrzeit, steht dort „Bitte später erneut versuchen.“
- `rate_limited` und `auth_required` erscheinen zusätzlich als Band oben auf „Heute“ (wie 5.1, aber `warning`). So sieht der Nutzer den Grund, ohne den Sync-Block zu suchen.
- Ist der Lauf fertig, erscheint ein Toast „Daten aktualisiert“ und die Ansichten laden neu.

### 5.3 Bausteine (shadcn/ui, Varianten und Zustände)

| Baustein | shadcn | Varianten | Zustände |
|---|---|---|---|
| Knopf | `Button` | `default` (Akzent, höchstens **einer** je Bereich), `secondary` (Fläche muted), `outline`, `ghost` (Symbolknöpfe), `destructive` | normal, Hover, Fokus (Ring 2 px `ring`, Abstand 2), gedrückt, gesperrt (50 % Deckkraft und Grund daneben als Text), lädt (Symbol `Loader2` + Text „… wird gespeichert“ usw., Breite bleibt gleich). Höhe 44 (Handy) bzw. 36/44 (Desktop) |
| Eingabefeld | `Input`, `Label` | Text, Zahl (`inputMode="decimal"`, Komma erlaubt), Passwort mit „Anzeigen“-Knopf, Code (`inputMode="numeric"`, `autoComplete="one-time-code"`) | normal, Fokus, Fehler (Rahmen und Text `destructive`, Meldung unter dem Feld, `aria-invalid`, `aria-describedby`), gesperrt. Beschriftung **immer sichtbar über dem Feld**, nie nur Platzhalter |
| Auswahl | `Select`, `ToggleGroup` | Zeitraum 14/30 Tage, Sportart, Mahlzeit | Fokus, Tastatur (Pfeiltasten) |
| Karte | `Card` | Standard (Linie, kein Schatten) | – |
| Kennzahl-Zeile | eigen (`components/dashboard/MetricRow`) | mit oder ohne Messleiste, mit Mini-Verlauf | gefüllt, ohne Wert („–“ und „Heute noch kein Wert“), lädt (Skeleton), zu wenig Vergleich |
| Messleiste | eigen (`components/common/Gauge`) | Kennzahl (Min–Ø–Heute), Ziel (gegessen/Ziel; nur mit gespeichertem Ziel), Woche (absolviert/geplant) | normal, über dem Ziel (Spanne läuft über die Zielmarke hinaus, Text „120 kcal über Ziel“ in `warning`), zu wenig Daten |
| Status-Plakette | `Badge` | Erledigt (`success`, `CheckCircle2`), Verpasst (`destructive`, `XCircle`), Heute (`primary`, `CircleDot`), Geplant (neutral, `Circle`), Zusätzlich (neutral, `Plus`) | **immer Symbol + Text**, nie nur Farbe |
| Hinweisband | `Alert` | info (neutral), warning, destructive, success | mit Aktion (Link/Knopf), schließbar oder fest |
| Dialog | `Dialog`, `AlertDialog` | Formular, Bestätigung, Gefahr | Fokus fängt im Dialog, `Esc` schließt (außer während des Speicherns), Fokus kehrt zum Auslöser zurück |
| Sheet | `Sheet` (Desktop rechts 480 px) / `Drawer` (Handy unten, volle Höhe minus 32 px) | Lebensmittel hinzufügen | wie Dialog |
| Toast | `Sonner` | erfolgreich, Fehler, mit „Rückgängig“ | 5 s sichtbar, mit Fokus/Hover pausiert, `aria-live="polite"`. Am Handy **über** der Tab-Leiste |
| Liste | eigen auf `Card` | Aktivitäten, Mahlzeit-Einträge | Zeile ≥ 48 px, ganze Zeile anklickbar (ein Link pro Zeile) |
| Tabelle | `Table` | Aktivitäten (Desktop) | Zahlen rechtsbündig, tabular-nums, Kopf fest beim Scrollen |
| Skeleton | `Skeleton` | Zeile, Karte, Diagramm | in der Form des späteren Inhalts, bei reduzierter Bewegung ohne Pulsieren |
| Leerzustand | eigen (`components/common/EmptyState`) | – | linksbündig: Symbol 24, Titel (section), ein Satz, **eine** Aktion. Nicht zentriert |
| Fehlerzustand | eigen (`components/common/ErrorState`) | Laden fehlgeschlagen, nicht gefunden | Titel, Meldung des Servers (`detail`), Ausweg („Erneut versuchen“ und/oder Link) |
| Diagramm | shadcn `Chart` (Recharts) | Linie+Fläche, Band, Balken (Woche) | lädt (Skeleton), zu wenig Daten (< 2 Punkte: Text statt Diagramm), Lücken |
| OFF-Hinweis | eigen (`components/nutrition/OffAttribution`) | unter OFF-Suchergebnissen (nur wenn welche angezeigt werden), Fußzeile der Ernährung | fest, nicht schließbar (siehe 6.4) |
| Quellen-Fußzeile | eigen (`components/nutrition/SourceFooter`) | Ernährung, Seitenende | OFF-Hinweis mit Links **und** „Basis-Lebensmittel: USDA FoodData Central (gemeinfrei, CC0)“ als Text **ohne Link** |

### 5.4 Allgemeine Fehlertexte

| Lage | Text |
|---|---|
| Server nicht erreichbar | „Simfit antwortet gerade nicht. Läuft das Programm noch? Starte es mit ‚Simfit starten‘ neu und versuche es dann erneut.“ + „Erneut versuchen“ |
| 500 „Interner Fehler“ | „Da ist etwas schiefgelaufen. Deine Daten sind nicht verloren. Versuche es erneut, sonst starte Simfit neu.“ |
| Fachfehler (`detail`) | Meldung des Servers wörtlich (sie ist deutsch und ohne Interna, AE-13) + passender Ausweg |
| Speichern fehlgeschlagen | Formular bleibt offen und alle Eingaben bleiben stehen; Meldung über dem Speichern-Knopf |

---

## 6. Bildschirme

Skizzen: Desktop 1440 px (Seitenleiste 232 + Inhalt max. 1120), Handy 390 px. `[ ]` = Knopf, `( )` = Feld, `▮▯` = Messleiste/Balken.

### 6.1 Heute (`/`) – A2

**Rangfolge:** 1. Hinweise (Demo, Rate-Limit), 2. Kopf mit Datum und Sync, 3. Kennzahlen mit Messleiste, 4. Ernährung heute und Training heute (Brücke zu den anderen Bereichen), 5. Verlauf (ein großes Diagramm mit Umschalter), 6. letzte Aktivitäten.

Die Kennzahlen stehen als **Zeilen in einer Karte** (Instrumententafel), nicht als sechs gleiche Kacheln. Pro Zeile: Bezeichnung, Wert groß, Messleiste, Mini-Verlauf 14 Tage (Desktop).

Desktop 1440:
```
┌────────────┬──────────────────────────────────────────────────────────────────────────┐
│ Simfit Demo│ ⚑ Beispieldaten. Du siehst erfundene Werte …  Mit Garmin verbinden →   [x]│
│            │                                                                          │
│▌Heute      │ Heute                                                                    │
│ Aktivitäten│ Mittwoch, 4. November                                                    │
│ Ernährung  │                                                                          │
│ Training   │ ┌─ Erholung & Bewegung ─────────────────────┐ ┌─ Ernährung heute ──────┐ │
│ Einstellung│ │ Schlaf        5 h 48 min  ├──●──┼────┤  ~~~│ │ 1.420 von 2.200 kcal   │ │
│            │ │ Body Battery  6 – 79      ├────┼──●─┤  ~~~│ │ ▮▮▮▮▮▮▮▮▯▯▯▯           │ │
│            │ │ Ruhepuls      51 bpm      ├──●─┼────┤  ~~~│ │ Verbrauch bisher 2.495 │ │
│            │ │ HRV           69 ms       ├────┼─●──┤  ~~~│ │ [Mahlzeit eintragen]   │ │
│            │ │ Stress        22          ├─●──┼────┤  ~~~│ ├─ Training heute ───────┤ │
│            │ │ Schritte      13.076      ├────┼───●┤  ~~~│ │ [Fuß] Locker. Dauerlauf│ │
│            │ │ Spanne = deine letzten 30 Tage            │ │ 45 min · ○ Geplant     │ │
│            │ └───────────────────────────────────────────┘ │ Zum Trainingsplan →    │ │
│            │                                               └────────────────────────┘ │
│            │ ┌─ Verlauf ─────────────────────────────────────────────────────────────┐│
│ ────────── │ │ (Schlaf)(Body Battery)(Ruhepuls)(HRV)(Stress)(Schritte) [14T|30T][Tab.]││
│ Aktualisiert│ │  ╭╮    ╭─╮        ╭╮          (ein Diagramm, Höhe 280)              ││
│ 12:40 Uhr  │ │ ─╯╰────╯ ╰── Ø 53 ╯╰───                                             ││
│[Aktualisier]│ └───────────────────────────────────────────────────────────────────────┘│
│            │ ┌─ Letzte Aktivitäten ─────────────────────────────── Alle anzeigen → ─┐│
│            │ │ Dumbbell Krafttraining      Mi, 4. Nov., 08:00     43:48 min  381 kcal││
│            │ │ Footprints Lauf             So, 26. Okt., 13:00  4,9 km 14:42 min     ││
│            │ └───────────────────────────────────────────────────────────────────────┘│
└────────────┴──────────────────────────────────────────────────────────────────────────┘
```
(`[Fuß]` usw. stehen in den Skizzen für die Lucide-Symbole aus 3.5. Der Zeitraum 14/30 Tage gilt für den Verlauf; die Messleisten nutzen immer 30 Tage.)

Raster Desktop: Erholung 2/3 und rechte Spalte 1/3 (12er-Raster 8/4), Abstand 24. Verlauf und Aktivitäten volle Breite.

Handy 390:
```
┌──────────────────────────────┐
│ ⚑ Beispieldaten. Du siehst   │
│ erfundene Werte.             │
│ Mit Garmin verbinden →    [x]│
│ Heute           [Aktualisier.]│
│ Mi, 4. Nov. · 12:40 Uhr      │
│ ┌──────────────────────────┐ │
│ │ Schlaf       5 h 48 min  │ │
│ │ 4h50├──●──┼────┤7h40     │ │
│ │──────────────────────────│ │
│ │ Body Battery     6 – 79  │ │
│ │ …  (6 Zeilen à 64 px)    │ │
│ └──────────────────────────┘ │
│ ┌ Ernährung heute ─────────┐ │
│ │ 1.420 von 2.200 kcal     │ │
│ │ ▮▮▮▮▮▮▮▯▯▯  [+ Eintragen]│ │
│ └──────────────────────────┘ │
│ ┌ Training heute ──────────┐ │
│ │ Lockerer Dauerlauf 45 min│ │
│ │ ○ Geplant                │ │
│ └──────────────────────────┘ │
│ Verlauf          [14T|30T]   │
│ (Schlaf)(Body B.)(Ruhepuls)  │
│ (HRV)(Stress)(Schritte)      │
│ [Diagramm Höhe 200]          │
│ Letzte Aktivitäten           │
│ …3 Zeilen · Alle anzeigen →  │
├──────────────────────────────┤
│ Heute Aktiv. Ernähr. Train. ⚙│
└──────────────────────────────┘
```
Am Handy entfällt der Mini-Verlauf (Messleiste reicht), die Werte an den Enden der Messleiste bleiben. Die Umschalter des Verlaufs brechen auf zwei Zeilen um (Chips 36 px hoch, mit Abstand zur Tippfläche ≥ 44 px), es gibt kein waagrechtes Scrollen. Die Aktivitäten-Liste zeigt 3 statt 5 Einträge.

**Zustände**

| Zustand | Desktop | Handy |
|---|---|---|
| Erster Start (keine Daten, nie synchronisiert) | Statt Kennzahlen eine Karte **„Willkommen bei Simfit“**, linksbündig als Schrittliste: ① „Mit Garmin verbinden“ [Verbinden] · ② „Oder erst mit Beispieldaten ausprobieren“ [Beispieldaten laden] (startet Sync mit Demo-Quelle) · ③ „Kalorienziel festlegen“ → Ernährung · ④ „Trainingsplan anlegen“ → Training. Erledigte Schritte bekommen `CheckCircle2` und „erledigt“. Schritt ③ gilt als erledigt, sobald ein Ziel gespeichert ist (`goal !== null`); es gibt **kein Standardziel**. Schritt ② entfällt, wenn früher schon mit Garmin verbunden war (Demo wird dann nie geladen, M1). | gleich, eine Spalte |
| Lädt | Skeleton: 6 Zeilen in der Kennzahlkarte, Kartenrahmen rechts, Diagrammfläche. Der Kopf mit Datum ist sofort da. | gleich |
| Gefüllt | wie Skizze | wie Skizze |
| Heute noch kein Wert (Uhr noch nicht synchronisiert) | Zeile zeigt „–“ und klein „Heute noch kein Wert · gestern 5 h 12 min“. Die Messleiste zeigt dann keinen Punkt. | gleich |
| Teilweise Daten (z. B. kein HRV-Gerät) | Kennzahl ohne einen einzigen Wert in 30 Tagen wird **ausgeblendet** (nicht als leere Zeile gezeigt); Hinweis unter der Karte: „HRV liefert deine Uhr nicht.“ | gleich |
| Viele Daten | 30 Tage im Verlauf, Achse zeigt höchstens 5 Datumswerte | höchstens 4 Datumswerte |
| Sync läuft | Plakette „Läuft“ im Sync-Block, Knopf gesperrt; Werte bleiben sichtbar (kein Skeleton) | Knopf im Kopf zeigt `Loader2` + „Wird aktualisiert …“ |
| Rate-Limit / Anmeldung nötig | Band oben (5.2) | gleich, Text bricht um |
| Fehler beim Laden | Je Karte eigener Fehlerzustand: Bricht nur der Verlauf, bleiben die Kennzahlen stehen. Text 5.4 + „Erneut versuchen“. | gleich |
| Kein Trainingsplan | Karte „Training heute“: „Kein Plan angelegt.“ + Link „Plan anlegen“ | gleich |
| Heute nichts geplant | „Heute ist nichts geplant.“ (Karte zeigt **nur den heutigen Tag**, keine Zeile „Als Nächstes …“; Quelle `GET /training/today`, M6) | gleich |
| Training heute gefüllt | je Einheit Sportart-Symbol, Titel, Dauer, Status-Plakette (meist „Heute“, nach Abhaken „Erledigt“) + „Zum Trainingsplan →“ | gleich |
| Kein Ernährungsziel (`goal === null`) | Zeile „1.420 kcal gegessen“ **ohne** Messleiste „Ziel“ und ohne „von … kcal“; darunter Link „Ziel festlegen“ (→ `/nutrition`) | gleich |
| Nichts gegessen | „Noch nichts eingetragen.“ + [Mahlzeit eintragen]; mit Ziel bleibt die Messleiste bei 0 | gleich |
| Verbrauch laufender Tag (`burned_partial`) | „Verbrauch bisher 2.495 kcal“ (Wert wächst bis Tagesende) | gleich |
| Kein Garmin-Verbrauch (`burned_kcal === null`) | „Kein Verbrauch von Garmin“, keine Bilanz | gleich |

### 6.2 Aktivitäten (`/activities`) – A2

**Rangfolge:** Filter → Liste nach Wochen gruppiert → „Ältere laden“.

Desktop 1440 (Tabelle):
```
Aktivitäten                                    (Alle Sportarten ▾)
Diese Woche · 3 Einheiten · 2 h 41 min
┌────────────┬───────────────────────────┬─────────┬────────┬─────────┬───────┬────────┐
│ Datum      │ Aktivität                 │   Dauer │ Distanz│    Pace │ Ø Puls│    kcal│
├────────────┼───────────────────────────┼─────────┼────────┼─────────┼───────┼────────┤
│ Mi 4. Nov. │ Dumbbell Krafttraining    │ 43:48 m │      – │       – │   112 │     381│
│ Mo 2. Nov. │ Footprints Abendlauf      │ 52:10 m │ 10,2 km│ 5:07/km │   148 │     702│
└────────────┴───────────────────────────┴─────────┴────────┴─────────┴───────┴────────┘
Letzte Woche · KW 44 · 26. Okt. – 1. Nov.
…
                          [Ältere Aktivitäten laden]
```
Die ganze Zeile ist ein Link zu `/activities/detail?id=…`, Hover-Fläche `accent`. Zahlen rechtsbündig.

Handy 390 (Liste):
```
Aktivitäten        (Sportart ▾)
DIESE WOCHE · 2 h 41 min
┌──────────────────────────────┐
│ [Hantel] Krafttraining     › │
│ Mi, 4. Nov., 08:00           │
│ 43:48 min · 381 kcal         │
├──────────────────────────────┤
│ [Fuß] Abendlauf            › │
│ Mo, 2. Nov., 18:30           │
│ 10,2 km · 52:10 min · 5:07/km│
└──────────────────────────────┘
```

| Zustand | Inhalt |
|---|---|
| Leer (nie synchronisiert) | EmptyState `Activity`: „Noch keine Aktivitäten. Sobald deine Uhr Einheiten an Garmin übertragen hat, holt Simfit sie hierher.“ [Daten holen] |
| Leer mit Filter | „Keine Radfahrten in diesem Zeitraum.“ [Filter zurücksetzen] |
| Lädt | 6 Skeleton-Zeilen |
| Gefüllt | wie Skizze |
| Viele Daten | erst 50 Einträge, dann [Ältere Aktivitäten laden] (nächste 50 über `to` = ältestes Datum − 1). Wochenköpfe bleiben beim Scrollen kleben (sticky). Ende: „Das waren alle Aktivitäten.“ |
| Langer Name | einzeilig mit Auslassung „…“, voller Name als `title` und in der Detailseite |
| Fehler | ErrorState 5.4 + „Erneut versuchen“; bereits geladene Seiten bleiben stehen, wenn nur „Ältere laden“ scheitert |

### 6.3 Aktivität – Detail (`/activities/detail?id=`) – A2

**Rangfolge:** Zurück → Titel mit Sportart und Zeit → Kennwerte → (zurückgestellt: Karte, Pulszonen – **keine** Platzhalterflächen dafür zeigen).

```
Desktop                                         Handy
← Aktivitäten                                   ← Aktivitäten
[Fuß] Abendlauf                                 [Fuß] Abendlauf
Laufen · Montag, 2. November, 18:30 Uhr         Laufen · Mo, 2. Nov., 18:30
┌──────────────────────────────────────────┐   ┌────────────────────────┐
│ Dauer        Distanz      Ø Pace         │   │ Dauer       Distanz    │
│ 52:10 min    10,2 km      5:07 /km       │   │ 52:10 min   10,2 km    │
│──────────────────────────────────────────│   │ Ø Pace      Höhenmeter │
│ Ø Puls       Max. Puls    Höhenmeter     │   │ 5:07 /km    86 m       │
│ 148 bpm      171 bpm      86 m           │   │ Ø Puls      Max. Puls  │
│──────────────────────────────────────────│   │ 148 bpm     171 bpm    │
│ Energie 702 kcal                         │   │ Energie     702 kcal   │
└──────────────────────────────────────────┘   └────────────────────────┘
Quelle: Garmin Connect                          Quelle: Garmin Connect
```
Desktop 3 Spalten, Handy 2 Spalten. Werte ohne Inhalt (z. B. Distanz bei Kraft) werden **weggelassen**, nicht als „–“ gezeigt. Die Quelle steht als `caption` darunter („Beispieldaten“ bei Demo).

| Zustand | Inhalt |
|---|---|
| Lädt | Skeleton Titel + 6 Wertfelder |
| Gefüllt | wie Skizze |
| `id` fehlt oder ist keine Zahl | ErrorState „Keine Aktivität ausgewählt.“ [Zu den Aktivitäten] |
| 404 | ErrorState „Diese Aktivität gibt es nicht (mehr). Vielleicht wurden die Daten gelöscht.“ [Zu den Aktivitäten] |
| Fehler | 5.4 + „Erneut versuchen“ |
| Langer Name | bricht um (bis 3 Zeilen), kein Abschneiden |

### 6.4 Ernährung (`/nutrition`) – A3

**Rangfolge:** Tag wählen → Tagesübersicht (gegessen gegen Ziel, Makros, Bilanz) → Mahlzeiten mit Einträgen → Quellenhinweis.

Desktop 1440:
```
Ernährung                                   [‹]  Mittwoch, 4. November  [›]  [Heute]
┌─ Tagesübersicht ──────────────────────────────────────────────┐ ┌─ Bilanz ─────────────┐
│ 1.420 von 2.200 kcal                     noch 780 kcal         │ │ Gegessen   1.420 kcal│
│ ▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▮▯▯▯▯▯▯▯▯▯▯ │ Ziel                           │ │ Verbrauch bisher     │
│ Eiweiß   82 / 130 g   ▮▮▮▮▮▮▯▯▯                               │ │ (laut Garmin) 2.495  │
│ Kohlenh. 160 / 250 g  ▮▮▮▮▮▮▯▯▯                               │ │ Bilanz bisher −1.075 │
│ Fett     48 / 70 g    ▮▮▮▮▮▮▮▯▯              [Ziel ändern]    │ │ unter dem Verbrauch  │
└───────────────────────────────────────────────────────────────┘ └──────────────────────┘
┌─ Frühstück · 520 kcal ──────────────────────────────── [+ Hinzufügen] ┐
│ Haferflocken, kernig        80 g   E 11 · KH 47 · F 5     297 kcal [Mül]│
│ Milch 1,5 %                200 g   E 7 · KH 10 · F 3       94 kcal [Mül]│
│ Skyr Natur  [Open Food Facts] 150 g  E 17 · KH 6 · F 0     93 kcal [Mül]│
└───────────────────────────────────────────────────────────────────────┘
┌─ Mittagessen · 0 kcal ─────────────────────────────── [+ Hinzufügen] ┐
│ Noch nichts eingetragen.                                             │
└──────────────────────────────────────────────────────────────────────┘
… Abendessen, Snacks
Lebensmitteldaten teilweise von Open Food Facts, Lizenz ODbL.  openfoodfacts.org · Lizenz
Basis-Lebensmittel: USDA FoodData Central (gemeinfrei, CC0)
```
(`[Mül]` steht in der Skizze für das Lucide-Symbol `Trash2`.) Die Skizze zeigt den laufenden Tag, deshalb „bisher“. Mengen gibt es nur in **g** (API `amount_g`, 0,5–5.000 g), auch bei Getränken – entschieden, M5 in Abschnitt 9.

Handy 390:
```
Ernährung
[‹]  Mi, 4. Nov.  [›]  [Heute]
┌──────────────────────────────┐
│ 1.420 von 2.200 kcal         │
│ ▮▮▮▮▮▮▮▮▯▯▯▯  noch 780 kcal  │
│ Eiweiß    82/130 g ▮▮▮▮▯▯    │
│ Kohlenh. 160/250 g ▮▮▮▮▯▯    │
│ Fett      48/70 g  ▮▮▮▮▮▯    │
│ Verbrauch bisher   2.495 kcal│
│ Bilanz bisher −1.075 [Ziel ä.]│
└──────────────────────────────┘
┌ Frühstück · 520 kcal  [+ ]──┐
│ Haferflocken, kernig 297 kcal│
│ 80 g · E 11 · KH 47 · F5 [Mül]│
└──────────────────────────────┘
…
Daten teilw. von Open Food Facts (ODbL)
Basis: USDA FoodData Central (CC0)
├──── Tab-Leiste ──────────────┤
```
Am Handy rutscht die Bilanz in die Tagesübersicht. „+ Hinzufügen“ ist ein Knopf 44 × 44 mit Symbol `Plus` und `aria-label="Zu Frühstück hinzufügen"`.

**Bilanz ohne Wertung:** Die Bilanz bekommt **keine** grüne oder rote Farbe, weil sie je nach Ziel (abnehmen, halten, zunehmen) anders zu lesen ist. Darunter steht nur Text: „unter dem Verbrauch“ bzw. „über dem Verbrauch“.

**Bilanz nur mit Garmin-Verbrauch:** Liegt für den Tag kein Verbrauch von Garmin vor (`burned_kcal` und `balance_kcal` sind `null`), zeigt die Bilanz-Karte „–“ und den Satz „Für diesen Tag liegt kein Verbrauch von Garmin vor.“ Das Ziel wird **nie** als Ersatz für den Verbrauch gerechnet. Am laufenden Tag (`burned_partial`) heißt es „Verbrauch bisher (laut Garmin)“ und „Bilanz bisher“, weil der Wert bis zum Abend wächst. An abgeschlossenen Tagen: „Verbrauch (laut Garmin)“ und „Bilanz“. Über dem Kalorienziel: Die Messleiste läuft über die Zielmarke hinaus, der Text „120 kcal über Ziel“ steht in `warning`.

**Ablauf „Lebensmittel hinzufügen“** (Desktop Sheet rechts, Handy Drawer von unten):
```
┌ Zu Frühstück hinzufügen                      [x] ┐
│ ([Lupe] Lebensmittel oder Barcode suchen  )       │
│ Barcode eintippen geht auch                       │
│ DEINE LEBENSMITTEL                                │
│  Haferflocken, kernig       370 kcal/100 g  USDA  │
│  Skyr Natur · Arla          63 kcal/100 g  OFF    │
│ [Auch bei Open Food Facts suchen]  (oder Enter)   │
│        ↓ erst nach Klick bzw. Enter               │
│ OPEN FOOD FACTS                                   │
│  Haferdrink Barista · Oatly 59 kcal/100 g         │
│  …                                                │
│  Daten von Open Food Facts, Lizenz ODbL ↗         │
│ ───────────────────────────────────────────────── │
│ Nicht dabei? [Eigenes Lebensmittel anlegen]       │
└───────────────────────────────────────────────────┘
        ↓ Auswahl
┌ ← Haferflocken, kernig                       [x] ┐
│ Menge                                             │
│ Menge (g)                                         │
│ (  80  ) g    [50 g][100 g][150 g][200 g]         │
│ 297 kcal · Eiweiß 11 g · KH 47 g · Fett 5 g       │
│ Mahlzeit (Frühstück ▾)                            │
│                         [Zu Frühstück hinzufügen] │
└───────────────────────────────────────────────────┘
```
- Das Suchfeld bekommt beim Öffnen den Fokus. **Nur die eigene Suche** (Daten bleiben im Gerät) startet 300 ms nach der letzten Eingabe ab 2 Zeichen.
- **Open Food Facts nur auf ausdrückliche Aktion:** Knopf [Auch bei Open Food Facts suchen] (`outline`, unter den eigenen Treffern, voll breit am Handy) oder `Enter` im Suchfeld. **Nie** bei einer Tipppause – der Suchbegriff geht erst auf Wunsch an einen fremden Dienst. Danach lädt die Gruppe „Open Food Facts“ mit eigenem Skeleton (3 Zeilen), der Knopf ist währenddessen gesperrt und zeigt `Loader2` + „Suche bei Open Food Facts …“. Tippt man weiter, wird die laufende Online-Suche abgebrochen und die OFF-Gruppe verschwindet, bis erneut Knopf/Enter kommt.
- Unter dem Knopf klein (`caption`): „Dein Suchbegriff wird dafür an Open Food Facts geschickt.“
- Reine Ziffern mit 8–14 Stellen gelten als Barcode: **kein** Suchlauf beim Tippen, Hinweis unter dem Feld „Barcode erkannt – mit Enter suchen“; erst `Enter` bzw. der Knopf (dann beschriftet [Barcode suchen]) ruft `/foods/barcode/{code}` auf. Hinweis im leeren Feld: „Barcode eintippen geht auch“.
- Eigene Treffer tragen ihre Herkunft als kleine Textmarke rechts: „USDA“ (Basis-Lebensmittel), „OFF“ (importiert), nichts bei eigenen.
- Ein OFF-Treffer wird beim Auswählen importiert (`POST /foods/import`); währenddessen zeigt die Zeile `Loader2`.
- **OFF-Hinweis (AE-10) nur dort, wo OFF-Daten erscheinen:** Unter der Gruppe „Open Food Facts“ (also sobald OFF-Treffer oder ein Barcode-Treffer von OFF angezeigt werden) steht der Text „Daten von Open Food Facts, Lizenz ODbL“ mit zwei Links (openfoodfacts.org, opendatacommons.org/licenses/odbl). Ohne OFF-Treffer kein Hinweis im Sheet. Einträge im Tagebuch mit `food_origin = off` tragen die Plakette „Open Food Facts“. Die Fußzeile der Ernährungsseite zeigt den OFF-Hinweis immer (das Tagebuch kann jederzeit OFF-Einträge enthalten). **Keine Produktbilder** (AE-12).
- **USDA-Quellenangabe:** Basis-Lebensmittel stammen aus USDA FoodData Central (gemeinfrei, CC0). Angabe als **reiner Text ohne Link** in der Fußzeile: „Basis-Lebensmittel: USDA FoodData Central (gemeinfrei, CC0)“ und als Textmarke „USDA“ an den Treffern. Fremde Links gibt es nur zu `openfoodfacts.org` und `opendatacommons.org`.
- Rückmeldung: Nach dem Hinzufügen schließt das Sheet, Toast „Haferflocken zu Frühstück hinzugefügt“, die Zeile erscheint in der Mahlzeit und ist für 1 s mit `primary-soft` hinterlegt (bei reduzierter Bewegung ohne Übergang).
- Löschen eines Eintrags: Symbolknopf `Trash2` (44 px, `aria-label="Haferflocken löschen"`). Die Zeile verschwindet sofort, Toast „Haferflocken entfernt“ mit [Rückgängig] (legt den Eintrag neu an). Hat der Eintrag kein Lebensmittel mehr (`food_id` leer), gibt es kein Rückgängig: Vorher fragt ein AlertDialog „Eintrag löschen?“.

| Zustand | Inhalt |
|---|---|
| Kein Ziel (`goal === null`, auch nach „Alles löschen“; es gibt kein Standardziel) | Band `info`: „Lege ein Tagesziel fest, dann siehst du, wie viel noch fehlt.“ [Ziel festlegen] (öffnet den Ziel-Dialog, Felder leer); Übersicht zeigt nur „1.420 kcal gegessen“ und die Makros in Gramm, **ohne** Messleiste „Ziel“, ohne „noch … kcal“ und ohne Makro-Ziele. Knopf „Ziel ändern“ heißt hier „Ziel festlegen“ |
| Leerer Tag | mit Ziel: „0 von 2.200 kcal“; ohne Ziel: „0 kcal gegessen“; jede Mahlzeit „Noch nichts eingetragen.“ |
| Lädt | Skeleton Übersicht + 4 Mahlzeitkarten mit Kopf |
| Gefüllt | wie Skizze |
| Viele Einträge (> 8 je Mahlzeit) | alle anzeigen, Kopf der Mahlzeit mit Summe bleibt oben; kein Paging nötig (ein Tag) |
| Kein Garmin-Verbrauch (`burned_kcal`/`balance_kcal` `null`) | Bilanz „–“ und Text „Für diesen Tag liegt kein Verbrauch von Garmin vor.“ (auch an künftigen Tagen und im Demo ohne Verbrauch) |
| Laufender Tag (`burned_partial`) | „Verbrauch bisher (laut Garmin)“, „Bilanz bisher“ |
| Zukünftiger Tag | erlaubt (Planen), Kopf zeigt Plakette „Zukunft“ |
| Suche: weniger als 2 Zeichen | „Mindestens 2 Zeichen eingeben.“ |
| Suche: nur eigene Treffer (OFF noch nicht gefragt) | eigene Treffer + Knopf [Auch bei Open Food Facts suchen]; kein OFF-Hinweis |
| Suche: OFF lädt | 3 Skeleton-Zeilen unter „Open Food Facts“, Knopf gesperrt „Suche bei Open Food Facts …“ |
| Barcode getippt | „Barcode erkannt – mit Enter suchen“, kein automatischer Aufruf |
| Suche: nichts gefunden | lokal ohne Treffer: „Nichts in deinen Lebensmitteln für ‚Haferdrinkk‘.“ + [Auch bei Open Food Facts suchen]; nach der OFF-Suche ohne Treffer: „Nichts gefunden für ‚Haferdrinkk‘. Prüfe die Schreibweise oder lege es selbst an.“ [Eigenes Lebensmittel anlegen] (Name vorbelegt) |
| Suche: OFF nicht erreichbar (`online_error`) | lokale Treffer bleiben; unter „Open Food Facts“: Band `warning`: „Open Food Facts ist gerade nicht erreichbar. Deine eigenen Lebensmittel findest du trotzdem.“ [Erneut suchen] |
| Suche: OFF-Grenze erreicht | Meldung des Servers, z. B. „Zu viele Suchen in kurzer Zeit. Bitte eine Minute warten.“ |
| Barcode unbekannt | „Zu diesem Barcode kennt weder Simfit noch Open Food Facts ein Produkt.“ [Eigenes Lebensmittel anlegen] (Barcode vorbelegt) |
| Menge ungültig (unter 0,5 g, über 5.000 g, leer, keine Zahl) | unter dem Feld: „Bitte eine Menge zwischen 0,5 und 5.000 g eingeben.“ Komma erlaubt („12,5“) |
| Speichern fehlgeschlagen | Sheet bleibt offen, Meldung über dem Knopf, Menge bleibt erhalten |
| Langer Lebensmittelname | 2 Zeilen, dann „…“; Marke in `muted-foreground` |

**Ziel ändern** (Dialog): Felder „Kalorien pro Tag (kcal)“, „Eiweiß (g)“, „Kohlenhydrate (g)“, „Fett (g)“; Hinweis klein: „Rechnung zur Kontrolle: Makros ergeben 2.150 kcal“ (bei 130 / 250 / 70 g; 4/4/9 kcal pro g, nur Info, keine Pflicht). Ohne gespeichertes Ziel heißt der Dialog „Ziel festlegen“ und alle Felder sind leer (kein Vorschlagswert). Fehler: „Bitte eine ganze Zahl ab 0 eingeben.“ Rückmeldung: Toast „Ziel gespeichert“.

**Eigenes Lebensmittel** (Dialog bzw. zweiter Schritt im Sheet): Name*, Marke, Barcode, kcal/100 g*, Eiweiß*, Kohlenhydrate*, Fett* (alles pro 100 g; Komma erlaubt). Fehler je Feld: „Bitte eine Zahl angeben, z. B. 12,5.“ Nach dem Anlegen geht es direkt zum Mengenschritt.

### 6.5 Training (`/training`) – A4

**Rangfolge:** Plan wählen → Woche wählen → Wochenleiste (geplant gegen absolviert) → Tage mit Einheiten und Status → zusätzlich absolvierte Aktivitäten.

Desktop 1440:
```
Training     (Frühjahrs-Halbmarathon ▾)   [Plan bearbeiten] [⋯]          [+ Neuer Plan]
[‹]  Woche 2 von 8 · 9. – 15. November  [›]  [Diese Woche]
┌─ Wochenumfang ────────────────────────────────────────────────────────────────────┐
│ Absolviert 2 h 15 min von 4 h 30 min geplant   ▮▮▮▮▮▮▮▮▮▯▯▯▯▯▯▯▯▯ │              │
│ 2 von 4 Einheiten erledigt · 1 verpasst                                           │
└───────────────────────────────────────────────────────────────────────────────────┘
┌──Mo 9.──┬──Di 10.─┬─▌Mi 11.─┬──Do 12.─┬──Fr 13.─┬──Sa 14.─┬──So 15.─┐
│Fuß      │         │ HEUTE   │Hantel   │         │Fuß      │         │
│Locker   │ Nichts  │Fuß      │Kraft    │ Nichts  │Langer   │ Nichts  │
│45 min   │ geplant │Interv.  │40 min   │ geplant │Lauf     │ geplant │
│✓Erledigt│         │40 min   │○Geplant │         │90 min   │         │
│→Lauf    │         │◉Heute   │         │         │○Geplant │         │
│ 47:12   │         │         │         │         │         │         │
│ 8,4 km  │         │         │         │         │         │         │
│[+]      │[+]      │[+]      │[+]      │[+]      │[+]      │[+]      │
└─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘
Zusätzlich absolviert (nicht im Plan)
 Bike Radfahrt · Di 10. Nov. · 57:28 min · 25,9 km                     ›
```
- Spalten 7 × gleich breit (1120/7 = 160 px minus Abstände). Der heutige Tag hat einen 3 px Balken `highlight` oben und den Kopf in `primary`.
- Einheit als kleine Karte (Fläche `card`, Linie, Radius 8, Innenabstand 12). Inhalt: Sportart-Symbol und Titel (2 Zeilen, dann „…“), geplant „45 min · 8 km“, Status-Plakette (**Symbol + Text**). Bei „Erledigt“ folgt die zugeordnete Aktivität als Link („Lauf · 47:12 min · 8,4 km ›“ → Detailseite).
- Status-Texte: „Erledigt“ (`done`), „Verpasst“ (`missed`), „Heute“ (`today`), „Geplant“ (`planned`). Verpasste Einheiten sind nicht ausgegraut (sie müssen lesbar bleiben), sie tragen die Plakette „Verpasst“.
- Klick auf eine Einheit öffnet den Dialog „Einheit bearbeiten“. `[+]` (ghost, 44 px, `aria-label="Einheit am Montag, 9. Nov. hinzufügen"`) ist immer sichtbar, nicht nur beim Überfahren mit der Maus.
- Wochenleiste: Messleiste Variante „Woche“; geplant = Umriss/Spur in `chart-4`, absolviert = Füllung `chart-1`. Text steht immer daneben.

Handy 390 (Tage als Liste, nicht als 7 Spalten):
```
Training
(Frühjahrs-Halbmarathon ▾) [⋯]
[‹] Woche 2 von 8 [›]
9. – 15. Nov.   [Diese Woche]
┌──────────────────────────────┐
│ 2 h 15 von 4 h 30 min        │
│ ▮▮▮▮▮▮▮▯▯▯▯▯▯▯               │
│ 2 von 4 erledigt · 1 verpasst│
└──────────────────────────────┘
MO, 9. NOV.
┌──────────────────────────────┐
│ [Fuß] Lockerer Dauerlauf     │
│ 45 min · 8 km   ✓ Erledigt   │
│ → Lauf 47:12 min · 8,4 km  › │
└──────────────────────────────┘
DI, 10. NOV.
  Nichts geplant  [+ Einheit]
▌MI, 11. NOV. · HEUTE
┌──────────────────────────────┐
│ [Fuß] Intervalle 40 min      │
│ ◉ Heute                      │
└──────────────────────────────┘
…
Zusätzlich absolviert
 [Rad] Radfahrt · Di · 57 min ›
```
Auf Mobilgeräten scrollt die Seite beim Öffnen der laufenden Woche zum heutigen Tag. Zwischen den Wochen wechselt man mit [‹] [›] (keine Wischgeste als einziger Weg).

**Plan anlegen / bearbeiten** (Dialog): „Name des Plans“* (z. B. „Frühjahrs-Halbmarathon“), „Erste Woche beginnt am“* (Datumsfeld; gewählter Tag wird auf den Montag davor gesetzt, Hinweis darunter: „Beginnt am Montag, 9. November“), „Anzahl Wochen“* (1–52). Fehler: „Bitte 1 bis 52 Wochen angeben.“ Rückmeldung: Toast „Plan angelegt“, Ansicht springt in Woche 1 bzw. die laufende Woche.

**Einheit anlegen / bearbeiten** (Dialog): „Sportart“* (ToggleGroup mit Symbol + Text: Laufen, Radfahren, Schwimmen, Kraft, Gehen, Sonstiges; am Handy 2 Zeilen à 3), „Titel“* (z. B. „Lockerer Dauerlauf“), „Datum“* (innerhalb des Plans), „Dauer“ (Stunden und Minuten, zwei Felder), „Distanz (km)“ optional, „Notiz“ optional (Textfeld, 500 Zeichen, Zähler). Im Bearbeiten-Dialog links [Einheit löschen] (`destructive`, ghost) mit Rückfrage. Fehler: „Bitte Titel und Datum angeben.“ / „Das Datum liegt außerhalb des Plans (9. Nov. – 3. Jan.).“

**Plan löschen** (AlertDialog): „Plan ‚Frühjahrs-Halbmarathon‘ löschen? Alle 23 geplanten Einheiten werden gelöscht. Deine Garmin-Aktivitäten bleiben erhalten.“ [Abbrechen] [Plan löschen].

| Zustand | Inhalt |
|---|---|
| Kein Plan (erste Nutzung) | EmptyState `CalendarCheck`: „Noch kein Trainingsplan. Lege fest, was du in den nächsten Wochen trainieren willst. Simfit hakt erledigte Einheiten automatisch ab, sobald deine Uhr sie überträgt.“ [Plan anlegen] |
| Plan ohne Einheiten | Wochenansicht mit „Nichts geplant“ an allen Tagen, Band `info`: „Füge deine erste Einheit hinzu: Tippe bei einem Tag auf +.“ |
| Lädt | Skeleton Wochenleiste + 7 Spalten (Handy: 3 Tagesblöcke) |
| Gefüllt | wie Skizze |
| Woche außerhalb des Plans | [‹]/[›] an den Grenzen gesperrt mit Text „Erste Woche“ / „Letzte Woche“. Läuft der Plan noch nicht: „Plan startet am Mo, 16. Nov.“ + [Zu Woche 1]. Ist er vorbei: „Plan beendet am 3. Jan.“ |
| Viele Einheiten an einem Tag (> 3) | Spalte wächst nach unten (alle sichtbar), kein Abschneiden; am Handy ohnehin Liste |
| Viele Pläne | Auswahl ▾ listet alle Pläne, neueste zuerst; der aktuell laufende steht oben mit Plakette „läuft“ |
| Langer Plan (52 Wochen) | nur Wochennavigation, „Woche 37 von 52“; Auswahl „Gehe zu Woche“ im Menü ⋯ |
| Keine Garmin-Daten (Demo/leer) | Status wird trotzdem berechnet; Band: „Ohne Garmin-Daten kann Simfit nichts automatisch abhaken.“ (nur wenn keine einzige Aktivität vorhanden) |
| Fehler beim Laden | ErrorState 5.4 + „Erneut versuchen“ |
| Speichern fehlgeschlagen | Dialog bleibt offen mit Eingaben, Meldung über dem Knopf |

### 6.6 Einstellungen (`/settings`) – A6, A7, A9, A10

**Rangfolge:** Garmin-Verbindung → Daten holen → Deine Daten (Export, Löschen) → Über Simfit. Abschnitte als Karten untereinander, Desktop max. 720 px breit (Formularbreite), mit Sprungmarken `#garmin`, `#sync`, `#daten`.

```
Einstellungen
┌─ Garmin-Verbindung ───────────────────────────────── #garmin ┐
│ ⚠ Nicht verbunden – Simfit zeigt Beispieldaten.               │
│ Verbinde dein Garmin-Konto, damit Simfit die Werte deiner Uhr │
│ holen kann.                                [Mit Garmin verbinden]
└───────────────────────────────────────────────────────────────┘
┌─ Daten holen ──────────────────────────────────────── #sync ─┐
│ Zuletzt aktualisiert: heute, 12:40 Uhr · Erfolgreich         │
│ Simfit holt automatisch alle 6 Stunden neue Daten, solange   │
│ es läuft.                                                    │
│ Zeitraum (Letzte 30 Tage ▾)  höchstens 90   [Jetzt holen]     │
└───────────────────────────────────────────────────────────────┘
┌─ Deine Daten ──────────────────────────────────────── #daten ┐
│ Daten exportieren                                            │
│ Eine ZIP-Datei mit allen Werten, Mahlzeiten und Plänen.      │
│ Ohne Garmin-Passwort und ohne Schlüssel.   [Export herunterladen]
│ ──────────────────────────────────────────────────────────── │
│ Alles löschen                                                │
│ Entfernt alle deine Daten, die Garmin-Anmeldung und die      │
│ Sicherungen aus Simfit.                       [Alles löschen…]
└───────────────────────────────────────────────────────────────┘
┌─ Über Simfit ────────────────────────────────────────────────┐
│ Lebensmitteldaten: Open Food Facts (ODbL) ↗                  │
│ Basis-Lebensmittel: USDA FoodData Central (gemeinfrei, CC0)  │
│ Schrift: Geist (SIL OFL) · Simfit gibt keine medizinischen    │
│ Ratschläge.                                                  │
└───────────────────────────────────────────────────────────────┘
```
Handy: dieselben Karten in voller Breite. Knöpfe stehen unter dem Text und sind voll breit. „Über Simfit“ zeigt keine Versionsnummer, solange es keine Versionsquelle gibt; die USDA-Angabe ist Text ohne Link.

**Ablauf „Mit Garmin verbinden“** (in der Karte, kein Seitenwechsel):

1. [Mit Garmin verbinden] → Formular in der Karte:
   „E-Mail-Adresse deines Garmin-Kontos“ (`autoComplete="username"`), „Garmin-Passwort“ (`autoComplete="current-password"`, Knopf „Anzeigen“).
   Hinweis darunter (`small`, Symbol `Lock`): „Dein Passwort geht nur einmal direkt an Garmin und wird nicht gespeichert. Simfit merkt sich danach nur eine verschlüsselte Anmeldung.“
   [Verbinden] · [Abbrechen]
2. Senden: Knopf zeigt `Loader2` + „Verbinde mit Garmin …“, Felder gesperrt. Das kann bis zu 30 s dauern, ab 5 s erscheint darunter „Garmin braucht manchmal etwas länger.“
3. Antwort `mfa_required` → Schritt 2 in derselben Karte, Schrittanzeige „Schritt 2 von 2“:
   „Garmin hat dir einen Bestätigungscode geschickt (per E-Mail oder in der Garmin-App).“ Feld „Code“ (6 Ziffern, `inputMode="numeric"`, `autoComplete="one-time-code"`, Fokus darauf). [Bestätigen] · [Abbrechen]
4. Antwort `connected` → Karte zeigt Erfolg (Band `success`, `CheckCircle2`): „Verbunden mit Garmin. Simfit holt jetzt deine Daten der letzten 30 Tage.“ Der erste Abruf über 30 Tage startet einmal (M4: ausgelöst von der Oberfläche mit `POST /sync {range_days: 30}`, das Backend startet beim Verbinden selbst keinen), der Status ist im Abschnitt „Daten holen“ sichtbar. Das Demo-Band verschwindet.
5. Verbunden-Zustand der Karte: „✓ Verbunden“ (Plakette `success`) · „Simfit holt Daten aus deinem Garmin-Konto.“ · [Verbindung trennen] (outline).

**Fehlertexte der Verbindung**

| Lage | Text (in der Karte, Band `destructive` bzw. `warning`) |
|---|---|
| E-Mail/Passwort falsch | „Garmin hat die Anmeldung abgelehnt. Prüfe E-Mail und Passwort – am besten auch einmal auf connect.garmin.com.“ |
| Code falsch/abgelaufen | „Der Code passt nicht oder ist abgelaufen. Prüfe ihn oder starte die Verbindung neu.“ [Neu starten] |
| Zu viele Anmeldeversuche (3/h, AE-8) | „Zu viele Anmeldeversuche. Damit Garmin dein Konto nicht sperrt, ist der nächste Versuch ab **15:10 Uhr** möglich.“ Der Knopf bleibt gesperrt und zeigt „Wieder möglich ab 15:10 Uhr“ |
| Garmin meldet 429 | wie oben, Text: „Garmin hat zu viele Anfragen gemeldet. Nächster Versuch ab 14:35 Uhr.“ |
| Garmin nicht erreichbar | „Garmin ist gerade nicht erreichbar. Prüfe deine Internetverbindung und versuche es in ein paar Minuten erneut.“ |
| Leere Felder | je Feld: „Bitte deine E-Mail-Adresse eingeben.“ / „Bitte dein Passwort eingeben.“ |

Nach einem Fehler wird das Passwortfeld geleert, die E-Mail bleibt stehen.

**Verbindung trennen** (AlertDialog): „Verbindung zu Garmin trennen? Simfit löscht die gespeicherte Anmeldung und holt keine neuen Daten mehr. Bereits geholte Werte bleiben erhalten.“ [Abbrechen] [Trennen]. Der Satz „bleiben erhalten“ ist durch M1 gesichert: Beispieldaten überschreiben nie Garmin-Daten, und nach einer ersten Verbindung lädt Simfit keine Beispieldaten mehr (Karte zeigt dann „Nicht verbunden“ statt Demo).

**Daten holen:** Zeitraum (Select): Letzte 7 Tage / 30 Tage / 90 Tage (Standard 30; **höchstens 90 Tage**, eine Auswahl „1 Jahr“ gibt es nicht – das schont das Garmin-Konto). Unter dem Select klein: „Simfit holt höchstens die letzten 90 Tage.“ Bei „90 Tage“ zusätzlich: „Dauert einige Minuten. Garmin bremst manchmal bei großen Abrufen – Simfit wartet dann automatisch.“ Status und Sperre wie 5.2.

**Export:** [Export herunterladen] → Knopf `Loader2` „Export wird erstellt …“ → Browser lädt `simfit-export-2026-11-04.zip` herunter → Toast „Export gespeichert – du findest ihn in deinem Download-Ordner.“ Fehler: „Der Export konnte nicht erstellt werden. Versuche es erneut.“

**Alles löschen** (AlertDialog, Gefahr):
```
┌ Wirklich alle Daten löschen? ─────────────────────┐
│ Das entfernt endgültig aus Simfit:                │
│ • alle Tageswerte und Aktivitäten                 │
│ • alle Mahlzeiten, eigenen Lebensmittel und Ziele │
│ • alle Trainingspläne                             │
│ • die Garmin-Anmeldung und die Sicherungen        │
│   in Simfit                                       │
│ Die Basis-Lebensmittel (USDA) bleiben verfügbar.  │
│ Heruntergeladene Exporte und deine Daten bei      │
│ Garmin bleiben. Exporte im Download-Ordner        │
│ löschst du bei Bedarf selbst.                     │
│ Tipp: Lade vorher einen [Export] herunter.        │
│                                                   │
│ Tippe ALLES LÖSCHEN, um zu bestätigen             │
│ (                                        )        │
│                    [Abbrechen] [Endgültig löschen]│
└───────────────────────────────────────────────────┘
```
- [Endgültig löschen] (`destructive`) ist gesperrt, bis die Eingabe **genau** „ALLES LÖSCHEN“ lautet. Groß- und Kleinschreibung zählen, Leerzeichen am Rand werden entfernt. Darunter steht live: „Noch nicht bestätigt“ bzw. nichts, sobald es passt.
- Der Fokus startet auf [Abbrechen]. `Enter` im Feld löst nur aus, wenn der Text passt.
- Danach: Toast „Alle Daten wurden gelöscht.“, Wechsel zu „Heute“. Dort erscheint der Erster-Start-Zustand (Willkommenskarte, kein Ziel). Beispieldaten lädt Simfit danach **nicht von selbst**, nur auf [Beispieldaten laden] (M2).
- Fehler (Datenbank-Teil gescheitert): „Löschen hat nicht geklappt. Es wurde nichts gelöscht.“ – das sichert das Backend zu (eine Transaktion, M2).
- Fehler `delete_incomplete` (Datenbank gelöscht, aber Anmeldung oder Sicherungen nicht): Meldung des Servers wörtlich in einem Band `destructive` im Dialog, z. B. „Nicht alles wurde gelöscht: gespeicherte Garmin-Anmeldung, Sicherungen. Bitte Simfit neu starten und erneut löschen.“ Der Dialog bleibt offen, [Endgültig löschen] wieder bedienbar.

| Zustand | Inhalt |
|---|---|
| Lädt | Skeleton je Karte (Status-Zeile) |
| Nicht verbunden (Demo) | wie Skizze |
| Verbunden | Plakette „Verbunden“, [Verbindung trennen] |
| Anmeldung abgelaufen (`auth_required`) | Band `warning`: „Garmin hat die Anmeldung beendet. Bitte verbinde dein Konto neu.“ [Neu verbinden] öffnet Schritt 1 |
| Fehler beim Laden des Status | ErrorState in der Karte; die übrigen Karten bleiben bedienbar |

### 6.7 Seite nicht gefunden
„Diese Seite gibt es nicht.“ + [Zu Heute]. Navigation bleibt sichtbar.

---

## 7. Abläufe je Anforderung (Start → Ziel, Rückmeldung nach jedem Schritt)

| Anf. | Ablauf | Rückmeldung |
|---|---|---|
| A6/A7 erster Start | App öffnen → „Heute“ zeigt Willkommen + Demo-Band → [Beispieldaten laden] → Sync läuft → Kennzahlen erscheinen | Knopf lädt, Toast „Daten aktualisiert“, Demo-Band bleibt |
| A1/A6 Garmin verbinden | Demo-Band „Mit Garmin verbinden →“ → Einstellungen#garmin → E-Mail + Passwort → [Verbinden] → (Code) → Verbunden → Oberfläche startet den ersten Abruf über 30 Tage (M4) | Ladeknopf, Schritt 2 mit Fokus, Erfolgsband, Sync-Status „Läuft“, dann Toast |
| A1/A9 Aktualisieren | [Aktualisieren] (Seitenleiste bzw. Kopf „Heute“) → Lauf → Werte neu | „Wird aktualisiert …“, Toast; bei 429 Band mit Uhrzeit, Knopf gesperrt mit Uhrzeit |
| A9 Anmeldung abgelaufen | Band auf „Heute“ → [Neu verbinden] → Einstellungen Schritt 1 | Band verschwindet nach Erfolg |
| A2 Tag ansehen | „Heute“ öffnen → Kennzahlen lesen → Verlauf-Chip wählen → Tooltip | Chip aktiv (`aria-pressed`), Diagramm wechselt (150 ms) |
| A2 Aktivität ansehen | Aktivitäten → (Filter) → Zeile → Detail → „← Aktivitäten“ | Detail lädt mit Skeleton; zurück an dieselbe Scrollstelle |
| A3 Mahlzeit eintragen | Ernährung (heute) → „+ “ bei Frühstück → suchen (eigene Treffer) → falls nötig [Auch bei Open Food Facts suchen] bzw. Enter → Treffer → Menge (g) → [Zu Frühstück hinzufügen] | eigene Treffer live, OFF erst nach Knopf/Enter mit Skeleton, Nährwerte live gerechnet, Toast, Zeile hervorgehoben, Übersicht aktualisiert |
| A3 per Barcode | wie oben, Ziffern eintippen → „Barcode erkannt – mit Enter suchen“ → Enter → Produkt → Menge | „Produkt gefunden“ bzw. Barcode-unbekannt-Text |
| A3 eigenes Lebensmittel | Suche ohne Treffer → [Eigenes Lebensmittel anlegen] → Werte → [Anlegen] → Menge | Feldfehler sofort beim Verlassen, Toast „Lebensmittel angelegt“ |
| A3 Ziel setzen | Ernährung → [Ziel festlegen] (ohne Ziel, aus Band oder Willkommenskarte) bzw. [Ziel ändern] → Werte → [Speichern] | Toast, Messleiste „Ziel“ erscheint bzw. aktualisiert, Band „Lege ein Tagesziel fest“ verschwindet |
| A3 Eintrag löschen | Zeile → `Trash2` → (Rückgängig) | Zeile weg, Toast mit Rückgängig |
| A4 Plan anlegen | Training (leer) → [Plan anlegen] → Name, Start, Wochen → [Anlegen] → Woche 1 | Toast, Hinweis „Füge deine erste Einheit hinzu“ |
| A4 Einheit planen | Tag → [+] → Sportart, Titel, Dauer → [Speichern] | Dialog schließt, Karte erscheint am Tag, Toast |
| A4 geplant gegen absolviert | Training → laufende Woche (automatisch) → Status je Einheit + Wochenleiste → Aktivität-Link | Status mit Symbol + Text, Link zur Detailseite |
| A10 Export | Einstellungen → [Export herunterladen] | Ladeknopf, Download, Toast |
| A10 Alles löschen | Einstellungen → [Alles löschen…] → Text tippen → [Endgültig löschen] | Knopf erst bei exaktem Text aktiv, Toast, „Heute“ im Erststart; bei `delete_incomplete` Band mit dem, was noch da ist |
| A1 Zeitraum holen | Einstellungen#sync → Zeitraum 7/30/90 Tage → [Jetzt holen] | Sync-Status „Läuft“, dann Toast; bei 429 Uhrzeit aus `retry_after` |

---

## 8. Pflichtboden (Barrierefreiheit, gilt für alle Pakete)

- **Tastatur:** Alles ist mit Tab, Enter, Leertaste, Pfeiltasten (Chips, ToggleGroup, Select) und Esc (Dialoge) bedienbar. Ein Link „Zum Inhalt springen“ steht als erstes Element. Die Reihenfolge folgt der Leserichtung.
- **Fokus:** `focus-visible` mit Ring 2 px `ring` und 2 px Abstand auf jedem Element. Wird ein Dialog geschlossen, kehrt der Fokus zum Auslöser zurück.
- **Beschriftungen:** Jedes Feld hat ein sichtbares `<Label>`. Symbolknöpfe tragen ein `aria-label` mit Bezug („Haferflocken löschen“, „Einheit am Montag, 9. Nov. hinzufügen“). Diagramme haben eine Textzusammenfassung und eine Tabellenansicht. Messleisten haben `role="img"` und `aria-label`.
- **Status nie nur über Farbe:** Trainingsstatus, Sync-Status und „über Ziel“ immer mit Symbol + Text.
- **Kontrast:** siehe 3.2 (alle Textpaare ≥ 4,5:1, Grafik ≥ 3:1).
- **Klickflächen:** am Handy ≥ 44 × 44 px (Tab-Reiter 78 × 64, Listenzeilen ≥ 48 hoch, Symbolknöpfe 44).
- **Reduzierte Bewegung:** alle Übergänge 0 ms, Diagramme ohne Animation, Skeleton ohne Pulsieren.
- **Live-Meldungen:** Sync-Status und Toasts `aria-live="polite"`, Fehlerbänder `role="alert"`.
- **Sprache:** `<html lang="de">`, Datums- und Zahlenformate über `Intl` mit `de-DE`.
- **Zoom:** bis 200 % ohne Abschneiden; Eingabefelder 16 px (kein Zwangszoom auf iOS).

---

## 9. Merkposten für Projektleiter und Architekt – entschieden (Planprüfung 2026-11-04)

Alle sechs Punkte sind entschieden und in ARCHITEKTUR §6 bzw. AE-15/AE-16/AE-20 und den Bauplänen P6, P8, P10, P11, P13 festgehalten. Die Texte in Abschnitt 6 sind danach ausgerichtet.

- **M1 – Demo überschreibt nie Garmin-Daten. Entschieden.** Beispieldaten schreiben nie über Zeilen mit `source="garmin"`; nach der ersten Garmin-Verbindung lädt Simfit keine Beispieldaten mehr (AE-6, AE-15). Damit ist der Satz „Bereits geholte Werte bleiben erhalten“ im Trennen-Dialog gesichert.
- **M2 – „Alles löschen“. Entschieden.** Entfernt alle Inhalte der Datenbank (Tageswerte, Aktivitäten, Rohdaten, Mahlzeiten, eigene und importierte Lebensmittel, Ziel, Pläne, Abruf-Verlauf), die gespeicherte Garmin-Anmeldung (Tokens), alle Sicherungen in `backups/` und setzt die Merker zur Garmin-Verbindung zurück (z. B. „war schon verbunden“). Die USDA-Basis-Lebensmittel bleiben bzw. werden wieder angelegt (keine persönlichen Daten). Der Datenbank-Teil läuft **ganz oder gar nicht** (eine Transaktion): Scheitert er, ist nichts gelöscht → Text „Löschen hat nicht geklappt. Es wurde nichts gelöscht.“ Scheitert danach das Entfernen von Anmeldung oder Sicherungen, meldet der Server `delete_incomplete` mit dem, was noch da ist; die Oberfläche zeigt diesen Text wörtlich (6.6). Ehrlicher Löschtext: **Heruntergeladene Exporte im Download-Ordner und die Daten bei Garmin bleiben** – das steht im Dialog. Hinweis aus P13: Die Garmin-Bremse (Wartezeit nach 429, Zähler der Anmeldeversuche) bleibt absichtlich bestehen, damit ein Löschen das Konto nicht der Sperre aussetzt; das muss der Nutzer nicht sehen.
- **M3 – `retry_after` auch in Fehlerantworten. Entschieden.** Die 429-Antwort (`garmin_rate_limited`, Anmeldesperre) trägt `retry_after` (ISO, UTC). Die Oberfläche zeigt daraus „Wieder möglich ab 14:35 Uhr“ (5.2, 6.6); fehlt der Wert, „Bitte später erneut versuchen.“
- **M4 – Erster Abruf nach dem Verbinden. Entschieden: genau einer.** Laut ARCHITEKTUR AE-16 und Bauplan P6/P8 startet ihn die **Oberfläche** (`POST /sync {range_days: 30}` nach `connected`); das Backend startet beim Verbinden selbst keinen. So wird nicht doppelt geholt. Für Nutzer sieht es gleich aus: „Simfit holt jetzt deine Daten der letzten 30 Tage.“
- **M5 – Mengen nur in Gramm. Entschieden.** Feld „Menge (g)“, 0,5–5.000 g, Komma erlaubt, Schnellwahl 50/100/150/200 g. Getränke ebenfalls in g. Portionen und ml sind zurückgestellt (ARCHITEKTUR §10) – Hinweis an Simon bleibt bestehen.
- **M6 – „Training heute“. Entschieden.** Eigener Endpunkt `GET /training/today` → `{plan, sessions}` (laufender Plan, bei mehreren der zuletzt angelegte). Die Karte zeigt nur den heutigen Tag, keine Vorschau „Als Nächstes …“.

---

## 10. Übergabe an Architekt und Entwickler

### 10.1 P2 – Oberflächen-Grundlage
- Tailwind 4 + shadcn/ui (Stil „new-york“, Basisfarbe neutral, danach mit den Tokens überschrieben), `lucide-react`, Recharts bleibt; `next-themes` für Hell/Dunkel/System (Abhängigkeits-Schranke), `sonner` für Toasts.
- `design/tokens.json` → `src/app/globals.css` (`@theme` + `:root`/`.dark` CSS-Variablen). Entweder per kleinem Skript erzeugen oder von Hand übertragen, aber **mit Test** abgesichert.
- Schrift Geist als `woff2` in `src/app/fonts/` über `next/font/local` einbinden, `OFL.txt` daneben legen. **Prüfen:** Greift `tabular-nums` bei Geist? (Ziffernbreite „1111“ vs. „0000“ messen.) Falls nicht, Zahlen in Geist Mono setzen und hier melden.
- Grundgerüst: `AppShell` (Seitenleiste ≥ 1024, Schmalleiste 768–1023, Tab-Leiste < 768, Inhaltsabstand unten für die Tab-Leiste), `SkipLink`, `DemoBanner`, `SyncStatus`, `EmptyState`, `ErrorState`, `Gauge` (Messleiste, 3 Varianten), `StatusBadge`, `MetricRow`, `ChartCard` (mit Tabellenumschalter), Formatierer in `lib/format.ts` (Formate aus 3.3).
- shadcn-Bausteine: `button, input, label, select, toggle-group, card, badge, alert, dialog, alert-dialog, sheet, drawer, sonner, table, skeleton, tooltip, dropdown-menu, chart`.

### 10.2 Zustände, die je Paket gebaut werden müssen

| Paket | Bildschirm | Pflicht-Zustände |
|---|---|---|
| P8 | Heute | Erster Start, lädt, gefüllt, heute kein Wert, Kennzahl ganz ohne Daten (ausgeblendet), zu wenig Vergleich, Sync läuft, Rate-Limit-Band mit Uhrzeit, Anmeldung nötig, Fehler je Karte, kein Plan / heute nichts geplant (ohne „Als Nächstes“) / Einheit heute, kein Ziel (`goal null`, Schritt ③ nicht erledigt), Verbrauch „bisher“, kein Garmin-Verbrauch |
| P8 | Aktivitäten | leer, leer mit Filter, lädt, gefüllt, „Ältere laden“ + Ende, langer Name, Fehler (auch beim Nachladen) |
| P8 | Detail | lädt, gefüllt (Felder ohne Wert weggelassen), `id` fehlt, 404, Fehler |
| P8 | Einstellungen | Demo, Verbinden Schritt 1 und 2 (MFA), lädt, verbunden, alle Verbindungsfehler (Tabelle 6.6), Anmeldesperre mit Uhrzeit, trennen, Sync-Zeitraum genau 7/30/90 Tage, Export lädt/fertig/Fehler, Alles-löschen-Dialog (Knopf gesperrt bis exakter Text, Text nennt Anmeldung/Sicherungen und was bleibt, Fehler „nichts gelöscht“ und `delete_incomplete`), Über Simfit mit USDA-Text ohne Link |
| P8 | global | Demo-Band (ausblendbar je Sitzung), Sync-Status alle 7 Fälle (Tabelle 5.2), Navigation 3 Breiten, 404-Seite |
| P10 | Ernährung | kein Ziel (ohne Messleiste), leerer Tag mit/ohne Ziel, lädt, gefüllt, über Ziel, kein Garmin-Verbrauch, laufender Tag „bisher“, Zukunft, Sheet: < 2 Zeichen, nur eigene Treffer + OFF-Knopf, OFF lädt (nach Knopf/Enter), OFF-Fehler, OFF-Grenze, nichts gefunden (lokal / nach OFF), Barcode erkannt (kein Auto-Aufruf) / gefunden / unbekannt, Menge ungültig (0,5–5.000 g), Speichern-Fehler; Löschen mit Rückgängig; Ziel-Dialog; eigenes Lebensmittel; **OFF-Hinweis** im Sheet nur bei OFF-Treffern, Fußzeile immer mit OFF- und USDA-Text (USDA ohne Link) |
| P12 | Training | kein Plan, Plan ohne Einheiten, lädt, gefüllt, alle 4 Status + „Zusätzlich“, heutiger Tag markiert, Grenzen des Plans, Plan noch nicht gestartet / beendet, viele Einheiten an einem Tag, viele Pläne, Dialoge Plan/Einheit mit Fehlern, Löschen mit Rückfrage |

### 10.3 Tests, die ich vorschlage (Architekt nimmt sie in die Baupläne auf)
1. **Token-Treue (P2):** Test liest `design/tokens.json` und prüft, dass jede Farbrolle für hell und dunkel als CSS-Variable mit genau diesem Wert in `globals.css` steht. Ergänzend ein Architekturtest: keine Hex-Farben (`#[0-9a-f]{3,8}`) und keine `rgb(`-Angaben in `src/components` und `src/app` außer `globals.css`. In Recharts nur `var(--chart-n)`.
2. **Keine externe Schrift (P2):** kein `next/font/google`, keine `fonts.googleapis`/`fonts.gstatic` (deckt sich mit `test_a10_keine_externen_ressourcen_im_browser`).
3. **Zustands-Tests je Bildschirm (P8/P10/P12, Vitest + Testing Library):** Für jede Zeile der Tabelle 10.2 rendert ein Test die Seite mit gefälschter API-Antwort und prüft den **Text** aus diesem Dokument (z. B. „Wieder möglich ab 14:35 Uhr“, „Noch kein Trainingsplan.“, „Daten von Open Food Facts, Lizenz ODbL“).
4. **Status nicht nur Farbe (P12):** Für `done/missed/today/planned` ist der Text „Erledigt/Verpasst/Heute/Geplant“ im DOM sichtbar.
5. **Alles löschen (P8/P13):** Knopf gesperrt bei „alles löschen“, „ALLES LÖSCHE“ und leer; aktiv bei „ALLES LÖSCHEN“ und „ ALLES LÖSCHEN “; Enter vorher löst nichts aus. Gesendet wird `{confirm: "ALLES LÖSCHEN"}`.
6. **MFA-Ablauf (P8):** `mfa_required` → Codefeld hat Fokus und `autocomplete="one-time-code"`; das Passwort steht nach dem Absenden nicht mehr im DOM bzw. Zustand.
7. **Rate-Limit-Uhrzeit (P8):** `next_attempt_after` 13:35Z mit Zeitzone Europe/Berlin → „14:35 Uhr“; am Folgetag → „morgen, …“ (Zeit als Parameter, nicht `Date.now()` im Formatierer).
8. **OFF-Hinweis (P10):** Sobald die Suchantwort OFF-Treffer enthält oder ein Tagebucheintrag `food_origin="off"` hat, ist der Hinweis mit Link sichtbar; ohne OFF-Treffer steht im Sheet keiner. Fußzeile immer mit OFF- und USDA-Text, USDA ohne Link.
11. **OFF nur auf Knopf/Enter (P10):** Tippen und Warten ruft die Suche nur mit `online=false`; erst Knopf oder `Enter` ruft `online=true`; Barcode erst nach `Enter` (deckt sich mit `test_s12_off_nur_auf_knopf_oder_enter`).
9. **Tastatur (alle):** Dialog fängt den Fokus, Esc schließt, der Fokus kehrt zum Auslöser zurück (mit `fireEvent`, siehe Lektion zu userEvent/Fake-Timers).
10. **Sichtprüfung (Entwickler vor FERTIG, Prüfliste Oberflächen-Standard):** Playwright-Screenshots 1440 und 390, hell **und** dunkel, je Pflicht-Zustand. Überlagerungen (Demo-Band, Toasts über der Tab-Leiste, Sheet/Drawer, Dialoge) in jeder Ansicht am Handy und Desktop fotografieren (Lektion „Überlagerungen“). Kein waagrechtes Scrollen bei 390 px (Test: `document.documentElement.scrollWidth <= 390`).

### 10.4 Was vom Prototyp wegfällt
Eigenes CSS (`globals.css` alt), obere Navigationsleiste, Kachelraster, fünf Einzeldiagramme mit `--c1…--c5`, Drehkreisel als Ladeanzeige für Inhalte, rote/grüne Bilanzfarbe, Unicode-Symbole „✕ ← →“ als Knopfinhalt (durch Lucide ersetzen), „Quelle: demo“ als Rohtext.
