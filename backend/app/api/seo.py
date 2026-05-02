from __future__ import annotations

from datetime import datetime
from email.utils import format_datetime
from html import escape
from urllib.parse import quote, urljoin

from fastapi import APIRouter
from fastapi.responses import Response

from app.config import get_settings
from app.services.content_service import MarkdownStore

router = APIRouter(tags=["seo"])


def _frontend_base_url() -> str:
    configured = get_settings().public_base_url.strip().rstrip("/")
    if not configured:
        return "http://127.0.0.1:5173"
    if configured in {"http://127.0.0.1:8000", "http://localhost:8000"}:
        return configured.replace(":8000", ":5173")
    return configured


def _absolute(path: str) -> str:
    return urljoin(_frontend_base_url() + "/", path.lstrip("/"))


def _parse_date(value: str) -> datetime | None:
    text = (value or "").strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            source = text[:16] if "%H:%M" in fmt else text[:10]
            return datetime.strptime(source, fmt)
        except ValueError:
            continue
    return None


def _rfc822(value: str) -> str:
    parsed = _parse_date(value)
    if not parsed:
        parsed = datetime.now()
    return format_datetime(parsed)


def _iso_date(value: str) -> str:
    parsed = _parse_date(value)
    if not parsed:
        return ""
    return parsed.date().isoformat()


def _items(section: str):
    return MarkdownStore(get_settings().data_path, section).list(include_drafts=False)


@router.get("/api/rss.xml", include_in_schema=False)
def rss_feed():
    settings = get_settings()
    entries = [(item, "posts") for item in _items("posts")]
    entries.extend((item, "chatters") for item in _items("chatters")[:10])
    entries = sorted(entries, key=lambda pair: pair[0].meta.date or "", reverse=True)[:30]
    channel_items = []
    for item, section in entries:
        path = f"/{section}/{item.slug}"
        description = item.meta.summary or item.content[:220]
        channel_items.append(
            "\n".join(
                [
                    "    <item>",
                    f"      <title>{escape(item.meta.title)}</title>",
                    f"      <link>{escape(_absolute(path))}</link>",
                    f"      <guid>{escape(_absolute(path))}</guid>",
                    f"      <pubDate>{escape(_rfc822(item.meta.date))}</pubDate>",
                    f"      <description>{escape(description)}</description>",
                    "    </item>",
                ]
            )
        )
    xml = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0">',
            "  <channel>",
            "    <title>SRBlogs</title>",
            f"    <link>{escape(_frontend_base_url())}</link>",
            "    <description>SRBlogs public posts feed</description>",
            f"    <lastBuildDate>{escape(format_datetime(datetime.now()))}</lastBuildDate>",
            *channel_items,
            "  </channel>",
            "</rss>",
        ]
    )
    return Response(content=xml, media_type="application/rss+xml; charset=utf-8")


@router.get("/api/sitemap.xml", include_in_schema=False)
def sitemap():
    routes = [
        "/",
        "/posts",
        "/moments",
        "/chatters",
        "/friends",
        "/projects",
        "/music",
        "/photowall",
        "/about",
        "/timeline",
        "/search",
        "/tags",
        "/archive",
    ]
    urls: list[tuple[str, str]] = [(path, "") for path in routes]
    for item in _items("posts"):
        urls.append((f"/posts/{item.slug}", _iso_date(item.meta.date)))
    for item in _items("chatters"):
        urls.append((f"/chatters/{item.slug}", _iso_date(item.meta.date)))
    tag_set: set[str] = set()
    for section in ("posts", "moments", "chatters"):
        for item in _items(section):
            tag_set.update(item.meta.tags or [])
    for tag in sorted(tag_set):
        urls.append((f"/tags/{quote(tag)}", ""))
    url_nodes = []
    for path, lastmod in urls:
        lines = ["  <url>", f"    <loc>{escape(_absolute(path))}</loc>"]
        if lastmod:
            lines.append(f"    <lastmod>{escape(lastmod)}</lastmod>")
        lines.append("  </url>")
        url_nodes.append("\n".join(lines))
    xml = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            *url_nodes,
            "</urlset>",
        ]
    )
    return Response(content=xml, media_type="application/xml; charset=utf-8")


@router.get("/robots.txt", include_in_schema=False)
def robots():
    text = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin",
            f"Sitemap: {_frontend_base_url()}/api/sitemap.xml",
            "",
        ]
    )
    return Response(content=text, media_type="text/plain; charset=utf-8")
