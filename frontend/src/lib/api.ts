// Zentraler, typisierter API-Client passend zu docs/API.md.

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");

export type SyncStatus = "running" | "ok" | "error";
export interface SyncRun {
  id: number;
  started_at: string;
  finished_at: string | null;
  status: SyncStatus;
  message: string | null;
  days: number;
  source: string;
}
export interface Health {
  status: string;
  source: "demo" | "garmin";
}

export interface DailyMetrics {
  date: string;
  steps: number | null;
  distance_m: number | null;
  resting_hr: number | null;
  avg_hr: number | null;
  sleep_seconds: number | null;
  sleep_score: number | null;
  hrv_ms: number | null;
  stress_avg: number | null;
  body_battery_high: number | null;
  body_battery_low: number | null;
  active_kcal: number | null;
  total_kcal: number | null;
  weight_kg: number | null;
}

export interface Activity {
  id: number;
  source_id: string | null;
  type: string | null;
  name: string | null;
  start_time: string;
  duration_s: number | null;
  distance_m: number | null;
  avg_hr: number | null;
  max_hr: number | null;
  calories: number | null;
  elevation_gain_m: number | null;
  avg_pace_s_per_km: number | null;
}

export type Meal = "breakfast" | "lunch" | "dinner" | "snack";
export const MEALS: Meal[] = ["breakfast", "lunch", "dinner", "snack"];

export interface Food {
  id: number;
  name: string;
  brand: string | null;
  kcal_100g: number;
  protein_100g: number;
  carbs_100g: number;
  fat_100g: number;
  barcode: string | null;
}
/** Body für POST /api/foods (Vertrag nennt keinen Body; Annahme: Food ohne id). */
export type NewFood = Omit<Food, "id">;

export interface FoodLogEntry {
  id: number;
  date: string;
  meal: Meal;
  food: Food;
  grams: number;
  kcal: number;
  protein: number;
  carbs: number;
  fat: number;
}
export interface NewFoodLogEntry {
  date: string;
  meal: Meal;
  food_id: number;
  grams: number;
}
export interface NutritionGoal {
  kcal_target: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}
export interface NutritionDay {
  date: string;
  eaten: { kcal: number; protein: number; carbs: number; fat: number };
  burned_kcal: number | null;
  goal: NutritionGoal;
  balance_kcal: number | null;
}

export class ApiError extends Error {
  status: number | null;
  constructor(message: string, status: number | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function qs(params: Record<string, string | number | undefined | null>): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") sp.set(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
      cache: "no-store",
    });
  } catch {
    throw new ApiError(`Backend nicht erreichbar (${API_URL}). Läuft der Server?`);
  }
  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      const d = body?.detail ?? body?.message;
      detail = typeof d === "string" ? d : d ? JSON.stringify(d) : "";
    } catch {
      /* kein JSON */
    }
    throw new ApiError(`Fehler ${res.status}${detail ? `: ${detail}` : ""}`, res.status);
  }
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  return (text ? JSON.parse(text) : null) as T;
}

export const api = {
  health: () => request<Health>("/api/health"),
  startSync: (days = 14) =>
    request<SyncRun>("/api/sync", { method: "POST", body: JSON.stringify({ days }) }),
  syncStatus: () => request<SyncRun | null>("/api/sync/status"),

  daily: (from: string, to: string) => request<DailyMetrics[]>(`/api/daily${qs({ from, to })}`),

  activities: (opts: { from?: string; to?: string; limit?: number } = {}) =>
    request<Activity[]>(`/api/activities${qs({ limit: 50, ...opts })}`),
  activity: (id: string | number) => request<Activity>(`/api/activities/${encodeURIComponent(String(id))}`),

  foods: (q = "") => request<Food[]>(`/api/foods${qs({ q })}`),
  createFood: (food: NewFood) =>
    request<Food>("/api/foods", { method: "POST", body: JSON.stringify(food) }),
  foodLog: (date: string) => request<FoodLogEntry[]>(`/api/food-log${qs({ date })}`),
  addFoodLog: (entry: NewFoodLogEntry) =>
    request<FoodLogEntry>("/api/food-log", { method: "POST", body: JSON.stringify(entry) }),
  deleteFoodLog: (id: number) => request<void>(`/api/food-log/${id}`, { method: "DELETE" }),
  nutritionDay: (date: string) => request<NutritionDay>(`/api/nutrition/day${qs({ date })}`),
  nutritionGoal: () => request<NutritionGoal>("/api/nutrition/goal"),
  saveNutritionGoal: (goal: NutritionGoal) =>
    request<NutritionGoal>("/api/nutrition/goal", { method: "PUT", body: JSON.stringify(goal) }),
};

export function errorMessage(e: unknown): string {
  return e instanceof Error ? e.message : "Unbekannter Fehler";
}
