# MPLADS AI Audit — Deployment

## Architecture

- Frontend: Vercel (Vite/React), root directory `frontend`
- Backend: Render (FastAPI), repository root
- Frontend environment variable:
  `VITE_API_URL=https://YOUR-RENDER-SERVICE.onrender.com`

## Render

Build:
```bash
pip install -r requirements.txt
```

Start:
```bash
uvicorn backend.api:app --host 0.0.0.0 --port $PORT
```

Health check:
```text
/api/meta
```

## Vercel

Root Directory: `frontend`

Build Command:
```bash
npm run build
```

Output Directory:
```text
dist
```

Environment Variable:
```text
VITE_API_URL=https://YOUR-RENDER-SERVICE.onrender.com
```

After changing `VITE_API_URL`, redeploy the frontend.

## Important

The backend reads these files at runtime:
- `outputs/anomaly_results.csv`
- `data/processed/expenditures.csv`
- `data/processed/mp_allocation.csv`
- `data/processed/works_master.csv` when available

Keep those files in the deployed backend repository.

The backend already enables CORS for the frontend.
