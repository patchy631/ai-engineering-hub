import os

import streamlit as st
from crw import CrwClient
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Run the scraper as a local process instead of calling a hosted scraping API.
os.environ.setdefault("CRW_LOCAL", "1")

st.set_page_config(page_title="Local Web RAG", page_icon="🕸️", layout="wide")
st.title("🕸️ Local Web RAG")
st.markdown(
    "Crawl any site with a local engine, then ask questions about it. "
    "No scraping API key: the crawler runs as a process on your machine."
)

with st.sidebar:
    st.header("Settings")
    openai_key = st.text_input("OpenAI API Key", type="password")
    max_pages = st.slider("Pages to crawl", 1, 25, 8)
    max_depth = st.slider("Crawl depth", 1, 3, 1)
    st.caption("The engine binary is downloaded once on first run, then reused.")

url = st.text_input("Site to crawl:", placeholder="https://docs.crewai.com/")


def crawl(url: str, max_depth: int, max_pages: int) -> list[dict]:
    pages = CrwClient().crawl(url, max_depth=max_depth, max_pages=max_pages)
    return [
        {"url": p.get("metadata", {}).get("sourceURL", url), "text": p["markdown"]}
        for p in pages
        if p.get("markdown")
    ]


def chunk(pages: list[dict], size: int = 1500, per_page_limit: int = 60000) -> list[dict]:
    chunks = []
    for page in pages:
        # A single generated page (a changelog, an API dump) can run to megabytes and
        # would swamp the index, so only the head of each page is kept.
        text = page["text"][:per_page_limit]
        for i in range(0, len(text), size):
            piece = text[i : i + size].strip()
            if piece:
                chunks.append({"url": page["url"], "text": piece})
    return chunks


def retrieve(chunks: list[dict], question: str, k: int = 5) -> list[dict]:
    vectorizer = TfidfVectorizer(stop_words="english", max_features=50000)
    matrix = vectorizer.fit_transform([c["text"] for c in chunks])
    scores = cosine_similarity(vectorizer.transform([question]), matrix)[0]
    ranked = sorted(zip(scores, chunks), key=lambda pair: pair[0], reverse=True)
    return [c for score, c in ranked[:k] if score > 0]


def answer(client: OpenAI, question: str, context: list[dict]) -> str:
    sources = "\n\n".join(f"[{i}] {c['url']}\n{c['text']}" for i, c in enumerate(context, 1))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Answer using only the provided page excerpts. Cite the bracketed source "
                    "number after each claim. If the excerpts do not contain the answer, say so."
                ),
            },
            {"role": "user", "content": f"Question: {question}\n\nExcerpts:\n{sources}"},
        ],
    )
    return response.choices[0].message.content


if st.button("Crawl site", disabled=not url.strip()):
    with st.spinner("Crawling with the local engine..."):
        try:
            pages = crawl(url.strip(), max_depth, max_pages)
        except Exception as e:
            st.error(f"Crawl failed: {e}")
            st.stop()
    if not pages:
        st.warning("Crawl returned no readable pages.")
        st.stop()
    st.session_state["chunks"] = chunk(pages)
    st.success(f"Indexed {len(pages)} pages into {len(st.session_state['chunks'])} chunks")

if "chunks" in st.session_state:
    question = st.text_input("Ask a question about the site:")
    if question and openai_key:
        context = retrieve(st.session_state["chunks"], question)
        if not context:
            st.warning("Nothing in the crawled pages matched that question.")
        else:
            with st.spinner("Answering..."):
                st.markdown(answer(OpenAI(api_key=openai_key), question, context))
            st.subheader("Sources")
            for i, c in enumerate(context, 1):
                st.markdown(f"[{i}] {c['url']}")
    elif question:
        st.info("Add your OpenAI key in the sidebar to generate an answer.")
