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
      1) If README (README.md, README, README.txt) exists — return README content (possibly summarized if large).
      2) Else: pick top N largest text files and run hierarchical summarizer.
    """

    README_CANDIDATES = ("README.md", "README.MD", "README", "readme.md", "readme")

    def __init__(self):
        self.hierarchical_summarizer = RepositoryOverviewConfiguration.get_hierarchical_summarizer()
        self.readme_max_chars = 20000
        self.top_files_for_summary = 10

    def build_overview(self, repo_id: str, branch: Optional[str], file_map: Dict[str, bytes]) -> Document:
        """
        file_map: dict[path] = raw_bytes
        returns haystack Document for overview with meta containing repository info.
        """
        # 1) Look for README
        for candidate in self.README_CANDIDATES:
            # README might be at repo root or inside a single top-level folder; search keys
            for path in file_map.keys():
                if os.path.basename(path).lower() == candidate.lower():
                    try:
                        raw = file_map[path]
                        try:
                            text = raw.decode("utf-8")
                        except Exception:
                            text = raw.decode("latin-1", errors="replace")
                        # if very long, summarize by hierarchical_summarizer
                        if len(text) > self.readme_max_chars:
                            logger.info("README too long: summarizing using hierarchical summarizer.")
                            summary = self.hierarchical_summarizer.summarize([text])
                        else:
                            summary = text
                        meta = {"repository_id": repo_id, "branch": branch, "type": "overview", "source": path}
                        doc = Document(id=f"{repo_id}_overview", content=summary, meta=meta)
                        logger.info("Overview built from README: %s", path)
                        return doc
                    except Exception as e:
                        logger.exception("Failed to use README %s as overview: %s", path, e)
                        # fallthrough to other methods

        # 2) No README found -> use hierarchical summarizer over top N largest files
        logger.info("No README found; building overview from top %d files.", self.top_files_for_summary)
        # sort files by size desc
        items = sorted(file_map.items(), key=lambda kv: len(kv[1]), reverse=True)[: self.top_files_for_summary]
        texts = []
        for path, raw in items:
            try:
                try:
                    t = raw.decode("utf-8")
                except Exception:
                    t = raw.decode("latin-1", errors="replace")
                # limit per-file length to avoid OOM
                limit = getattr(config.application.milvus.repository.overview, "per_file_limit", 5000)
                texts.append(t[:limit])
            except Exception as e:
                logger.exception("Failed to decode file %s while building overview: %s", path, e)

        if not texts:
            logger.warning("No texts available to build overview; returning empty doc.")
            return Document(id=f"{repo_id}_overview", content="", meta={"repository_id": repo_id, "branch": branch, "type": "overview"})

        try:
            overview_text = self.hierarchical_summarizer.summarize(texts)
            meta = {"repository_id": repo_id, "branch": branch, "type": "overview", "source": "generated"}
            return Document(id=f"{repo_id}_overview", content=overview_text, meta=meta)
        except Exception as e:
            logger.exception("Hierarchical summarizer failed; concatenating top files.")
            overview_text = "\n\n".join(texts[:5])
            return Document(id=f"{repo_id}_overview", content=overview_text, meta={"repository_id": repo_id, "branch": branch, "type": "overview", "source": "concat_fallback"})
