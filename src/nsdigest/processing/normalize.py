import hashlib
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

from nsdigest.models import Article
from nsdigest.processing.classify import classify
from nsdigest.processing.scoring import matched_keywords, score_article
from nsdigest.sources.rss import RawArticle


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/"),
            parts.query,
            "",
        )
    )


def article_id(url: str) -> str:
    canonical_url = canonicalize_url(url)

    return hashlib.sha256(
        canonical_url.encode("utf-8")
    ).hexdigest()


def clean_summary(summary: str | None) -> str | None:
    if not summary:
        return None

    text = BeautifulSoup(summary, "html.parser").get_text(
        " ",
        strip=True,
    )

    return text or None


def extract_keywords(title: str, summary: str | None) -> list[str]:
    text = f"{title} {summary or ''}"

    return matched_keywords(text)


def normalize(raw: RawArticle) -> Article:
    summary = clean_summary(raw.summary)

    article = Article(
        id=article_id(raw.url),
        title=raw.title,
        url=canonicalize_url(raw.url),
        source=raw.source,
        published_at=raw.published_at,
        fetched_at=datetime.now(timezone.utc),
        summary=summary,
        category=classify(raw.title, summary),
        keywords=extract_keywords(raw.title, summary),
        doi=raw.doi,
    )

    article.importance_score = score_article(article)
    return article
