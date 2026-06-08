import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api import chat, ingest
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    logger.info("RAG Website Chatbot API starting up...")
    logger.info(f"GROQ Model: {settings.GROQ_MODEL}")
    logger.info(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    yield
    logger.info("API shutting down.")


app = FastAPI(
    title="RAG Website Chatbot API",
    description="A production-ready RAG chatbot that crawls websites and answers questions using LLM.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    return {"message": "RAG Website Chatbot API", "version": "1.0.0", "status": "running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
