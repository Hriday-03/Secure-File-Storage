"""End-to-end API tests covering auth, profile, files, and security middleware."""

import io

from app.services.storage_service import StorageService


class TestHealth:
    def test_health_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestAuth:
    def test_register_and_login(self, client):
        register = client.post(
            "/api/auth/register",
            json={"name": "New User", "email": "new@example.com", "password": "strongpass1"},
        )
        assert register.status_code == 201
        payload = register.json()["data"]
        assert payload["user"]["email"] == "new@example.com"
        assert payload["access_token"]

        login = client.post(
            "/api/auth/login",
            json={"email": "new@example.com", "password": "strongpass1"},
        )
        assert login.status_code == 200
        assert login.json()["data"]["access_token"]

    def test_register_duplicate_email_conflict(self, client):
        payload = {"name": "Dup", "email": "dup@example.com", "password": "strongpass1"}
        assert client.post("/api/auth/register", json=payload).status_code == 201
        duplicate = client.post("/api/auth/register", json=payload)
        assert duplicate.status_code == 409
        assert duplicate.json()["error"] == "EMAIL_ALREADY_REGISTERED"

    def test_login_wrong_password(self, client):
        client.post(
            "/api/auth/register",
            json={"name": "Bad", "email": "bad@example.com", "password": "strongpass1"},
        )
        login = client.post(
            "/api/auth/login",
            json={"email": "bad@example.com", "password": "wrongpass"},
        )
        assert login.status_code == 401
        assert login.json()["error"] == "INVALID_CREDENTIALS"

    def test_me_requires_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_me_with_token(self, client, auth_headers):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["email"] == "test@example.com"


class TestProfile:
    def test_update_profile(self, client, auth_headers):
        response = client.put("/api/users/profile", json={"name": "Renamed"}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Renamed"

    def test_change_password_and_login_again(self, client, auth_headers):
        change = client.post(
            "/api/users/change-password",
            json={"current_password": "securepass123", "new_password": "newpass456"},
            headers=auth_headers,
        )
        assert change.status_code == 200

        old_login = client.post(
            "/api/auth/login", json={"email": "test@example.com", "password": "securepass123"}
        )
        assert old_login.status_code == 401

        new_login = client.post(
            "/api/auth/login", json={"email": "test@example.com", "password": "newpass456"}
        )
        assert new_login.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        response = client.post(
            "/api/users/change-password",
            json={"current_password": "nope", "new_password": "newpass456"},
            headers=auth_headers,
        )
        assert response.status_code == 401


class TestFiles:
    def _upload(self, client, headers, name="hello.txt", content=b"hello encrypted world"):
        return client.post(
            "/api/files/upload",
            headers=headers,
            files={"file": (name, io.BytesIO(content), "text/plain")},
        )

    def test_upload_encrypts_to_storage(self, client, auth_headers, tmp_path):
        response = self._upload(client, auth_headers)
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["original_name"] == "hello.txt"
        assert data["algorithm"] == "AES-256-GCM"
        assert data["size"] == len(b"hello encrypted world")

        blobs = list((tmp_path / "storage").glob("*.enc"))
        assert len(blobs) == 1
        blob = blobs[0].read_bytes()
        assert b"hello encrypted world" not in blob

    def test_upload_blocked_extension(self, client, auth_headers):
        response = self._upload(client, auth_headers, name="evil.exe", content=b"MZ")
        assert response.status_code == 415
        assert response.json()["error"] == "FILE_TYPE_NOT_ALLOWED"

    def test_upload_empty_file(self, client, auth_headers):
        response = self._upload(client, auth_headers, name="empty.txt", content=b"")
        assert response.status_code == 422

    def test_list_search_rename_delete(self, client, auth_headers):
        self._upload(client, auth_headers, name="alpha.txt", content=b"alpha data")
        self._upload(client, auth_headers, name="beta.log", content=b"beta data")

        listing = client.get("/api/files", headers=auth_headers)
        assert listing.status_code == 200
        assert listing.json()["data"]["total"] == 2

        search = client.get("/api/files?search=alpha", headers=auth_headers)
        items = search.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["original_name"] == "alpha.txt"

        file_id = items[0]["id"]
        rename = client.put(
            f"/api/files/{file_id}/rename", json={"new_name": "alpha-final.txt"}, headers=auth_headers
        )
        assert rename.status_code == 200
        assert rename.json()["data"]["original_name"] == "alpha-final.txt"

        delete = client.delete(f"/api/files/{file_id}", headers=auth_headers)
        assert delete.status_code == 200

        gone = client.get(f"/api/files/{file_id}", headers=auth_headers)
        assert gone.status_code == 404

    def test_download_roundtrip(self, client, auth_headers):
        original = b"roundtrip payload" * 5000
        upload = self._upload(client, auth_headers, name="big.log", content=original)
        file_id = upload.json()["data"]["id"]

        download = client.get(f"/api/files/{file_id}/download", headers=auth_headers)
        assert download.status_code == 200
        assert download.content == original
        assert "attachment" in download.headers["content-disposition"]

    def test_other_user_cannot_access(self, client, auth_headers):
        upload = self._upload(client, auth_headers, name="private.txt", content=b"secret")
        file_id = upload.json()["data"]["id"]

        other = client.post(
            "/api/auth/register",
            json={"name": "Other", "email": "other@example.com", "password": "strongpass1"},
        )
        other_headers = {"Authorization": f"Bearer {other.json()['data']['access_token']}"}

        response = client.get(f"/api/files/{file_id}", headers=other_headers)
        assert response.status_code == 403


class TestSecurity:
    def test_security_headers_present(self, client):
        response = client.get("/api/health")
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["referrer-policy"] == "no-referrer"
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]

    def test_rate_limit_auth_endpoints(self, client):
        for _ in range(10):
            login = client.post(
                "/api/auth/login", json={"email": "x@example.com", "password": "wrongpass"}
            )
            assert login.status_code == 401

        blocked = client.post(
            "/api/auth/login", json={"email": "x@example.com", "password": "wrongpass"}
        )
        assert blocked.status_code == 429
        assert blocked.json()["error"] == "RATE_LIMIT_EXCEEDED"
        assert blocked.headers.get("retry-after")
