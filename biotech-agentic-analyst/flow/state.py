from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field
from models import ExtractedFigure, FigureIntelligence


class ScienceFlowState(BaseModel):
    """State for the science flow."""

    file_path: str = ""
    figures: list[ExtractedFigure] = Field(default_factory=list)
    figure_intelligences: list[FigureIntelligence] = Field(default_factory=list)
    quality: str = "unknown"
    error: Optional[str] = None
