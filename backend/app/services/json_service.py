from pathlib import Path
from typing import Any
import json


class JsonStore:
    def __init__(self, base: Path, filename: str, default: Any):
        self.file = base / filename
        self.default = default
        self.file.parent.mkdir(parents=True, exist_ok=True)
        if not self.file.exists():
            self.write(default)

    def read(self) -> Any:
        try:
            return json.loads(self.file.read_text(encoding="utf-8"))
        except Exception:
            return self.default

    def write(self, data: Any) -> Any:
        self.file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data
