from typing import List
from app.core.config import settings


class TextChunk:
    def __init__(self, text: str, url: str, title: str, chunk_index: int):
        self.text = text
        self.url = url
        self.title = title
        self.chunk_index = chunk_index
        self.id = f"{url}::chunk_{chunk_index}"


class TextChunker:
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def chunk_text(self, text: str, url: str, title: str) -> List[TextChunk]:
        if not text or len(text.strip()) < 50:
            return []

        words = text.split()
        chunks = []
        chunk_index = 0
        start = 0

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            if len(chunk_text.strip()) > 30:
                chunks.append(
                    TextChunk(
                        text=chunk_text,
                        url=url,
                        title=title,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1

            if end == len(words):
                break

            start = end - self.chunk_overlap

        return chunks
