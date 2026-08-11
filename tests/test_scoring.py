from datetime import datetime, timezone

from nsdigest.models import Article
from nsdigest.processing.scoring import matched_keywords, score_article


def _article(title: str, summary: str | None = None) -> Article:
    return Article(
        id="x",
        title=title,
        url="https://example.com/x",
        source="Test",
        fetched_at=datetime.now(timezone.utc),
        summary=summary,
    )


def test_high_value_paper_scores_higher_than_generic():
    strong = _article(
        "A transformer for EEG-based brain-computer interface decoding",
        "State-of-the-art spectral feature extraction on a public dataset.",
    )
    weak = _article(
        "A study of dendritic morphology in zebrafish",
    )

    assert score_article(strong) > score_article(weak)


def test_score_is_capped_at_100():
    kitchen_sink = _article(
        "transformer deep learning EEG BCI brain-computer interface "
        "spectral features feature extraction security privacy adversarial "
        "seizure state-of-the-art benchmark neural decoding",
    )

    assert score_article(kitchen_sink) == 100


def test_word_boundaries_avoid_false_positives():
    # "omega" must not match the MEG keyword; "declare" must not match "decoding".
    keywords = matched_keywords("The omega index and a clear declaration")

    assert "MEG" not in keywords
    assert "decoding" not in keywords


def test_generic_paper_scores_zero():
    assert score_article(_article("Notes on axon guidance in flies")) == 0
