from datetime import datetime

from pydantic import BaseModel, HttpUrl


class Article(BaseModel):
    id: str

    title: str
    url: HttpUrl

    source: str

    published_at: datetime | None = None
    fetched_at: datetime

    summary: str | None = None

    category: str = "uncategorized"

    importance_score: float | None = None

    # Neuroscience-relevant keywords matched in the title/abstract.
    keywords: list[str] = []

    # Digital Object Identifier, when the source exposes one.
    doi: str | None = None
