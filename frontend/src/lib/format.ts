const nf0 = new Intl.NumberFormat("de-DE", { maximumFractionDigits: 0 });
const nf1 = new Intl.NumberFormat("de-DE", { maximumFractionDigits: 1 });

export const DASH = "–";

export function num(v: number | null | undefined, digits: 0 | 1 = 0): string {
  if (v === null || v === undefined || Number.isNaN(v)) return DASH;
  return (digits === 0 ? nf0 : nf1).format(v);
}

export function km(m: number | null | undefined): string {
  if (m === null || m === undefined) return DASH;
  return `${nf1.format(m / 1000)} km`;
}

export function duration(s: number | null | undefined): string {
  if (s === null || s === undefined) return DASH;
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.round(s % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")} h`;
  return `${m}:${String(sec).padStart(2, "0")} min`;
}

export function sleep(s: number | null | undefined): string {
  if (s === null || s === undefined) return DASH;
  const h = Math.floor(s / 3600);
  const m = Math.round((s % 3600) / 60);
  return `${h} h ${String(m).padStart(2, "0")} min`;
}

export function pace(sPerKm: number | null | undefined): string {
  if (sPerKm === null || sPerKm === undefined || sPerKm <= 0) return DASH;
  const m = Math.floor(sPerKm / 60);
  const s = Math.round(sPerKm % 60);
  return `${m}:${String(s).padStart(2, "0")} min/km`;
}

/** Lokales Datum als YYYY-MM-DD. */
export function isoDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function today(): string {
  return isoDate(new Date());
}

export function addDays(date: string, n: number): string {
  const [y, m, d] = date.split("-").map(Number);
  return isoDate(new Date(y, m - 1, d + n));
}

export function shortDate(date: string): string {
  const [, m, d] = date.split("-");
  return `${d}.${m}.`;
}

export function longDate(date: string): string {
  const [y, m, d] = date.split("-").map(Number);
  return new Intl.DateTimeFormat("de-DE", {
    weekday: "long",
    day: "2-digit",
    month: "long",
    year: "numeric",
  }).format(new Date(y, m - 1, d));
}

export function dateTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium", timeStyle: "short" }).format(d);
}

const TYPES: Record<string, string> = {
  running: "Laufen",
  trail_running: "Trailrun",
  treadmill_running: "Laufband",
  cycling: "Radfahren",
  road_biking: "Rennrad",
  mountain_biking: "Mountainbike",
  walking: "Gehen",
  hiking: "Wandern",
  swimming: "Schwimmen",
  lap_swimming: "Bahnschwimmen",
  strength_training: "Krafttraining",
  yoga: "Yoga",
  indoor_cardio: "Cardio",
  elliptical: "Crosstrainer",
};

export function activityType(t: string | null | undefined): string {
  if (!t) return "Aktivität";
  return TYPES[t.toLowerCase()] ?? t.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());
}

export const MEAL_LABEL = {
  breakfast: "Frühstück",
  lunch: "Mittagessen",
  dinner: "Abendessen",
  snack: "Snacks",
} as const;
