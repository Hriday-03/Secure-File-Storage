# 🔐 Secure File Storage System

A secure, modern, full-stack web application for storing encrypted files using industry-standard cryptography. Files are encrypted with **AES-256-GCM** before storage, while **RSA-2048/4096** is used for secure key management. Only authenticated users can access and decrypt their own files.

---

## ✨ Features

### Authentication
- User Registration
- User Login
- JWT Authentication
- Password Hashing (bcrypt/Argon2)
- Protected Routes
- Session Management

### Secure File Storage
- Secure File Upload
- AES-256-GCM File Encryption
- RSA Key Encryption
- Secure File Download
- Delete Files
- Search Files
- Pagination
- File Metadata Management

### Security
- JWT Authentication
- Password Hashing
- File Ownership Verification
- HTTPS Ready
- SQL Injection Protection
- XSS Protection
- Input Validation
- Secure File Handling

### User Interface
- Modern Dashboard
- Drag & Drop Upload
- Responsive Design
- Dark / Light Theme
- Toast Notifications
- Upload Progress
- Search & Filter
- File Management

---

# 🏗 Architecture

```
React (Frontend)
        │
        │ HTTPS + JWT
        ▼
FastAPI Backend
        │
 ┌──────┴─────────┐
 │                │
 ▼                ▼
PostgreSQL   Encrypted Storage
               (Disk / S3)
```

---

# 🛠 Tech Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios
- TanStack Query

## Backend

- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Uvicorn

## Database

- PostgreSQL
- SQLite (Development)

## Cryptography

- cryptography
- bcrypt
- python-jose

---

# 📁 Project Structure

```
secure-file-storage/
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── docs/
│   ├── PRD.md
│   ├── Architecture.md
│   ├── Design.md
│   ├── Rules.md
│   └── Phases.md
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# 🚀 Getting Started

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/secure-file-storage.git

cd secure-file-storage
```

---

## 2. Backend Setup

Create a virtual environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
DATABASE_URL=postgresql://user:password@localhost/secure_storage

SECRET_KEY=your-secret-key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

RSA_KEY_SIZE=2048

STORAGE_PATH=storage/encrypted_files
```

Run migrations

```bash
alembic upgrade head
```

Run backend

```bash
uvicorn app.main:app --reload
```

Backend URL

```
http://localhost:8000
```

Swagger Documentation

```
http://localhost:8000/docs
```

---

## 3. Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend

```
http://localhost:5173
```

---

# 🐳 Docker Deployment

Build and run both services with Compose (frontend on `http://localhost:8080`, backend on port 8000 inside the network):

```bash
docker compose up --build
```

- Backend image runs `alembic upgrade head` before starting uvicorn.
- Encrypted blobs, SQLite database, and logs persist in the `storage_data` volume.
- Nginx serves the built frontend, proxies `/api` to the backend, and limits uploads to 100 MB.
- Set `SECRET_KEY` (and a real `DATABASE_URL` if using PostgreSQL) in `backend/.env` before deploying.

---

# 🔒 Encryption Workflow

```
User Upload
      │
      ▼
Generate AES Key
      │
      ▼
Encrypt File (AES-256-GCM)
      │
      ▼
Encrypt AES Key (RSA)
      │
      ▼
Store Encrypted File
      │
      ▼
Save Metadata
```

Download

```
Retrieve File
      │
      ▼
Decrypt AES Key
      │
      ▼
Decrypt File
      │
      ▼
Return Original File
```

---

# 📚 API Endpoints

## Authentication

```
POST   /api/auth/register

POST   /api/auth/login

POST   /api/auth/logout

GET    /api/auth/me
```

## Files

```
POST   /api/files/upload

GET    /api/files

GET    /api/files/{id}

GET    /api/files/{id}/download

DELETE /api/files/{id}

PUT    /api/files/{id}/rename
```

## User

```
GET    /api/users/profile

PUT    /api/users/profile

POST   /api/users/change-password
```

## Dashboard

```
GET    /api/dashboard/stats
```

---

Full request/response contracts, error codes, and hardening details are in **[API.md](API.md)**.

---

# 🔐 Security Features

- AES-256-GCM Encryption (chunked streaming, 1 MiB chunks)
- RSA-2048 key pairs with OAEP-SHA-256
- Private keys encrypted at rest (HKDF master key from SECRET_KEY)
- bcrypt password hashing
- JWT Authentication (30 min expiry)
- File Ownership Verification
- Rate Limiting (auth 10/min, general 120/min)
- Security Headers (CSP, X-Frame-Options, nosniff, etc.)
- Filename Sanitization + path traversal protection
- Input Validation
- SQL Injection Protection (ORM)
- Error envelope that never leaks internals
- CORS pinned to configured origins

---

# 🧪 Testing

Run backend tests

```bash
cd backend
python -m pytest
```

Run with coverage

```bash
python -m pytest --cov=app
```

Current suite: 33 tests (16 crypto unit tests + 17 API integration tests), ~92% coverage.

---

# 📖 Documentation

- **[API.md](API.md)** — endpoint contracts, error codes, security details
- **[prd.md](prd.md)** — product requirements
- **[Architecture.md](Architecture.md)** — system architecture
- **[design.md](design.md)** — design decisions
- **[rules.md](rules.md)** — coding standards
- **[phases.md](phases.md)** — development phases
- **[memory.md](memory.md)** — build progress tracker

---

# 🚀 Future Features

- Two-Factor Authentication (2FA)
- Secure File Sharing
- Folder Management
- Version History
- Audit Logs
- Storage Analytics
- AWS S3 Integration
- Azure Blob Storage
- Malware Scanning
- File Expiration
- Activity Timeline
- Admin Dashboard

---

# 🤝 Contributing

1. Fork the repository.
2. Create a feature branch.
3. Follow the coding standards in `Rules.md`.
4. Write tests for new functionality.
5. Submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

Secure File Storage System

Built with ❤️ using FastAPI, React, and modern cryptography.