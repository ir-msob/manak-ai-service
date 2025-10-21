import logging
from typing import List

import nltk
import numpy as np
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# ---------- Logging ----------
logger = logging.getLogger(__name__)
nltk.download("punkt", quiet=True)


class ExtractiveSummarizer:
    """
    Extractive summarizer using sentence embeddings and centroid similarity.
    """

    def __init__(self,
                 model_name: str,
                 device: str,
                 max_sentences: int):
        self.model_name = model_name
        self.max_sentences = max_sentences
        self.model = SentenceTransformer(self.model_name, device=device)

    def summarize(self, text: str) -> str:
        if not text or not text.strip():
            logger.warning("Empty text received for extractive summarization.")
            return ""

        sentences = sent_tokenize(text)
        if len(sentences) <= self.max_sentences:
            return " ".join(sentences)

        embeddings = self.model.encode(sentences, show_progress_bar=False)
        centroid = np.mean(embeddings, axis=0)

        from numpy import dot
        from numpy.linalg import norm

        scores = [
            dot(e, centroid) / (norm(e) * norm(centroid) + 1e-8)
            for e in embeddings
        ]
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.max_sentences]
        top_idx = sorted(top_idx)

        summary = " ".join([sentences[i] for i in top_idx])
        logger.debug(f"Extractive summary generated with {len(top_idx)} sentences.")
        return summary


class AbstractiveSummarizer:
    """
    Abstractive summarizer using a HuggingFace transformer pipeline.
    """

    def __init__(self,
                 model_name: str,
                 device: str,
                 max_length: int,
                 min_length: int):
        self.max_length = max_length
        self.min_length = min_length
        self.model_name = model_name

        self.pipe = pipeline("summarization", model=self.model_name, device=device)

    def summarize(self, text: str) -> str:
        if not text or not text.strip():
            logger.warning("Empty text received for abstractive summarization.")
            return ""

        try:
            out = self.pipe(text, max_length=self.max_length, min_length=self.min_length, truncation=True)
            summary = out[0]["summary_text"]
            logger.debug(f"Abstractive summary generated (len={len(summary)}).")
            return summary
        except Exception as e:
            logger.error(f"Abstractive summarization failed: {e}")
            return text[:500]  # fallback to truncated original


class HybridSummarizer:
    """
    Combines Extractive and Abstractive summarization sequentially.
    """

    def __init__(self,
                 extractive: ExtractiveSummarizer,
                 abstractive: AbstractiveSummarizer):
        self.extractive = extractive
        self.abstractive = abstractive

    def summarize(self, text: str) -> str:
        logger.info("Running hybrid summarization (extractive → abstractive).")
        small = self.extractive.summarize(text)
        return self.abstractive.summarize(small)


class HierarchicalSummarizer:
    """
    Builds a hierarchical overview by splitting large documents into chunks,
    summarizing each, then summarizing the summaries.
    """

    def __init__(self,
                 extractive: ExtractiveSummarizer,
                 abstractive: AbstractiveSummarizer):
        self.extractive = extractive
        self.abstractive = abstractive

    def summarize(self, chunks: List[str]) -> str:
        logger.info(f"Document split into {len(chunks)}.")

        # First-level extractive summaries
        summaries = [
            self.extractive.summarize(c)
            for c in chunks
        ]
        merged = "\n".join(summaries)

        logger.info("Running top-level abstractive summarization for overview.")
        return HybridSummarizer(self.extractive, self.abstractive).summarize(merged)
