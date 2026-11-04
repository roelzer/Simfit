"use client";

import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { shortDate } from "@/lib/format";

export interface Series {
  key: string;
  name: string;
  color: string;
}

type Row = { date: string } & Record<string, number | string | null>;

export default function TrendChart({
  title,
  data,
  series,
  unit = "",
  digits = 0,
}: {
  title: string;
  data: Row[];
  series: Series[];
  unit?: string;
  digits?: number;
}) {
  const hasData = data.some((r) => series.some((s) => typeof r[s.key] === "number"));
  return (
    <div className="card">
      <h3>{title}</h3>
      <div className="chart-box" role="img" aria-label={`Verlauf ${title}`}>
        {hasData ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 12, right: 8, bottom: 0, left: -12 }}>
              <CartesianGrid stroke="var(--grid)" strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={shortDate}
                tick={{ fill: "var(--muted)", fontSize: 11 }}
                stroke="var(--border)"
                minTickGap={24}
              />
              <YAxis
                tick={{ fill: "var(--muted)", fontSize: 11 }}
                stroke="var(--border)"
                domain={["auto", "auto"]}
                width={48}
              />
              <Tooltip
                contentStyle={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: 8 }}
                labelStyle={{ color: "var(--text)" }}
                labelFormatter={(l) => shortDate(String(l))}
                formatter={(v) =>
                  typeof v === "number"
                    ? `${v.toLocaleString("de-DE", { maximumFractionDigits: digits })}${unit ? " " + unit : ""}`
                    : "–"
                }
              />
              {series.length > 1 && <Legend wrapperStyle={{ fontSize: 12 }} />}
              {series.map((s) => (
                <Line
                  key={s.key}
                  type="monotone"
                  dataKey={s.key}
                  name={s.name}
                  stroke={s.color}
                  strokeWidth={2}
                  dot={false}
                  connectNulls={false}
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="state">Keine Daten im Zeitraum</div>
        )}
      </div>
    </div>
  );
}
