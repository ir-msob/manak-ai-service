import logging
from typing import List

from haystack.dataclasses import Document

from src.main.python.ir.msob.manak.ai.client.dms.document_dto import DocumentDto, Attachment
from src.main.python.ir.msob.manak.ai.document.beans.document_chunk_configuration import DocumentChunkConfiguration
from src.main.python.ir.msob.manak.ai.document.beans.document_overview_configuration import \
    DocumentOverviewConfiguration
from src.main.python.ir.msob.manak.ai.document.document_chunker import DocumentChunker
from src.main.python.ir.msob.manak.ai.document.document_overview_generator import DocumentOverviewGenerator
from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """
    Generic document indexer supporting multiple file types (Markdown, PDF, DOCX, etc.).
    Handles document chunking, overview generation, and indexing into Milvus.
    """

    def __init__(self):
        self.chunker = DocumentChunker()
        self.overview_generator = DocumentOverviewGenerator()
        self.overview_pipeline = DocumentOverviewConfiguration.get_pipeline()
        self.chunk_pipeline = DocumentChunkConfiguration.get_pipeline()

    # ------------------------ Public API ------------------------

    def index(self, dto: DocumentDto, content: str) -> DocumentResponse:
        """Main entry point for indexing a document into Milvus."""
        attachment: Attachment = dto.get_latest_attachment()
        response = DocumentResponse(
            document_id=dto.id,
            file_path=attachment.file_path,
            file_name=attachment.file_name,
            mime_type=attachment.mime_type
        )

        context = f"[{attachment.file_name} | id={dto.id}]"
        logger.info("🚀 Starting indexing %s", context)

        try:
            # Step 1: Chunking
            chunks = self._process_chunks(response, content, context)

            # Step 2: Overview generation
            overview_doc = self._process_overview(response, chunks, context)

            # Step 3: Store overview and chunks
            self._store_documents(overview_doc, chunks, context)

            logger.info("✅ Completed indexing %s", context)
            return response

        except Exception as e:
            logger.exception("❌ Indexing failed for %s: %s", context, e)
            raise

    # ------------------------ Internal Steps ------------------------

    def _process_chunks(self, res: DocumentResponse, content: str, context: str) -> List[Document]:
        """Chunk the file into smaller pieces."""
        logger.info("🧩 Chunking document %s", context)
        chunks = self.chunker.chunk_file(res.document_id, None, res.file_path, content.encode("utf-8"))
        if not chunks:
            logger.warning("⚠️ No chunks produced for %s", context)
            raise ValueError(f"No chunks generated for {res.file_path}")
        logger.info("✅ Generated %d chunks for %s", len(chunks), context)
        return chunks

    def _process_overview(self, res: DocumentResponse, chunks: List[Document], context: str) -> Document:
        """Generate an overview document summarizing the content."""
        logger.info("🧠 Generating overview for %s", context)
        # Collect all chunk contents
        texts = [chunk.content for chunk in chunks]
        overview_text = self.overview_generator.hierarchical_summarizer.summarize(texts)
        overview_doc = Document(
            id=f"{res.document_id}_overview",
            content=overview_text,
            meta=self._build_meta(res, doc_type="overview")
        )
        logger.debug("Overview length: %d chars for %s", len(overview_text), context)
        return overview_doc

    def _store_documents(self, overview_doc: Document, chunks: List[Document], context: str):
        """Store overview and chunks into their respective Milvus collections."""
        # Store overview
        logger.info("📥 Storing overview document for %s", context)
        try:
            self.overview_pipeline.run({"embedder": {"documents": [overview_doc]}})
            logger.info("✅ Overview stored for %s", context)
        except Exception as e:
            logger.exception("❌ Failed to store overview document for %s: %s", context, e)
            raise

        # Store chunks
        logger.info("📦 Storing %d chunks for %s", len(chunks), context)
        try:
            self.chunk_pipeline.run({"embedder": {"documents": chunks}})
            logger.info("✅ Chunks stored for %s", context)
        except Exception as e:
            logger.exception("❌ Failed to store chunks for %s: %s", context, e)
            raise

    # ------------------------ Utility ------------------------

    @staticmethod
    def _build_meta(res: DocumentResponse, doc_type: str) -> dict:
        return {
            "source": res.file_path,
            "doc_id": res.document_id,
            "type": doc_type,
            "mime_type": res.mime_type,
            "meta": res.meta,
        }
