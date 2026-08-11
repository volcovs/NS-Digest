from nsdigest.processing.normalize import normalize
from nsdigest.sources.catalog import SOURCES
from nsdigest.storage.articles import ArticleRepository
from nsdigest.storage.dropbox import DropboxStorage


def main() -> None:
    storage = DropboxStorage()
    repository = ArticleRepository(storage)

    total_fetched = 0
    total_new = 0

    for source in SOURCES:
        print(f"\nFetching {source.name}...")

        try:
            raw_articles = source.fetch()
        except Exception as error:  # noqa: BLE001 - never let one bad feed stop the run
            print(f"  ! failed: {error}")
            continue

        total_fetched += len(raw_articles)

        articles = [normalize(raw) for raw in raw_articles]

        new_articles = repository.save_articles(articles)

        total_new += len(new_articles)

        print(
            f"Fetched {len(articles)}, "
            f"new {len(new_articles)}"
        )

    print("\nDone.")
    print(f"Fetched: {total_fetched}")
    print(f"New:     {total_new}")


if __name__ == "__main__":
    main()
