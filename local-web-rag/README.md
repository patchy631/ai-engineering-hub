# Local Web RAG

Crawl a website and ask questions about it, with the crawler running as a local process instead of
a hosted scraping API. There is no scraping API key and no per-page billing: the engine binary is
downloaded once on first run and reused after that.

We use the following stack:

- [CRW](https://github.com/us/crw) as the crawler, running locally via `CRW_LOCAL=1`
- scikit-learn TF-IDF for retrieval, so the index has no service dependency either
- OpenAI `gpt-4o-mini` to write the answer with inline citations

Only the answering step needs an API key. If you swap the last function for a local model, the whole
pipeline runs offline.

## Installation and setup

**Install dependencies**:

```bash
pip install -r requirements.txt
```

**Run the app**:

```bash
streamlit run app.py
```

Paste an OpenAI key in the sidebar, enter a site, pick crawl depth and page count, and press
Crawl site. Once the crawl finishes you can ask questions and every claim in the answer carries the
page it came from.

## How it works

1. `CrwClient().crawl()` walks the site to the requested depth and returns markdown per page.
2. Pages are trimmed and split into 1500-character chunks. Generated pages such as changelogs can
   be megabytes long, so only the head of each page is indexed.
3. A TF-IDF matrix over the chunks ranks them against the question by cosine similarity.
4. The top chunks go to the model as numbered excerpts, and it answers from those only.

## Notes

CRW is open source under AGPL-3.0, so the crawl step has no vendor lock-in. If you would rather not
run the engine locally, set `CRW_API_KEY` and it will use the hosted API instead with no code
change.
