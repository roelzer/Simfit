"use client";

import Link from "next/link";
import { useState } from "react";
import { api, type DailyMetrics } from "@/lib/api";
import { addDays, DASH, longDate, num, today } from "@/lib/format";
import { useApi } from "@/lib/useApi";
import { ErrorBox, Loading } from "@/components/State";
import SyncPanel from "@/components/SyncPanel";
import TrendChart from "@/components/TrendChart";
import ActivityList from "@/components/ActivityList";

function Tile({ label, value, unit }: { label: string; value: string; unit?: string }) {
  return (
    <div className="tile">
      <div className="label">{label}</div>
      <div className="value">
        {value}
        {unit && value !== DASH ? <span className="unit">{unit}</span> : null}
      </div>
    </div>
  );
}

function sleepHours(s: number | null): string {
  return s === null ? DASH : num(s / 3600, 1);
}

export default function Dashboard() {
  const [range, setRange] = useState<14 | 30>(14);
  const to = today();
  const from = addDays(to, -(range - 1));
  const daily = useApi(`daily:${from}:${to}`, () => api.daily(from, to));
  const acts = useApi("activities:recent", () => api.activities({ limit: 5 }));

  const refresh = () => {
    daily.reload();
    acts.reload();
  };

  const rows: DailyMetrics[] = daily.data ?? [];
  const todayRow = rows.find((r) => r.date === to);
  const latest = todayRow ?? rows[rows.length - 1];
  const chartData = rows.map((r) => ({
    date: r.date,
    steps: r.steps,
    resting_hr: r.resting_hr,
    sleep_h: r.sleep_seconds === null ? null : r.sleep_seconds / 3600,
    hrv_ms: r.hrv_ms,
    bb_high: r.body_battery_high,
    bb_low: r.body_battery_low,
  }));

  return (
    <div className="stack">
      <div className="row between">
        <h1 style={{ margin: 0 }}>Dashboard</h1>
        <div className="seg" role="group" aria-label="Zeitraum">
          {([14, 30] as const).map((d) => (
            <button key={d} className={range === d ? "active" : ""} onClick={() => setRange(d)}>
              {d} Tage
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <SyncPanel days={Math.max(range, 14)} onDone={refresh} />
      </div>

      {daily.loading ? (
        <Loading text="Tagesdaten werden geladen…" />
      ) : daily.error ? (
        <ErrorBox message={daily.error} onRetry={daily.reload} />
      ) : (
        <>
          <section>
            <h2>
              {latest ? (latest.date === to ? "Heute" : `Zuletzt: ${longDate(latest.date)}`) : "Heute"}
            </h2>
            {latest ? (
              <div className="grid-tiles">
                <Tile label="Schritte" value={num(latest.steps)} />
                <Tile label="Ruhepuls" value={num(latest.resting_hr)} unit="bpm" />
                <Tile label="Schlaf" value={sleepHours(latest.sleep_seconds)} unit="h" />
                <Tile label="HRV" value={num(latest.hrv_ms)} unit="ms" />
                <Tile
                  label="Body Battery"
                  value={
                    latest.body_battery_high === null && latest.body_battery_low === null
                      ? DASH
                      : `${num(latest.body_battery_low)}–${num(latest.body_battery_high)}`
                  }
                />
                <Tile label="Stress" value={num(latest.stress_avg)} />
              </div>
            ) : (
              <div className="card muted">
                Noch keine Tagesdaten vorhanden. Starte oben eine Synchronisierung.
              </div>
            )}
          </section>

          <section>
            <h2>Trends (letzte {range} Tage)</h2>
            <div className="grid-charts">
              <TrendChart title="Schritte" data={chartData} series={[{ key: "steps", name: "Schritte", color: "var(--c1)" }]} />
              <TrendChart title="Ruhepuls" unit="bpm" data={chartData} series={[{ key: "resting_hr", name: "Ruhepuls", color: "var(--c5)" }]} />
              <TrendChart title="Schlafdauer (h)" unit="h" digits={1} data={chartData} series={[{ key: "sleep_h", name: "Schlaf", color: "var(--c3)" }]} />
              <TrendChart title="HRV" unit="ms" data={chartData} series={[{ key: "hrv_ms", name: "HRV", color: "var(--c4)" }]} />
              <TrendChart
                title="Body Battery"
                data={chartData}
                series={[
                  { key: "bb_high", name: "Max", color: "var(--c4)" },
                  { key: "bb_low", name: "Min", color: "var(--c2)" },
                ]}
              />
            </div>
          </section>
        </>
      )}

      <section className="card">
        <div className="row between">
          <h2>Letzte Aktivitäten</h2>
          <Link href="/activities">Alle anzeigen</Link>
        </div>
        {acts.loading ? (
          <Loading />
        ) : acts.error ? (
          <ErrorBox message={acts.error} onRetry={acts.reload} />
        ) : (
          <ActivityList items={acts.data ?? []} />
        )}
      </section>
    </div>
  );
}
