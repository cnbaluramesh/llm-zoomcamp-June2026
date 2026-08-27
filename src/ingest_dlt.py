"""dlt ingestion pipeline: Wikipedia corpus -> SQLite knowledge base."""
import json
import sys
from pathlib import Path

import dlt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import CORPUS_DIR, DB_PATH  # noqa: E402
from chunking import chunk_article  # noqa: E402


def load_articles() -> list[dict]:
    articles = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(CORPUS_DIR.glob("*.json"))]
    print(f"loaded {len(articles)} articles from {CORPUS_DIR}")
    return articles


def run_pipeline() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="wikipedia_ingestion",
        destination=dlt.destinations.sqlalchemy(f"sqlite:///{DB_PATH}"),
        dataset_name="kb",
    )
    docs_resource = [load_articles()]
    info_docs = pipeline.run(docs_resource, table_name="documents", write_disposition="replace")
    print(info_docs)

    chunks = [c for a in load_articles() for c in chunk_article(a)]
    info_chunks = pipeline.run([chunks], table_name="chunks", write_disposition="replace")
    print(info_chunks)
    print(f"knowledge base at {DB_PATH}: {len(chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
