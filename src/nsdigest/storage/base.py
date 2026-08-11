from abc import ABC, abstractmethod

from nsdigest.models import Article


class NewsStorage(ABC):

    @abstractmethod
    def save_articles(self, articles: list[Article]) -> None:
        ...

    @abstractmethod
    def load_articles(self) -> list[Article]:
        ...

    @abstractmethod
    def delete_articles(self, article_ids: list[str]) -> None:
        ...
