"""Local filesystem storage for encrypted files."""

from pathlib import Path

from app.core.config import settings
from app.utils.exceptions import StorageError


class StorageService:
    """Stores encrypted files on the local filesystem."""

    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = Path(base_path or settings.STORAGE_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve(self, stored_name: str) -> Path:
        """Resolve a stored name inside the base path, blocking traversal."""
        path = (self.base_path / stored_name).resolve()
        if not str(path).startswith(str(self.base_path)):
            raise StorageError("Invalid storage path.")
        return path

    def open_write(self, stored_name: str):
        """Open a file for binary writing."""
        try:
            return self._resolve(stored_name).open("wb")
        except OSError as exc:
            raise StorageError() from exc

    def open_read(self, stored_name: str):
        """Open a stored file for binary reading."""
        try:
            return self._resolve(stored_name).open("rb")
        except FileNotFoundError as exc:
            raise StorageError("Stored file is missing.") from exc
        except OSError as exc:
            raise StorageError() from exc

    def delete(self, stored_name: str) -> None:
        """Remove a stored file if it exists."""
        try:
            path = self._resolve(stored_name)
            if path.exists():
                path.unlink()
        except OSError as exc:
            raise StorageError() from exc


storage = StorageService()
