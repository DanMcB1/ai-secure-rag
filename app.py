"""Row-Level Secure RAG Engine — Streamlit UI.

Run with:  streamlit run app.py
Works fully offline. No API key required.
"""

from __future__ import annotations

from html import escape

import streamlit as st

from securerag import COMPANY
from securerag.engine import SecureRagEngine
from securerag.llm import llm_config
from securerag.models import (
    label_category,
    label_dept,
    label_roles,
    label_stores,
)
from securerag.samples import DEFAULT_QUESTION, SAMPLES
from securerag.users import DEFAULT_LEFT_USER, DEFAULT_RIGHT_USER, all_users

st.set_page_config(
    page_title="Row-Level Secure RAG Engine",
    page_icon="blueprint",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
  .block-container { padding-top: 1.4rem; max-width: 1280px; }
  .demo-banner {
    background: #fff6e5;
    border: 1px solid #e6d2a8;
    color: #5a4500;
    padding: 0.7rem 1rem;
    border-radius: 8px;
    font-size: 0.95rem;
    margin-bottom: 0.8rem;
  }
  .leak-banner {
    background: #fdecea;
    border: 1px solid #e8b4b4;
    color: #7a1f1f;
    padding: 0.7rem 1rem;
    border-radius: 8px;
    font-size: 0.95rem;
    margin-bottom: 0.8rem;
  }
  .ok-banner {
    background: #e8f6f1;
    border: 1px solid #b7ddd0;
    color: #1c4d3e;
    padding: 0.7rem 1rem;
    border-radius: 8px;
    font-size: 0.95rem;
    margin-bottom: 0.8rem;
  }
  .user-chip {
    background: #e8eef6;
    border: 1px solid #c5d0e0;
    border-radius: 10px;
    padding: 0.65rem 0.85rem;
    margin-bottom: 0.6rem;
  }
  .chunk-card {
    background: #fff;
    border: 1px solid #d5dbe3;
    border-left: 4px solid #1e3a5f;
    border-radius: 10px;
    padding: 0.75rem 0.9rem;
    margin: 0 0 0.7rem;
  }
  .chunk-card.leak {
    border-left-color: #9b2c2c;
    background: #fff7f7;
  }
  .acl-pill {
    display: inline-block;
    background: #e8eef6;
    border: 1px solid #c5d0e0;
    border-radius: 999px;
    padding: 2px 10px;
    margin: 0 6px 6px 0;
    font-size: 0.8rem;
  }
  .acl-pill.restricted { background: #fdecea; border-color: #e8b4b4; color: #7a1f1f; }
  .acl-pill.confidential { background: #fff6e5; border-color: #e6d2a8; color: #5a4500; }
  .acl-pill.internal { background: #e8eef6; }
  .acl-pill.public { background: #e8f6f1; border-color: #b7ddd0; color: #1c4d3e; }
  .chunk-kicker {
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #4a5a70;
    font-weight: 700;
    margin: 0 0 0.25rem;
  }
  h1 { letter-spacing: -0.02em; }
  div[data-testid="stMetric"] {
    background: #f3f5f8;
    border: 1px solid #d5dbe3;
    border-radius: 10px;
    padding: 8px 12px;
  }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Building the local document index…")
def get_engine() -> SecureRagEngine:
    return SecureRagEngine()


def _init_state() -> None:
    defaults = {
        "question": DEFAULT_QUESTION,
        "left_user": DEFAULT_LEFT_USER,
        "right_user": DEFAULT_RIGHT_USER,
        "single_user": DEFAULT_LEFT_USER,
        "naive": False,
        "compare_results": None,
        "single_result": None,
        "auto_ran": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _user_options() -> dict[str, str]:
    return {user.id: user.display for user in all_users()}


def _sensitivity_class(sensitivity: str) -> str:
    if sensitivity in {"restricted", "confidential", "internal", "public"}:
        return sensitivity
    return "internal"


def _filtered_label(retrieval) -> str:
    if retrieval.mode == "naive":
        return "0 (filter off)"
    return str(retrieval.filtered_out_count)


def _breakdown_sentence(retrieval) -> str:
    if retrieval.mode == "naive":
        n = retrieval.unauthorized_corpus_count
        leaked = len(retrieval.leaked_chunks)
        extra = (
            f" Of the chunks that were actually retrieved, {leaked} would have been blocked in secure mode."
            if leaked
            else ""
        )
        return (
            f"Naive mode is on, so nothing was filtered before ranking. "
            f"{n} chunk(s) in the corpus would have been held back in secure mode.{extra}"
        )
    if retrieval.filtered_out_count == 0:
        return "No chunks were held back for this user."
    parts = [
        f"{count} {name}"
        for name, count in sorted(retrieval.filtered_out_by_sensitivity.items(), key=lambda kv: kv[0])
    ]
    return (
        f"{retrieval.filtered_out_count} chunk(s) were held back before ranking "
        f"({', '.join(parts)}). Their content is not shown."
    )


def _render_chunk_card(item, number: int | None = None) -> None:
    chunk = item.chunk
    leak = not item.allowed
    kicker = f"Citation [{number}] · score {item.score:.2f}" if number is not None else f"Score {item.score:.2f}"
    if leak:
        kicker += " · UNAUTHORIZED — leaked in naive mode"
    pills = [
        f'<span class="acl-pill {_sensitivity_class(chunk.sensitivity)}">{escape(chunk.sensitivity)}</span>',
        f'<span class="acl-pill">{escape(label_roles(chunk.roles))}</span>',
        f'<span class="acl-pill">{escape(label_stores(chunk.store_ids))}</span>',
        f'<span class="acl-pill">{escape(label_category(chunk.category))}</span>',
    ]
    klass = "chunk-card leak" if leak else "chunk-card"
    st.markdown(
        f'<div class="{klass}">'
        f'<div class="chunk-kicker">{escape(kicker)}</div>'
        f"<strong>{escape(chunk.title)}</strong>"
        f"<div style='margin:0.35rem 0 0.2rem'>{''.join(pills)}</div>"
        f"<div>{escape(chunk.text)}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _render_result(result, heading: str) -> None:
    user = result.user
    retrieval = result.retrieval
    answer = result.answer
    st.markdown(
        f'<div class="user-chip"><strong>{escape(heading)}: {escape(user.name)}</strong><br>'
        f"{escape(user.title)} · {escape(user.store_label)} · "
        f"clearance {escape(user.max_sensitivity)}</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Retrieved", len(retrieval.chunks))
    c2.metric("Filtered out", _filtered_label(retrieval))
    c3.metric("Candidates scored", retrieval.candidates_considered)

    if retrieval.mode == "naive" and retrieval.leaked_chunks:
        titles = ", ".join(dict.fromkeys(item.chunk.title for item in retrieval.leaked_chunks))
        st.markdown(
            f'<div class="leak-banner"><strong>Leak (naive mode):</strong> this answer used '
            f"{len(retrieval.leaked_chunks)} chunk(s) {escape(user.name)} is not allowed to see, "
            f"including: {escape(titles)}.</div>",
            unsafe_allow_html=True,
        )
    elif retrieval.mode == "secure":
        st.markdown(
            f'<div class="ok-banner"><strong>Secure retrieval:</strong> {_breakdown_sentence(retrieval)} '
            "Unauthorized chunks were not scored and did not reach the answer.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info(_breakdown_sentence(retrieval))

    st.markdown("**Answer**")
    st.write(answer.text)
    if answer.note:
        st.caption(answer.note)
    if answer.injection_flagged:
        st.caption(
            "The question looks like an attempt to bypass access rules. "
            "The wording was flagged for the audit log; the real defense is the retrieval filter."
        )
    if answer.citations:
        st.caption("Citations: " + " · ".join(f"[{c.number}] {c.title}" for c in answer.citations))

    if retrieval.chunks:
        st.markdown("**Retrieved chunks (with ACL tags)**")
        cite_by_id = {c.chunk_id: c.number for c in answer.citations}
        for item in retrieval.chunks:
            _render_chunk_card(item, number=cite_by_id.get(item.chunk.id))
    else:
        st.caption("No chunks were retrieved for this user.")


def _run_compare(engine: SecureRagEngine) -> None:
    question = st.session_state.question.strip()
    if not question:
        st.session_state.compare_results = None
        st.warning("Enter a question, or click one of the sample buttons.")
        return
    left, right = engine.compare(
        st.session_state.left_user,
        st.session_state.right_user,
        question,
        naive=st.session_state.naive,
        use_llm=True,
    )
    st.session_state.compare_results = (left, right)


def _run_single(engine: SecureRagEngine) -> None:
    question = st.session_state.question.strip()
    if not question:
        st.session_state.single_result = None
        st.warning("Enter a question, or click one of the sample buttons.")
        return
    st.session_state.single_result = engine.ask(
        st.session_state.single_user,
        question,
        naive=st.session_state.naive,
        use_llm=True,
    )


_init_state()
engine = get_engine()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("How this works")
    st.markdown(
        """
This is a **document Q&A assistant with access control at retrieval**, not a chatbot that "tries to be careful."

1. Each sample file has ACL tags: role, store, department, and sensitivity.
2. You pick a person (for example a service advisor at Honda) and ask a question.
3. The app **drops unauthorized chunks first**, then ranks only what remains, then writes an extractive answer with citations.
4. Flip **Naive RAG** to see the leak when that filter is off.

The same question, user, and mode always produce the same extractive answer. It runs with **no API key and no internet**.
        """
    )
    st.markdown("---")
    st.toggle(
        "Naive RAG (no ACL filter)",
        key="naive",
        help="Turns off access control so you can demonstrate the leak. This would not be a user-facing switch in production.",
    )
    if st.session_state.get("_last_naive") != st.session_state.naive:
        st.session_state.compare_results = None
        st.session_state.single_result = None
        st.session_state.auto_ran = False
        st.session_state._last_naive = st.session_state.naive
    if st.session_state.naive:
        st.error("Naive mode is on. Unauthorized documents can appear in the answer. Use this only to show the contrast.")
    else:
        st.success("Secure mode: unauthorized chunks are filtered out before ranking.")
    st.markdown("---")
    backend = "TF-IDF (scikit-learn, local)" if engine.backend_name == "tfidf" else engine.backend_name
    st.caption(
        f"{len(engine.documents)} sample documents · {len(engine.index.chunks)} chunks · {backend}"
    )
    cfg = llm_config()
    if cfg:
        st.success(
            f"Optional LLM rewrite is on ({cfg['model']} at {cfg['base']}). "
            "Only allowed passages are sent. If the call fails, the extractive answer is kept."
        )
    else:
        st.info("Optional LLM is off. No `OPENAI_API_KEY` is set, which is the default. Answers are extractive, with citations.")
    st.markdown("---")
    st.caption(f"Portfolio demo for Daniel McBrearty · {COMPANY}")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("Row-Level Secure RAG Engine")
st.caption(
    "Ask questions over company documents — each person only gets answers from files they're allowed to see. "
    "A portfolio demo — not production software."
)
st.markdown(
    f'<div class="demo-banner">'
    f"<strong>Honest label:</strong> this is a demo for interviews and practice, running on "
    f"<em>sample documents</em> for {escape(COMPANY)}. It is not connected to a real DMS, "
    "SharePoint library, or identity provider. The answers are pulled from passages the "
    "current user is allowed to see (or, in naive mode, from everything — to show the leak). "
    "This is not a production access-control system."
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Question + samples
# ---------------------------------------------------------------------------
st.subheader("Question")
st.markdown("Click a sample, or type your own. Then ask it as two people, or as one.")

cols = st.columns(4)
for i, sample in enumerate(SAMPLES):
    with cols[i % 4]:
        if st.button(sample["label"], use_container_width=True, key=f"sample_{sample['key']}"):
            st.session_state.question = sample["question"]
            st.session_state.compare_results = None
            st.session_state.single_result = None
            st.session_state.auto_ran = False

st.text_area("Question text", key="question", height=80, label_visibility="collapsed")

options = _user_options()

tab_compare, tab_single, tab_catalog, tab_audit = st.tabs(
    ["Side-by-side compare", "Ask as one user", "Document catalog", "Audit log"]
)

# ---------------------------------------------------------------------------
# Compare
# ---------------------------------------------------------------------------
with tab_compare:
    st.markdown("Same question, two users. This is the interview view.")
    left_col, mid, right_col = st.columns([3, 1, 3])
    with left_col:
        st.selectbox(
            "Left user",
            options=list(options.keys()),
            format_func=lambda uid: options[uid],
            key="left_user",
        )
    with mid:
        st.write("")
        st.write("")
        st.markdown("<div style='text-align:center;color:#4a5a70;font-weight:700'>VS</div>", unsafe_allow_html=True)
    with right_col:
        st.selectbox(
            "Right user",
            options=list(options.keys()),
            format_func=lambda uid: options[uid],
            key="right_user",
        )
    if st.button("Ask both", type="primary", use_container_width=False):
        _run_compare(engine)
        st.session_state.auto_ran = True

    # First load: run the default Honda pay-plan comparison so the screen
    # already shows the point of the demo.
    if not st.session_state.auto_ran and st.session_state.compare_results is None:
        _run_compare(engine)
        st.session_state.auto_ran = True

    if st.session_state.compare_results:
        left, right = st.session_state.compare_results
        a, b = st.columns(2)
        with a:
            _render_result(left, "Left")
        with b:
            _render_result(right, "Right")

# ---------------------------------------------------------------------------
# Single user
# ---------------------------------------------------------------------------
with tab_single:
    st.selectbox(
        "Ask as",
        options=list(options.keys()),
        format_func=lambda uid: options[uid],
        key="single_user",
    )
    if st.button("Ask", type="primary"):
        _run_single(engine)
    if st.session_state.single_result:
        _render_result(st.session_state.single_result, "User")

# ---------------------------------------------------------------------------
# Catalog — labeled as a demo admin view
# ---------------------------------------------------------------------------
with tab_catalog:
    st.markdown(
        f'<div class="demo-banner">'
        "<strong>Demo admin view:</strong> this catalog lists every sample document and its "
        "ACL tags so you can explain the corpus in an interview. A service advisor using a "
        "real assistant would not get this list. Bodies of restricted files are hidden here "
        "unless you expand a row."
        "</div>",
        unsafe_allow_html=True,
    )
    rows = []
    for doc in engine.documents:
        rows.append(
            {
                "id": doc.id,
                "title": doc.title,
                "category": label_category(doc.category),
                "sensitivity": doc.sensitivity,
                "stores": label_stores(doc.store_ids),
                "roles": label_roles(doc.roles),
                "departments": (
                    "Any department" if "any" in doc.departments else ", ".join(label_dept(d) for d in doc.departments)
                ),
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)
    with st.expander("Show document bodies (demo only)"):
        pick = st.selectbox(
            "Document",
            options=[d.id for d in engine.documents],
            format_func=lambda did: next(d.title for d in engine.documents if d.id == did),
        )
        doc = next(d for d in engine.documents if d.id == pick)
        st.caption(
            f"{doc.sensitivity} · {label_roles(doc.roles)} · {label_stores(doc.store_ids)}"
        )
        st.write(doc.body)

# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------
with tab_audit:
    st.markdown(
        "Every question is logged: who asked, the mode, which documents were retrieved, "
        "how many chunks were filtered out (counts only), and whether naive mode leaked. "
        "Times are shown in Eastern Time."
    )
    rows = engine.audit.as_rows()
    if not rows:
        st.caption("No questions yet in this session.")
    else:
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.download_button(
            "Download audit log (JSON)",
            data=engine.audit.dumps(),
            file_name="secure-rag-audit.json",
            mime="application/json",
        )
    if st.button("Clear audit log (this session)"):
        engine.audit.clear()
        st.rerun()
