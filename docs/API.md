# Simfit API (v0, Vertrag zwischen Backend und Frontend)

Basis-URL: `http://localhost:8000`. Alle Endpunkte unter `/api`. JSON, Datumsformat `YYYY-MM-DD`, Zeitstempel ISO 8601 (UTC).
Einzelnutzer-MVP, keine Authentifizierung.

## Sync
- `POST /api/sync` Body `{"days": 14}` → `SyncRun`. Holt die letzten N Tage von der Datenquelle.
- `GET /api/sync/status` → `SyncRun | null` (letzter Lauf).
- `GET /api/health` → `{"status":"ok","source":"demo"|"garmin"}`

`SyncRun`: `{id, started_at, finished_at, status: "running"|"ok"|"error", message, days, source}`

## Garmin-Tagesdaten
- `GET /api/daily?from=&to=` → `DailyMetrics[]`, aufsteigend nach Datum.

`DailyMetrics`:
```
{ date, steps, distance_m, resting_hr, avg_hr, sleep_seconds, sleep_score,
  hrv_ms, stress_avg, body_battery_high, body_battery_low,
  active_kcal, total_kcal, weight_kg }
```
Alle Felder außer `date` können `null` sein.

## Aktivitäten
- `GET /api/activities?from=&to=&limit=50` → `Activity[]`, neueste zuerst.
- `GET /api/activities/{id}` → `Activity`.

`Activity`:
```
{ id, source_id, type, name, start_time, duration_s, distance_m,
  avg_hr, max_hr, calories, elevation_gain_m, avg_pace_s_per_km }
```

## Ernährung
- `GET /api/foods?q=` → `Food[]` (lokale Datenbank, max. 50)
- `POST /api/foods` → `Food` (eigenes Lebensmittel anlegen)
- `GET /api/food-log?date=` → `FoodLogEntry[]`
- `POST /api/food-log` Body `{date, meal, food_id, grams}` → `FoodLogEntry`
- `DELETE /api/food-log/{id}` → 204
- `GET /api/nutrition/day?date=` → `NutritionDay`
- `GET /api/nutrition/goal` / `PUT /api/nutrition/goal` → `NutritionGoal`

`Food`: `{id, name, brand, kcal_100g, protein_100g, carbs_100g, fat_100g, barcode}` (Nährwerte pro 100 g)
`meal`: `"breakfast"|"lunch"|"dinner"|"snack"`
`FoodLogEntry`: `{id, date, meal, food: Food, grams, kcal, protein, carbs, fat}`
`NutritionGoal`: `{kcal_target, protein_g, carbs_g, fat_g}`
`NutritionDay`: `{date, eaten:{kcal,protein,carbs,fat}, burned_kcal (aus Garmin total_kcal, sonst null), goal: NutritionGoal, balance_kcal}`

## Training (folgt in der nächsten Iteration)
Trainingspläne sind noch nicht Teil von v0.
