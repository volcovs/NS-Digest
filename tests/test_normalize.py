from nsdigest.processing.normalize import (
    article_id,
    canonicalize_url,
    extract_keywords,
)


def test_canonicalize_url_removes_trailing_slash():
    assert (
        canonicalize_url("https://example.com/article/")
        == "https://example.com/article"
    )


def test_canonicalize_url_removes_fragment():
    assert (
        canonicalize_url("https://example.com/article#comments")
        == "https://example.com/article"
    )


def test_article_id_is_deterministic():
    url = "https://example.com/article"

    assert article_id(url) == article_id(url)


def test_equivalent_urls_have_same_id():
    assert (
        article_id("https://example.com/article/")
        == article_id("https://example.com/article")
    )


def test_extract_keywords_finds_domain_terms():
    keywords = extract_keywords(
        "A transformer for EEG decoding",
        "We evaluate spectral features on a public dataset.",
    )

    assert "transformer" in keywords
    assert "EEG" in keywords
    assert "spectral features" in keywords
