from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


FormatType = Literal["carousel", "post", "story"]


class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=2000)
    format: FormatType = "carousel"
    slide_count: int = Field(default=5, ge=3, le=8)


class SlideContent(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    text: str = Field(..., min_length=1, max_length=220)


class SlideResponse(SlideContent):
    id: str
    index: int
    image_prompt: str
    image_url: str | None = None
    format: FormatType


class GenerationResponse(BaseModel):
    prompt: str
    format: FormatType
    slide_count: int
    slides: list[SlideResponse]
