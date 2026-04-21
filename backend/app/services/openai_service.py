from __future__ import annotations

import json
import re
from uuid import uuid4

from openai import OpenAI

from app.config import settings
from app.prompts import SYSTEM_PROMPT, build_generation_prompt, build_image_prompt
from app.schemas import GenerationRequest, GenerationResponse, SlideContent, SlideResponse


class OpenAIStudioService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def generate_carousel(self, request: GenerationRequest) -> GenerationResponse:
        requested_slide_count = request.slide_count if request.format == "carousel" else 1
        slide_contents = self._generate_structured_slides(
            request.prompt,
            request.format,
            requested_slide_count,
        )
        slides: list[SlideResponse] = []

        for index, slide_content in enumerate(slide_contents, start=1):
            image_prompt = build_image_prompt(
                slide_content.title,
                slide_content.text,
                index,
                request.format,
            )
            image_url = self._generate_slide_image(image_prompt, index, request.format)
            slides.append(
                SlideResponse(
                    id=f"slide-{uuid4().hex[:8]}",
                    index=index,
                    title=slide_content.title.strip(),
                    text=slide_content.text.strip(),
                    image_prompt=image_prompt,
                    image_url=image_url,
                    format=request.format,
                )
            )

        return GenerationResponse(
            prompt=request.prompt,
            format=request.format,
            slide_count=len(slides),
            slides=slides,
        )

    def _generate_structured_slides(
        self,
        user_prompt: str,
        selected_format: str,
        slide_count: int,
    ) -> list[SlideContent]:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        try:
            response = self.client.responses.create(
                model=settings.text_model,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_generation_prompt(user_prompt, selected_format, slide_count),
                    },
                ],
            )
        except Exception as exc:
            raise RuntimeError(f"Text generation failed: {exc}") from exc

        raw_output = (response.output_text or "").strip()
        if not raw_output:
            raise RuntimeError("The text model returned an empty response.")

        data = _parse_json_array(raw_output)
        if data is None:
            raise RuntimeError("The text model did not return valid JSON.")

        if not isinstance(data, list) or len(data) != slide_count:
            raise RuntimeError(f"The text model did not return exactly {slide_count} slides.")

        try:
            return [SlideContent.model_validate(item) for item in data]
        except Exception as exc:
            raise RuntimeError(f"The text model returned slides in an invalid format: {exc}") from exc

    def _generate_slide_image(self, image_prompt: str, slide_index: int, selected_format: str) -> str:
        if not self.client:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        size = {
            "carousel": "1024x1024",
            "post": "1024x1024",
            "story": "1024x1536",
        }[selected_format]

        try:
            response = self.client.images.generate(
                model=settings.image_model,
                prompt=image_prompt,
                size=size,
            )
        except Exception as exc:
            raise RuntimeError(f"Image generation failed for slide {slide_index}: {exc}") from exc

        if not getattr(response, "data", None):
            raise RuntimeError(f"The image model returned no data for slide {slide_index}.")

        image_data = response.data[0]
        if getattr(image_data, "url", None):
            return image_data.url
        if getattr(image_data, "b64_json", None):
            return f"data:image/png;base64,{image_data.b64_json}"

        raise RuntimeError(f"The image model did not return a usable image for slide {slide_index}.")


def _parse_json_array(raw_output: str):
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        pass

    fenced_match = re.search(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", raw_output)
    if fenced_match:
        try:
            return json.loads(fenced_match.group(1))
        except json.JSONDecodeError:
            pass

    array_match = re.search(r"(\[[\s\S]*\])", raw_output)
    if array_match:
        try:
            return json.loads(array_match.group(1))
        except json.JSONDecodeError:
            return None

    return None
