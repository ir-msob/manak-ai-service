import io
import logging
import os
import zipfile
from typing import Dict, Optional

from src.main.python.ir.msob.manak.ai.client.rms.repository_dto import RepositoryDto
from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.repository.beans.repository_chunk_configuration import \
    RepositoryChunkConfiguration
from src.main.python.ir.msob.manak.ai.repository.beans.repository_overview_configuration import \
    RepositoryOverviewConfiguration
from src.main.python.ir.msob.manak.ai.repository.repository_chunker import RepositoryChunker
from src.main.python.ir.msob.manak.ai.repository.repository_overview_generator import RepositoryOverviewGenerator

logger = logging.getLogger(__name__)
config = ConfigConfiguration().get_properties()

REPO_INDEX_EXTS = {
    ".java", ".kt", ".xml", ".yml", ".yaml", ".properties", ".md", ".txt",
    ".py", ".js", ".ts", ".json", ".html", ".css", ".gradle", ".groovy",
    ".pom", ".sql", ".sh", ".bash", ".dockerfile"
}

class RepositoryIndexer:
    """
    Coordinates chunking + overview creation + storing into Milvus (via RepositoryChunkConfiguration & RepositoryOverviewConfiguration).
    """

    def __init__(self):
        self.chunker = RepositoryChunker()
        self.overview_generator = RepositoryOverviewGenerator()
        self.chunk_pipeline = RepositoryChunkConfiguration.get_pipeline()
        self.overview_pipeline = RepositoryOverviewConfiguration.get_pipeline()

    def index(self, repository: RepositoryDto, branch: Optional[str], zip_bytes: bytes) -> Dict:
        """
        Main entrypoint. Returns a dict with summary information about indexed files.
        """
        repo_id = repository.id or "unknown"
        logger.info("📦 Starting indexing for repository %s, branch='%s'", repo_id, branch)

        file_map: Dict[str, bytes] = {}
        indexed_files = []

        # 1) open zip and collect files (skip dirs and hidden)
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            members = [n for n in zf.namelist() if not n.endswith("/") and not os.path.basename(n).startswith(".")]
            logger.info("Repository zip contains %d candidate files", len(members))
            for path in members:
                try:
                    raw = zf.read(path)
                    _, ext = os.path.splitext(path)
                    if ext.lower() not in REPO_INDEX_EXTS:
                        logger.debug("Skipping non-indexable file: %s", path)
                        continue
                    file_map[path] = raw
                except Exception as e:
                    logger.exception("❌ Failed to read path %s from zip: %s", path, e)
                    continue

        if not file_map:
            logger.warning("No indexable files found in repository %s", repo_id)

        # 2) For each file, chunk & store chunks
        for path, raw in file_map.items():
            try:
                chunks = self.chunker.chunk_file(repo_id, branch, path, raw)
                if not chunks:
                    logger.warning("No chunks produced for %s", path)
                    continue

                logger.info("Storing %d chunks for file %s", len(chunks), path)
                self.chunk_pipeline.run({"embedder": {"documents": chunks}})
                indexed_files.append({"path": path, "chunks": len(chunks), "document_id_prefix": f"{repo_id}:{path}"})
                logger.info("✅ Stored chunks for %s", path)

            except Exception as e:
                logger.exception("❌ Failed to process file %s: %s", path, e)
                continue

        # 3) Build overview and store it
        try:
            overview_doc = self.overview_generator.build_overview(repo_id, branch, file_map)
            logger.info("Storing overview for repository %s", repo_id)
            self.overview_pipeline.run({"embedder": {"documents": [overview_doc]}})
            logger.info("✅ Stored overview for repository %s", repo_id)
        except Exception as e:
            logger.exception("❌ Failed to store overview for repository %s: %s", repo_id, e)
            # continue, return partial result
            overview_doc = overview_doc if 'overview_doc' in locals() else None

        return {
            "repository_id": repo_id,
            "name": repository.name,
            "indexed_files": indexed_files,
            "overview_id": overview_doc.id if overview_doc else None
        }
