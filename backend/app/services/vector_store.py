import hashlib
import os
from typing import Dict, List, Optional, Tuple

import chromadb
from chromadb import Settings as ChromaSettings
from loguru import logger
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.utils.chunker import TextChunk


class VectorStore:
    def __init__(self):
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(
    path=settings.CHROMA_PERSIST_DIR,
        )
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded.")

    def _get_or_create_collection(self, site_id: str):
        return self.client.get_or_create_collection(
            name=f"site_{site_id}",
            metadata={"hnsw:space": "cosine"},
        )

    def _collection_exists(self, site_id: str) -> bool:
        try:
            self.client.get_collection(f"site_{site_id}")
            return True
        except Exception:
            return False

    def delete_site(self, site_id: str):
        try:
            self.client.delete_collection(f"site_{site_id}")
            logger.info(f"Deleted collection for site {site_id}")
        except Exception as e:
            logger.warning(f"Could not delete collection {site_id}: {e}")

    def index_chunks(self, site_id: str, chunks: List[TextChunk]) -> int:
        if not chunks:
            return 0

        collection = self._get_or_create_collection(site_id)

        batch_size = 64
        total_indexed = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c.text for c in batch]
            ids = [
                hashlib.md5(c.id.encode()).hexdigest() for c in batch
            ]
            metadatas = [
                {"url": c.url, "title": c.title, "chunk_index": c.chunk_index}
                for c in batch
            ]

            embeddings = self.embedder.encode(texts, show_progress_bar=False).tolist()

            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
            total_indexed += len(batch)
            logger.debug(f"Indexed batch {i//batch_size + 1}: {len(batch)} chunks")

        logger.info(f"Total indexed for site {site_id}: {total_indexed} chunks")
        return total_indexed

    def query(
        self,
        site_id: str,
        query_text: str,
        top_k: int = None,
    ) -> List[Dict]:
        if not self._collection_exists(site_id):
            return []

        top_k = top_k or settings.TOP_K_RESULTS
        collection = self._get_or_create_collection(site_id)

        query_embedding = self.embedder.encode([query_text], show_progress_bar=False).tolist()

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        if not results["documents"] or not results["documents"][0]:
            return []

        output = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            similarity = 1 - dist  # cosine distance -> similarity
            output.append(
                {
                    "text": doc,
                    "url": meta.get("url", ""),
                    "title": meta.get("title", ""),
                    "score": round(similarity, 4),
                }
            )

        return sorted(output, key=lambda x: x["score"], reverse=True)

    def get_collection_count(self, site_id: str) -> int:
        try:
            collection = self.client.get_collection(f"site_{site_id}")
            return collection.count()
        except Exception:
            return 0


vector_store = VectorStore()
