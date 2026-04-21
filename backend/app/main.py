from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import GenerationRequest, GenerationResponse
from app.services.openai_service import OpenAIStudioService


app = FastAPI(title="Cuemath Carousel API", version="0.2.0")
service = OpenAIStudioService()
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate", response_model=GenerationResponse)
def generate_content(request: GenerationRequest) -> GenerationResponse:
    try:
        return service.generate_carousel(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected error while generating content")
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc}") from exc
