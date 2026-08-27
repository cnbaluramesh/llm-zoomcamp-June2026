"""Evaluate final LLM output across prompt variants using an LLM judge."""
import json
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import CHAT_MODEL, EVAL_DIR, OPENAI_API_KEY  # noqa: E402
from generate import PROMPT_V1, PROMPT_V2, generate_answer  # noqa: E402
from retrieval import Retriever  # noqa: E402

JUDGE_PROMPT = """You are evaluating a RAG answer. Score the ANSWER against the GROUND TRUTH using the CONTEXT.
Return JSON: {{"correctness": 0-5, "groundedness": 0-5}}
- correctness: does it convey the same facts as ground truth?
- groundedness: is every claim supported by the context?

GROUND TRUTH: {truth}
CONTEXT: {context}
ANSWER: {answer}"""


def judge(client: OpenAI, rec: dict, result: dict) -> dict:
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": JUDGE_PROMPT.format(
                    truth=rec["answer"],
                    context="\n".join(h.text[:600] for h in rec.get("_hits", [])),
                    answer=result["answer"],
                ),
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    return json.loads(resp.choices[0].message.content)


def main() -> None:
    client = OpenAI(api_key=OPENAI_API_KEY)
    records = json.loads((EVAL_DIR / "ground_truth.json").read_text(encoding="utf-8"))[:30]
    retriever = Retriever()
    summary = {}
    for name, template in [("prompt_v1", PROMPT_V1), ("prompt_v2", PROMPT_V2)]:
        scores = []
        detail = []
        for rec in records:
            hits = retriever.search(rec["question"], method="hybrid")
            rec["_hits"] = hits
            result = generate_answer(rec["question"], hits, template)
            s = judge(client, rec, result)
            scores.append(s)
            detail.append({"question": rec["question"], **s})
        avg_c = sum(s["correctness"] for s in scores) / len(scores)
        avg_g = sum(s["groundedness"] for s in scores) / len(scores)
        summary[name] = {"avg_correctness": round(avg_c, 3), "avg_groundedness": round(avg_g, 3), "n": len(scores)}
        (EVAL_DIR / f"llm_eval_{name}.json").write_text(json.dumps(detail, indent=2, ensure_ascii=False))
        print(name, summary[name])
    (EVAL_DIR / "llm_eval_summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
