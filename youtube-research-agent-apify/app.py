import streamlit as st

from research_crew import run_research

st.set_page_config(page_title="YouTube Research Agent", page_icon="🎬")

st.title("YouTube Research Agent")
st.caption("Ask a question about one or more YouTube videos. Built with CrewAI and Apify.")

if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.transcripts = []

with st.sidebar:
    st.header("Videos")
    urls_text = st.text_area(
        "YouTube URLs (one per line)",
        placeholder="https://www.youtube.com/watch?v=...",
        height=150,
    )
    language = st.text_input("Transcript language", value="en")
    st.divider()
    question = st.text_area(
        "Research question",
        value="What are the main points made in these videos?",
    )
    run_clicked = st.button("Run Research", type="primary")

if run_clicked:
    urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
    if not urls:
        st.warning("Add at least one YouTube URL.")
    elif not question.strip():
        st.warning("Enter a research question.")
    else:
        with st.spinner("Fetching transcripts and running the crew..."):
            try:
                result, transcripts = run_research(urls, question, language=language)
                st.session_state.result = result.raw
                st.session_state.transcripts = transcripts
            except Exception as e:
                st.error(f"Something went wrong: {e}")

if st.session_state.result:
    st.markdown("### Answer")
    st.markdown(st.session_state.result)

    st.download_button(
        label="Download Answer",
        data=st.session_state.result,
        file_name="youtube_research.md",
        mime="text/markdown",
    )

    with st.expander("Transcripts used"):
        for t in st.session_state.transcripts:
            st.markdown(f"**{t['title']}** ({len(t['text'])} characters)")
            st.write(t["text"][:1000] + ("..." if len(t["text"]) > 1000 else ""))
