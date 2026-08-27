"""Hybrid retrieval: dense (OpenAI embeddings) + sparse (BM25) fused with RRF."""
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from openai import OpenAI
from rank_bm25 import BM25Okapi

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DB_PATH, EMBED_MODEL, OPENAI_API_KEY, RRF_K, TOP_K  # noqa: E402


@dataclass
class Hit:
    doc_title: str
    url: str
    chunk_id: int
    text: str
    score: float


class Retriever:
    def __init__(self) -> None:
        conn = sqlite3.connect(DB_PATH)
        self.chunks = [
            {
                "rowid": r[0],
                "doc_title": r[1],
                "url": r[2],
                "chunk_id": r[3],
                "text": r[4],
                "embedding": np.array(json.loads(r[5]), dtype=np.float32),
            }
            for r in conn.execute(
                "SELECT rowid, doc_title, url, chunk_id, text, embedding FROM chunks WHERE embedding IS NOT NULL"
            ).fetchall()
        ]
        conn.close()
        tokenized = [self._tokenize(c["text"]) for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized)
        self._matrix = np.vstack([c["embedding"] for c in self.chunks])
        norms = np.linalg.norm(self._matrix, axis=1, keepdims=True)
        self._matrix /= np.maximum(norms, 1e-10)
        self._client = OpenAI(api_key=OPENAI_API_KEY)

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.lower())

    def embed_query(self, query: str) -> np.ndarray:
        resp = self._client.embeddings.create(input=[query], model=EMBED_MODEL)
        vec = np.array(resp.data[0].embedding, dtype=np.float32)
        return vec / max(np.linalg.norm(vec), 1e-10)

    def dense_search(self, query: str, k: int = TOP_K * 2) -> list[tuple[int, float]]:
        q = self.embed_query(query)
        sims = self._matrix @ q
        idx = np.argsort(-sims)[:k]
        return [(int(i), float(sims[i])) for i in idx]

    def bm25_search(self, query: str, k: int = TOP_K * 2) -> list[tuple[int, float]]:
        scores = self.bm25.get_scores(self._tokenize(query))
        idx = np.argsort(-scores)[:k]
        return [(int(i), float(scores[i])) for i in idx if scores[i] > 0]

    def hybrid_search(self, query: str, k: int = TOP_K) -> list[Hit]:
        dense = self.dense_search(query)
        sparse = self.bm25_search(query)
        scores: dict[int, float] = {}
        for rank, (i, _) in enumerate(dense):
            scores[i] = scores.get(i, 0.0) + 1.0 / (RRF_K + rank + 1)
        for rank, (i, _) in enumerate(sparse):
            scores[i] = scores.get(i, 0.0) + 1.0 / (RRF_K + rank + 1)
        top = sorted(scores.items(), key=lambda kv: -kv[1])[:k]
        return [self._hit(i, s) for i, s in top]

    def search(self, query: str, method: str = "hybrid", k: int = TOP_K) -> list[Hit]:
        if method == "vector":
            results = self.dense_search(query, k)
            return [self._hit(i, s) for i, s in results]
        if method == "bm25":
            results = self.bm25_search(query, k)
            return [self._hit(i, s) for i, s in results]
        return self.hybrid_search(query, k)

    def _hit(self, idx: int, score: float) -> Hit:
        c = self.chunks[idx]
        return Hit(doc_title=c["doc_title"], url=c["url"], chunk_id=c["chunk_id"], text=c["text"], score=score)


REWRITE_PROMPT = """Rewrite the user's question so it retrieves the most relevant space-exploration documents.
Expand abbreviations, resolve pronouns, keep it a single question. Return only the rewritten question.

Question: {question}"""


def rewrite_query(question: str, client: OpenAI | None = None) -> str:
    client = client or OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": REWRITE_PROMPT.format(question=question)}],
        temperature=0.0,
    )
    return resp.choices[0].message.content.strip()
