from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ExtractedFigure(BaseModel):
    """Extracted figure from the document."""

    figure_id: str
    page_number: int
    chart_type: str
    title: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    data_summary: str
    conditions: list[str] = Field(default_factory=list)
    caption: str
    thumbnail_b64: Optional[str] = None


class FigureIntelligence(BaseModel):
    """Figure intelligence."""

    figure_id: str
    chart_type: str
    key_finding: str
    variables_compared: list[str] = Field(default_factory=list)
    quantitative_highlights: list[str] = Field(default_factory=list)
    biological_significance: str
    knowledge_base_tags: list[str] = Field(default_factory=list)


class FigureIntelligenceList(BaseModel):
    """List of figure intelligences."""

    figures: list[FigureIntelligence] = Field(default_factory=list)
