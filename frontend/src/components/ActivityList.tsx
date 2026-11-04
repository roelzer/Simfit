import Link from "next/link";
import type { Activity } from "@/lib/api";
import { activityType, dateTime, duration, km, num } from "@/lib/format";
import { Empty } from "./State";

export default function ActivityList({ items }: { items: Activity[] }) {
  if (items.length === 0) return <Empty text="Keine Aktivitäten vorhanden." />;
  return (
    <ul className="list">
      {items.map((a) => (
        <li key={a.id}>
          <Link className="item" href={`/activities/${a.id}`}>
            <div>
              <strong>{a.name || activityType(a.type)}</strong>
              <div className="meta">
                {activityType(a.type)} · {dateTime(a.start_time)}
              </div>
            </div>
            <div className="right">
              <div>{km(a.distance_m)}</div>
              <div className="meta">
                {duration(a.duration_s)}
                {a.calories !== null ? ` · ${num(a.calories)} kcal` : ""}
              </div>
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}
