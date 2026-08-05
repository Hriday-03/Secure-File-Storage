# Project Memory

Progress tracker for the Secure File Storage System development.

## Phase 1 — Project Setup: COMPLETE

### Backend (`backend/`)
- FastAPI project created; entry point `app/main.py`
- `app/core/config.py` — pydantic-settings based config loaded from `.env`
- `app/core/logging.py` — loguru structured logging (console + `logs/`)
- CORS configured for `http://localhost:5173`
- Health endpoint: `GET /api/health`
- Folder skeleton: `app/{api,core,crypto,database,schemas,services,utils}`, `storage/encrypted_files/`
- `backend/requirements.txt` — dependencies installed into repo-root `venv/`
- `.env` / `.env.example` created
- Verified: `GET /api/health` returns `{"status":"ok"}`

### Frontend (`frontend/`)
- Vite + React + TypeScript scaffold
- Tailwind CSS v4 via `@tailwindcss/vite`; Inter font; dark theme default
- React Router v8 (`react-router@8.3.0`), Axios, TanStack Query v5
- ESLint flat config + Prettier (`npm run lint`, `npm run format`)
- Vite dev server pinned to `127.0.0.1:5173`, proxies `/api` → `http://127.0.0.1:8000`
- Folder skeleton: `src/{assets,components,pages,services,context,hooks,styles,types,utils}`
- Single root `.gitignore` consolidated
- Verified: dev server HTTP 200; `/api/health` via proxy returns `{"status":"ok"}`
- `npm audit`: 0 vulnerabilities

### Notes
- Local Python in venv is 3.11.9 (docs recommend 3.12+; works fine)
- `SECRET_KEY` in `.env` is a dev placeholder — must be changed for production

## Next: Phase 2 — Database Design
In progress when present.