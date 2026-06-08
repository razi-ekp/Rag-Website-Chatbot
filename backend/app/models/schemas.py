from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from enum import Enum


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    FALLBACK = "FALLBACK"


class IngestRequest(BaseModel):
    url: str = Field(..., description="Website URL to crawl and ingest")
    max_pages: Optional[int] = Field(None, description="Max pages to crawl (overrides default)")


class IngestStatus(BaseModel):
    site_id: str
    url: str
    status: str  # "crawling" | "indexing" | "ready" | "error"
    pages_crawled: int
    total_chunks: int
    message: Optional[str] = None


class CrawlProgress(BaseModel):
    url: str
    pages_found: int
    pages_crawled: int
    current_page: str
    status: str


class ChatRequest(BaseModel):
    site_id: str
    question: str = Field(..., min_length=1, max_length=1000)
    chat_history: Optional[List[dict]] = Field(default_factory=list)


class SourceChunk(BaseModel):
    url: str
    title: str
    snippet: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    confidence: ConfidenceLevel
    confidence_score: float
    sources: List[SourceChunk]
    is_injection: bool = False
    suggested_followups: Optional[List[str]] = None


class SuggestedQuestion(BaseModel):
    question: str
    category: str


class SiteInfo(BaseModel):
    site_id: str
    url: str
    title: str
    pages_count: int
    chunks_count: int
    status: str
    ingested_at: str


class InjectionCheckResult(BaseModel):
    is_injection: bool
    reason: Optional[str] = None
    sanitized_input: Optional[str] = None
