<div align="center">

# 🔐 Secure File Storage System
### Encrypted file storage where only you hold the keys

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=22&duration=3000&pause=1000&color=00D4FF&center=true&vCenter=true&width=700&lines=AES-256-GCM+File+Encryption;RSA-2048+Key+Management;Zero-Plaintext+Storage;JWT-Secured+REST+API" alt="Typing SVG" />

---

**Secure File Storage** is a full-stack web app for storing files no one else can read — not even the server operator. Every file gets its own random AES-256-GCM key, the key is sealed to your RSA public key, and only ciphertext ever touches the disk.

[Quick Start](#-quick-start) • [App Tour](#-app-tour) • [How It Works](#-how-it-works) • [Architecture](#-architecture) • [API Reference](API.md)

</div>

---

## ⚡ Quick Start

> [!NOTE]
> The default config uses SQLite and the local frontend origin, so the app runs out of the box — no database server needed. (Linux/macOS: swap `copy` → `cp` and `venv\Scripts\activate` → `source venv/bin/activate`.)

```powershell
# 1. Clone and enter the project
git clone https://github.com/Hriday-03/Secure-File-Storage.git
cd Secure-File-Storage

# 2. Backend — terminal 1
python -m venv venv
venv\Scripts\activate
cd backend
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
# → API at http://localhost:8000  (interactive docs at /docs)

# 3. Frontend — new terminal, from the repo root
cd frontend
npm install
npm run dev
# → App at http://localhost:5173
```

> [!TIP]
> Register a fresh account in the app, or sign in with the dev account `test@example.com` / `securepass123`.

---

## 🖱️ App Tour

Follow a file through the app in four steps:

### Step 1 — Create your account
Register with a name, email, and password. The server generates your personal **RSA-2048 keypair**, encrypts the private key with a master key, and hands you a **JWT** valid for 30 minutes. No email verification, no friction.

### Step 2 — Meet your dashboard
![Dashboard](Images/dashboard.png)
Total files, encrypted storage used, last upload, and the active cipher — one glance tells you the state of your vault.

### Step 3 — Upload files
![Upload](Images/upload.png)
Drag & drop (or browse) with live per-file progress. Each upload gets a **fresh random AES-256 key**, is encrypted in 1 MiB chunks, and executables (`.exe`, `.bat`, `.sh`, `.js`, …) plus files over 100 MB are rejected before touching storage.

### Step 4 — Manage and download
![My Files](Images/files.png)
Search by filename, sort by name/size/date, page through results, rename, delete — or download, which streams the file back decrypted byte-for-byte.

---

## 🔍 Key Capabilities

<div align="center">

| Feature | Description | Icon |
| :--- | :--- | :---: |
| **Per-File Encryption** | Fresh random AES-256-GCM key for every upload, chunked 1 MiB streaming. | 🔐 |
| **RSA Key Management** | RSA-2048 OAEP-SHA-256 seals each file key; private keys encrypted at rest (HKDF). | 🔑 |
| **JWT Authentication** | 30-minute tokens, bcrypt-hashed passwords (72-byte limit enforced). | 🎫 |
| **Upload Guardrails** | Extension allowlist + executable blocklist, empty-file and 100 MB size checks. | 🛡️ |
| **Search, Sort, Paginate** | Case-insensitive filename search with name/size/date sorting. | 🔍 |
| **Streaming Downloads** | Decrypt-on-the-fly delivery — constant memory even for large files. | 📥 |
| **Profile Management** | Update display name, change password with current-password verification. | 👤 |
| **Rate Limiting** | 10/min on auth endpoints, 120/min elsewhere, with `Retry-After`. | 🚦 |
| **Audit Logging** | Every request logged with method, path, status, duration, and user. | 📋 |
| **Resilient UI** | Error boundary, 404 page, toasts, and code-split routes. | ✨ |

</div>

---

## ⚙️ How It Works

Each file passes through four cryptographic stages:

<div align="center">

| Stage | Operation | Detail |
| :--- | :--- | :--- |
| **1. Encrypt** | `AES-256-GCM` | Fresh 256-bit key per file; 1 MiB chunks framed as `[len ‖ nonce ‖ ct+tag]` |
| **2. Wrap key** | `RSA-2048 OAEP-SHA-256` | File key sealed to the owner's public key (32 bytes — well under the 190 B limit) |
| **3. Store** | `Ciphertext only` | `.enc` blob on disk + metadata in DB; stored names and sealed keys never exposed via API |
| **4. Decrypt** | `Streamed` | Private key recovered → AES key unwrapped → bytes decrypted chunk-by-chunk on download |

</div>

---

## 🏗️ Architecture

```mermaid
graph TD
    U[React 19 + Tailwind<br/>localhost:5173] -->|JWT in Authorization header| A[FastAPI<br/>localhost:8000]

    subgraph Backend
    A --> AU[Auth: bcrypt + JWT 30min]
    A --> CR[Crypto: AES-256-GCM + RSA-2048 OAEP]
    A --> MW[Rate limit + audit log + security headers]
    end

    A --> DB[(SQLite dev / PostgreSQL prod)]
    A --> ST[Encrypted .enc blobs on disk]

    style U fill:#0ea5e9,stroke:#333,stroke-width:2px,color:#000
    style A fill:#009688,stroke:#333,stroke-width:2px,color:#fff
    style ST fill:#16a34a,stroke:#333,stroke-width:2px,color:#fff
```

---

## 📊 File Lifecycle

```
1. REGISTER        → RSA-2048 keypair generated, private key HKDF-encrypted at rest
2. LOGIN           → bcrypt verified, JWT issued (30 min)
3. UPLOAD          → Sanitized + validated → fresh AES key → chunked GCM encrypt → RSA-wrapped key
4. LIST            → Paginated search/sort over metadata (composite index on user + date)
5. DOWNLOAD        → Ownership check → unwrap key → streamed decrypt, byte-identical return
6. RENAME / DELETE → Metadata update, or blob + record removal
```

---

## 🧰 Tech Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2, Alembic, Pydantic, Uvicorn
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, React Router, Axios, TanStack Query
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Cryptography:** `cryptography` (AES-GCM, RSA-OAEP), `bcrypt`, `python-jose` (JWT)
- **Testing:** pytest — 33 tests (16 crypto + 17 API), 92% coverage
- **Deploy:** Docker + Compose, nginx (SPA + `/api` reverse proxy)

---

## 📁 Repository Overview

```ascii
Secure-File-Storage/
├── backend/
│   ├── app/              # api · core · crypto · database · middleware · services
│   ├── migrations/       # Alembic revisions (schema + RSA keys + file index)
│   ├── tests/            # conftest + test_crypto + test_api
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/              # pages · components · services · context
│   ├── nginx.conf        # prod reverse proxy (/api → backend)
│   └── package.json
├── Images/               # screenshots used in this README
├── docker-compose.yml    # backend + frontend + shared volume
├── API.md                # full endpoint + error-code reference
└── README.md             # this file
```

---

## 🐳 Docker Deployment

```powershell
# Build and run both services (frontend → http://localhost:8080)
docker compose up --build
```

> [!WARNING]
> - Set a strong `SECRET_KEY` in `backend/.env` before deploying — the default is a placeholder.
> - Point `DATABASE_URL` at PostgreSQL for production; SQLite lives in the shared volume.
> - If you serve the frontend from a non-localhost origin, add it to `CORS_ORIGINS`.

---

## 🚨 Important Notes

> [!CAUTION]
> - **Back up `SECRET_KEY`.** Private keys are encrypted with a master key derived from it — rotating or losing it makes every stored file permanently unreadable.
> - **Never commit `backend/.env`** — it holds `SECRET_KEY` (already gitignored).

> [!NOTE]
> - Uploads are capped at 100 MB (`MAX_UPLOAD_SIZE_MB`); executables and scripts are blocked by extension.
> - Auth endpoints are rate-limited to 10 requests/min per IP — hammering login in tests will return `429`.

---

## 🧪 Testing

```powershell
cd backend
python -m pytest            # 33 tests
python -m pytest --cov=app  # coverage report (~92%)
```

---

<div align="center">

**Your files. Your keys. Nobody else's business.**

*Built with FastAPI, React, and modern cryptography — all 17 build phases complete.*

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![33 Tests Passing](https://img.shields.io/badge/Tests-33_passing-brightgreen?style=for-the-badge)](backend/tests)

</div>
