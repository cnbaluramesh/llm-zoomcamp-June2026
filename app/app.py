"""SpaceQuest RAG - Streamlit app: chat interface + monitoring dashboard."""
import json
import sqlite3
import sys
import time
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import CHAT_MODEL, DB_PATH  # noqa: E402
from generate import PROMPT_V1, PROMPT_V2, generate_answer  # noqa: E402
from monitoring import log_feedback, log_query  # noqa: E402
from retrieval import Retriever, rewrite_query  # noqa: E402

st.set_page_config(page_title="SpaceQuest RAG", page_icon="🚀", layout="wide")

METHODS = {
    "BM25 (best)": "bm25",
    "Hybrid (BM25 + vectors)": "hybrid",
    "Vector search": "vector",
}


@st.cache_resource
def get_retriever() -> Retriever:
    return Retriever()


def tab_chat() -> None:
    st.title("🚀 SpaceQuest")
    st.caption("RAG over Wikipedia space-exploration articles · grounded answers with citations")

    col_q, col_m = st.columns([3, 2])
    with col_m:
        method_label = st.selectbox("Retrieval method", list(METHODS), index=0)
        do_rewrite = st.checkbox("Rewrite query before retrieval", value=False)

    question = st.text_input(
        "Ask a question about space exploration:",
        placeholder="e.g. How did the Space Shuttle differ from earlier spacecraft?",
    )
    ask = st.button("Ask", type="primary")

    if ask and question:
        retriever = get_retriever()
        method = METHODS[method_label]
        rewritten = rewrite_query(question) if do_rewrite else ""
        effective_q = rewritten or question
        hits = retriever.search(effective_q, method=method)
        t0 = time.time()
        out = generate_answer(question, hits)
        with st.chat_message("assistant"):
            st.markdown(out["answer"])
            with st.expander(f"📚 Sources ({len(hits)} chunks)"):
                for h in hits:
                    st.markdown(f"- **[{h.doc_title} chunk {h.chunk_id}]**({h.url}) — score {h.score:.3f}")
                    st.text(h.text[:300] + ("..." if len(h.text) > 300 else ""))
            if rewritten:
                st.caption(f"Query rewritten to: “{rewritten}”")

        query_id = log_query(
            question=question,
            rewritten=rewritten,
            method=method,
            answer=out["answer"],
            latency_s=time.time() - t0,
            prompt_tokens=out["prompt_tokens"],
            completion_tokens=out["completion_tokens"],
            sources=out["sources"],
        )
        st.session_state["last_query_id"] = query_id

        c1, c2, _ = st.columns([1, 1, 6])
        if c1.button("👍"):
            log_feedback(query_id, 1)
            st.toast("Thanks for the feedback!")
        if c2.button("👎"):
            log_feedback(query_id, -1)
            st.toast("Feedback recorded")


@st.cache_data(ttl=30)
def load_dashboard_data():
    conn = sqlite3.connect(DB_PATH)
    queries = pd.read_sql("SELECT * FROM query_log ORDER BY ts", conn)
    feedback = pd.read_sql(
        "SELECT f.*, q.question FROM feedback f LEFT JOIN query_log q ON f.query_id = q.id", conn
    )
    conn.close()
    return queries, feedback


def tab_dashboard() -> None:
    st.title("📊 Monitoring Dashboard")
    queries, feedback = load_dashboard_data()
    if queries.empty:
        st.info("No queries logged yet — ask something in the Chat tab first.")
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total questions", len(queries))
    avg_lat = queries["latency_s"].mean()
    k2.metric("Avg latency (s)", f"{avg_lat:.2f}")
    k3.metric("Avg tokens / query", int((queries.prompt_tokens + queries.completion_tokens).mean()))
    pos = (feedback.rating == 1).sum() if not feedback.empty else 0
    neg = (feedback.rating == -1).sum() if not feedback.empty else 0
    k4.metric("👍 / 👎", f"{pos} / {neg}")

    queries["ts"] = pd.to_datetime(queries.ts)
    queries["date"] = queries.ts.dt.date

    c1, c2 = st.columns(2)
    with c1:
        daily = queries.groupby("date").size().reset_index(name="questions")
        st.altair_chart(
            alt.Chart(daily).mark_bar().encode(x="date:T", y="questions:Q").properties(title="Questions per day"),
            use_container_width=True,
        )
    with c2:
        st.altair_chart(
            alt.Chart(queries.reset_index())
            .mark_line(point=True)
            .encode(x="index:Q", y="latency_s:Q")
            .properties(title="Answer latency per query"),
            use_container_width=True,
        )
    c3, c4 = st.columns(2)
    with c3:
        method_counts = queries.method.value_counts().reset_index()
        method_counts.columns = ["method", "count"]
        st.altair_chart(
            alt.Chart(method_counts).mark_bar().encode(x="method:N", y="count:Q").properties(title="Queries by retrieval method"),
            use_container_width=True,
        )
    with c4:
        by_doc = queries.head(200).assign(sources=lambda d: d.sources.apply(lambda s: [x["doc_title"] for x in json.loads(s)]))
        exploded = by_doc.explode("sources")
        top_docs = exploded.sources.value_counts().head(10).reset_index()
        top_docs.columns = ["document", "retrievals"]
        st.altair_chart(
            alt.Chart(top_docs).mark_bar().encode(x="retrievals:Q", y=alt.Y("document:N", sort="-x")).properties(title="Top retrieved documents"),
            use_container_width=True,
        )
    c5, _ = st.columns(2)
    with c5:
        if feedback.empty:
            st.info("No feedback yet.")
        else:
            fb = feedback.copy()
            fb["ts"] = pd.to_datetime(fb.ts)
            ratings = fb.rating.map({1: "👍 positive", -1: "👎 negative"}).value_counts().reset_index()
            ratings.columns = ["rating", "count"]
            st.altair_chart(
                alt.Chart(ratings).mark_arc().encode(theta="count:Q", color="rating:N").properties(title="User feedback split"),
                use_container_width=True,
            )


tab_chat_tab, tab_dash = st.tabs(["💬 Chat", "📊 Monitoring"])
with tab_chat_tab:
    tab_chat()
with tab_dash:
    tab_dashboard()
