import re


CATEGORIES = {
    "neural_signals": [
        r"\beeg\b",
        r"\bmeg\b",
        r"\becog\b",
        r"\bieeg\b",
        r"\bfmri\b",
        r"\blfp\b",
        r"\bspectral\b",
        r"\boscillation(s)?\b",
        r"\btime[- ]frequency\b",
        r"\bspike(s)?\b",
    ],
    "machine_learning": [
        r"\btransformer(s)?\b",
        r"\bdeep learning\b",
        r"\bmachine learning\b",
        r"\bneural network(s)?\b",
        r"\bfeature extraction\b",
        r"\bclassif\w+\b",
        r"\bself[- ]supervised\b",
        r"\bfoundation model(s)?\b",
    ],
    "bci": [
        r"\bbrain[- ]computer interface(s)?\b",
        r"\bbci(s)?\b",
        r"\bneural decoding\b",
        r"\bdecod\w+\b",
        r"\bneuroprosthe\w+\b",
        r"\bneural interface(s)?\b",
    ],
    "clinical": [
        r"\balzheimer\w*\b",
        r"\bparkinson\w*\b",
        r"\bepilep\w+\b",
        r"\bseizure(s)?\b",
        r"\bstroke\b",
        r"\bdepression\b",
        r"\bschizophreni\w+\b",
        r"\bdisorder(s)?\b",
        r"\bdisease(s)?\b",
        r"\bpatient(s)?\b",
    ],
    "security_privacy": [
        r"\bsecurity\b",
        r"\bprivacy\b",
        r"\badversarial\b",
        r"\bencryption\b",
        r"\bdifferential privacy\b",
    ],
}


def classify(title: str, summary: str | None) -> str:
    text = f"{title} {summary or ''}".lower()

    scores: dict[str, int] = {}

    for category, patterns in CATEGORIES.items():
        scores[category] = sum(
            1
            for pattern in patterns
            if re.search(pattern, text)
        )

    best_category = max(
        scores,
        key=scores.get,
    )

    if scores[best_category] == 0:
        return "other"

    return best_category
