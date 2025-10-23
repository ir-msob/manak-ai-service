import logging
import uuid
from typing import List

from haystack.dataclasses import Document

from src.main.python.ir.msob.manak.ai.client.dms.document_dto import DocumentDto, Attachment
from src.main.python.ir.msob.manak.ai.document.beans.document_chunk_configuration import DocumentChunkConfiguration
from src.main.python.ir.msob.manak.ai.document.beans.document_overview_configuration import \
    DocumentOverviewConfiguration
from src.main.python.ir.msob.manak.ai.document.document_chunker import DocumentChunker
from src.main.python.ir.msob.manak.ai.document.document_overview_generator import DocumentOverviewGenerator
from src.main.python.ir.msob.manak.ai.document.model.document_request import DocumentRequest
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

        context = f"[{dto.get_latest_attachment().file_name} | id={dto.id}]"
        logger.info(f"🚀 Starting indexing {context}")

        try:
            chunks = self._process_chunks(response, content, context)
            overview_doc = self._process_overview(response, chunks, context)

            self._store_documents(overview_doc, chunks, context)

            logger.info(f"✅ Completed indexing {context}")
            return response

        except Exception as e:
            logger.exception(f"❌ Indexing failed for {context}: {e}")
            raise

    # ------------------------ Internal Steps ------------------------

    def _process_chunks(self, res: DocumentResponse, content: str, context: str) -> List[Document]:
        """Chunk the file into smaller pieces."""
        logger.info(f"🧩 Chunking document {context}")
        chunks = self.chunker.chunk_file(res, content)
        if not chunks:
            logger.warning(f"No chunks produced for {context}. Skipping indexing.")
            raise ValueError(f"No chunks generated for {res.file_path}")
        logger.info(f"✅ Generated {len(chunks)} chunks for {context}")
        return chunks

    def _process_overview(self, res: DocumentResponse, chunks: List[Document], context: str) -> Document:
        """Generate an overview document summarizing the content."""
        logger.info(f"🧠 Generating overview for {context}")
        overview_text = self.overview_generator.generate(chunks)
        overview_doc = Document(
            id=f"{res.document_id}_overview",
            content=overview_text,
            meta=self._build_meta(res, doc_type="overview")
        )
        logger.debug(f"Overview length: {len(overview_text)} chars for {context}")
        return overview_doc

    def _store_documents(self, overview_doc: Document, chunks: List[Document], context: str):
        """Store overview and chunks into their respective Milvus collections."""
        logger.info(f"📥 Storing overview document for {context}")
        try:
            self.overview_pipeline.run({"embedder": {"documents": [overview_doc]}})
            logger.info(f"✅ Overview stored for {context}")
        except Exception as e:
            logger.exception(f"Failed to store overview document for {context}: {e}")
            raise

        logger.info(f"📦 Storing {len(chunks)} chunks for {context}")
        try:
            self.chunk_pipeline.run({"embedder": {"documents": chunks}})
            logger.info(f"✅ Chunks stored for {context}")
        except Exception as e:
            logger.exception(f"Failed to store chunks for {context}: {e}")
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
