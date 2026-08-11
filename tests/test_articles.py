from datetime import datetime, timezone

from nsdigest.models import Article
from nsdigest.storage.articles import ArticleRepository
from nsdigest.storage.dropbox import DropboxStorage


def test_article_repository_deduplicates():
    storage = DropboxStorage()
    repository = ArticleRepository(storage)

    article = Article(
        id="test-article-123",
        title="Test neuroscience article",
        url="https://example.com/test",
        source="Test",
        fetched_at=datetime.now(timezone.utc),
    )

    repository.save_articles([article])
    repository.save_articles([article])

    loaded = repository.load_date(
        article.fetched_at.date()
    )

    matching = [
        a for a in loaded
        if a.id == article.id
    ]

    assert len(matching) == 1

    storage.delete(
        f"articles/{article.fetched_at.date().isoformat()}.jsonl"
    )
