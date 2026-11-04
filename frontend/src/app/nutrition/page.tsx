"use client";

import { useState } from "react";
import { api, errorMessage, MEALS, type FoodLogEntry, type Meal } from "@/lib/api";
import { addDays, DASH, longDate, MEAL_LABEL, num, today } from "@/lib/format";
import { useApi } from "@/lib/useApi";
import { ErrorBox, Loading } from "@/components/State";
import FoodPicker from "@/components/FoodPicker";
import GoalForm from "@/components/GoalForm";

function Progress({ label, value, goal, unit }: { label: string; value: number; goal: number; unit: string }) {
  const pct = goal > 0 ? Math.min(100, (value / goal) * 100) : 0;
  const over = goal > 0 && value > goal;
  return (
    <div className="bar-row">
      <div className="bar-head">
        <span>{label}</span>
        <span className={over ? "neg" : ""}>
          {num(value)} / {num(goal)} {unit}
        </span>
      </div>
      <div className="bar" role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={goal} aria-valuenow={Math.round(value)}>
        <span className={over ? "over" : ""} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function NutritionPage() {
  const [date, setDate] = useState(today());
  const [addMeal, setAddMeal] = useState<Meal | null>(null);
  const [editGoal, setEditGoal] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const data = useApi(`nutrition:${date}`, async () => {
    const [day, log] = await Promise.all([api.nutritionDay(date), api.foodLog(date)]);
    return { day, log };
  });
  const { reload } = data;

  async function remove(e: FoodLogEntry) {
    setActionError(null);
    try {
      await api.deleteFoodLog(e.id);
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  }

  const day = data.data?.day;
  const log = data.data?.log ?? [];
  const isToday = date === today();

  return (
    <div className="stack">
      <h1 style={{ marginBottom: 0 }}>Ernährung</h1>

      <div className="row between">
        <div className="row" style={{ gap: 8 }}>
          <button onClick={() => setDate(addDays(date, -1))} aria-label="Vorheriger Tag">←</button>
          <input
            type="date"
            value={date}
            aria-label="Datum"
            onChange={(e) => e.target.value && setDate(e.target.value)}
          />
          <button onClick={() => setDate(addDays(date, 1))} aria-label="Nächster Tag">→</button>
          {!isToday && <button onClick={() => setDate(today())}>Heute</button>}
        </div>
        <span className="muted">{longDate(date)}</span>
      </div>

      {actionError && <div className="state error" role="alert">{actionError}</div>}

      {data.loading ? (
        <Loading />
      ) : data.error ? (
        <ErrorBox message={data.error} onRetry={reload} />
      ) : day ? (
        <>
          <section className="card">
            <div className="row between">
              <h2>Tagesziel</h2>
              <button onClick={() => setEditGoal((v) => !v)}>{editGoal ? "Schließen" : "Ziel bearbeiten"}</button>
            </div>
            <Progress label="Kalorien" value={day.eaten.kcal} goal={day.goal.kcal_target} unit="kcal" />
            <Progress label="Eiweiß" value={day.eaten.protein} goal={day.goal.protein_g} unit="g" />
            <Progress label="Kohlenhydrate" value={day.eaten.carbs} goal={day.goal.carbs_g} unit="g" />
            <Progress label="Fett" value={day.eaten.fat} goal={day.goal.fat_g} unit="g" />
          </section>

          {editGoal && (
            <GoalForm
              goal={day.goal}
              onClose={() => setEditGoal(false)}
              onSaved={() => {
                setEditGoal(false);
                reload();
              }}
            />
          )}

          <section className="card">
            <h2>Bilanz</h2>
            <div className="kv">
              <div><div className="label">Gegessen</div><div className="value">{num(day.eaten.kcal)} kcal</div></div>
              <div>
                <div className="label">Verbrannt (Garmin)</div>
                <div className="value">{day.burned_kcal === null ? DASH : `${num(day.burned_kcal)} kcal`}</div>
              </div>
              <div>
                <div className="label">Bilanz</div>
                <div className={`value ${day.balance_kcal === null ? "" : day.balance_kcal > 0 ? "neg" : "pos"}`}>
                  {day.balance_kcal === null
                    ? DASH
                    : `${day.balance_kcal > 0 ? "+" : ""}${num(day.balance_kcal)} kcal`}
                </div>
              </div>
            </div>
            {day.burned_kcal === null && (
              <p className="muted" style={{ marginBottom: 0 }}>
                Für diesen Tag liegen keine Garmin-Verbrauchsdaten vor.
              </p>
            )}
          </section>

          {MEALS.map((meal) => {
            const entries = log.filter((l) => l.meal === meal);
            const kcal = entries.reduce((s, e) => s + e.kcal, 0);
            return (
              <section key={meal} className="card">
                <div className="row between">
                  <h2 style={{ marginBottom: 0 }}>
                    {MEAL_LABEL[meal]} <span className="muted">· {num(kcal)} kcal</span>
                  </h2>
                  <button onClick={() => setAddMeal(addMeal === meal ? null : meal)}>
                    {addMeal === meal ? "Schließen" : "+ Hinzufügen"}
                  </button>
                </div>
                {entries.length > 0 && (
                  <ul className="list" style={{ marginTop: 8 }}>
                    {entries.map((e) => (
                      <li key={e.id}>
                        <div className="item">
                          <div>
                            <div>{e.food.name}</div>
                            <div className="meta">
                              {num(e.grams)} g · E {num(e.protein, 1)} · KH {num(e.carbs, 1)} · F {num(e.fat, 1)}
                            </div>
                          </div>
                          <div className="row" style={{ gap: 8, flexWrap: "nowrap" }}>
                            <strong>{num(e.kcal)} kcal</strong>
                            <button className="icon danger" onClick={() => remove(e)} aria-label={`${e.food.name} löschen`}>
                              ✕
                            </button>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
                {addMeal === meal && (
                  <div style={{ marginTop: 12 }}>
                    <FoodPicker
                      date={date}
                      meal={meal}
                      onClose={() => setAddMeal(null)}
                      onAdded={() => {
                        setAddMeal(null);
                        reload();
                      }}
                    />
                  </div>
                )}
              </section>
            );
          })}
        </>
      ) : null}

      <p className="footnote">
        Lebensmitteldaten können aus Open Food Facts (ODbL) stammen. Quelle: openfoodfacts.org
      </p>
    </div>
  );
}
