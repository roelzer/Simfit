"use client";

import { api } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { ErrorBox, Loading } from "@/components/State";
import ActivityList from "@/components/ActivityList";

export default function ActivitiesPage() {
  const acts = useApi("activities:list", () => api.activities({ limit: 50 }));
  return (
    <div className="stack">
      <h1>Aktivitäten</h1>
      <div className="card">
        {acts.loading ? (
          <Loading />
        ) : acts.error ? (
          <ErrorBox message={acts.error} onRetry={acts.reload} />
        ) : (
          <ActivityList items={acts.data ?? []} />
        )}
      </div>
    </div>
  );
}
