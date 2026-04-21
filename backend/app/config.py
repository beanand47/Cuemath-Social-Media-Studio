from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    text_model: str = os.getenv("OPENAI_TEXT_MODEL", "gpt-5.4-mini")
    image_model: str = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    )


settings = Settings()
