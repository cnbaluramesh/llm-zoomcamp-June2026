"""LLM-based document re-ranking: scores candidate chunks for question relevance."""
import json
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import OPENAI_API_KEY  # noqa: E402
from retrieval import Hit  # noqa: E402

RERANK_PROMPT = """Rate how relevant each passage is to answering the question, 0-3
(0 = irrelevant, 1 = slightly, 2 = mostly, 3 = directly answers it).
Return JSON: {{"scores": [s1, s2, ...]}} in the same order as passages.

QUESTION: {question}
{passages}"""


def rerank(question: str, hits: list[Hit], top_k: int = 5) -> list[Hit]:
    client = OpenAI(api_key=OPENAI_API_KEY)
    numbered = "\n".join(
        f"[{i}] ({h.doc_title})\n{h.text[:500]}" for i, h in enumerate(hits)
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": RERANK_PROMPT.format(question=question, passages=numbered)}],
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    try:
        scores = json.loads(resp.choices[0].message.content)["scores"]
    except (json.JSONDecodeError, KeyError):
        return hits[:top_k]
    ranked = sorted(zip(hits, scores), key=lambda p: -p[1])
    return [h for h, _ in ranked[:top_k]]
