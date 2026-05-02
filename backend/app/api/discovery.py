from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query

from app.config import get_settings
from app.services.content_service import MarkdownStore
from app.services.file_store import validate_slug
from app.services.json_service import JsonStore

router = APIRouter(tags=["discovery"])

CONTENT_TYPES = ("posts", "moments", "chatters")
JSON_TYPES = ("projects", "photos", "friends", "music")
ALL_TYPES = ("all", *CONTENT_TYPES, *JSON_TYPES)


def _json_store(name: str, filename: str) -> JsonStore:
    return JsonStore(get_settings().data_path, filename, [])


def _safe_tags(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _date_key(value: str | None) -> str:
    text = (value or "").strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text[:16] if fmt.endswith("%H:%M") else text[:10], fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def _url_for(item_type: str, slug: str = "", index: int | None = None) -> str:
    if item_type == "posts":
        return f"/posts/{slug}"
    if item_type == "moments":
        return f"/moments/{slug}"
    if item_type == "chatters":
        return f"/chatters/{slug}"
    if item_type == "projects":
        return "/projects"
    if item_type == "photos":
        return "/photowall"
    if item_type == "friends":
        return "/friends"
    if item_type == "music":
        return "/music"
    return "/"


def _base_result(
    item_type: str,
    title: str,
    summary: str = "",
    slug: str = "",
    tags: list[str] | None = None,
    date: str = "",
    haystack: str = "",
) -> dict[str, Any]:
    if slug:
        validate_slug(slug)
    return {
        "type": item_type,
        "title": title or slug or item_type,
        "slug": slug,
        "summary": summary or "",
        "url": _url_for(item_type, slug),
        "tags": tags or [],
        "date": date or "",
        "score": 0,
        "_haystack": haystack,
    }


def _content_results() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for section in CONTENT_TYPES:
        store = MarkdownStore(get_settings().data_path, section)
        for entry in store.list(include_drafts=False):
            tags = entry.meta.tags or []
            haystack = " ".join([entry.meta.title, entry.meta.summary or "", " ".join(tags), entry.content])
            items.append(
                _base_result(
                    section,
                    entry.meta.title,
                    entry.meta.summary or entry.content[:140],
                    entry.slug,
                    tags,
                    _date_key(entry.meta.date) or entry.meta.date,
                    haystack,
                )
            )
    return items


def _structured_results() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    stores = {
        "projects": ("projects.json", lambda raw: (raw.get("name", ""), raw.get("description", ""), _safe_tags(raw.get("tags")))),
        "photos": ("photos/photos.json", lambda raw: (raw.get("title", ""), raw.get("description", ""), _safe_tags(raw.get("tags")))),
        "friends": ("friends.json", lambda raw: (raw.get("name", ""), " ".join([raw.get("description", ""), raw.get("url", "")]), _safe_tags(raw.get("tags")))),
        "music": ("music.json", lambda raw: (raw.get("title", ""), raw.get("artist", ""), [])),
    }
    for item_type, (filename, extractor) in stores.items():
        data = _json_store(item_type, filename).read()
        if not isinstance(data, list):
            continue
        for index, raw in enumerate(data):
            if not isinstance(raw, dict):
                continue
            title, summary, tags = extractor(raw)
            haystack = " ".join([str(title), str(summary), " ".join(tags)])
            result = _base_result(item_type, str(title), str(summary), str(index), tags, str(raw.get("date", "")), haystack)
            result["url"] = _url_for(item_type)
            items.append(result)
    return items


def _all_results() -> list[dict[str, Any]]:
    return _content_results() + _structured_results()


def _score(item: dict[str, Any], q: str, tag: str) -> int:
    score = 0
    haystack = str(item.get("_haystack", "")).lower()
    title = str(item.get("title", "")).lower()
    item_tags = [str(t).lower() for t in item.get("tags", [])]
    if q:
        q_lower = q.lower()
        score += title.count(q_lower) * 8
        score += haystack.count(q_lower) * 2
    if tag and any(tag.lower() in item_tag for item_tag in item_tags):
        score += 10
    if not q and not tag:
        score = 1
    return score


@router.get("/search")
def search(
    q: str = Query("", max_length=80),
    type: str = Query("all"),
    tag: str = Query("", max_length=60),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    if type not in ALL_TYPES:
        type = "all"
    results = []
    for item in _all_results():
        if type != "all" and item["type"] != type:
            continue
        score = _score(item, q.strip(), tag.strip())
        if score <= 0:
            continue
        clean = {key: value for key, value in item.items() if key != "_haystack"}
        clean["score"] = score
        results.append(clean)
    results.sort(key=lambda item: (item["score"], item.get("date", "")), reverse=True)
    return {"items": results[offset : offset + limit], "total": len(results), "limit": limit, "offset": offset}


@router.get("/tags")
def tags():
    buckets: dict[str, dict[str, Any]] = {}
    for item in _content_results():
        for tag in item["tags"]:
            current = buckets.setdefault(tag, {"tag": tag, "count": 0, "types": set(), "latestDate": ""})
            current["count"] += 1
            current["types"].add(item["type"])
            if item.get("date", "") > current["latestDate"]:
                current["latestDate"] = item.get("date", "")
    for item in _structured_results():
        if item["type"] != "projects":
            continue
        for tag in item["tags"]:
            current = buckets.setdefault(tag, {"tag": tag, "count": 0, "types": set(), "latestDate": ""})
            current["count"] += 1
            current["types"].add(item["type"])
    output = []
    for value in buckets.values():
        output.append({**value, "types": sorted(value["types"])})
    output.sort(key=lambda item: (-item["count"], item["tag"].lower()))
    return output


@router.get("/archive")
def archive():
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for item in _content_results():
        date = _date_key(item.get("date", "")) or "unknown"
        year, month = ("unknown", "unknown")
        if date != "unknown":
            parts = date.split("-")
            if len(parts) >= 2:
                year, month = parts[0], parts[1]
        grouped[year][month].append(
            {
                "type": item["type"],
                "title": item["title"],
                "slug": item["slug"],
                "url": item["url"],
                "date": item["date"],
                "tags": item["tags"],
            }
        )
    years = []
    for year in sorted(grouped.keys(), reverse=True):
        months = []
        for month in sorted(grouped[year].keys(), reverse=True):
            items = sorted(grouped[year][month], key=lambda item: item.get("date", ""), reverse=True)
            months.append({"month": month, "items": items})
        years.append({"year": year, "months": months})
    return {"years": years}
