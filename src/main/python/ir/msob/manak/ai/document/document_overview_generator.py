import logging
from typing import List

from haystack.dataclasses import Document

from src.main.python.ir.msob.manak.ai.document.beans.document_chunk_configuration import DocumentChunkConfiguration

logger = logging.getLogger(__name__)


class DocumentOverviewGenerator:
    """
    Generates a high-level overview from a list of document chunks.
    Uses hierarchical summarization to create a compact representation
    of the entire document.
    """

    def __init__(self, summarizer=None):
        """
        Optionally inject a custom summarizer for testing or configuration flexibility.
        """
        self.summarizer = summarizer or DocumentChunkConfiguration.get_hierarchical_summarizer()

    # ------------------------ Public API ------------------------

    def generate(self, chunks: List[Document]) -> str:
        """
        Generates a hierarchical overview from a list of Document chunks.
        Each chunk is expected to have a 'content' attribute.
        """
        if not chunks:
            logger.warning("⚠️ No chunks provided to DocumentOverviewGenerator.")
            return ""

        logger.info(f"🧠 Generating overview for {len(chunks)} document chunks...")

        texts = self._extract_texts(chunks)
        if not texts:
            logger.warning("⚠️ No valid text content found in chunks.")
            return ""

        try:
            overview = self._summarize(texts)
            logger.info(f"✅ Overview generation completed. Length: {len(overview)} chars.")
            return overview
        except Exception as e:
            logger.exception("❌ Overview summarization failed: %s", e)
            # fallback to simple concatenation if summarizer fails
            return "\n\n".join(texts[:5])  # limit to first 5 chunks

    # ------------------------ Internal Helpers ------------------------

    @staticmethod
    def _extract_texts(chunks: List[Document]) -> List[str]:
        """Extracts valid text content from chunks."""
        texts = [getattr(chunk, "content", None) for chunk in chunks if getattr(chunk, "content", None)]
        logger.debug(f"Extracted {len(texts)} valid chunk texts.")
        return texts

    def _summarize(self, texts: List[str]) -> str:
        """Performs hierarchical summarization."""
        logger.debug("Running hierarchical summarizer on chunk texts...")
        return self.summarizer.summarize(texts)
