from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Biotech Agentic Analyst",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

from datalab_pipeline.pipeline import (
    run_science_pipeline,
    parse_pipeline_results,
)
from flow.science_flow import ScienceFlow
from flow.state import ScienceFlowState
from models import ExtractedFigure
from utils import decode_thumbnail

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------


def _reset_analysis_metrics(*, increment_uploader: bool = False) -> None:
    st.session_state.flow_state = None
    st.session_state.page_count = 0
    st.session_state.quality_score = None
    st.session_state.extraction_score = None
    st.session_state.pipeline_steps = []
    if increment_uploader:
        st.session_state.uploader_key += 1


for _key, _default in [
    ("flow_state", None),
    ("page_count", 0),
    ("quality_score", None),
    ("extraction_score", None),
    ("pipeline_steps", []),
    ("uploader_key", 0),
]:
    if _key not in st.session_state:
        st.session_state[_key] = _default


# ---------------------------------------------------------------------------
# Datalab client — cached across reruns
# ---------------------------------------------------------------------------


@st.cache_resource
def init_datalab_client():
    api_key = os.getenv("DATALAB_API_KEY")
    if not api_key:
        return None, "DATALAB_API_KEY not set in environment"
    try:
        from datalab_sdk import DatalabClient

        client = DatalabClient(api_key=api_key)
        return client, True
    except Exception as exc:
        return None, str(exc)


# ---------------------------------------------------------------------------
# PDF preview — cached by file content so re-renders are instant
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def _render_pdf_pages(pdf_bytes: bytes) -> list[bytes]:
    import fitz

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    mat = fitz.Matrix(1.4, 1.4)
    pages = [doc[i].get_pixmap(matrix=mat).tobytes("png") for i in range(len(doc))]
    doc.close()
    return pages


def _render_pdf_preview(pdf_bytes: bytes) -> None:
    try:
        pages = _render_pdf_pages(pdf_bytes)
        for i, page_png in enumerate(pages):
            st.image(
                page_png,
                caption=f"Page {i + 1} of {len(pages)}",
                width="stretch",
            )
    except Exception:
        st.caption("PDF preview unavailable")


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

_TAG_COLORS = [
    ("#dbeafe", "#1d4ed8"),
    ("#dcfce7", "#166534"),
    ("#fef9c3", "#854d0e"),
    ("#fee2e2", "#991b1b"),
]


def _pill(text: str, bg: str, fg: str) -> str:
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;'
        f"border-radius:12px;font-size:0.8em;font-weight:500;"
        f'margin:2px;display:inline-block">{text}</span>'
    )


def _axis_pill(label: str, value: str) -> str:
    """Labeled axis pill with a distinct prefix badge (x / y / n)."""
    return (
        f'<span style="display:inline-flex;align-items:center;border-radius:8px;'
        f'overflow:hidden;margin:2px;font-size:0.8em;border:1px solid #4b5563">'
        f'<span style="background:#4b5563;color:#f9fafb;padding:2px 7px;font-weight:700">{label}</span>'
        f'<span style="padding:2px 8px">&nbsp;{value}</span>'
        f"</span>"
    )


def _section_label(text: str) -> str:
    return (
        f'<div style="font-size:0.7em;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.07em;color:#9ca3af;margin-top:8px;margin-bottom:2px">{text}</div>'
    )


def _render_thumbnail_strip(figures: list[ExtractedFigure]) -> None:
    seen: set[int] = set()
    for fig in figures:
        if fig.page_number in seen or not fig.thumbnail_b64:
            continue
        seen.add(fig.page_number)
        img = decode_thumbnail(fig.thumbnail_b64)
        if img:
            st.image(img, caption=f"p. {fig.page_number}", width="stretch")


def _render_figure_intelligence_tab(state: ScienceFlowState) -> None:
    if not state.figure_intelligences:
        st.info("No figure intelligence available.")
        return

    extracted_lookup: dict[str, ExtractedFigure] = {
        f.figure_id: f for f in state.figures
    }

    total = len(state.figure_intelligences)
    for idx, fi in enumerate(state.figure_intelligences):
        extracted = extracted_lookup.get(fi.figure_id)
        page_num = extracted.page_number if extracted else "?"
        title = extracted.title if (extracted and extracted.title) else fi.figure_id

        with st.expander(f"Figure {idx + 1} of {total}", expanded=(idx == 0)):
            col_title, col_badge = st.columns([8, 1])
            with col_title:
                st.markdown(f"**{title}**")
            with col_badge:
                st.markdown(
                    f'<div style="text-align:right">'
                    f'{_pill(f"p. {page_num}", "#f3f4f6", "#374151")}'
                    f"</div>",
                    unsafe_allow_html=True,
                )

            chart_types = [ct.strip() for ct in fi.chart_type.split(",") if ct.strip()]
            pills_html = " ".join(
                _pill(ct, *_TAG_COLORS[i % len(_TAG_COLORS)])
                for i, ct in enumerate(chart_types[:3])
            )
            st.markdown(
                f"{pills_html}&nbsp;&nbsp;<strong>{fi.key_finding}</strong>",
                unsafe_allow_html=True,
            )
            st.markdown("")

            col_img, col_meta = st.columns([1, 2])
            with col_img:
                if extracted and extracted.thumbnail_b64:
                    img = decode_thumbnail(extracted.thumbnail_b64)
                    if img:
                        st.image(img, width="stretch")
                    else:
                        st.markdown("*No preview*")
                else:
                    st.markdown("*No preview*")

            with col_meta:
                axis_html_parts = []
                if extracted and extracted.x_axis:
                    axis_html_parts.append(_axis_pill("x", extracted.x_axis))
                if extracted and extracted.y_axis:
                    axis_html_parts.append(_axis_pill("y", extracted.y_axis))
                if axis_html_parts:
                    st.markdown(
                        _section_label("Axes") + " ".join(axis_html_parts),
                        unsafe_allow_html=True,
                    )

                if fi.variables_compared:
                    vars_html = " ".join(
                        _pill(v, "#f3f4f6", "#374151")
                        for v in fi.variables_compared[:4]
                    )
                    st.markdown(
                        _section_label("Groups / Variables") + vars_html,
                        unsafe_allow_html=True,
                    )

                if fi.knowledge_base_tags:
                    tags_html = " ".join(
                        _pill(tag, *_TAG_COLORS[i % len(_TAG_COLORS)])
                        for i, tag in enumerate(fi.knowledge_base_tags)
                    )
                    st.markdown(
                        _section_label("Keywords") + tags_html,
                        unsafe_allow_html=True,
                    )

                if fi.quantitative_highlights:
                    highlights_html = " ".join(
                        _pill(h, "#f3f4f6", "#374151")
                        for h in fi.quantitative_highlights[:4]
                    )
                    st.markdown(
                        _section_label("Quantitative Highlights") + highlights_html,
                        unsafe_allow_html=True,
                    )

                st.markdown(_section_label("Significance"), unsafe_allow_html=True)
                st.markdown(fi.biological_significance)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("📄 Upload Document")

    uploaded_file = st.file_uploader(
        "Drag and drop your scientific PDF here",
        type=["pdf"],
        key=f"pdf_uploader_{st.session_state.uploader_key}",
    )

    if uploaded_file is not None:
        st.caption(f"**{uploaded_file.name}**")
        with st.container(height=420, border=True):
            _render_pdf_preview(bytes(uploaded_file.getbuffer()))

    client, client_err = init_datalab_client()
    if client is not None:
        st.success("✓ Analysis ready to run")
    else:
        st.error(f"Pipeline unavailable: {client_err}")

    analyze_button = st.button(
        "Run Analysis 🔍",
        disabled=(uploaded_file is None or client is None),
        type="primary",
        width="stretch",
    )


# ---------------------------------------------------------------------------
# Main panel — header + clear button
# ---------------------------------------------------------------------------

col_header, col_clear = st.columns([9, 1])

with col_header:
    st.header("🔬 Biotech Agentic Analyst")
    powered_by_html = """
        <div style='display: flex; align-items: center; gap: 10px; margin-top: 5px;'>
            <span style='font-size: 20px; color: #666;'>Powered by</span>
            <img src="https://cdn.prod.website-files.com/66cf2bfc3ed15b02da0ca770/66d07240057721394308addd_Logo%20(1).svg" width="80">
            <span style='font-size: 20px; color: #666;'>and</span>
            <img src="https://github.com/sitammeur/test-assets/blob/main/datalab-logo.png?raw=true" width="30">
            <span style='font-size: 20px; color: #666;'>and</span>
            <img src="https://files.buildwithfern.com/openrouter.docs.buildwithfern.com/docs/6f95fbca823560084c5593ea2aa4073f00710020e6a78f8a3f54e835d97a8a0b/content/assets/logo-white.svg" width="150">
        </div>
    """
    st.markdown(powered_by_html, unsafe_allow_html=True)
    st.markdown("")

with col_clear:
    if st.button("Clear ↺", width="stretch"):
        _reset_analysis_metrics(increment_uploader=True)
        st.rerun()


# ---------------------------------------------------------------------------
# Main panel — analysis execution
# ---------------------------------------------------------------------------

if analyze_button and uploaded_file is not None and client is not None:
    _reset_analysis_metrics()

    tmp_path: str | None = None
    pipeline_results: dict | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            tmp_path = tmp_file.name

        with st.status(
            "Running Document Processing...", expanded=True
        ) as status_pipeline:
            st.write("Uploading and running convert → extract steps…")
            try:
                from datalab_sdk.exceptions import DatalabAPIError, DatalabTimeoutError

                pipeline_results = run_science_pipeline(client, None, tmp_path)
                figures, page_count, quality_score, extraction_score = (
                    parse_pipeline_results(pipeline_results)
                )
                st.session_state.page_count = page_count
                st.session_state.quality_score = quality_score
                st.session_state.extraction_score = extraction_score
                st.write(f"Extracted {len(figures)} figures from {page_count} pages")
                status_pipeline.update(
                    label="Document processing completed",
                    state="complete",
                    expanded=False,
                )
                st.session_state.pipeline_steps = []
            except (DatalabAPIError, DatalabTimeoutError) as exc:
                status_pipeline.update(label="Datalab pipeline failed", state="error")
                st.error(f"Datalab error: {exc}")
                st.stop()
            except RuntimeError as exc:
                status_pipeline.update(label="Result parsing failed", state="error")
                st.error(str(exc))
                if pipeline_results is not None:
                    raw_schema = getattr(
                        pipeline_results.get("extract"), "extraction_schema_json", None
                    )
                    if raw_schema is not None:
                        with st.expander("Raw extraction_schema_json (for debugging)"):
                            st.code(str(raw_schema)[:4000], language="json")
                st.stop()

        if not figures:
            st.warning(
                "No figures were extracted from this document. "
                "The PDF may not contain charts or the extraction quality was too low."
            )
            if pipeline_results is not None:
                raw_schema = getattr(
                    pipeline_results.get("extract"), "extraction_schema_json", None
                )
                if raw_schema is not None:
                    with st.expander("Debug: raw extraction_schema_json"):
                        st.code(str(raw_schema)[:4000], language="json")
            st.stop()

        with st.status("Analyzing Figures...", expanded=True) as status_analyst:
            st.write(f"Running Agent analysis over {len(figures)} figures…")
            flow = ScienceFlow()
            flow.state.figures = figures
            flow.state.file_path = tmp_path

            try:
                flow.kickoff()
            except Exception as exc:
                status_analyst.update(label="Figure analysis failed", state="error")
                st.error(f"Figure Analyst agent error: {exc}")
                st.stop()

            if flow.state.quality == "poor":
                status_analyst.update(
                    label="Figure analysis skipped — no usable figures", state="error"
                )
                st.warning(flow.state.error or "No usable figures detected.")
            else:
                n = len(flow.state.figure_intelligences)
                q = st.session_state.quality_score
                q_str = f" · parse quality {round(q, 1)}/5" if q is not None else ""
                label = (
                    f"Figure intelligence generated · {n} figures interpreted{q_str}"
                )
                st.write(label)
                status_analyst.update(label=label, state="complete", expanded=False)
                st.session_state.pipeline_steps.append(label)

        st.session_state.flow_state = flow.state
        st.rerun()

    except Exception as exc:
        st.error(f"Unexpected error: {exc}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Main panel — results display
# ---------------------------------------------------------------------------

if st.session_state.flow_state is not None and uploaded_file is not None:
    state: ScienceFlowState = st.session_state.flow_state
    for step in st.session_state.pipeline_steps:
        st.markdown(
            f'<span style="color:#16a34a;font-size:1.1em">●</span>' f"&nbsp; {step}",
            unsafe_allow_html=True,
        )
    if st.session_state.pipeline_steps:
        st.markdown("")

    _render_figure_intelligence_tab(state)
