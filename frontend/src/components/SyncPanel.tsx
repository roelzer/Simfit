"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api, errorMessage, type SyncRun } from "@/lib/api";
import { dateTime } from "@/lib/format";

export default function SyncPanel({ days, onDone }: { days: number; onDone: () => void }) {
  const [run, setRun] = useState<SyncRun | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const onDoneRef = useRef(onDone);
  useEffect(() => {
    onDoneRef.current = onDone;
  }, [onDone]);

  useEffect(() => {
    let cancelled = false;
    api.syncStatus().then(
      (r) => {
        if (cancelled) return;
        setRun(r);
        setLoaded(true);
      },
      (e) => {
        if (cancelled) return;
        setError(errorMessage(e));
        setLoaded(true);
      },
    );
    return () => {
      cancelled = true;
    };
  }, []);

  const running = run?.status === "running";

  // Während ein Lauf aktiv ist, regelmäßig den Status abfragen.
  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => {
      api.syncStatus().then(
        (r) => {
          setRun(r);
          if (r && r.status !== "running") onDoneRef.current();
        },
        (e) => setError(errorMessage(e)),
      );
    }, 2000);
    return () => clearInterval(t);
  }, [running]);

  const start = useCallback(async () => {
    setStarting(true);
    setError(null);
    try {
      const r = await api.startSync(days);
      setRun(r);
      if (r.status !== "running") onDoneRef.current();
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setStarting(false);
    }
  }, [days]);

  return (
    <div className="row" aria-live="polite">
      <button className="primary" onClick={start} disabled={starting || running}>
        {starting || running ? (
          <>
            <span className="spinner" aria-hidden="true" />
            Synchronisiere…
          </>
        ) : (
          "Jetzt synchronisieren"
        )}
      </button>
      <span className="muted">
        {error ? (
          <span style={{ color: "var(--danger)" }}>{error}</span>
        ) : !loaded ? (
          "Status wird geladen…"
        ) : run ? (
          <>
            <span className={`badge ${run.status === "ok" ? "ok" : run.status === "error" ? "error" : ""}`}>
              {run.status === "ok" ? "Erfolgreich" : run.status === "error" ? "Fehler" : "Läuft"}
            </span>{" "}
            {run.finished_at ? dateTime(run.finished_at) : dateTime(run.started_at)}
            {run.source ? ` · Quelle: ${run.source}` : ""}
            {run.message ? ` · ${run.message}` : ""}
          </>
        ) : (
          "Noch nie synchronisiert"
        )}
      </span>
    </div>
  );
}
