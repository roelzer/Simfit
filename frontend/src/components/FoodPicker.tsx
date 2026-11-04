"use client";

import { useEffect, useState } from "react";
import { api, errorMessage, type Food, type Meal, type NewFood } from "@/lib/api";
import { MEAL_LABEL, num } from "@/lib/format";
import { useApi } from "@/lib/useApi";

function parseNum(s: string): number | null {
  const n = Number(s.replace(",", "."));
  return s.trim() !== "" && Number.isFinite(n) && n >= 0 ? n : null;
}

function CustomFoodForm({ onCreated, onCancel }: { onCreated: (f: Food) => void; onCancel: () => void }) {
  const [v, setV] = useState({ name: "", brand: "", kcal: "", protein: "", carbs: "", fat: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const set = (k: keyof typeof v) => (e: React.ChangeEvent<HTMLInputElement>) => setV({ ...v, [k]: e.target.value });

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const kcal = parseNum(v.kcal), protein = parseNum(v.protein), carbs = parseNum(v.carbs), fat = parseNum(v.fat);
    if (!v.name.trim() || kcal === null || protein === null || carbs === null || fat === null) {
      setError("Bitte Name und alle Nährwerte (pro 100 g) als Zahl ausfüllen.");
      return;
    }
    const body: NewFood = {
      name: v.name.trim(),
      brand: v.brand.trim() || null,
      kcal_100g: kcal,
      protein_100g: protein,
      carbs_100g: carbs,
      fat_100g: fat,
      barcode: null,
    };
    setBusy(true);
    setError(null);
    try {
      onCreated(await api.createFood(body));
    } catch (err) {
      setError(errorMessage(err));
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="stack" style={{ marginTop: 12 }}>
      <h3>Eigenes Lebensmittel (Werte pro 100 g)</h3>
      <div className="form-grid">
        <label className="field">Name<input value={v.name} onChange={set("name")} required /></label>
        <label className="field">Marke (optional)<input value={v.brand} onChange={set("brand")} /></label>
        <label className="field">Kalorien (kcal)<input inputMode="decimal" value={v.kcal} onChange={set("kcal")} /></label>
        <label className="field">Eiweiß (g)<input inputMode="decimal" value={v.protein} onChange={set("protein")} /></label>
        <label className="field">Kohlenhydrate (g)<input inputMode="decimal" value={v.carbs} onChange={set("carbs")} /></label>
        <label className="field">Fett (g)<input inputMode="decimal" value={v.fat} onChange={set("fat")} /></label>
      </div>
      {error && <div role="alert" style={{ color: "var(--danger)" }}>{error}</div>}
      <div className="row">
        <button className="primary" type="submit" disabled={busy}>Anlegen</button>
        <button type="button" onClick={onCancel}>Abbrechen</button>
      </div>
    </form>
  );
}

export default function FoodPicker({
  date,
  meal,
  onAdded,
  onClose,
}: {
  date: string;
  meal: Meal;
  onAdded: () => void;
  onClose: () => void;
}) {
  const [q, setQ] = useState("");
  const [debounced, setDebounced] = useState("");
  const [selected, setSelected] = useState<Food | null>(null);
  const [grams, setGrams] = useState("100");
  const [custom, setCustom] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(q.trim()), 250);
    return () => clearTimeout(t);
  }, [q]);

  const foods = useApi(`foods:${debounced}`, () => api.foods(debounced));

  const g = parseNum(grams);
  const factor = selected && g !== null ? g / 100 : 0;

  async function add() {
    if (!selected || g === null || g <= 0) {
      setError("Bitte ein Lebensmittel wählen und Gramm größer 0 angeben.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api.addFoodLog({ date, meal, food_id: selected.id, grams: g });
      onAdded();
    } catch (e) {
      setError(errorMessage(e));
      setBusy(false);
    }
  }

  return (
    <div className="card" style={{ borderColor: "var(--accent)" }}>
      <div className="row between">
        <h3>Hinzufügen zu: {MEAL_LABEL[meal]}</h3>
        <button className="icon" onClick={onClose} aria-label="Schließen">✕</button>
      </div>

      <div className="row" style={{ marginTop: 12 }}>
        <input
          type="search"
          placeholder="Lebensmittel suchen…"
          aria-label="Lebensmittel suchen"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{ flex: 1, minWidth: 0 }}
          autoFocus
        />
      </div>

      <div className="results" role="listbox" aria-label="Suchergebnisse">
        {foods.loading ? (
          <div className="state"><span className="spinner" aria-hidden="true" />Suche…</div>
        ) : foods.error ? (
          <div className="state" style={{ color: "var(--danger)" }}>{foods.error}</div>
        ) : (foods.data ?? []).length === 0 ? (
          <div className="state">Nichts gefunden. Lege ein eigenes Lebensmittel an.</div>
        ) : (
          foods.data!.map((f) => (
            <button
              key={f.id}
              role="option"
              aria-selected={selected?.id === f.id}
              className={selected?.id === f.id ? "sel" : ""}
              onClick={() => setSelected(f)}
            >
              <div>{f.name}{f.brand ? ` (${f.brand})` : ""}</div>
              <div style={{ fontSize: ".8rem", opacity: 0.8 }}>
                {num(f.kcal_100g)} kcal · E {num(f.protein_100g, 1)} · KH {num(f.carbs_100g, 1)} · F {num(f.fat_100g, 1)} (je 100 g)
              </div>
            </button>
          ))
        )}
      </div>

      {selected && (
        <div className="row" style={{ marginTop: 12 }}>
          <label className="field" style={{ width: 120 }}>
            Menge (g)
            <input inputMode="decimal" value={grams} onChange={(e) => setGrams(e.target.value)} />
          </label>
          <div className="muted" style={{ flex: 1 }}>
            {g !== null ? (
              <>
                {num(selected.kcal_100g * factor)} kcal · E {num(selected.protein_100g * factor, 1)} g · KH{" "}
                {num(selected.carbs_100g * factor, 1)} g · F {num(selected.fat_100g * factor, 1)} g
              </>
            ) : (
              "Ungültige Menge"
            )}
          </div>
          <button className="primary" onClick={add} disabled={busy}>Hinzufügen</button>
        </div>
      )}
      {error && <div role="alert" style={{ color: "var(--danger)", marginTop: 8 }}>{error}</div>}

      {custom ? (
        <CustomFoodForm
          onCancel={() => setCustom(false)}
          onCreated={(f) => {
            setCustom(false);
            setSelected(f);
            setQ(f.name);
          }}
        />
      ) : (
        <div style={{ marginTop: 12 }}>
          <button onClick={() => setCustom(true)}>Eigenes Lebensmittel anlegen</button>
        </div>
      )}
    </div>
  );
}
