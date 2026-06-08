import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from app.models.schemas import IngestRequest, SiteInfo
from app.services.crawler import WebCrawler
from app.services.llm_service import llm_service
from app.services.site_manager import site_manager
from app.services.vector_store import vector_store
from app.utils.chunker import TextChunker

router = APIRouter(prefix="/ingest", tags=["Ingest"])
chunker = TextChunker()


async def _crawl_and_index(site_id: str, url: str, max_pages: int):
    crawler = WebCrawler(max_pages=max_pages)
    all_chunks = []
    pages_count = 0
    first_content = ""

    try:
        site_manager.update_site(site_id, status="crawling")

        async for event in crawler.crawl(url):
            if event["type"] == "page":
                page_chunks = chunker.chunk_text(
                    text=event["content"],
                    url=event["url"],
                    title=event["title"],
                )
                all_chunks.extend(page_chunks)
                pages_count += 1

                if not first_content and event["content"]:
                    first_content = event["content"]

                site_manager.update_site(
                    site_id,
                    pages_count=pages_count,
                    title=event["title"] if pages_count == 1 else site_manager.get_site(site_id)["title"],
                )

            elif event["type"] == "done":
                break

        if all_chunks:
            site_manager.update_site(site_id, status="indexing")
            total_indexed = vector_store.index_chunks(site_id, all_chunks)
            suggested = await llm_service.generate_suggested_questions(first_content)

            site_manager.update_site(
                site_id,
                status="ready",
                chunks_count=total_indexed,
                suggested_questions=suggested,
            )
            logger.info(f"Site {site_id} ready: {pages_count} pages, {total_indexed} chunks")
        else:
            site_manager.update_site(site_id, status="error", message="No content found")

    except Exception as e:
        logger.error(f"Ingest error for {site_id}: {e}")
        site_manager.update_site(site_id, status="error", message=str(e))


@router.post("/start")
async def start_ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    url = str(request.url).rstrip("/")
    site_id = site_manager.generate_site_id(url)

    existing = site_manager.get_site(site_id)
    if existing and existing["status"] == "ready":
        return {"site_id": site_id, "message": "Already indexed", "status": "ready"}

    site_manager.create_site(url)
    max_pages = request.max_pages or 50

    background_tasks.add_task(_crawl_and_index, site_id, url, max_pages)

    return {"site_id": site_id, "message": "Ingestion started", "status": "crawling"}


@router.get("/stream/{site_id}")
async def stream_progress(site_id: str):
    async def event_generator() -> AsyncGenerator[str, None]:
        while True:
            site = site_manager.get_site(site_id)
            if not site:
                yield f"data: {json.dumps({'error': 'Site not found'})}\n\n"
                break

            payload = {
                "status": site["status"],
                "pages_crawled": site.get("pages_count", 0),
                "chunks_count": site.get("chunks_count", 0),
                "title": site.get("title", ""),
            }
            yield f"data: {json.dumps(payload)}\n\n"

            if site["status"] in ("ready", "error"):
                break

            await asyncio.sleep(1.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/status/{site_id}")
async def get_status(site_id: str):
    site = site_manager.get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.get("/sites", response_model=list)
async def list_sites():
    return site_manager.get_all_sites()


@router.delete("/sites/{site_id}")
async def delete_site(site_id: str):
    if not site_manager.site_exists(site_id):
        raise HTTPException(status_code=404, detail="Site not found")
    vector_store.delete_site(site_id)
    site_manager.delete_site(site_id)
    return {"message": "Site deleted successfully"}
