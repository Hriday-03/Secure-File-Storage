# OpenCode Development Rules

# Secure File Storage System

Version: 1.0

---

# Purpose

This document defines the coding standards, architectural boundaries, approved libraries, error handling practices, and implementation guidelines for the Secure File Storage System.

The goal is to ensure the project remains secure, maintainable, scalable, and production-ready.

---

# General Rules

## DO

- Write clean, readable, and modular code.
- Follow SOLID design principles.
- Use dependency injection where appropriate.
- Keep functions focused on a single responsibility.
- Write reusable components.
- Prefer composition over inheritance.
- Use environment variables for configuration.
- Validate all user inputs.
- Return consistent API responses.
- Log errors without exposing sensitive information.
- Use type hints throughout the backend.
- Keep secrets out of source code.
- Follow RESTful API conventions.
- Write self-documenting code with meaningful names.

---

## DON'T

- Do not hardcode secrets or credentials.
- Do not duplicate business logic.
- Do not place SQL queries directly inside API routes.
- Do not perform encryption logic in controllers/routes.
- Do not expose stack traces to users.
- Do not trust client-side validation alone.
- Do not store plaintext passwords.
- Do not store plaintext encryption keys.
- Do not create large monolithic classes or files.
- Do not use global mutable state.
- Do not bypass authentication checks.
- Do not disable SSL/TLS verification in production.

---

# Approved Tech Stack

## Frontend

Use only:

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios
- TanStack Query
- React Hook Form
- Zod

Avoid:

- jQuery
- Redux (unless project complexity requires it)
- Bootstrap
- Material UI (unless explicitly approved)

---

## Backend

Use only:

- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Uvicorn

Avoid:

- Flask
- Django
- Raw WSGI applications

---

## Database

Preferred:

- PostgreSQL

Development:

- SQLite

Avoid:

- MySQL
- MongoDB
- Firebase

unless specifically requested.

---

# Cryptography Rules

## Use

AES-256-GCM

for:

- File encryption
- Data integrity
- Authenticated encryption

RSA-2048 or RSA-4096

for:

- Encrypting AES keys
- Key exchange

Password hashing:

- bcrypt
- Argon2

Random values:

- Python `secrets` module
- `os.urandom()`

---

## Never Use

- MD5
- SHA1
- DES
- Triple DES
- RC4
- ECB mode
- Homemade encryption algorithms

Never implement cryptographic primitives manually.

Always use well-tested cryptographic libraries.

---

# Approved Python Libraries

Authentication

- python-jose
- passlib
- bcrypt
- argon2-cffi

Encryption

- cryptography

Database

- SQLAlchemy
- Alembic
- psycopg

Validation

- Pydantic

Utilities

- python-dotenv
- loguru

Testing

- pytest
- pytest-asyncio
- httpx

---

# Avoid These Libraries

- pycrypto (deprecated)
- pickle (for untrusted data)
- marshal
- eval
- exec

Never use libraries with known security vulnerabilities.

---

# API Design Rules

Every endpoint must:

- Validate input
- Validate authentication
- Validate authorization
- Return structured JSON
- Return appropriate HTTP status codes

Example response:

Success

```json
{
    "success": true,
    "message": "File uploaded successfully",
    "data": {}
}
```

Failure

```json
{
    "success": false,
    "message": "Unauthorized",
    "error": "AUTHENTICATION_REQUIRED"
}
```

---

# Error Handling Rules

Always

- Catch expected exceptions.
- Log unexpected exceptions.
- Return user-friendly messages.
- Use custom exception classes where appropriate.
- Include request identifiers in logs.

Never

- Return stack traces.
- Leak database errors.
- Leak filesystem paths.
- Leak encryption details.
- Leak JWT secrets.

Example

Bad

```
SQL Error:
duplicate key violates constraint
```

Good

```
Unable to create account.
Please try again.
```

---

# Logging Rules

Use structured logging.

Log:

- Authentication attempts
- Upload events
- Download events
- Delete operations
- Encryption failures
- Server errors

Never log:

- Passwords
- JWT tokens
- AES keys
- RSA private keys
- Uploaded file contents
- Sensitive personal information

---

# Authentication Rules

Must use:

- JWT Access Tokens
- Secure password hashing
- Token expiration
- Authorization middleware

Optional:

- Refresh Tokens

Never

- Store passwords
- Store plaintext tokens
- Allow anonymous file access

---

# Authorization Rules

Every file operation must verify:

- User identity
- File ownership
- User permissions

Users may never access files belonging to another user.

---

# File Upload Rules

Validate:

- Maximum size
- MIME type
- File extension
- Filename length

Reject:

- Empty files
- Executable files (if unsupported)
- Oversized uploads
- Corrupted uploads

Sanitize filenames before storage.

Never trust filenames provided by clients.

---

# Database Rules

Use:

- SQLAlchemy ORM
- Alembic migrations
- Transactions where appropriate

Never

- Build SQL using string concatenation.
- Allow SQL injection.
- Execute raw SQL unless absolutely necessary.

Always use parameterized queries.

---

# Folder Organization Rules

Keep layers separated.

Routes

Only:

- Receive requests
- Validate requests
- Call services
- Return responses

Services

Contain:

- Business logic
- Encryption
- File processing

Repositories (optional)

Contain:

- Database operations only

Models

Contain:

- ORM models

Schemas

Contain:

- API request/response models

Utilities

Contain:

- Shared helper functions only

---

# Frontend Rules

Components should:

- Be reusable
- Have one responsibility
- Be strongly typed
- Avoid duplicated logic

Business logic belongs in:

- Hooks
- Services
- Context

Never inside UI components.

---

# State Management

Use:

- React Context
- TanStack Query

Avoid:

- Global mutable variables
- Excessive prop drilling
- Unnecessary state duplication

---

# Security Rules

Always

- Use HTTPS
- Enable CORS properly
- Set secure HTTP headers
- Validate every request
- Escape user-generated content
- Protect against XSS
- Protect against CSRF (if using cookies)
- Protect against SQL Injection
- Protect against path traversal
- Protect against directory listing

Never

- Trust client input
- Expose internal APIs
- Disable security middleware

---

# Testing Rules

Each module should include:

- Unit tests
- Integration tests (for APIs)
- Authentication tests
- Encryption tests
- File upload tests
- Error handling tests

Critical paths should have high test coverage.

---

# Performance Rules

Avoid:

- Blocking I/O
- Large in-memory file reads
- Duplicate database queries
- N+1 query issues

Use:

- Async endpoints
- Streaming file uploads/downloads
- Pagination
- Lazy loading where appropriate

---

# Code Style Rules

Python

- Follow PEP 8
- Use type hints
- Maximum function length: ~50 lines (guideline)
- Maximum file length: ~500 lines (guideline)
- Use descriptive variable names
- Prefer dataclasses or Pydantic models where appropriate

TypeScript

- Enable strict mode
- Avoid `any`
- Prefer interfaces and typed APIs
- Use ESLint and Prettier

---

# Documentation Rules

Every public function should include:

- Purpose
- Parameters
- Return value
- Exceptions (if applicable)

Maintain:

- README.md
- PRD.md
- Architecture.md
- API.md

---

# OpenCode Boundaries

OpenCode **must**:

- Follow the architecture defined in `Architecture.md`.
- Implement only the approved features listed in `PRD.md`.
- Keep frontend, backend, cryptography, and storage concerns separate.
- Generate modular, production-ready code.
- Use only the approved libraries and frameworks in this document.
- Follow RESTful API design and consistent naming conventions.
- Write code that is secure by default.

OpenCode **must not**:

- Introduce new frameworks or libraries without explicit approval.
- Change the project structure unless requested.
- Implement experimental or insecure cryptographic algorithms.
- Store secrets, passwords, or encryption keys in source code.
- Expose sensitive information through logs or API responses.
- Add features that are outside the documented scope.
- Generate placeholder security logic that would be unsafe in production.

---

# Definition of Done

A task is considered complete when:

- Code compiles without errors.
- Linting passes.
- Tests pass.
- No security issues are introduced.
- Documentation is updated.
- Error handling is implemented.
- Input validation is complete.
- Authentication and authorization checks are enforced where applicable.
- The implementation follows the PRD, Architecture, and these development rules.
```