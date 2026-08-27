"""CLI interface: ask SpaceQuest a question from the terminal."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from generate import PROMPT_V1, generate_answer  # noqa: E402
from monitoring import log_feedback, log_query  # noqa: E402
from retrieval import Retriever  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="SpaceQuest RAG CLI")
    parser.add_argument("question")
    parser.add_argument("--method", default="bm25", choices=["bm25", "vector", "hybrid"])
    args = parser.parse_args()

    retriever = Retriever()
    hits = retriever.search(args.question, method=args.method)
    out = generate_answer(args.question, hits, PROMPT_V1)
    print(f"\n{out['answer']}\n\nLatency: {out['latency_s']}s | prompt tokens: {out['prompt_tokens']}")
    print("\nSources:")
    for s in out["sources"]:
        print(f"- {s['doc_title']} [chunk {s['chunk_id']}] ({s['url']})")

    rating = input("\nRate this answer: +1 / -1 (blank to skip): ").strip()
    query_id = log_query(
        question=args.question,
        rewritten="",
        method=args.method,
        answer=out["answer"],
        latency_s=out["latency_s"],
        prompt_tokens=out["prompt_tokens"],
        completion_tokens=out["completion_tokens"],
        sources=out["sources"],
    )
    if rating in ("+1", "1"):
        log_feedback(query_id, 1)
    elif rating == "-1":
        log_feedback(query_id, -1)


if __name__ == "__main__":
    main()
