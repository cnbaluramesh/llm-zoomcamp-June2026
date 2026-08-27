"""Fetch raw Wikipedia pages for the corpus."""
import json
import time
from pathlib import Path

import wikipediaapi

from config import CORPUS_DIR, TOPICS

USER_AGENT = "SpaceQuestRAG/1.0 (educational capstone project)"


def fetch_all() -> None:
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    wiki = wikipediaapi.Wikipedia(user_agent=USER_AGENT, language="en")
    for title in TOPICS:
        slug = title.replace("/", "_").replace("–", "-")
        out = CORPUS_DIR / f"{slug}.json"
        if out.exists():
            print(f"skip {title}")
            continue
        page = wiki.page(title)
        if not page.exists():
            print(f"MISSING: {title}")
            continue
        out.write_text(
            json.dumps({"title": page.title, "url": page.fullurl, "text": page.text}, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"saved {page.title} ({len(page.text)} chars)")
        time.sleep(0.5)


if __name__ == "__main__":
    fetch_all()
