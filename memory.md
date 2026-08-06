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

## Phase 5 — Cryptography Module: COMPLETE
- AES-256-GCM: whole-data + chunked streaming (1 MiB chunks, nonce+len framed)
- RSA-2048 OAEP-SHA256 key pairs; master-key-encrypted private keys (HKDF from SECRET_KEY)
- 16 unit tests passing (`backend/tests/test_crypto.py`)

## Phase 6 — File Upload: COMPLETE
- POST /api/files/upload: sanitize filename, extension allowlist, size limit (100 MB), streaming AES encrypt
- Frontend: drag-drop + browse, per-file progress bars, success/error states, query invalidation

## Phase 7 — File Storage Management: COMPLETE
- StorageService (local disk, traversal-safe), encrypted blobs `.enc`, metadata persistence

## Phase 8 — File Listing: COMPLETE
- GET /api/files: pagination, search (ilike), sort (name/size/date, asc/desc)
- Frontend FilesPage: debounced search, sortable headers, pagination, skeleton loaders

## Phase 9 — Download & Decryption: COMPLETE
- GET /api/files/{id}/download: ownership check, RSA key recovery, AES decrypt, StreamingResponse
- Frontend: axios blob download with filename from Content-Disposition

## Phase 10 — File Management: COMPLETE
- DELETE /api/files/{id} (blob + metadata), PUT /api/files/{id}/rename
- Frontend: delete-confirm modal + rename modal
- Full lifecycle verified: upload→encrypt→list→search→download (byte-identical)→rename→delete

## Phase 11 — User Profile: COMPLETE
- PUT /api/users/profile (name update), POST /api/users/change-password (verify current, enforce different)
- Frontend ProfilePage: edit name, change password form, toasts, AuthContext.updateUser
- Verified: wrong-current → 401, same password → 422, valid change → login works with new password

## Phase 12 — Security Hardening: COMPLETE
- Security headers: X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy, CSP, HSTS (HTTPS only)
- Rate limiting: per-IP sliding window, 10/min auth endpoints (login/register/change-password), 120/min general, 429 + Retry-After
- Audit logging middleware: method/path/status/duration/user_id/client per request
- Verified: headers present, 10 allowed then 429 with envelope

## Phase 13 — Error Handling: COMPLETE
- Frontend ErrorBoundary (class component, reset/reload actions) wrapping the whole app
- 404 NotFoundPage within protected layout (unknown paths show styled 404, not silent redirect)
- Existing backend envelopes already structured; catch-all handler never leaks internals

## Phase 14 — Testing: COMPLETE
- API test suite (conftest with isolated in-memory DB + temp storage + rate-limit reset)
- 17 API tests: health, auth (register/login/dup-409/wrong-pass/me), profile (update, change-password + relogin), files (upload/encrypt-on-disk/blocked-ext/empty/list/search/rename/delete/download roundtrip/ownership-403), security (headers, rate-limit 429)
- Coverage 92%; 33 tests passing (16 crypto + 17 API)

## Phase 15 — Performance: COMPLETE
- GZip middleware (>=1 KB) on API responses
- Efficient SQL count (func.count) instead of loading all rows for pagination
- Composite index (user_id, uploaded_at) via Alembic migration a8f9845cc844 — applied
- Frontend route code-splitting (React.lazy + Suspense): main bundle 360 KB → 306 KB, per-page chunks
- All 33 tests still passing after migration + count change

## Next: Phase 16 — Deployment