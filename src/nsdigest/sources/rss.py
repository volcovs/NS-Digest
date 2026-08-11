import re
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser


DOI_PATTERN = re.compile(r"10\.\d{4,9}/[-._;()/:a-z0-9]+", re.IGNORECASE)

# A browser-like UA. Some publishers (e.g. behind Cloudflare) reject the
# default Python/feedparser agent with a 403.
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; NS-Digest/0.1; +https://github.com/volcovs/NS-Digest)"
)


@dataclass
class RawArticle:
    title: str
    url: str
    source: str
    published_at: datetime | None
    summary: str | None
    doi: str | None = None


def _extract_doi(entry) -> str | None:
    """Best-effort DOI discovery across the fields feeds commonly use."""
    candidates = [
        entry.get("dc_identifier"),
        entry.get("prism_doi"),
        entry.get("id"),
        entry.get("link"),
        entry.get("summary"),
    ]

    for candidate in candidates:
        if not candidate:
            continue

        match = DOI_PATTERN.search(str(candidate))

        if match:
            return match.group(0).rstrip(".").lower()

    return None


class RSSSource:
    def __init__(self, name: str, feed_url: str, user_agent: str | None = None):
        self.name = name
        self.feed_url = feed_url
        self.user_agent = user_agent or DEFAULT_USER_AGENT

    def fetch(self) -> list[RawArticle]:
        feed = feedparser.parse(self.feed_url, agent=self.user_agent)

        if feed.bozo and not feed.entries:
            return []

        articles: list[RawArticle] = []
        for entry in feed.entries:
            title = entry.get("title", "").strip()
            url = entry.get("link", "").strip()

            if not title or not url:
                continue

            published_at = None
            if entry.get("published_parsed"):
                published_at = datetime(
                    *entry.published_parsed[:6],
                    tzinfo=timezone.utc,
                )

            articles.append(
                RawArticle(
                    title=title,
                    url=url,
                    source=self.name,
                    published_at=published_at,
                    summary=entry.get("summary"),
                    doi=_extract_doi(entry),
                )
            )

        return articles
