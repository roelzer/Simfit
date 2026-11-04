# Lastenheft: Simfit

**Stand:** 2026-11-04 · **Auftraggeber:** Simon (Eigenprojekt, Geschenk an einen Freund) · **Ansprechpartner:** Simon

## 1. Ausgangslage
Es gibt einen Prototyp (nicht über das Dev-Team gebaut, ohne Test-Schranke): Backend FastAPI mit Demo- und Garmin-Quelle, Sync, Ernährungs-API, ein Test; Frontend Next.js mit Dashboard, Aktivitäten, Ernährung, Platzhalter Training. Die Garmin-Anbindung ist nie gegen ein echtes Konto gelaufen. Machbarkeit, Funktionsvorschläge und Aufwand: `docs/ANFORDERUNGEN.md`.

## 2. Ziel
Eine Fitness-App, die die Daten einer Garmin-Uhr holt und als Dashboard zeigt, dazu Kalorientracking und Trainingsplanung. Sie wird einem Freund geschenkt.

## 3. Nutzer
Der Freund (ein Nutzer, eigenes Garmin-Konto), im Alltag, am Handy und am Rechner. Vorwissen: keine Technik.

## 4. Anforderungen (Simons Worte)
| Nr. | Anforderung | Muss/Soll/Kann | Akzeptanzkriterium |
|---|---|---|---|
| A1 | „fitness app, die sich von einer garmin uhr daten holt“ | Muss | Sync holt Tagesdaten (Schritte, Puls, Schlaf, HRV, Stress, Body Battery, Kalorien) und Aktivitäten aus Garmin Connect; erneuter Sync erzeugt keine Doppelungen; Zeitzonen stimmen. |
| A2 | „und auch als dashboard dafür dient“ | Muss | Dashboard zeigt Tageswerte, Trends (14/30 Tage) und letzte Aktivitäten; Aktivitätsdetails abrufbar; Desktop und Handy. |
| A3 | „sowas wie kalorien tracken“ | Muss | Mahlzeiten loggen, Kalorien und Makros pro Tag, Ziel, Bilanz gegen Garmin-Verbrauch; Lebensmittelsuche inkl. Open Food Facts mit Attribution. |
| A4 | „trainingsplan erstellen“ | Muss | Plan anlegen und bearbeiten (Wochen, Einheiten); geplant gegen absolviert (Garmin-Aktivitäten) sichtbar. |
| A5 | „erstmal per cloud“ | Muss | Erste Datenquelle ist die Garmin-Connect-Cloud; weitere Quellen später ohne Umbau (`DataSource`). |
| A6 | „die app ist ein geschenk für einen freund“ | Muss | Der Freund kann die App ohne Technikwissen in Betrieb nehmen (Anleitung, ein Startweg) und mit seinem eigenen Konto nutzen. |
| A7 | „zugangsdaten werden erst am ende kommen, wenn alles schon fertig ist“ | Muss | Bis zur Übergabe keine echten Zugangsdaten in Sitzung, Repo oder Tests; der Freund trägt sie selbst ein; Betrieb mit Demo-Daten jederzeit möglich. |
| A8 | „du machst [die agenten] nacheinander wie es am meisten sinn macht“ | Muss | Das Team arbeitet in sinnvoller Reihenfolge nacheinander (Protokoll `docs/AGENTEN_LOG.md`). |
| A9 | (aus ANFORDERUNGEN.md) Garmin-Tokens statt Passwort, Backoff bei 429, Tokens verschlüsselt | Muss | Server loggt sich nie mit Passwort ein; Tokens nicht im Klartext, nicht im Repo; Test beweist Backoff mit aufgezeichneten Beispieldaten. |
| A10 | (aus ANFORDERUNGEN.md) Datenschutz für Gesundheitsdaten | Muss | Daten bleiben bei dem Freund bzw. unter seiner Kontrolle; Löschen und Export möglich; keine Weitergabe an Dritte außer Open Food Facts (nur Suchbegriff/Barcode). |
| A11 | „überprüf machbarkeit und aufwand“, „recherchier welche funktionen“ | erledigt | `docs/ANFORDERUNGEN.md` |

## 5. Rahmenbedingungen
- Garmin: inoffizielle Bibliothek `garminconnect` (kann brechen, Rate Limits); offizielle API später, falls zugänglich.
- Daten: Gesundheitsdaten einer Person (DSGVO Art. 9).
- Offen: wo die App läuft (Rechner des Freundes oder gemieteter Server), siehe Startfreigabe.

## 6. Nicht im Umfang
Mobile App (Health Connect/HealthKit), KI-Coach, Export von Trainings auf die Uhr, Mehrnutzerbetrieb.

## 7. Offene Fragen
Siehe `docs/OFFENE_FRAGEN.md`.
