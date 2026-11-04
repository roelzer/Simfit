# Simfit Frontend

Next.js (App Router) + TypeScript, Recharts, eigenes CSS. UI auf Deutsch, Dark/Light per `prefers-color-scheme`.

## Start

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # Produktions-Build
npm run lint
```

Backend-URL über `NEXT_PUBLIC_API_URL` (Default `http://localhost:8000`, siehe `.env.example`).
API-Vertrag: `../docs/API.md`; der typisierte Client liegt in `src/lib/api.ts`.

## Seiten

- `/` Dashboard (Sync, Tageskacheln, Trends 14/30 Tage, letzte Aktivitäten)
- `/activities`, `/activities/[id]`
- `/nutrition` Tagesansicht, Lebensmittelsuche, eigene Lebensmittel, Ziel
- `/training` Platzhalter
