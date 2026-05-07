from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
import sys

import requests as _http

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import ExtractedFigure

_FIGURE_SCHEMA = {
    "type": "object",
    "properties": {
        "figures": {
            "type": "array",
            "description": "List of figures extracted from the document",
            "items": {
                "type": "object",
                "properties": {
                    "figure_id": {
                        "type": "string",
                        "description": "Figure label e.g. Figure 1, Fig. 2A",
                    },
                    "page_number": {
                        "type": "integer",
                        "description": "Page where the figure appears",
                    },
                    "chart_type": {
                        "type": "string",
                        "description": "bar, line, scatter, survival curve, dose-response, heatmap, Western blot, micrograph, other",
                    },
                    "title": {
                        "type": "string",
                        "description": "Figure title or caption headline",
                    },
                    "x_axis": {
                        "type": "string",
                        "description": "X-axis label and units if applicable",
                    },
                    "y_axis": {
                        "type": "string",
                        "description": "Y-axis label and units if applicable",
                    },
                    "data_summary": {
                        "type": "string",
                        "description": "Key values, ranges, or trends visible in the figure",
                    },
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Experimental conditions or comparison groups",
                    },
                    "caption": {
                        "type": "string",
                        "description": "Full figure caption text",
                    },
                },
            },
        }
    },
}

_IMG_SRC_RE = re.compile(r'<img[^>]+src="([^"]+)"')


def _build_citation_image_map(convert_result) -> dict:
    """Walk JSON blocks to map citation IDs and page indices to base64 image data.

    The extract step cites figures via Caption block IDs (e.g. /page/2/Caption/3)
    rather than Figure block IDs (/page/2/Figure/2). Both share the same page index,
    so we index by both the Figure block ID and the integer page index so either
    citation form resolves correctly.
    """
    data = getattr(convert_result, "json", None) or {}
    images: dict = getattr(convert_result, "images", {}) or {}
    citation_map: dict = {}

    def walk(blocks: list) -> None:
        for block in blocks:
            if block.get("block_type") == "Figure":
                block_id = block.get("id", "")  # e.g. /page/2/Figure/2
                m = _IMG_SRC_RE.search(block.get("html", ""))
                if m and block_id:
                    src = m.group(1)
                    b64 = images.get(src) or images.get(os.path.basename(src))
                    if b64:
                        citation_map[block_id] = b64
                        # Also index by page number so /page/2/Caption/3 resolves too
                        parts = block_id.split("/")
                        if len(parts) >= 3:
                            try:
                                citation_map[int(parts[2])] = b64
                            except ValueError:
                                pass
            walk(block.get("children", []))

    if isinstance(data, dict):
        walk(data.get("children", []))

    return citation_map


def _poll_for_scores(check_url: str, api_key: str, max_wait: int = 60) -> float | None:
    """Keep polling request_check_url until extraction_score_average appears."""
    headers = {"X-API-Key": api_key}
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            data = _http.get(check_url, headers=headers, timeout=10).json()
            if "extraction_score_average" in data:
                return float(data["extraction_score_average"])
        except Exception:
            pass
        time.sleep(2)
    return None


def run_science_pipeline(
    client,
    pipeline_id: str | None,  # kept for API compatibility, not used
    file_path: str,
    poll_interval: int = 1,
    timeout: int = 1800,
) -> dict:
    """Convert and extract figures using direct SDK calls (no pipeline overhead)."""
    from datalab_sdk import ConvertOptions, ExtractOptions

    convert_result = client.convert(
        file_path,
        options=ConvertOptions(
            mode="accurate",
            output_format="json",
            extras="chart_understanding",
            save_checkpoint=True,
        ),
        poll_interval=poll_interval,
        max_polls=timeout // max(poll_interval, 1),
    )

    if not getattr(convert_result, "success", False):
        error = getattr(convert_result, "error", None)
        raise RuntimeError(f"Conversion failed: {error}")

    extract_result = client.extract(
        options=ExtractOptions(
            page_schema=json.dumps(_FIGURE_SCHEMA),
            mode="accurate",
            checkpoint_id=convert_result.checkpoint_id,
        ),
        poll_interval=poll_interval,
        max_polls=timeout // max(poll_interval, 1),
    )

    if not getattr(extract_result, "success", False):
        error = getattr(extract_result, "error", None)
        raise RuntimeError(f"Extraction failed: {error}")

    # Continue polling for confidence scores (free beta feature — scores arrive
    # asynchronously after extraction completes).
    extraction_score_average: float | None = None
    check_url = getattr(extract_result, "request_check_url", None)
    api_key = os.getenv("DATALAB_API_KEY", "")
    if check_url and api_key:
        extraction_score_average = _poll_for_scores(check_url, api_key)

    return {
        "convert": convert_result,
        "extract": extract_result,
        "citation_image_map": _build_citation_image_map(convert_result),
        "extraction_score_average": extraction_score_average,
        "execution_id": None,
    }


def parse_pipeline_results(
    pipeline_results: dict,
) -> tuple[list[ExtractedFigure], int, float | None, float | None]:
    """Parse pipeline results into figures, page count, parse quality, extraction score."""
    convert_result = pipeline_results["convert"]
    extract_result = pipeline_results["extract"]
    citation_image_map: dict[str, str] = pipeline_results.get("citation_image_map", {})
    extraction_score_average: float | None = pipeline_results.get(
        "extraction_score_average"
    )

    page_count: int = getattr(convert_result, "page_count", 0) or 0
    _raw_quality = getattr(convert_result, "parse_quality_score", None)
    quality_score: float | None = float(_raw_quality) if _raw_quality else None

    try:
        raw = extract_result.extraction_schema_json
        if raw is None:
            raise ValueError(
                "extraction_schema_json is None — the extract step returned no structured data. "
                f"extract success={getattr(extract_result, 'success', '?')}, "
                f"error={getattr(extract_result, 'error', '?')}"
            )
        if isinstance(raw, str):
            pages_data = json.loads(raw)
        else:
            pages_data = raw

        figures: list[ExtractedFigure] = []

        if isinstance(pages_data, dict) and "figures" in pages_data:
            # flat document-level result: {"figures": [...]}
            all_figs = pages_data["figures"] or []
        elif isinstance(pages_data, dict) and "pages" in pages_data:
            # wrapped: {"pages": [{"figures": [...]}, ...]}
            all_figs = [
                f
                for page in pages_data["pages"]
                if isinstance(page, dict)
                for f in (page.get("figures") or [])
            ]
        elif isinstance(pages_data, dict):
            # keyed by page index: {"0": {"figures": [...]}, ...}
            all_figs = [
                f
                for page in pages_data.values()
                if isinstance(page, dict)
                for f in (page.get("figures") or [])
            ]
        elif isinstance(pages_data, list):
            # Detect flat list of figure objects vs list of per-page dicts.
            # A per-page dict has a "figures" key; a figure object has "figure_id".
            first = next((item for item in pages_data if isinstance(item, dict)), None)
            if first is not None and "figures" not in first and "figure_id" in first:
                # flat list of figure objects
                all_figs = [item for item in pages_data if isinstance(item, dict)]
            else:
                # list of per-page dicts: [{"figures": [...]}, ...]
                all_figs = [
                    f
                    for page in pages_data
                    if isinstance(page, dict)
                    for f in (page.get("figures") or [])
                ]
        else:
            raise ValueError(
                f"Unrecognised extraction_schema_json structure: type={type(pages_data).__name__}, "
                f"value={str(pages_data)[:200]}"
            )

        for fig in all_figs:
            page_num = fig.get("page_number", 0)
            # Resolve thumbnail via citation IDs. The extract step may cite Caption blocks
            # (/page/N/Caption/X) rather than Figure blocks (/page/N/Figure/X);
            # _build_citation_image_map indexes by both block ID and page index (int).
            thumb: str | None = None
            for citation in fig.get("figure_id_citations", []):
                thumb = citation_image_map.get(citation)
                if thumb:
                    break
                parts = citation.split("/")
                if len(parts) >= 3:
                    try:
                        thumb = citation_image_map.get(int(parts[2]))
                        if thumb:
                            break
                    except ValueError:
                        pass
            if not thumb:
                thumb = citation_image_map.get(page_num)

            figures.append(
                ExtractedFigure(
                    figure_id=fig.get("figure_id", f"Figure {len(figures)+1}"),
                    page_number=page_num,
                    chart_type=fig.get("chart_type", "unknown"),
                    title=fig.get("title", ""),
                    x_axis=fig.get("x_axis"),
                    y_axis=fig.get("y_axis"),
                    data_summary=fig.get("data_summary", ""),
                    conditions=fig.get("conditions") or [],
                    caption=fig.get("caption", ""),
                    thumbnail_b64=thumb,
                )
            )

        return figures, page_count, quality_score, extraction_score_average

    except Exception as exc:
        raise RuntimeError(f"Failed to parse extraction results: {exc}") from exc
