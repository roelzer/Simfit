"use client";

import { useCallback, useEffect, useState } from "react";
import { errorMessage } from "./api";

interface Settled<T> {
  key: string;
  data?: T;
  error?: string;
}

export interface ApiState<T> {
  data: T | undefined;
  error: string | undefined;
  loading: boolean;
  reload: () => void;
}

/**
 * Lädt Daten, sobald sich `key` ändert. `fn` sollte nur von `key` abhängen.
 */
export function useApi<T>(key: string, fn: () => Promise<T>): ApiState<T> {
  const [nonce, setNonce] = useState(0);
  const [settled, setSettled] = useState<Settled<T> | null>(null);
  const fullKey = `${key}#${nonce}`;

  useEffect(() => {
    let cancelled = false;
    fn().then(
      (data) => {
        if (!cancelled) setSettled({ key: fullKey, data });
      },
      (e) => {
        if (!cancelled) setSettled({ key: fullKey, error: errorMessage(e) });
      },
    );
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fullKey]);

  const reload = useCallback(() => setNonce((n) => n + 1), []);
  const current = settled && settled.key === fullKey ? settled : null;
  return { data: current?.data, error: current?.error, loading: current === null, reload };
}
