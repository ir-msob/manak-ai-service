import logging
import os
from typing import Dict, Optional

from haystack.dataclasses import Document

from src.main.python.ir.msob.manak.ai.config.config_configuration import ConfigConfiguration
from src.main.python.ir.msob.manak.ai.repository.beans.repository_overview_configuration import \
    RepositoryOverviewConfiguration

logger = logging.getLogger(__name__)
config = ConfigConfiguration().get_properties()

class RepositoryOverviewGenerator:
    """
    Produces an overview for the whole repository.
    Priority:
      1) If README exists — return README content (possibly summarized if large).
      2) Else: pick top N largest text files and run hierarchical summarizer.
    """

    README_CANDIDATES = ("README.md", "README.MD", "README", "readme.md", "readme")

    def __init__(self):
        self.hierarchical_summarizer = RepositoryOverviewConfiguration.get_hierarchical_summarizer()
        self.readme_max_chars = 20000
        self.top_files_for_summary = 10

    def build_overview(self, repo_id: str, branch: Optional[str], file_map: Dict[str, bytes]) -> Document:
        logger.info("📖 Building repository overview for repo_id='%s', branch='%s'", repo_id, branch)

        # 1) Look for README
        for candidate in self.README_CANDIDATES:
            for path in file_map.keys():
                if os.path.basename(path).lower() == candidate.lower():
                    try:
                        raw = file_map[path]
                        try:
                            text = raw.decode("utf-8")
                        except Exception:
                            text = raw.decode("latin-1", errors="replace")

                        if len(text) > self.readme_max_chars:
                            logger.info("README too long (%d chars): summarizing.", len(text))
                            summary = self.hierarchical_summarizer.summarize([text])
                        else:
                            summary = text

                        meta = {"repository_id": repo_id, "branch": branch, "type": "overview", "source": path}
                        doc = Document(id=f"{repo_id}_overview", content=summary, meta=meta)
                        logger.info("✅ Overview built from README: %s", path)
                        return doc
                    except Exception as e:
                        logger.exception("❌ Failed to use README %s as overview: %s", path, e)
                        # continue to other files

        # 2) No README -> summarize top N largest files
        logger.info("No README found; summarizing top %d largest files.", self.top_files_for_summary)
        items = sorted(file_map.items(), key=lambda kv: len(kv[1]), reverse=True)[:self.top_files_for_summary]
        texts = []

        for path, raw in items:
            try:
                try:
                    t = raw.decode("utf-8")
                except Exception:
                    t = raw.decode("latin-1", errors="replace")
                limit = getattr(config.application.milvus.repository.overview, "per_file_limit", 5000)
                texts.append(t[:limit])
            except Exception as e:
                logger.exception("❌ Failed to decode file %s: %s", path, e)

        if not texts:
            logger.warning("No valid texts available to build overview; returning empty document.")
            return Document(
                id=f"{repo_id}_overview",
                content="",
                meta={"repository_id": repo_id, "branch": branch, "type": "overview"}
            )

        try:
            overview_text = self.hierarchical_summarizer.summarize(texts)
            meta = {"repository_id": repo_id, "branch": branch, "type": "overview", "source": "generated"}
            logger.info("✅ Overview built from top files (chars=%d).", len(overview_text))
            return Document(id=f"{repo_id}_overview", content=overview_text, meta=meta)
        except Exception as e:
            logger.exception("❌ Hierarchical summarizer failed; using concatenation fallback: %s", e)
            overview_text = "\n\n".join(texts[:5])
            return Document(
                id=f"{repo_id}_overview",
                content=overview_text,
                meta={"repository_id": repo_id, "branch": branch, "type": "overview", "source": "concat_fallback"}
            )
