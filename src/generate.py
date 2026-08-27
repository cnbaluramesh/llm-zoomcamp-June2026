"""Grounded answer generation with OpenAI."""
import sys
import time
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import CHAT_MODEL, OPENAI_API_KEY  # noqa: E402
from retrieval import Hit  # noqa: E402

PROMPT_V1 = """You are SpaceQuest, an assistant that answers questions about space exploration.
Answer ONLY using the context below. Cite sources as [title]. If the context doesn't contain the answer, say you don't know.

CONTEXT:
{context}

QUESTION: {question}"""

PROMPT_V2 = """You are SpaceQuest, an expert space-exploration historian.
Rules:
1. Ground every factual claim in the CONTEXT. No outside knowledge.
2. Cite supporting passages inline as [title].
3. If the answer isn't in the context, reply exactly: I don't have enough information in my knowledge base.
4. Be concise: 2-5 sentences unless asked for more.

CONTEXT:
{context}

QUESTION: {question}"""


def build_context(hits: list[Hit]) -> str:
    blocks = []
    for h in hits:
        blocks.append(f"[{h.doc_title}] ({h.url})\n{h.text}")
    return "\n\n---\n\n".join(blocks)


def generate_answer(
    question: str,
    hits: list[Hit],
    prompt_template: str = PROMPT_V1,
    model: str = CHAT_MODEL,
    client: OpenAI | None = None,
) -> dict:
    client = client or OpenAI(api_key=OPENAI_API_KEY)
    prompt = prompt_template.format(context=build_context(hits), question=question)
    start = time.time()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    answer = resp.choices[0].message.content.strip()
    return {
        "answer": answer,
        "latency_s": round(time.time() - start, 2),
        "prompt_tokens": resp.usage.prompt_tokens,
        "completion_tokens": resp.usage.completion_tokens,
        "sources": [{"doc_title": h.doc_title, "url": h.url, "chunk_id": h.chunk_id} for h in hits],
    }
