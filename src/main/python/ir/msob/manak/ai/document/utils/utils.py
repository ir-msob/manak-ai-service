import os, re
import frontmatter
from typing import List, Tuple, Dict, Any

from src.main.python.ir.msob.manak.ai.document.model.document_response import DocumentResponse


def read_markdown_file(res: DocumentResponse, content: str) -> Tuple[str, Dict[str, Any]]:
    """
    Read markdown content and extract frontmatter metadata and content.
    Returns (content, metadata) tuple.

    Args:
        content: Markdown content as bytes or string
        filename: Optional filename for error messages
    """
    try:
        # Use frontmatter to parse content from string
        post = frontmatter.loads(content)
        return post.content, post.metadata or {}

    except Exception as e:
        print(f"Error reading markdown content {res.file_path}: {e}")
        # Fallback: return content with empty metadata
        return content, {}


def discover_md_files(root_dir: str):
    """Discover all markdown files in a folder recursively."""
    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".md") or f.endswith(".markdown"):
                yield os.path.join(root, f)


def split_markdown_to_sections(text: str) -> List[str]:
    """
    Split markdown text into sections based on headers.
    Returns list of sections.
    """
    # Split on markdown headings
    parts = re.split(r"\n(?=#+ )", text)
    cleaned = [p.strip() for p in parts if p.strip()]

    # If sections are still too large, split by paragraphs
    sections = []
    for p in cleaned:
        if len(p.split()) > 1200:  # If section has more than 1200 words
            paras = [pp.strip() for pp in p.split("\n\n") if pp.strip()]
            sections.extend(paras)
        else:
            sections.append(p)

    return sections
