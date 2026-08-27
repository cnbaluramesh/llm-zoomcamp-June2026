"""Generate ground-truth Q&A from the corpus using the LLM."""
import json
import sqlite3
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import DB_PATH, EVAL_DIR, OPENAI_API_KEY  # noqa: E402

QUESTIONS_PER_DOC = 3

PROMPT = """You are generating an evaluation dataset for a RAG system about space exploration.
From the document section below, write {n} questions a user could ask.
Each question must be answerable ONLY from this text.

Return a JSON array of objects: {{"question": ..., "answer": ..., "doc_title": ...}}

DOCUMENT: {title}
TEXT:
{text}"""


def main() -> None:
    client = OpenAI(api_key=OPENAI_API_KEY)
    conn = sqlite3.connect(DB_PATH)
    docs = conn.execute(
        "SELECT doc_title, GROUP_CONCAT(text, ' ') FROM chunks WHERE rowid % 5 = 0 GROUP BY doc_title"
    ).fetchall()
    records = []
    for title, text in docs:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": PROMPT.format(n=QUESTIONS_PER_DOC, title=title, text=text[:8000])}
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        try:
            items = json.loads(resp.choices[0].message.content)
            if isinstance(items, dict):
                items = items.get("questions", [items])
            records.extend(items)
            print(f"{title}: +{len(items)}")
        except json.JSONDecodeError as e:
            print(f"{title}: FAILED ({e})")
    out = EVAL_DIR / "ground_truth.json"
    out.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(records)} ground-truth records to {out}")


if __name__ == "__main__":
    main()
