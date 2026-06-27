# MultiShield AI Dashboard

This is a React + TypeScript dashboard for MultiShield AI.

Quick start:

```bash
cd frontend
npm install
npm run dev
```

The app expects the backend at `http://localhost:8000` by default. To override, set `VITE_API_BASE_URL` in your environment or `.env`.
# MultiShield AI Dashboard

React + TypeScript dashboard for analyzing text and image content with MultiShield AI.

## Structure

- `src/pages/` dashboard views
- `src/components/` reusable UI blocks
- `src/api/` Axios client and API types
- `src/context/` shared theme and analysis state
- `src/theme.ts` application theme and dark mode palette

## Run

1. Copy `.env.example` to `.env`.
2. Install dependencies.
3. Start the backend at `http://localhost:8000`.
4. Run `npm run dev`.

## Build

```bash
npm run build
```

## Deployment

The included Dockerfile builds the app and serves it through Nginx.
