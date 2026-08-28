"""Build docs/course-summary.html with inlined screenshots."""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def b64(name: str) -> str:
    return "data:image/png;base64," + base64.b64encode((DOCS / name).read_bytes()).decode()


html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SpaceQuest — LLM Zoomcamp Capstone</title>
<style>
  :root {
    --bg:#ffffff; --fg:#24292f; --muted:#57606a; --accent:#8250df; --accent-fg:#fff;
    --border:#d0d7de; --code-bg:#f6f8fa; --card:#ffffff; --chip:#ddf4ff; --chip-fg:#0969da;
    --ok:#1a7f37; --warn:#9a6700; --side:#f6f8fa;
  }
  @media (prefers-color-scheme: dark) { :root:not([data-theme=light]) {
    --bg:#0d1117; --fg:#e6edf3; --muted:#8b949e; --accent:#a371f7; --border:#30363d;
    --code-bg:#161b22; --card:#161b22; --chip:#121d2f; --chip-fg:#58a6ff; --side:#010409;
  } }
  * { box-sizing:border-box; }
  body { margin:0; font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
         background:var(--bg); color:var(--fg); line-height:1.6; }
  a { color:var(--accent); text-decoration:none; }
  a:hover { text-decoration:underline; }
  header.site { background:var(--side); border-bottom:1px solid var(--border);
    padding:14px 24px; display:flex; gap:18px; align-items:center; position:sticky; top:0; z-index:10; }
  header.site .brand { font-weight:700; font-size:17px; }
  header.site .tag { color:var(--muted); font-size:13px; }
  .wrap { display:grid; grid-template-columns:230px minmax(0,1fr) 220px; gap:32px;
          max-width:1400px; margin:0 auto; padding:28px 24px 80px; }
  nav.side, aside.toc { position:sticky; top:70px; align-self:start; font-size:13.5px;
          max-height:calc(100vh - 90px); overflow:auto; }
  nav.side h4, aside.toc h4 { margin:0 0 8px; font-size:11px; text-transform:uppercase;
          letter-spacing:.08em; color:var(--muted); }
  nav.side a, aside.toc a { display:block; padding:3px 8px; border-radius:6px; color:var(--fg); }
  nav.side a:hover, aside.toc a:hover { background:var(--code-bg); text-decoration:none; }
  nav.side a.lvl2 { padding-left:22px; color:var(--muted); }
  main { min-width:0; }
  h1 { font-size:32px; border-bottom:1px solid var(--border); padding-bottom:12px; }
  h2 { font-size:24px; border-bottom:1px solid var(--border); padding-bottom:8px; margin-top:44px; }
  h3 { font-size:18px; margin-top:28px; }
  code { background:var(--code-bg); border-radius:6px; padding:2px 6px;
         font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:.9em; }
  pre { background:var(--code-bg); border:1px solid var(--border); border-radius:10px;
        padding:14px 16px; overflow-x:auto; }
  pre code { background:none; padding:0; }
  table { border-collapse:collapse; width:100%; font-size:14.5px; margin:14px 0; }
  th, td { border:1px solid var(--border); padding:7px 12px; text-align:left; }
  th { background:var(--code-bg); }
  .chip { display:inline-block; background:var(--chip); color:var(--chip-fg); border-radius:999px;
          padding:2px 12px; font-size:12.5px; font-weight:600; margin-right:8px; }
  .card { background:var(--card); border:1px solid var(--border); border-radius:12px;
          padding:18px 20px; margin:18px 0; }
  .win { color:var(--ok); font-weight:600; }
  .note { color:var(--warn); }
  img.shot { max-width:100%; border:1px solid var(--border); border-radius:10px; margin:10px 0; }
  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  @media (max-width:1100px) { .wrap { grid-template-columns:1fr; } nav.side, aside.toc { display:none; } }
  @media (max-width:760px) { .grid2 { grid-template-columns:1fr; } }
  .kbd { border:1px solid var(--border); border-bottom-width:2px; border-radius:5px;
         padding:1px 6px; font-size:.85em; background:var(--code-bg); }
</style>
</head>
<body>
<header class="site">
  <span class="brand">🚀 SpaceQuest — Course Showcase</span>
  <span class="tag">LLM Zoomcamp capstone · RAG over Wikipedia space-exploration articles</span>
</header>

<div class="wrap">
<nav class="side">
  <h4>Project</h4>
  <a href="#overview">Overview</a>
  <a href="#problem">Problem statement</a>
  <a href="#arch">Architecture</a>
  <h4>Pipeline modules</h4>
  <a class="lvl2" href="#ingestion">1 · Ingestion (dlt)</a>
  <a class="lvl2" href="#kb">2 · Knowledge base (SQLite)</a>
  <a class="lvl2" href="#retrieval">3 · Hybrid retrieval</a>
  <a class="lvl2" href="#rewriting">4 · Query rewriting</a>
  <a class="lvl2" href="#rerank">5 · Re-ranking</a>
  <a class="lvl2" href="#generation">6 · Generation</a>
  <a class="lvl2" href="#eval">7 · Evaluation</a>
  <a class="lvl2" href="#interface">8 · Interface</a>
  <a class="lvl2" href="#monitoring">9 · Monitoring</a>
  <a class="lvl2" href="#docker">10 · Docker</a>
  <h4>Results</h4>
  <a href="#rubric">Rubric scorecard</a>
</nav>

<main>
<h1>SpaceQuest: Hybrid RAG over Space-Exploration Articles</h1>
<p>
<span class="chip">Python 3.12</span><span class="chip">OpenAI gpt-4o-mini</span>
<span class="chip">SQLite knowledge base</span><span class="chip">dlt ingestion</span>
<span class="chip">Streamlit UI + dashboard</span><span class="chip">Docker</span>
</p>
<p>End-to-end RAG capstone for the LLM Zoomcamp. 30 curated Wikipedia articles (~762 chunks)
about space exploration are ingested with <code>dlt</code> into SQLite, embedded with OpenAI,
retrieved via BM25 / dense / hybrid RRF, and answered by a grounded GPT-4o-mini prompt with
inline citations. Every query and 👍/👎 rating is logged and charted in a monitoring dashboard.</p>

<div class="card">
<b>Course concepts applied in this project:</b>
agentic-RAG module → retrieval/generation split · vector search → embeddings + cosine retrieval ·
evaluation → ground-truth generation, hit-rate/MRR, LLM-as-judge · monitoring → feedback
collection + dashboard · best practices → hybrid search, re-ranking, query rewriting.
</div>

<h2 id="overview">Overview</h2>
<div class="grid2">
  <div><img class="shot" src="{CHAT}" alt="SpaceQuest chat interface with grounded answer and sources"></div>
  <div><img class="shot" src="{DASH}" alt="Monitoring dashboard"></div>
</div>

<h2 id="problem">Problem statement</h2>
<p>General-purpose chatbots answer space-exploration questions from pre-training memory, so
mission facts get hallucinated — wrong crew counts, confused rover timelines, invented dates.
SpaceQuest constrains generation to retrieved evidence: each question first retrieves relevant
chunks from a dedicated knowledge base; the LLM may only use that context and cites sources
inline. Retrieval quality was measured across six approaches and generation quality across two
prompt designs; the best variant shipped.</p>

<h2 id="arch">Architecture</h2>
<img class="shot" src="{ARCH}" alt="SpaceQuest architecture diagram">

<h2 id="ingestion">1 · Ingestion pipeline (dlt)</h2>
<p><code>src/ingest_dlt.py</code> runs a dlt pipeline (course automation tool) that loads the
committed corpus and chunked children into SQLite with <code>write_disposition="replace"</code>:</p>
<pre><code>pipeline = dlt.pipeline(
    pipeline_name="wikipedia_ingestion",
    destination=dlt.destinations.sqlalchemy(f"sqlite:///{DB_PATH}"),
    dataset_name="kb",
)
pipeline.run([load_articles()], table_name="documents", write_disposition="replace")
pipeline.run([chunks], table_name="chunks", write_disposition="replace")   # 762 chunks</code></pre>
<p>Chunking (<code>src/chunking.py</code>): 300-word windows, 50-word overlap; chunks under
30 words dropped.</p>

<h2 id="kb">2 · Knowledge base (SQLite)</h2>
<p>Single file <code>data/knowledge_base__kb.db</code> holds the corpus, the chunk index, the
OpenAI embeddings (<code>text-embedding-3-small</code>, 1536-d, written back by
<code>src/indexing.py</code>), and the monitoring tables (<code>query_log</code>,
<code>feedback</code>). Retrieval loads everything into memory once:</p>
<pre><code>SELECT rowid, doc_title, url, chunk_id, text, embedding
FROM chunks WHERE embedding IS NOT NULL</code></pre>

<h2 id="retrieval">3 · Hybrid retrieval</h2>
<p><code>src/retrieval.py</code> implements three search modes fused with Reciprocal Rank
Fusion (k = 60): BM25 (<code>rank-bm25</code>, tokenized <code>[a-z0-9]+</code>), dense cosine
similarity over normalized embeddings, and the RRF combination:</p>
<pre><code>for rank, (i, _) in enumerate(dense):
    scores[i] = scores.get(i, 0.0) + 1.0 / (RRF_K + rank + 1)
for rank, (i, _) in enumerate(sparse):
    scores[i] = scores.get(i, 0.0) + 1.0 / (RRF_K + rank + 1)</code></pre>
<p>The UI lets the user switch method live; BM25 is the default because it won the evaluation
below.</p>

<h2 id="rewriting">4 · Query rewriting (best practice)</h2>
<p><code>rewrite_query()</code> asks gpt-4o-mini (temperature 0) to expand abbreviations and
resolve pronouns before retrieval. Evaluated on the full ground-truth set — it did not beat
plain BM25 on this corpus, so it ships as an opt-in checkbox rather than the default.</p>

<h2 id="rerank">5 · Document re-ranking (best practice)</h2>
<p><code>src/rerank.py</code> prompts gpt-4o-mini to score each candidate chunk 0–3 for
question relevance and reorders. Evaluated: hit-rate unchanged (0.9885), MRR dropped
(0.9636 → 0.882) — the lexical ordering was already right, so re-ranking is available but not
the default. Both attempts are reported honestly in the README.</p>

<h2 id="generation">6 · Grounded generation</h2>
<p><code>src/generate.py</code> builds the context (top-5 chunks with titles + URLs) and calls
gpt-4o-mini at temperature 0.1. Two prompt variants were judged; the winner rules: answer
<em>only</em> from context, cite as <code>[title]</code>, refuse when absent:</p>
<pre><code>Answer ONLY using the context below. Cite sources as [title].
If the context doesn't contain the answer, say you don't know.</code></pre>
<p>Verified output: <em>“Twelve people have walked on the Moon during the Apollo program
[Apollo program].”</em></p>

<h2 id="eval">7 · Evaluation</h2>
<h3>Ground truth</h3>
<p><code>eval/build_ground_truth.py</code> generated 87 Q&amp;A pairs from the corpus itself
(gpt-4o-mini, JSON response format), committed to <code>data/eval/ground_truth.json</code>.</p>
<h3>Retrieval evaluation — hit-rate@5 / MRR@5</h3>
<table>
<tr><th>Method</th><th>Hit-rate@5</th><th>MRR@5</th></tr>
<tr><td>Vector only</td><td>0.9655</td><td>0.9540</td></tr>
<tr><td class="win">BM25 only (shipped)</td><td class="win">0.9885</td><td class="win">0.9636</td></tr>
<tr><td>Hybrid (RRF)</td><td>0.9770</td><td>0.9626</td></tr>
<tr><td>Hybrid + query rewrite</td><td>0.9770</td><td>0.9540</td></tr>
<tr><td>BM25 + LLM re-rank</td><td>0.9885</td><td>0.8820</td></tr>
<tr><td>Hybrid + LLM re-rank</td><td>0.9770</td><td>0.9253</td></tr>
</table>
<h3>LLM output evaluation — LLM-as-judge (30 questions, 0–5)</h3>
<table>
<tr><th>Prompt variant</th><th>Correctness</th><th>Groundedness</th></tr>
<tr><td class="win">PROMPT_V1 (shipped)</td><td class="win">4.700</td><td class="win">4.533</td></tr>
<tr><td>PROMPT_V2</td><td>4.667</td><td>4.367</td></tr>
</table>

<h2 id="interface">8 · Interface</h2>
<p><code>app/app.py</code> — Streamlit chat with a retrieval-method selector, rewrite toggle,
expandable chunk-level sources, and 👍/👎 buttons. A terminal CLI (<code>scripts/ask.py</code>)
covers the same flow headlessly. Run with <code>streamlit run app/app.py</code>.</p>

<h2 id="monitoring">9 · Monitoring</h2>
<p><code>src/monitoring.py</code> writes every query (question, rewritten question, method,
answer, latency, token usage, sources) and each 👍/👎 into SQLite. The dashboard tab renders
four KPIs (volume, avg latency, avg tokens, 👍/👎) and five charts: questions per day, latency
per query, queries by retrieval method, top retrieved documents, feedback split.</p>

<h2 id="docker">10 · Containerization &amp; reproducibility</h2>
<pre><code>docker compose up --build     # app at http://localhost:8501 (APP_PORT override)</code></pre>
<p>Dockerfile (python:3.12-slim) + compose service with <code>data/</code> and
<code>logs/</code> volumes; secrets via <code>.env</code>. Corpus and evaluation data are
committed, <code>requirements.txt</code> is fully pinned, and the README's quick start
rebuilds the KB from scratch with four commands.</p>

<h2 id="rubric">Rubric scorecard</h2>
<table>
<tr><th>Criterion</th><th>Evidence in this project</th><th>Target</th></tr>
<tr><td>Problem description</td><td>README problem statement</td><td>2</td></tr>
<tr><td>Retrieval flow</td><td>SQLite KB + grounded LLM</td><td>2</td></tr>
<tr><td>Retrieval evaluation</td><td>6 variants compared, winner shipped</td><td>2</td></tr>
<tr><td>LLM evaluation</td><td>2 prompt variants judged, winner shipped</td><td>2</td></tr>
<tr><td>Interface</td><td>Streamlit UI + CLI</td><td>2</td></tr>
<tr><td>Ingestion pipeline</td><td>dlt automated pipeline</td><td>2</td></tr>
<tr><td>Monitoring</td><td>Feedback + 5-chart dashboard</td><td>2</td></tr>
<tr><td>Containerization</td><td>App in docker-compose, verified</td><td>2</td></tr>
<tr><td>Reproducibility</td><td>Committed data, pinned deps, docker path</td><td>2</td></tr>
<tr><td>Hybrid search · re-ranking · query rewriting</td><td>All implemented and evaluated</td><td>+3</td></tr>
</table>
</main>

<aside class="toc">
<h4>On this page</h4>
<a href="#overview">Overview</a>
<a href="#problem">Problem statement</a>
<a href="#arch">Architecture</a>
<a href="#ingestion">1 · Ingestion</a>
<a href="#kb">2 · Knowledge base</a>
<a href="#retrieval">3 · Hybrid retrieval</a>
<a href="#rewriting">4 · Query rewriting</a>
<a href="#rerank">5 · Re-ranking</a>
<a href="#generation">6 · Generation</a>
<a href="#eval">7 · Evaluation</a>
<a href="#interface">8 · Interface</a>
<a href="#monitoring">9 · Monitoring</a>
<a href="#docker">10 · Docker</a>
<a href="#rubric">Rubric scorecard</a>
</aside>
</div>
</body>
</html>
"""

out = DOCS / "course-summary.html"
out.write_text(
    html.replace("{CHAT}", b64("screenshot_chat.png"))
    .replace("{DASH}", b64("screenshot_dashboard.png"))
    .replace("{ARCH}", b64("architecture.png")),
    encoding="utf-8",
)
print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
