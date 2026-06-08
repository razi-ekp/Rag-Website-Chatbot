import pytest
from app.utils.chunker import TextChunker, TextChunk


class TestTextChunker:
    def setup_method(self):
        self.chunker = TextChunker(chunk_size=50, chunk_overlap=10)

    def test_basic_chunking(self):
        text = " ".join([f"word{i}" for i in range(200)])
        chunks = self.chunker.chunk_text(text, "http://example.com", "Test Page")
        assert len(chunks) > 1

    def test_short_text_returns_one_chunk(self):
        text = "This is a short paragraph with enough words."
        chunks = self.chunker.chunk_text(text, "http://example.com", "Test")
        assert len(chunks) == 1

    def test_empty_text_returns_empty(self):
        chunks = self.chunker.chunk_text("", "http://example.com", "Test")
        assert chunks == []

    def test_very_short_text_skipped(self):
        chunks = self.chunker.chunk_text("hi", "http://example.com", "Test")
        assert chunks == []

    def test_chunk_has_correct_url(self):
        text = " ".join([f"word{i}" for i in range(100)])
        chunks = self.chunker.chunk_text(text, "http://example.com/page", "Page Title")
        for chunk in chunks:
            assert chunk.url == "http://example.com/page"

    def test_chunk_has_correct_title(self):
        text = " ".join([f"word{i}" for i in range(100)])
        chunks = self.chunker.chunk_text(text, "http://example.com", "My Title")
        for chunk in chunks:
            assert chunk.title == "My Title"

    def test_chunk_ids_are_unique(self):
        text = " ".join([f"word{i}" for i in range(200)])
        chunks = self.chunker.chunk_text(text, "http://example.com", "Test")
        ids = [c.id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_index_increments(self):
        text = " ".join([f"word{i}" for i in range(200)])
        chunks = self.chunker.chunk_text(text, "http://example.com", "Test")
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_overlap_produces_more_chunks(self):
        text = " ".join([f"word{i}" for i in range(200)])
        chunker_no_overlap = TextChunker(chunk_size=50, chunk_overlap=0)
        chunker_with_overlap = TextChunker(chunk_size=50, chunk_overlap=20)
        chunks_no = chunker_no_overlap.chunk_text(text, "http://example.com", "Test")
        chunks_with = chunker_with_overlap.chunk_text(text, "http://example.com", "Test")
        assert len(chunks_with) >= len(chunks_no)

    def test_chunk_text_not_empty(self):
        text = " ".join([f"word{i}" for i in range(100)])
        chunks = self.chunker.chunk_text(text, "http://example.com", "Test")
        for chunk in chunks:
            assert len(chunk.text.strip()) > 0

    def test_none_text_handling(self):
        chunks = self.chunker.chunk_text(None, "http://example.com", "Test")
        assert chunks == []

    def test_whitespace_only_text(self):
        chunks = self.chunker.chunk_text("   \n\n   ", "http://example.com", "Test")
        assert chunks == []
