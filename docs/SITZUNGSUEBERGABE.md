# Sitzungsübergabe

**Übergeben am:** 2026-11-11 · **Auftrag:** Simfit weiterbauen · **Dev-Team-Version:** 3.16.2
**Durchlauf:** aus (keine Startfreigabe erteilt)

## Wo wir stehen
- **Phase:** 5 – Startfreigabe (wartet) · **Meilenstein:** 0 von 4
- **Arbeitsbranch:** claude/lucid-gates-69jllu · **Letzter Commit:** siehe `git log` (gepusht: ja bis auf diese Übergabe)
- **Letzter grüner Stand:** 38 Architekturtests

## Nächster Schritt
Simon die Klärungsfragen zu „alles lokal“ / iPhone / Google-Apple-Login / „Infos im Repo“ stellen; nach seiner Antwort architekt + kritiker + sicherheitspruefer neu planen lassen.

## Pakete
| Nr. | Stand | Branch | Was noch fehlt |
|---|---|---|---|
| P1a–P15 | Baupläne fertig, nichts gebaut | – | Neuplanung wegen Betriebsmodell, Login, deutsche Bezeichner (A14) |

## Laufende Agenten
Keine.

## Nur in dieser Sitzung entschieden oder besprochen
- Simon: „ne wir speichern alles lokal, angemeldet wird per google konto oder apple falls das auch geht, infos dann in einem repo speichern? weiß nicht wies am besten ist“ – Server-Hosting abgelehnt, aber Freund hat nur iPhone: Widerspruch, zu klären.
- Empfehlung zu „Repo“: Projektdoku ja; Gesundheitsdaten, Tokens, Zugangsdaten nie ins Repo; verschlüsselte Sicherung woanders.
- Apple-Login kostet 99 $/Jahr (Developer Program), Google kostenlos; für Einzelnutzer evtl. Passkey/PIN einfacher.

## Fallstricke
- Garmin-Zugriff von Rechenzentrums-IPs kann blockiert sein; erst am Ende mit echten Zugangsdaten testbar.
- Keine Zugangsdaten lesen/anlegen/ausgeben; nur auf Branch claude/lucid-gates-69jllu pushen; kein PR ohne Auftrag.
- Nur benannte Dev-Team-Agenten benutzen.

## Erst lesen
`docs/STATUS.md`, `docs/plan.md`, `docs/ENTSCHEIDUNGEN.md`, `docs/OFFENE_FRAGEN.md`, `docs/lastenheft.md`
