import hashlib
import logging
import mimetypes
import os
from typing import List, Optional

from haystack.dataclasses import Document

from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration

logger = logging.getLogger(__name__)

class RepositoryChunker:
    """
    Responsible for splitting a single file content into chunks.
    Behavior:
    - Uses character-based sliding window chunking (configurable size + overlap).
    - Returns a list of haystack.dataclasses.Document with full metadata in .meta.
    """

    def __init__(self):
        # default values chosen conservatively; override via config if present
        props = ConfigConfiguration().get_properties().application.milvus.repository.chunk
        self.chunk_size = props.chunk_words_size
        self.overlap = props.chunk_overlap

    @staticmethod
    def _sha256_bytes(b: bytes) -> str:
        h = hashlib.sha256()
        h.update(b)
        return h.hexdigest()

    def chunk_file(self, repo_id: str, branch: Optional[str], path: str, raw_bytes: bytes) -> List[Document]:
        """
        Returns list of Documents (chunks). Each Document.meta contains:
        {
          "repository_id", "branch", "file_path", "file_name",
          "mime_type", "file_size", "sha256", "chunk_index", "total_chunks"
        }
        Document.id is "<repo_id>:<path>:chunk:<index>"
        """
        logger.info("📝 Starting chunking file '%s' (repo=%s)", path, repo_id)

        # decode text
        try:
            try:
                text = raw_bytes.decode("utf-8")
            except Exception:
                text = raw_bytes.decode("latin-1", errors="replace")
        except Exception as e:
            logger.exception("❌ Failed to decode file %s: %s", path, e)
            return []

        if not text:
            logger.warning("File %s is empty, skipping chunking.", path)
            return []

        length = len(text)
        chunks: List[Document] = []
        step = max(self.chunk_size - self.overlap, 1)

        indices = list(range(0, length, step))
        total_chunks = len(indices)
        file_name = os.path.basename(path)
        mime_type, _ = mimetypes.guess_type(path)
        if not mime_type:
            mime_type = "text/plain"
        sha = self._sha256_bytes(raw_bytes)
        file_size = len(raw_bytes)

        for idx, start in enumerate(indices):
            end = min(start + self.chunk_size, length)
            content = text[start:end]
            meta = {
                "repository_id": repo_id,
                "branch": branch,
                "file_path": path,
                "file_name": file_name,
                "mime_type": mime_type,
                "file_size": file_size,
                "sha256": sha,
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "type": "chunk",
            }
            doc_id = f"{repo_id}:{path}:chunk:{idx}"
            chunks.append(Document(id=doc_id, content=content, meta=meta))

        logger.info("✅ Finished chunking file '%s' into %d chunks (repo=%s)", path, total_chunks, repo_id)
        return chunks
