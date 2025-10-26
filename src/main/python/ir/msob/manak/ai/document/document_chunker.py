import logging
from typing import List

from haystack.dataclasses import Document

from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse
from src.main.python.ir.msob.manak.ai.document.utils.utils import (
    read_markdown_file,
    split_markdown_to_sections
)

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Generic document chunker that supports multiple file types.
    Currently, supports: markdown (.md)
    """

    def __init__(self):
        self.config = ConfigConfiguration().get_properties()
        # Ensure overlap is non-negative and smaller than chunk size
        self.chunk_size = max(1, self.config.application.milvus.document.chunk.chunk_words_size)
        self.overlap = min(self.chunk_size - 1, max(0, self.config.application.milvus.document.chunk.chunk_overlap))

        logger.info(
            f"DocumentChunker initialized (chunk_size={self.chunk_size}, overlap={self.overlap})"
        )

    def chunk_file(self, res: DocumentResponse, content: str) -> List[Document]:
        mime_type = res.mime_type.lower().strip()

        if mime_type in [
            "text/markdown",
            "text/x-markdown",
            "application/markdown"
        ]:
            return self._chunk_markdown(res, content)
        else:
            raise NotImplementedError(f"Unsupported mime type: {mime_type}")

    # ============================================================
    # MARKDOWN CHUNKING
    # ============================================================
    def _chunk_markdown(self, res: DocumentResponse, content: str) -> List[Document]:
        logger.info(f"Chunking markdown file: {res.file_path}")

        text, meta = read_markdown_file(res, content)
        res.meta = meta

        sections = split_markdown_to_sections(text)
        logger.debug(f"Markdown split into {len(sections)} sections before chunking.")

        chunks: List[Document] = []
        chunk_counter = 0

        for section_idx, section in enumerate(sections):
            sub_chunks = self._split_text_into_chunks(section)
            for sub_chunk in sub_chunks:
                chunk_id = f"{res.document_id}_{chunk_counter}"
                chunks.append(
                    Document(
                        id=chunk_id,
                        content=sub_chunk,
                        meta={
                            "source": res.file_path,
                            "doc_id": res.document_id,
                            "chunk_id": chunk_id,
                            "chunk_order": chunk_counter,
                            "type": "chunk",
                            "section_index": section_idx,
                            "original_section_length": len(section.split())
                        },
                    )
                )
                logger.debug(f"Created chunk {chunk_id} ({len(sub_chunk.split())} words).")
                chunk_counter += 1

        logger.info(f"✅ Created {len(chunks)} chunks from markdown file: {res.file_path}")
        return chunks

    # ============================================================
    # SHARED TEXT SPLITTER
    # ============================================================
    def _split_text_into_chunks(self, text: str) -> List[str]:
        words = text.split()
        if not words:
            return []

        chunks = []
        step = max(1, self.chunk_size - self.overlap)
        start = 0

        while start < len(words):
            end = start + self.chunk_size
            chunks.append(" ".join(words[start:end]))
            start += step

        logger.debug(f"Generated {len(chunks)} chunks from section ({len(words)} words total).")
        return chunks
