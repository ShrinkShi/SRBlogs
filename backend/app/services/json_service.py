from pathlib import Path
from typing import Any

from app.services.file_store import resolve_data_path, safe_read_json, safe_write_json


class JsonStore:
    def __init__(self, base: Path, filename: str, default: Any):
        self.file = resolve_data_path(Path(filename))
        self.default = default
        self.file.parent.mkdir(parents=True, exist_ok=True)

    def read(self) -> Any:
        return safe_read_json(self.file, self.default)

    def write(self, data: Any) -> Any:
        safe_write_json(self.file, data)
        return data
