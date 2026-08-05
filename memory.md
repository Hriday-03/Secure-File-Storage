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

## Phase 2 — Database Design: COMPLETE
- SQLAlchemy 2.0 + UUID (native PG / CHAR(32) SQLite)
- `users` (name, email, password_hash, public_key, encrypted_private_key, is_active, timestamps)
- `files` (original_name, stored_name, encrypted_key, algorithm, size, mime_type, timestamps)
- Alembic wired to app settings; migrations `2e3060ed59f1` + `a39bc03b736b` applied
- Dev DB: SQLite (`secure_storage.db`); PostgreSQL-ready via DATABASE_URL

## Phase 3 — Authentication System: COMPLETE
- bcrypt hashing (direct `bcrypt` lib; passlib 1.7.4 is incompatible with bcrypt 4.x)
- JWT access tokens (python-jose, HS256, 30 min expiry)
- Registration generates RSA-2048 keypair; private key encrypted at rest with master key (HKDF from SECRET_KEY) — AES-256-GCM
- Endpoints: POST /api/auth/register|login|logout, GET /api/auth/me — all verified via API
- Frontend: Login/Register pages, AuthContext (useReducer), ProtectedRoute, axios interceptors, localStorage session persistence

## Phase 4 — User Dashboard: COMPLETE
- GET /api/users/profile, GET /api/dashboard/stats (verified)
- AppLayout (Navbar + Sidebar), UserMenu, responsive (mobile drawer)
- Dashboard: welcome, 4 stat cards, empty state
- Placeholder pages: Upload, My Files, Recent, Profile

## Next: Phase 5 — Cryptography Module