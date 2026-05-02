from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from app.models.schemas import ContentItem, ContentMeta, ContentWrite
from app.services.file_store import backup_file, resolve_data_path, safe_read_text, safe_write_text, validate_slug


class ContentError(ValueError):
    pass


def ensure_slug(slug: str) -> str:
    try:
        return validate_slug(slug)
    except ValueError as exc:
        raise ContentError(str(exc)) from exc


def _split_front_matter(raw: str) -> tuple[dict, str]:
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            meta_raw = parts[1].strip()
            content = parts[2].lstrip("\n")
            meta = yaml.safe_load(meta_raw) or {}
            return meta, content
    return {}, raw


def _dump_front_matter(meta: dict, content: str) -> str:
    meta_text = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{meta_text}\n---\n\n{content.strip()}\n"


class MarkdownStore:
    def __init__(self, base: Path, section: str):
        self.path = resolve_data_path(section)
        self.path.mkdir(parents=True, exist_ok=True)

    def _file(self, slug: str) -> Path:
        return self.path / f"{ensure_slug(slug)}.md"

    def list(self, include_drafts: bool = False) -> list[ContentItem]:
        items: list[ContentItem] = []
        for file in sorted(self.path.glob("*.md")):
            item = self.read(file.stem)
            if item.meta.draft and not include_drafts:
                continue
            items.append(item)
        items.sort(key=lambda x: x.meta.date or "", reverse=True)
        return items

    def read(self, slug: str) -> ContentItem:
        file = self._file(slug)
        if not file.exists():
            raise FileNotFoundError(slug)
        raw = safe_read_text(file)
        meta_dict, content = _split_front_matter(raw)
        if not meta_dict.get("date"):
            meta_dict["date"] = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        return ContentItem(slug=file.stem, meta=ContentMeta(**meta_dict), content=content)

    def save(self, payload: ContentWrite, old_slug: str | None = None) -> ContentItem:
        slug = ensure_slug(payload.slug)
        if not payload.meta.date:
            payload.meta.date = datetime.now().strftime("%Y-%m-%d %H:%M")
        target = self._file(slug)
        if old_slug and ensure_slug(old_slug) != slug:
            old = self._file(old_slug)
            if old.exists():
                backup_file(old)
                old.unlink()
        safe_write_text(target, _dump_front_matter(payload.meta.model_dump(), payload.content))
        return self.read(slug)

    def delete(self, slug: str) -> None:
        file = self._file(slug)
        if not file.exists():
            raise FileNotFoundError(slug)
        backup_file(file)
        file.unlink()
