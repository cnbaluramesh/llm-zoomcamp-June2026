"""Render the architecture diagram to PNG via mermaid in headless Chromium."""
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

DIAGRAM = """
flowchart TB
    subgraph ING["INGESTION (dlt)"]
        W["Wikipedia API<br/>30 space-exploration articles"] --> C[("data/corpus/*.json<br/>(committed)")]
        C --> D["dlt pipeline<br/>chunking: 300 words / 50 overlap<br/>762 chunks"]
    end
    subgraph KB["KNOWLEDGE BASE"]
        S[("SQLite<br/>kb.chunks + embeddings<br/>query_log + feedback")]
    end
    subgraph RET["RETRIEVAL (src/retrieval.py)"]
        R["Query rewriting<br/>(optional, gpt-4o-mini)"]
        B["BM25<br/>sparse lexical"]
        V["Dense search<br/>cosine similarity"]
        F["Reciprocal Rank<br/>Fusion (RRF)"]
        RR["LLM re-ranking<br/>(evaluated, not default)"]
        R --> B
        R --> V
        B --> F
        V --> F
        F -.-> RR
    end
    subgraph GEN["GENERATION (src/generate.py)"]
        CT["Context builder<br/>top-5 chunks + sources"] --> L["OpenAI gpt-4o-mini<br/>grounded prompt (eval winner)<br/>citations [title]"]
        L --> A["Answer + cited sources"]
    end
    subgraph UI["INTERFACE + MONITORING (Streamlit)"]
        CH["Chat tab<br/>answer + citations + 👍/👎"]
        DA["Monitoring tab<br/>5 charts + KPIs"]
    end
    subgraph EV["EVALUATION"]
        GT["87 ground-truth Q&A"] --> RE["Retrieval eval:<br/>6 variants — hit-rate, MRR<br/>winner: BM25"]
        GT --> LE["LLM eval:<br/>2 prompts — judge 0-5<br/>winner: PROMPT_V1"]
    end
    DEP["Docker: Dockerfile + docker-compose<br/>(app service, volumes, .env)"]

    D --> S
    IDX["indexing.py<br/>OpenAI embeddings"] --> S
    S --> B
    S --> V
    F --> CT
    A --> CH
    CH --> M["monitoring.py<br/>logs queries + feedback"]
    M --> DA
    L -.-> O["OpenAI API<br/>(OPENAI_API_KEY)"]
    style ING fill:#dae8fc,stroke:#6c8ebf
    style KB fill:#d5e8d4,stroke:#82b366
    style RET fill:#ffe6cc,stroke:#d79b00
    style GEN fill:#e1d5e7,stroke:#9673a6
    style UI fill:#f8cecc,stroke:#b85450
    style EV fill:#fff2cc,stroke:#d6b656
"""


def main() -> None:
    html = f"""<!doctype html><html><head>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <style>body{{margin:0;background:white;}}#d{{padding:12px;}}</style>
    </head><body><pre class="mermaid" id="d">{DIAGRAM}</pre>
    <script>mermaid.initialize({{startOnLoad:true, theme:'default'}});
    window.done=false; mermaid.run().then(()=>{{window.done=true}});</script>
    </body></html>"""
    (ROOT / "logs").mkdir(exist_ok=True)
    tmp = ROOT / "logs" / "arch.html"
    tmp.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1900, "height": 1400})
        page.goto(tmp.as_uri(), timeout=60000)
        page.wait_for_function("window.done === true", timeout=60000)
        page.wait_for_timeout(1500)
        page.locator("#d").screenshot(path=str(ROOT / "docs" / "architecture.png"))
        browser.close()
    print("wrote docs/architecture.png")


if __name__ == "__main__":
    main()
