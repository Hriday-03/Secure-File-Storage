# Architecture Document

# Secure File Storage System

Version: 1.0

---

# 1. System Overview

The Secure File Storage System is a full-stack web application that allows authenticated users to securely upload, store, and download encrypted files. The system encrypts every uploaded file using AES-256 before storing it, while RSA is used to securely encrypt the AES encryption key for each file.

The application follows a modular client-server architecture with clear separation between presentation, business logic, cryptographic services, storage, and database layers.

---

# 2. High-Level Architecture

```
                   +----------------------+
                   |      Web Browser     |
                   |   React Frontend     |
                   +----------+-----------+
                              |
                              |
                         HTTPS + JWT
                              |
                              ▼
               +-----------------------------+
               |      FastAPI Backend        |
               |-----------------------------|
               | Authentication Service      |
               | File Upload Service         |
               | Encryption Service          |
               | File Management Service     |
               | Download Service            |
               +--------------+--------------+
                              |
             +----------------+----------------+
             |                                 |
             ▼                                 ▼
    PostgreSQL Database               Encrypted File Storage
         (Metadata)                  (Local / AWS S3 / Azure)
```

---

# 3. Application Flow

## User Registration

```
User
   │
   ▼
Registration Form
   │
   ▼
Validate Input
   │
   ▼
Hash Password (bcrypt)
   │
   ▼
Store User
   │
   ▼
Registration Success
```

---

## User Login

```
User
   │
   ▼
Login Form
   │
   ▼
Validate Credentials
   │
   ▼
Verify Password Hash
   │
   ▼
Generate JWT Token
   │
   ▼
Authenticated Session
```

---

## File Upload Flow

```
User
   │
   ▼
Select File
   │
   ▼
Upload API
   │
   ▼
Validate File
   │
   ▼
Generate Random AES Key
   │
   ▼
Encrypt File (AES-256)
   │
   ▼
Encrypt AES Key (RSA)
   │
   ▼
Store Encrypted File
   │
   ▼
Save Metadata
   │
   ▼
Return Success
```

---

## File Download Flow

```
User
   │
   ▼
Request File
   │
   ▼
Verify JWT
   │
   ▼
Verify Ownership
   │
   ▼
Retrieve Encrypted File
   │
   ▼
Decrypt AES Key (RSA)
   │
   ▼
Decrypt File (AES)
   │
   ▼
Return Original File
```

---

## File Delete Flow

```
User
   │
   ▼
Delete Request
   │
   ▼
Verify Ownership
   │
   ▼
Delete Metadata
   │
   ▼
Delete Stored File
   │
   ▼
Success
```

---

# 4. Encryption Workflow

```
                Original File
                      │
                      ▼
          Generate Random AES Key
                      │
                      ▼
          Encrypt File using AES-256
                      │
                      ▼
         Encrypt AES Key using RSA
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
Encrypted File            Encrypted AES Key
          │                       │
          └───────────┬───────────┘
                      ▼
                 Database Metadata
```

---

# 5. Folder Structure

```
secure-file-storage/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── files.py
│   │   │   └── users.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── jwt_handler.py
│   │   │
│   │   ├── crypto/
│   │   │   ├── aes.py
│   │   │   ├── rsa.py
│   │   │   └── key_manager.py
│   │   │
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── migrations/
│   │   │
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── encryption_service.py
│   │   │   ├── file_service.py
│   │   │   └── storage_service.py
│   │   │
│   │   ├── storage/
│   │   │   └── encrypted_files/
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── file.py
│   │   │   └── user.py
│   │   │
│   │   ├── utils/
│   │   │   ├── validators.py
│   │   │   └── logger.py
│   │   │
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   │
│   ├── public/
│   │
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── Navbar/
│   │   │   ├── Sidebar/
│   │   │   ├── FileCard/
│   │   │   ├── UploadModal/
│   │   │   └── ProtectedRoute/
│   │   │
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Upload.jsx
│   │   │   └── Profile.jsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── auth.js
│   │   │   └── file.js
│   │   │
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   │
│   │   ├── hooks/
│   │   │
│   │   ├── styles/
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   ├── PRD.md
│   ├── Architecture.md
│   └── API.md
│
├── README.md
├── docker-compose.yml
└── .gitignore
```

---

# 6. Backend Architecture

The backend is divided into independent modules.

### API Layer
Responsible for handling HTTP requests.

- Authentication APIs
- File APIs
- User APIs

---

### Service Layer

Contains business logic.

Examples:

- Authenticate users
- Encrypt files
- Store metadata
- Verify permissions

---

### Cryptography Layer

Responsible for all encryption operations.

Modules:

- AES Encryption
- RSA Encryption
- Key Generation
- Key Management

---

### Database Layer

Responsible for:

- User records
- File metadata
- Encryption metadata
- Audit logs (future)

---

### Storage Layer

Stores encrypted files only.

Possible storage options:

- Local filesystem
- AWS S3
- Azure Blob Storage
- Google Cloud Storage

---

# 7. Frontend Architecture

The frontend follows a component-based architecture.

```
App
│
├── Authentication
│   ├── Login
│   └── Register
│
├── Dashboard
│   ├── File List
│   ├── Upload Button
│   ├── Search Bar
│   └── Statistics
│
├── Upload Module
│
├── Profile
│
└── Settings
```

State management is handled using React Context API. API communication is encapsulated in dedicated service modules.

---

# 8. Database Design

## Users Table

| Column | Type |
|---------|------|
| id | UUID |
| name | VARCHAR |
| email | VARCHAR |
| password_hash | TEXT |
| created_at | TIMESTAMP |

---

## Files Table

| Column | Type |
|---------|------|
| id | UUID |
| user_id | UUID |
| original_name | TEXT |
| stored_name | TEXT |
| encrypted_key | TEXT |
| algorithm | VARCHAR |
| size | BIGINT |
| uploaded_at | TIMESTAMP |

---

# 9. Security Architecture

Authentication:
- JWT Access Tokens
- Refresh Tokens (optional)

Password Security:
- bcrypt or Argon2 hashing
- Strong password policy

Encryption:
- AES-256-GCM for file encryption (provides confidentiality and integrity)
- RSA-2048 or RSA-4096 for encrypting AES keys

Transport Security:
- HTTPS
- TLS 1.3

Application Security:
- CSRF protection (if using cookies)
- XSS prevention
- SQL Injection protection (ORM + parameterized queries)
- File type validation
- File size limits
- Rate limiting
- Secure HTTP headers

---

# 10. Recommended Tech Stack

## Frontend

- React
- Vite
- TypeScript
- Tailwind CSS
- React Router
- Axios
- React Query (TanStack Query)

---

## Backend

- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Uvicorn

---

## Database

- PostgreSQL

Development:
- SQLite

---

## Authentication

- JWT
- bcrypt / Argon2

---

## Cryptography

- cryptography
- PyCryptodome (optional)

---

## File Storage

Development:
- Local File Storage

Production:
- AWS S3
- Azure Blob Storage

---

## DevOps

- Docker
- Docker Compose
- GitHub Actions (CI/CD)
- Nginx (reverse proxy)

---

# 11. API Endpoints

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
PUT    /api/users/change-password
```

---

# 12. Deployment Architecture

```
                Internet
                    │
                    ▼
               Nginx Reverse Proxy
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   React Frontend      FastAPI Backend
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
          PostgreSQL Database       Encrypted File Storage
                                      (Disk / S3)
```

---

# 13. Future Improvements

- End-to-end encryption with client-side encryption
- Multi-factor authentication (MFA)
- Role-Based Access Control (RBAC)
- File versioning
- Secure file sharing
- Audit logging
- Malware scanning
- Virus detection
- File integrity verification
- Key rotation
- Hardware Security Module (HSM) integration
- Kubernetes deployment
- Monitoring with Prometheus and Grafana

---

# 14. Summary

The Secure File Storage System is designed with a layered, modular architecture that separates concerns between the frontend, backend, cryptographic operations, storage, and database. AES-256-GCM provides efficient and authenticated encryption for files, while RSA secures the symmetric keys. Combined with JWT-based authentication, PostgreSQL metadata storage, and scalable object storage, the architecture is secure, maintainable, and production-ready.