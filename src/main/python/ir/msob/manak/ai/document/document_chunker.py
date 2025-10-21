import logging
from typing import List

from haystack.dataclasses import Document

from src.main.python.ir.msob.manak.ai.config.config import ConfigLoader
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
        # 🔹 Load configuration
        self.config = ConfigLoader().get_config()

        logger.info(
            f"DocumentChunker initialized (chunk_size={self.config.application.milvus.document.chunk.chunk_words_size}, overlap={self.config.application.milvus.document.chunk.chunk_overlap})"
        )

    def chunk_file(self, res: DocumentResponse, content: str) -> List[Document]:
        """
        Dispatch method — calls the right chunking logic based on file_type.
        """
        file_type = res.file_type.lower().strip()

        if file_type in ["md", "markdown"]:
            return self._chunk_markdown(res, content)
        else:
            raise NotImplementedError(f"Unsupported file type: {file_type}")

    # ============================================================
    # MARKDOWN CHUNKING
    # ============================================================
    def _chunk_markdown(self, res: DocumentResponse, content: str) -> List[Document]:
        """
        Splits a markdown file into smaller chunks using configured size and overlap.
        """
        logger.info(f"Chunking markdown file: {res.file_path}")

        text, meta = read_markdown_file(res, content)
        res.meta = meta

        # Split by markdown headers (section-level split)
        sections = split_markdown_to_sections(text)
        logger.debug(f"Markdown split into {len(sections)} sections before chunking.")

        chunks: List[Document] = []
        chunk_counter = 0

        for section_idx, section in enumerate(sections):
            sub_chunks = self._split_text_into_chunks(section)
            for sub_chunk in sub_chunks:
                chunk_id = f"{res.id}_{chunk_counter}"
                chunks.append(
                    Document(
                        id=chunk_id,
                        content=sub_chunk,
                        meta={
                            "source": res.file_path,
                            "doc_id": res.id,
                            "chunk_id": chunk_id,
                            "chunk_order": chunk_counter,
                            "type": "chunk",
                            "section_index": section_idx,
                            "original_section_length": len(section)
                        },
                    )
                )
                chunk_counter += 1

        logger.info(f"✅ Created {len(chunks)} chunks from markdown file: {res.file_path}")
        return chunks

    # ============================================================
    # SHARED TEXT SPLITTER
    # ============================================================
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """
        Generic text splitter with overlap.
        """
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = start + self.config.application.milvus.document.chunk.chunk_words_size
            chunk_words = words[start:end]
            chunks.append(" ".join(chunk_words))
            start += self.config.application.milvus.document.chunk.chunk_words_size - self.config.application.milvus.document.chunk.chunk_overlap

        logger.debug(
            f"Generated {len(chunks)} chunks from section ({len(words)} words total)."
        )
        return chunks
