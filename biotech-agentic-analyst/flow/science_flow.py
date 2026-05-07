from __future__ import annotations

import base64
import os
import tempfile
import time
from typing import Any

from crewai.flow.flow import Flow, listen, router, start

from flow.crews.figure_analyst.crew import FigureAnalystCrew
from flow.state import ScienceFlowState

_MAX_RETRIES = 2
_RETRY_DELAY = 3  # seconds between retries


def _require_pydantic(result: Any, step_name: str) -> Any:
    if result.pydantic is None:
        raise ValueError(
            f"{step_name} produced no structured output: {result.raw[:200]}"
        )
    return result.pydantic


class ScienceFlow(Flow[ScienceFlowState]):
    """Orchestrates figure analysis."""

    @start()
    def validate_extraction(self):
        if not self.state.figures:
            self.state.quality = "poor"
            self.state.error = "No figures extracted from document."
        else:
            self.state.quality = "good"
        return self.state.quality

    @router(validate_extraction)
    def route_on_quality(self, quality: str):
        if quality == "good":
            return "analyze"
        return "abort"

    @listen("analyze")
    def analyze_figures(self):
        all_intelligences = []
        for f in self.state.figures:
            tmp_path: str | None = None
            try:
                fig_dict = f.model_dump(exclude={"thumbnail_b64"})
                if f.thumbnail_b64:
                    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    tmp.write(base64.b64decode(f.thumbnail_b64))
                    tmp.close()
                    tmp_path = tmp.name
                    fig_dict["image_path"] = tmp_path

                last_exc: Exception | None = None
                for attempt in range(1 + _MAX_RETRIES):
                    try:
                        result = (
                            FigureAnalystCrew()
                            .crew()
                            .kickoff(inputs={"figures": [fig_dict]})
                        )
                        out = _require_pydantic(
                            result, f"Figure analyst ({f.figure_id})"
                        )
                        all_intelligences.extend(out.figures)
                        last_exc = None
                        break
                    except Exception as exc:
                        last_exc = exc
                        if attempt < _MAX_RETRIES:
                            print(
                                f"[ScienceFlow] {f.figure_id} attempt {attempt + 1} failed "
                                f"({type(exc).__name__}), retrying in {_RETRY_DELAY}s…"
                            )
                            time.sleep(_RETRY_DELAY)

                if last_exc is not None:
                    print(
                        f"[ScienceFlow] Skipping {f.figure_id} after {1 + _MAX_RETRIES} attempts: {last_exc}"
                    )
            finally:
                if tmp_path:
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass

        self.state.figure_intelligences = all_intelligences
        return "analyzed"

    @listen("abort")
    def handle_poor_quality(self):
        return "aborted"
