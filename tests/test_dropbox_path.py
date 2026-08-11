import os

# DropboxStorage imports config, which requires these at import time. Set
# dummy values so the pure path helper can be tested without real creds.
os.environ.setdefault("DROPBOX_APP_KEY", "x")
os.environ.setdefault("DROPBOX_APP_SECRET", "x")
os.environ.setdefault("DROPBOX_REFRESH_TOKEN", "x")

from nsdigest.storage.dropbox import _normalize_path  # noqa: E402


def test_adds_leading_slash():
    assert _normalize_path("articles/2026-08-11.jsonl") == "/articles/2026-08-11.jsonl"


def test_collapses_duplicate_slashes():
    assert _normalize_path("//articles///x.jsonl") == "/articles/x.jsonl"


def test_converts_backslashes():
    assert _normalize_path("\\articles\\x.jsonl") == "/articles/x.jsonl"


def test_empty_path_raises():
    import pytest

    with pytest.raises(ValueError):
        _normalize_path("   ")


def test_article_paths_are_root_relative():
    # DROPBOX_ROOT is intentionally left empty (a single space in GitHub, which
    # rejects empty secrets). The Python writer never prefixes the root, so
    # articles always land at /articles/<date>.jsonl — matching the readers.
    assert _normalize_path("articles/2026-08-11.jsonl").startswith("/articles/")
