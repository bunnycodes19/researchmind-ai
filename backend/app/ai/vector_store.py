import json
import pickle
from pathlib import Path
from uuid import UUID

import faiss
import numpy as np

from app.config import get_settings


class FaissVectorStore:
    """Per-user FAISS index with metadata sidecar for filtering."""

    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        settings = get_settings()
        self.base_dir = Path(settings.faiss_dir) / str(user_id)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.base_dir / "index.faiss"
        self.meta_path = self.base_dir / "metadata.json"
        self._index: faiss.IndexFlatIP | None = None
        self._metadata: list[dict] = []
        self._dim = 768
        self._load()

    def _load(self) -> None:
        if self.index_path.exists():
            self._index = faiss.read_index(str(self.index_path))
            self._dim = self._index.d
        else:
            self._index = faiss.IndexFlatIP(self._dim)

        if self.meta_path.exists():
            self._metadata = json.loads(self.meta_path.read_text(encoding="utf-8"))
        else:
            self._metadata = []

    def _save(self) -> None:
        if self._index is not None:
            faiss.write_index(self._index, str(self.index_path))
        self.meta_path.write_text(json.dumps(self._metadata), encoding="utf-8")

    def add_vectors(
        self,
        vectors: list[list[float]],
        metadatas: list[dict],
    ) -> list[int]:
        if not vectors:
            return []
        arr = np.array(vectors, dtype=np.float32)
        if self._index is None or self._index.ntotal == 0:
            self._dim = arr.shape[1]
            self._index = faiss.IndexFlatIP(self._dim)
        elif arr.shape[1] != self._index.d:
            raise ValueError(f"Embedding dimension mismatch: index={self._index.d}, vectors={arr.shape[1]}")
        faiss.normalize_L2(arr)
        start = self._index.ntotal if self._index else 0
        self._index.add(arr)
        indices = list(range(start, start + len(vectors)))
        for i, meta in zip(indices, metadatas):
            meta["faiss_index"] = i
            self._metadata.append(meta)
        self._save()
        return indices

    def similarity_search(
        self,
        query_vector: list[float],
        k: int = 8,
        paper_ids: list[UUID] | None = None,
    ) -> list[tuple[dict, float]]:
        if self._index is None or self._index.ntotal == 0:
            return []

        q = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(q)
        scores, indices = self._index.search(q, min(k * 3, self._index.ntotal))

        results: list[tuple[dict, float]] = []
        paper_set = {str(p) for p in paper_ids} if paper_ids else None

        for idx, score in zip(indices[0], scores[0]):
            if idx < 0 or idx >= len(self._metadata):
                continue
            meta = self._metadata[idx]
            if paper_set and meta.get("paper_id") not in paper_set:
                continue
            results.append((meta, float(score)))
            if len(results) >= k:
                break
        return results

    def hybrid_search(
        self,
        query_vector: list[float],
        keywords: list[str],
        k: int = 8,
        paper_ids: list[UUID] | None = None,
    ) -> list[tuple[dict, float]]:
        dense = self.similarity_search(query_vector, k=k * 2, paper_ids=paper_ids)
        if not keywords:
            return dense[:k]

        boosted: list[tuple[dict, float]] = []
        for meta, score in dense:
            text = meta.get("content", "").lower()
            kw_score = sum(1 for kw in keywords if kw.lower() in text) * 0.05
            boosted.append((meta, score + kw_score))
        boosted.sort(key=lambda x: x[1], reverse=True)
        return boosted[:k]

    def remove_paper(self, paper_id: UUID) -> None:
        """Rebuild index without paper (FAISS lacks delete-by-id on flat index)."""
        keep_meta = [m for m in self._metadata if m.get("paper_id") != str(paper_id)]
        if len(keep_meta) == len(self._metadata):
            return
        backup_vectors = []
        for m in keep_meta:
            vec = m.get("_vector")
            if vec is not None:
                backup_vectors.append((vec, m))
        self._metadata = []
        self._index = faiss.IndexFlatIP(self._dim)
        if backup_vectors:
            vectors = [v for v, _ in backup_vectors]
            metas = [{k: v for k, v in m.items() if k != "_vector"} for _, m in backup_vectors]
            self.add_vectors(vectors, metas)
        else:
            self._save()
