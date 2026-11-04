"use client";

import { useState } from "react";
import { api, errorMessage, type NutritionGoal } from "@/lib/api";

export default function GoalForm({
  goal,
  onSaved,
  onClose,
}: {
  goal: NutritionGoal;
  onSaved: () => void;
  onClose: () => void;
}) {
  const [v, setV] = useState({
    kcal_target: String(goal.kcal_target),
    protein_g: String(goal.protein_g),
    carbs_g: String(goal.carbs_g),
    fat_g: String(goal.fat_g),
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const set = (k: keyof typeof v) => (e: React.ChangeEvent<HTMLInputElement>) => setV({ ...v, [k]: e.target.value });

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const n = Object.fromEntries(Object.entries(v).map(([k, s]) => [k, Number(s.replace(",", "."))])) as unknown as NutritionGoal;
    if (Object.values(n).some((x) => !Number.isFinite(x) || x < 0) || n.kcal_target <= 0) {
      setError("Bitte gültige Zahlen eingeben (Kalorien größer 0).");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api.saveNutritionGoal(n);
      onSaved();
    } catch (err) {
      setError(errorMessage(err));
      setBusy(false);
    }
  }

  return (
    <form className="card stack" onSubmit={submit} style={{ borderColor: "var(--accent)" }}>
      <h3>Tagesziel bearbeiten</h3>
      <div className="form-grid">
        <label className="field">Kalorien (kcal)<input inputMode="decimal" value={v.kcal_target} onChange={set("kcal_target")} /></label>
        <label className="field">Eiweiß (g)<input inputMode="decimal" value={v.protein_g} onChange={set("protein_g")} /></label>
        <label className="field">Kohlenhydrate (g)<input inputMode="decimal" value={v.carbs_g} onChange={set("carbs_g")} /></label>
        <label className="field">Fett (g)<input inputMode="decimal" value={v.fat_g} onChange={set("fat_g")} /></label>
      </div>
      {error && <div role="alert" style={{ color: "var(--danger)" }}>{error}</div>}
      <div className="row">
        <button className="primary" type="submit" disabled={busy}>Speichern</button>
        <button type="button" onClick={onClose}>Abbrechen</button>
      </div>
    </form>
  );
}
