# Secure File Storage — API Reference

All endpoints are served under the `/api` prefix on port `8000` (dev default). Interactive docs: `/docs`.

Every response (except `GET /api/health` and file downloads) uses the standard envelope:

```json
{
  "success": true,
  "message": "Human-readable message.",
  "data": { },
  "error": null
}
```

On failure, `success` is `false`, `data` is `null`, and `error` holds a stable error code.
Validation failures also include a `details` array (`422 VALIDATION_ERROR`).

---

## Error codes

| Code | HTTP | Meaning |
| --- | --- | --- |
| `AUTHENTICATION_REQUIRED` | 401 | Missing/invalid/expired token |
| `INVALID_CREDENTIALS` | 401 | Wrong credentials (login, change-password) |
| `FORBIDDEN` | 403 | Accessing another user's file |
| `NOT_FOUND` | 404 | Resource not found |
| `EMAIL_ALREADY_REGISTERED` | 409 | Duplicate email on registration |
| `VALIDATION_ERROR` | 422 | Payload or field validation failed |
| `EMPTY_FILE` | 422 | Uploaded file is empty |
| `FILE_TOO_LARGE` | 413 | Upload exceeds `MAX_UPLOAD_SIZE_MB` (default 100 MB) |
| `FILE_TYPE_NOT_ALLOWED` | 415 | Extension is blocked or not allowed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests (includes `Retry-After` header) |
| `ENCRYPTION_ERROR` | 500 | Encryption/processing failed |
| `STORAGE_ERROR` | 500 | Storage read/write failed |
| `DECRYPTION_ERROR` | 500 | Decryption failed (tampering, wrong key) |
| `INTERNAL_ERROR` | 500 | Unhandled error (internals never leaked) |

---

## Health

### `GET /api/health`

Returns `{"status": "ok"}`. Unauthenticated.

---

## Authentication

### `POST /api/auth/register`

Register a new user. Generates the RSA-2048 keypair and encrypts the private key at rest
(master key HKDF-derived from `SECRET_KEY`).

Request:

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "a-secure-password"
}
```

`password` is limited to 72 bytes (bcrypt limit). Success: `201` with token + user.

### `POST /api/auth/login`

```json
{ "email": "jane@example.com", "password": "a-secure-password" }
```

Success: `200` with `data.access_token` (JWT, 30 min), `token_type`, `expires_in`, `user`.
Use the token as `Authorization: Bearer <token>` on protected endpoints.

### `POST /api/auth/logout`

Authenticated. Successful no-op token invalidation on the client; always clears the local session.
Returns `200`.

### `GET /api/auth/me`

Authenticated. Returns the current `UserResponse`.

---

## Users

`UserResponse` = `{id, name, email, created_at}`.

### `GET /api/users/profile`
Authenticated. Returns the profile.

### `PUT /api/users/profile`
Authenticated. Update display name.

```json
{ "name": "Jane McAllister" }
```
`name` must be 2–255 chars. Returns updated `UserResponse`.

### `POST /api/users/change-password`
Authenticated. Verifies the current password, rejects identical passwords.

```json
{ "current_password": "old-password", "new_password": "new-password" }
```

Wrong current password → `401 INVALID_CREDENTIALS`. Same password → `422 VALIDATION_ERROR`.

---

## Dashboard

### `GET /api/dashboard/stats`
Authenticated. Returns storage usage statistics.

---

## Files

`FileResponse` = `{id, original_name, size, mime_type, algorithm, uploaded_at}`.
`stored_name` and `encrypted_key` are never exposed.

### `POST /api/files/upload`
Authenticated. `multipart/form-data` with field `file`.

- Extension must be in the allowlist and not in the blocklist (`exe`, `bat`, `sh`, `js`, … rejected).
- Empty files rejected (`422`). Files over `MAX_UPLOAD_SIZE_MB` rejected (`413`).
- File is encrypted with a fresh random AES-256-GCM key; the AES key is RSA-encrypted to the
  user's public key; only the ciphertext is written to disk.
- Success: `201` with `FileResponse`.

### `GET /api/files`
Authenticated. Paginated list with search and sort.

Query params:

| Param | Default | Notes |
| --- | --- | --- |
| `page` | `1` | ≥ 1 |
| `page_size` | `10` | 1–100 |
| `search` | — | Case-insensitive substring on `original_name` |
| `sort_by` | `date` | `name`, `size`, `date` |
| `sort_order` | `desc` | `asc` or `desc` |

Response `data` = `{items: [FileResponse], total, page, page_size, total_pages}`.

### `GET /api/files/{id}`
Authenticated. Returns a single owned file or `404`. Another user's file → `403`.

### `GET /api/files/{id}/download`
Authenticated. Recovers the AES key via the user's RSA private key, streams decrypted bytes.
Sets `Content-Disposition: attachment`. Blob is streamed and decrypted chunk-by-chunk.

### `DELETE /api/files/{id}`
Authenticated. Deletes metadata and the encrypted blob. `404` if gone.

### `PUT /api/files/{id}/rename`
Authenticated.

```json
{ "new_name": "renamed.txt" }
```

Returns updated `FileResponse`.

---

## Security & hardening

- **Rate limiting** (per IP, sliding window): auth endpoints 10/min, all other `/api` 120/min →
  `429 RATE_LIMIT_EXCEEDED`.
- **Security headers** on every response: `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy`, `Strict-Transport-Security`
  (HTTPS only).
- **Audit logging**: structured request log with method, path, status, duration, user id, client.
- Filenames sanitized (path traversal blocked); CORS pinned to configured origins only.