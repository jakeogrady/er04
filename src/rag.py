"""Module that batches chunks and finds most useful chunks to query."""

import logging
from collections.abc import Generator
from itertools import batched
from typing import Any

from docling.document_converter import DocumentConverter
from sentence_transformers import SentenceTransformer, util
from torch import Tensor

MAX_CHUNK_SIZE = 2500
TOP_K_CHUNKS = 3

logger = logging.getLogger(__name__)


class RagModel:
    """Class responsible for finding most useful chunks to query."""

    def __init__(self, embedder: SentenceTransformer) -> None:
        """Embedder is used to encode query and chunks."""
        self.embedder = embedder

    def chunk_text(self, text: str) -> list[str]:
        """Split text into smaller chunks for RAG."""
        chunks = []
        current_chunk = ""
        paragraphs = text.split("\n")

        for para in paragraphs:
            if len(current_chunk) + len(para) > MAX_CHUNK_SIZE:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            else:
                current_chunk += para + "\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def embed_chunks(self, chunks: list[str]) -> Tensor:
        """Embed chunks into RAG."""
        return self.embedder.encode(chunks, convert_to_tensor=True)

    def embed_query(self, query: str) -> Tensor:
        """Embed user query for RAG similarity."""
        return self.embedder.encode(query)

    def retrieve_chunks(
        self, query: str, chunks: list[str]
    ) -> list[list[dict[str, int | float]]]:
        """Embed chunks and query to retrieve similar chunks."""
        embedded_chunks = self.embed_chunks(chunks)
        embedded_query = self.embed_query(query)

        return util.semantic_search(embedded_query, embedded_chunks, top_k=TOP_K_CHUNKS)

    def retrieve_batched_chunks(
        self, query: str, chunks: list[str], num_chunks: int = 3
    ) -> Generator[list[list[dict[str, int | float]]], Any, None]:
        """Return batch of chunks instead of feeding all chunks to LLM at once."""
        batched_chunks = list(batched(chunks, num_chunks))
        for chunk in batched_chunks:
            yield self.retrieve_chunks(query, list(chunk))


if __name__ == "__main__":
    reader = DocumentConverter()

    result = reader.convert("../bitcoin.pdf")
    md_document = result.document.export_to_markdown()

    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    rag_model = RagModel(embedder)

    chunks = rag_model.chunk_text(md_document)

    for index, batch in enumerate(
        rag_model.retrieve_batched_chunks(md_document, chunks)
    ):
        logger.info(f"\n\nBatch {index + 1} {batch}")
        most_similar_doc = chunks[batch[0][0]["corpus_id"]]
        logger.info(f"Most Similar Chunk {most_similar_doc}")
