"""Evaluate retrieval approaches: vector, bm25, hybrid, hybrid+rewritten query.

Metrics: hit-rate@5 and MRR@5 against LLM-generated ground truth.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import EVAL_DIR  # noqa: E402
from retrieval import Retriever, rewrite_query  # noqa: E402

K = 5


def normalize(title: str) -> str:
    return title.strip().lower()


def metrics(retriever: Retriever, records: list[dict], method: str, rewrite: bool) -> dict:
    hits_total = 0
    rr_total = 0.0
    for rec in records:
        question = rec["question"]
        if rewrite:
            question = rewrite_query(question)
        results = retriever.search(question, method=method, k=K)
        titles = [normalize(h.doc_title) for h in results]
        target = normalize(rec["doc_title"])
        rank = next((i + 1 for i, t in enumerate(titles) if t == target), None)
        if rank:
            hits_total += 1
            rr_total += 1.0 / rank
    n = len(records)
    return {
        "method": f"{method}{'_rewrite' if rewrite else ''}",
        "hit_rate": round(hits_total / n, 4),
        "mrr": round(rr_total / n, 4),
        "n_questions": n,
    }


def main() -> None:
    records = json.loads((EVAL_DIR / "ground_truth.json").read_text(encoding="utf-8"))
    retriever = Retriever()
    variants = [("vector", False), ("bm25", False), ("hybrid", False), ("hybrid", True)]
    results = []
    for method, rewrite in variants:
        m = metrics(retriever, records, method, rewrite)
        print(m)
        results.append(m)
    out = EVAL_DIR / "retrieval_results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    best = max(results, key=lambda r: r["hit_rate"])
    print(f"BEST: {best['method']} (hit-rate {best['hit_rate']})")


if __name__ == "__main__":
    main()
