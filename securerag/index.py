"""Local vector index with access control applied *before* ranking.

Default backend is TF-IDF (scikit-learn) plus cosine similarity over a
NumPy matrix. That is a local sparse embedding: no model download, no
API, and it runs offline on CPU.

If SECURE_RAG_EMBEDDINGS=sbert and sentence-transformers is installed,
the same pre-filter path can use a small local MiniLM model instead.
If that import or model load fails, the index falls back to TF-IDF.

The security property is the same for either backend: unauthorized
chunks are removed from the candidate set, then similarity is computed
only on what remains. They never enter ranking and never enter the
answer context.
"""

from __future__ import annotations

import os
from collections import Counter
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .acl import user_can_read
from .chunking import chunk_all
from .corpus import load_documents
from .models import Chunk, Document, RetrievalResult, ScoredChunk, User

DEFAULT_TOP_K = 5
# TF-IDF cosine below this is treated as "no useful match" so a user who
# cannot see the real answer gets a clean refusal, not a weak nearby file.
MIN_SHOW_SCORE = 0.11


def _embedding_choice() -> str:
    return os.environ.get("SECURE_RAG_EMBEDDINGS", "tfidf").strip().lower()


class TfidfBackend:
    """Sparse TF-IDF vectors stored as a matrix (the default local store)."""

    name = "tfidf"

    def __init__(self, texts: list[str]) -> None:
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform(texts)

    def encode_query(self, query: str):
        return self.vectorizer.transform([query])

    def similarities(self, query: str, row_indices: np.ndarray) -> np.ndarray:
        if row_indices.size == 0:
            return np.array([], dtype=float)
        query_vec = self.encode_query(query)
        subset = self.matrix[row_indices]
        return cosine_similarity(query_vec, subset).ravel()


class SbertBackend:
    """Optional dense embeddings. Only used when explicitly requested."""

    name = "sbert"

    def __init__(self, texts: list[str]) -> None:
        from sentence_transformers import SentenceTransformer

        model_name = os.environ.get(
            "SECURE_RAG_SBERT_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.model = SentenceTransformer(model_name)
        vectors = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        self.matrix = np.asarray(vectors, dtype=np.float32)

    def similarities(self, query: str, row_indices: np.ndarray) -> np.ndarray:
        if row_indices.size == 0:
            return np.array([], dtype=float)
        q = self.model.encode([query], normalize_embeddings=True, show_progress_bar=False)
        subset = self.matrix[row_indices]
        # Vectors are L2-normalized, so cosine is a dot product.
        return (subset @ np.asarray(q, dtype=np.float32).ravel())


def _build_backend(texts: list[str]) -> tuple[object, str]:
    choice = _embedding_choice()
    if choice in {"sbert", "sentence-transformers", "minilm"}:
        try:
            backend = SbertBackend(texts)
            return backend, backend.name
        except Exception as exc:  # noqa: BLE001 — fallback is intentional
            print(
                f"sentence-transformers backend failed ({type(exc).__name__}: {exc}); "
                "falling back to TF-IDF."
            )
    return TfidfBackend(texts), "tfidf"



_STORE_NAMES = ("honda", "toyota", "ford")


def _apply_store_mention_weight(query: str, scores: np.ndarray, chunks: list[Chunk]) -> np.ndarray:
    """Down-weight a store-specific chunk when the question names a different store.

    This is a relevance tweak only. It does not grant or deny access.
    """
    mentioned = [name for name in _STORE_NAMES if name in query.lower()]
    if not mentioned or scores.size == 0:
        return scores
    weighted = scores.copy()
    for i, chunk in enumerate(chunks):
        if "any" in chunk.store_ids:
            continue
        haystack = " ".join(chunk.store_ids) + " " + chunk.title.lower()
        if any(name in haystack for name in mentioned):
            continue
        weighted[i] = float(weighted[i]) * 0.45
    return weighted


class VectorIndex:
    """In-memory local vector store with metadata pre-filtering."""

    def __init__(self, chunks: list[Chunk], documents: list[Document] | None = None) -> None:
        if not chunks:
            raise ValueError("Cannot build an index over an empty corpus.")
        self.chunks = list(chunks)
        self.documents = documents or []
        self._id_to_chunk = {c.id: c for c in self.chunks}
        texts = [c.text for c in self.chunks]
        self.backend, self.backend_name = _build_backend(texts)

    def eligible_indices(self, user: User | None, naive: bool) -> np.ndarray:
        if naive or user is None:
            return np.arange(len(self.chunks), dtype=int)
        flags = [user_can_read(user, chunk) for chunk in self.chunks]
        return np.flatnonzero(np.asarray(flags, dtype=bool))

    def ineligible_chunks(self, user: User) -> list[Chunk]:
        return [chunk for chunk in self.chunks if not user_can_read(user, chunk)]

    def eligible_chunks(self, user: User | None, naive: bool = False) -> list[Chunk]:
        return [self.chunks[i] for i in self.eligible_indices(user, naive)]

    def search(
        self,
        query: str,
        user: User,
        top_k: int = DEFAULT_TOP_K,
        naive: bool = False,
    ) -> RetrievalResult:
        eligible = self.eligible_indices(user, naive=naive)
        ineligible = (
            []
            if naive
            else [self.chunks[i] for i in range(len(self.chunks)) if i not in set(eligible.tolist())]
        )
        if naive:
            # Still compute what the ACL *would* have blocked, for the leak banner.
            ineligible = [c for c in self.chunks if not user_can_read(user, c)]
        filtered_counts = dict(Counter(c.sensitivity for c in ineligible))
        filtered_out_count = len(ineligible) if not naive else 0

        candidate_ids = tuple(self.chunks[i].id for i in eligible)
        unauthorized_count = len(ineligible)
        if eligible.size == 0:
            return RetrievalResult(
                chunks=[],
                filtered_out_count=filtered_out_count,
                filtered_out_by_sensitivity=filtered_counts if not naive else {},
                candidates_considered=0,
                candidate_ids=(),
                leaked_chunks=[],
                mode="naive" if naive else "secure",
                query=query,
                user_id=user.id,
                unauthorized_corpus_count=unauthorized_count,
            )

        scores = self.backend.similarities(query, eligible)
        scores = _apply_store_mention_weight(query, scores, [self.chunks[int(i)] for i in eligible])
        order = np.argsort(-scores)
        picked: list[ScoredChunk] = []
        for rank_i in order:
            score = float(scores[rank_i])
            if score < MIN_SHOW_SCORE:
                break
            chunk = self.chunks[int(eligible[rank_i])]
            allowed = user_can_read(user, chunk)
            picked.append(ScoredChunk(chunk=chunk, score=score, allowed=allowed))
            if len(picked) >= top_k:
                break

        leaked = [item for item in picked if not item.allowed]
        return RetrievalResult(
            chunks=picked,
            filtered_out_count=filtered_out_count,
            filtered_out_by_sensitivity=filtered_counts if not naive else {},
            candidates_considered=int(eligible.size),
            candidate_ids=candidate_ids,
            leaked_chunks=leaked,
            mode="naive" if naive else "secure",
            query=query,
            user_id=user.id,
            unauthorized_corpus_count=unauthorized_count,
        )

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        return self._id_to_chunk.get(chunk_id)

    def documents_by_id(self) -> dict[str, Document]:
        return {d.id: d for d in self.documents}


def build_index(
    documents: Iterable[Document] | None = None,
) -> VectorIndex:
    docs = list(documents) if documents is not None else load_documents()
    chunks = chunk_all(docs)
    return VectorIndex(chunks, documents=docs)
