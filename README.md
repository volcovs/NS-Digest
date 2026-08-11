# NS-Digest

An automated **neuroscience literature digest**. NS-Digest polls neuroscience
journals and preprint servers, scores each paper against a configurable set of
importance keywords (EEG, transformers, spectral features, BCI, …), stores the
results in Dropbox, serves them as a static website, and emails a weekly digest
of the most important papers.

It is the neuroscience sibling of a personal cybersecurity news dashboard —
same architecture (Python fetcher + Dropbox persistence + Netlify site &
functions + Resend email + GitHub Actions schedulers), retargeted at scientific
literature.

---

## How it works

```
                    ┌──────────────────────────────────────────┐
   GitHub Actions   │  scripts/fetch_news.py  (hourly)          │
   (hourly cron) ──▶│  RSS feeds → normalize → classify → score │
                    └───────────────────────┬──────────────────┘
                                             │ JSONL (one file per day)
                                             ▼
                                    ┌──────────────────┐
                                    │      Dropbox     │
                                    │  /articles/*.jsonl│
                                    └────────┬─────────┘
                        reads               │              reads
              ┌──────────────────────┐      │      ┌───────────────────────┐
              │  Netlify function    │◀─────┴─────▶│  Netlify function     │
              │  /api/news           │             │  send-digest (weekly) │
              └──────────┬───────────┘             └───────────┬───────────┘
                         │ JSON                                │ HTML email
                         ▼                                     ▼
                 ┌───────────────┐                     ┌──────────────┐
                 │  web/ (static)│                     │    Resend    │
                 │  index.html   │                     │  → your inbox│
                 └───────────────┘                     └──────────────┘
```

The pipeline:

1. **Fetch** — `scripts/fetch_news.py` pulls every feed in
   [`sources/catalog.py`](src/nsdigest/sources/catalog.py).
2. **Normalize** — canonicalize the URL, derive a stable `id`, strip HTML from
   the abstract, extract a DOI where available.
3. **Classify** — bucket each paper into `neural_signals`, `machine_learning`,
   `bci`, `clinical`, `security_privacy`, or `other`.
4. **Score** — add up the weights of every importance keyword found in the
   title/abstract (capped at 100). See
   [`processing/scoring.py`](src/nsdigest/processing/scoring.py).
5. **Store** — append new (deduplicated) papers to `articles/<YYYY-MM-DD>.jsonl`
   in Dropbox.
6. **Serve & digest** — the Netlify site reads via `/api/news`; the weekly
   function emails the top 10 by importance via Resend.

---

## Sources

Curated in [`src/nsdigest/sources/catalog.py`](src/nsdigest/sources/catalog.py):

- **Preprints** — arXiv `q-bio.NC`, `eess.SP`, `cs.NE`, `cs.LG`; bioRxiv Neuroscience
- **Journals** — Nature Neuroscience, Nature Communications (Neuroscience),
  Journal of Neuroscience, eNeuro, eLife, PLOS Computational Biology,
  NeuroImage, Frontiers (Neuroscience & Human Neuroscience)
- **Neurotech / BCI** — Journal of Neural Engineering

Add a source by appending an `RSSSource(name=..., feed_url=...)` to `SOURCES`.

## Importance keywords

The ranking heuristic lives in `_KEYWORD_WEIGHTS` in
[`processing/scoring.py`](src/nsdigest/processing/scoring.py). Each keyword maps
to a regex and a weight; a paper's score is the sum of the weights of the
keywords it matches. Current high-value terms include `transformer`, `EEG`,
`brain-computer interface`, `spectral features`, `feature extraction`,
`deep/machine learning`, `security`, `privacy`, and `seizure`. Edit the dict to
retune — it is the single source of truth for both the score and the keyword
chips shown on each paper.

---

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Create a Dropbox app (scoped, with `files.content.read`/`write`), then:

```bash
cp .env.example .env
# fill DROPBOX_APP_KEY and DROPBOX_APP_SECRET, then:
python scripts/authorize_dropbox.py   # prints DROPBOX_REFRESH_TOKEN → add to .env
```

Run a fetch and the tests:

```bash
python scripts/fetch_news.py
pytest                 # Dropbox tests need a valid .env; logic tests run offline
```

Preview the site locally with the Netlify CLI (serves `web/` + functions):

```bash
npm install
npx netlify dev
```

---

## Deployment

**Netlify** — connect the repo. `netlify.toml` publishes `web/` and exposes the
functions. Set these environment variables in the Netlify dashboard:

| Variable | Purpose |
| --- | --- |
| `DROPBOX_APP_KEY` / `DROPBOX_APP_SECRET` / `DROPBOX_REFRESH_TOKEN` | Dropbox access |
| `DROPBOX_ROOT` | Leave empty. GitHub rejects empty secrets, so enter a single space — the readers trim it back to empty |
| `RESEND_API_KEY` | Resend API key for the digest email |
| `DIGEST_RECIPIENT` | Where to send the weekly digest |
| `DIGEST_FROM` | Verified Resend sender (defaults to `onboarding@resend.dev`) |

**GitHub Actions** — three schedulers in `.github/workflows/`:

- `fetch-news.yml` — hourly fetch (needs the `DROPBOX_*` secrets).
- `weekly-digest.yml` — Sundays 20:00 UTC; POSTs `NETLIFY_DIGEST_URL`
  (`https://<site>/.netlify/functions/send-digest`).
- `cleanup-news.yml` — monthly; POSTs `NETLIFY_CLEANUP_URL`
  (`https://<site>/.netlify/functions/cleanup-news`), deleting files older than
  90 days.

> **Note:** Articles are stored at `/articles/<date>.jsonl` in the app's Dropbox
> root. `DROPBOX_ROOT` is intentionally left empty; because GitHub Actions
> rejects empty secret values, set that secret to a single space — the readers
> trim it back to empty and everything resolves to `/articles`.

---

## Project layout

```
src/nsdigest/
  config.py            # env settings (pydantic)
  models.py            # Article model
  sources/
    rss.py             # generic RSS fetcher + DOI extraction
    catalog.py         # the list of neuroscience feeds
  processing/
    normalize.py       # id, canonical URL, summary cleanup, keyword extraction
    classify.py        # category buckets
    scoring.py         # importance keywords + weights (the ranking heuristic)
  storage/
    dropbox.py         # Dropbox client wrapper
    articles.py        # daily JSONL repository with dedup
scripts/
  fetch_news.py        # the pipeline entrypoint
  authorize_dropbox.py # one-time OAuth to mint a refresh token
netlify/functions/
  news.mjs             # GET /api/news  → JSON feed
  send-digest.mjs      # POST → weekly email via Resend
  cleanup-news.mjs     # POST → prune old JSONL files
web/                   # static site (index.html, app.js, styles.css)
tests/                 # pytest (logic tests offline; Dropbox tests need creds)
```
