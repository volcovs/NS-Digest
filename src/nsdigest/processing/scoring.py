import re

from nsdigest.models import Article


# Importance vocabulary.
#
# Each entry maps a canonical keyword label to (regex pattern, weight).
# The same vocabulary drives both the importance score and the list of
# keywords surfaced on each article, so there is a single source of truth
# for "what this project cares about".
#
# Tune the weights to reshape the ranking — higher weight == more important.
_KEYWORD_WEIGHTS: dict[str, tuple[str, float]] = {
    # Modelling / ML methods
    "transformer": (r"\btransformer(s)?\b", 25),
    "foundation model": (r"\bfoundation model(s)?\b", 20),
    "deep learning": (r"\bdeep learning\b", 15),
    "machine learning": (r"\bmachine learning\b", 12),
    "self-supervised": (r"\bself[- ]supervised\b", 12),
    "attention": (r"\battention\b", 8),
    "neural network": (r"\bneural network(s)?\b", 8),
    "classification": (r"\bclassif\w+\b", 8),
    # Signal / feature engineering
    "EEG": (r"\beeg\b", 20),
    "MEG": (r"\bmeg\b", 12),
    "ECoG": (r"\becog\b", 12),
    "iEEG": (r"\bieeg\b", 12),
    "fMRI": (r"\bfmri\b", 8),
    "spectral features": (r"\bspectral feature(s)?\b", 18),
    "spectral": (r"\bspectral\b", 15),
    "feature extraction": (r"\bfeature extraction\b", 15),
    "time-frequency": (r"\btime[- ]frequency\b", 10),
    "connectivity": (r"\bconnectivity\b", 6),
    # Neurotech / BCI
    "brain-computer interface": (r"\bbrain[- ]computer interface(s)?\b", 20),
    "BCI": (r"\bbci(s)?\b", 18),
    "neural decoding": (r"\bneural decoding\b", 18),
    "decoding": (r"\bdecod\w+\b", 12),
    # Security / privacy
    "security": (r"\bsecurity\b", 15),
    "privacy": (r"\bprivacy\b", 15),
    "adversarial": (r"\badversarial\b", 12),
    # Clinical impact
    "seizure": (r"\bseizure(s)?\b", 12),
    "epilepsy": (r"\bepilep\w+\b", 10),
    # Rigor / reusability signals
    "benchmark": (r"\bbenchmark(s|ing)?\b", 8),
    "dataset": (r"\bdataset(s)?\b", 6),
    "state-of-the-art": (r"\bstate[- ]of[- ]the[- ]art\b|\bsota\b", 10),
}

_COMPILED: dict[str, tuple[re.Pattern[str], float]] = {
    label: (re.compile(pattern, re.IGNORECASE), weight)
    for label, (pattern, weight) in _KEYWORD_WEIGHTS.items()
}


def _article_text(article: Article) -> str:
    return f"{article.title} {article.summary or ''}"


def matched_keywords(text: str) -> list[str]:
    """Return the canonical labels of every importance keyword found in text."""
    return sorted(
        label
        for label, (pattern, _weight) in _COMPILED.items()
        if pattern.search(text)
    )


def score_article(article: Article) -> float:
    text = _article_text(article)

    score = 0.0

    for _label, (pattern, weight) in _COMPILED.items():
        if pattern.search(text):
            score += weight

    return min(score, 100)
