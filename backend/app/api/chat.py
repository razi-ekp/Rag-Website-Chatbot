import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ConfidenceLevel,
    SourceChunk,
)
from app.services.llm_service import llm_service
from app.services.site_manager import site_manager
from app.services.vector_store import vector_store
from app.utils.injection_detector import injection_detector

router = APIRouter(prefix="/chat", tags=["Chat"])


def _build_sources(chunks: list) -> list[SourceChunk]:
    seen_urls = set()
    sources = []
    for chunk in chunks:
        url = chunk["url"]
        if url not in seen_urls:
            seen_urls.add(url)
            sources.append(
                SourceChunk(
                    url=url,
                    title=chunk["title"],
                    snippet=chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"],
                    score=chunk["score"],
                )
            )
    return sources[:5]


def _get_confidence(chunks: list) -> tuple[ConfidenceLevel, float]:
    if not chunks:
        return ConfidenceLevel.FALLBACK, 0.0
    top = chunks[0]["score"]
    from app.core.config import settings
    if top >= settings.CONFIDENCE_HIGH_THRESHOLD:
        return ConfidenceLevel.HIGH, top
    elif top >= settings.CONFIDENCE_MEDIUM_THRESHOLD:
        return ConfidenceLevel.MEDIUM, top
    else:
        return ConfidenceLevel.LOW, top


@router.post("/ask", response_model=ChatResponse)
async def ask(request: ChatRequest):
    site = site_manager.get_site(request.site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found. Please ingest a website first.")
    if site["status"] != "ready":
        raise HTTPException(status_code=400, detail=f"Site is not ready yet. Status: {site['status']}")

    injection_result = injection_detector.check(request.question)
    if injection_result.is_injection:
        return ChatResponse(
            answer="⚠️ Your message was flagged as a potential prompt injection attempt and cannot be processed.",
            confidence=ConfidenceLevel.FALLBACK,
            confidence_score=0.0,
            sources=[],
            is_injection=True,
        )

    chunks = vector_store.query(request.site_id, request.question)
    confidence, score = _get_confidence(chunks)
    sources = _build_sources(chunks)

    answer = await llm_service.get_answer(
        question=request.question,
        chunks=chunks,
        chat_history=request.chat_history,
    )

    return ChatResponse(
        answer=answer,
        confidence=confidence,
        confidence_score=round(score, 4),
        sources=sources,
        is_injection=False,
    )


@router.post("/stream")
async def stream_ask(request: ChatRequest):
    site = site_manager.get_site(request.site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found.")
    if site["status"] != "ready":
        raise HTTPException(status_code=400, detail=f"Site not ready. Status: {site['status']}")

    injection_result = injection_detector.check(request.question)
    chunks = vector_store.query(request.site_id, request.question)
    confidence, score = _get_confidence(chunks)
    sources = _build_sources(chunks)

    async def event_generator() -> AsyncGenerator[str, None]:
        # Send metadata first
        meta = {
            "type": "meta",
            "confidence": confidence.value,
            "confidence_score": score,
            "sources": [s.model_dump() for s in sources],
            "is_injection": injection_result.is_injection,
        }
        yield f"data: {json.dumps(meta)}\n\n"

        if injection_result.is_injection:
            msg = {"type": "token", "content": "⚠️ Prompt injection detected. Message blocked."}
            yield f"data: {json.dumps(msg)}\n\n"
        else:
            async for token in llm_service.stream_answer(
                question=request.question,
                chunks=chunks,
                chat_history=request.chat_history,
            ):
                payload = {"type": "token", "content": token}
                yield f"data: {json.dumps(payload)}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/suggested/{site_id}")
async def get_suggested_questions(site_id: str):
    site = site_manager.get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return {"questions": site.get("suggested_questions", [])}
