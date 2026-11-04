"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { activityType, dateTime, duration, km, num, pace } from "@/lib/format";
import { useApi } from "@/lib/useApi";
import { ErrorBox, Loading } from "@/components/State";

function Kv({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  );
}

export default function ActivityDetail() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const act = useApi(`activity:${id}`, () => api.activity(id));
  const a = act.data;

  return (
    <div className="stack">
      <Link href="/activities">← Alle Aktivitäten</Link>
      {act.loading ? (
        <Loading />
      ) : act.error ? (
        <ErrorBox message={act.error} onRetry={act.reload} />
      ) : a ? (
        <>
          <div>
            <h1 style={{ marginBottom: 4 }}>{a.name || activityType(a.type)}</h1>
            <div className="muted">
              {activityType(a.type)} · {dateTime(a.start_time)}
            </div>
          </div>
          <div className="card kv">
            <Kv label="Dauer" value={duration(a.duration_s)} />
            <Kv label="Distanz" value={km(a.distance_m)} />
            <Kv label="Ø Pace" value={pace(a.avg_pace_s_per_km)} />
            <Kv label="Ø Puls" value={a.avg_hr === null ? "–" : `${num(a.avg_hr)} bpm`} />
            <Kv label="Max. Puls" value={a.max_hr === null ? "–" : `${num(a.max_hr)} bpm`} />
            <Kv label="Kalorien" value={a.calories === null ? "–" : `${num(a.calories)} kcal`} />
            <Kv label="Höhenmeter" value={a.elevation_gain_m === null ? "–" : `${num(a.elevation_gain_m)} m`} />
          </div>
        </>
      ) : null}
    </div>
  );
}
