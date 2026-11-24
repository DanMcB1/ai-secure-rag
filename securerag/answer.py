"""Deterministic extractive answers with citations.

Default path: pick the highest-scoring sentences from the already-filtered
retrieved chunks. No model is called. The same question, user, and mode
always produce the same answer.

Optional path (off by default): if OPENAI_API_KEY is set, a local or
OpenAI-compatible model may rewrite an answer *from those same allowed
passages only*. On any failure, the extractive text is kept.
"""

from __future__ import annotations

import re

from .inject import injection_flagged
from .llm import llm_config, maybe_rewrite_answer
from .models import Answer, Citation, RetrievalResult, ScoredChunk

STOPWORDS = frozenset(
    """
    a an the and or but if in on at to for of from with as by is are was were
    be been being it this that these those i you we they he she them my your
    our their what which who whom whose how why when where can could should
    would will may might do does did done have has had not no nor so than then
    too very just about into over after before also any some each other only
    more most such own same me us please tell show give list
    """.split()
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[a-z0-9$]+(?:'[a-z]+)?", re.I)
_ABBREV = re.compile(r"\b([aApP])\.m\.", re.I)

# Light synonyms so "pay plan" still matches a "base salary" sentence.
_SYNONYMS = {
    "pay": {"salary", "compensation", "earnings", "wage"},
    "salary": {"pay", "compensation", "earnings"},
    "compensation": {"pay", "salary", "bonus", "earnings"},
    "bonus": {"compensation", "kicker"},
    "profit": {"earnings", "net"},
    "reserve": {"backend"},
    "products": {"vsc", "gap", "service"},
}


def _tokens(text: str) -> list[str]:
    return [m.group(0).lower() for m in _WORD.finditer(text)]


def _content_tokens(text: str) -> list[str]:
    return [t for t in _tokens(text) if t not in STOPWORDS and len(t) > 1]


def _sentences(text: str) -> list[str]:
    # Keep "p.m." / "a.m." and initials like "R. Miles" from splitting a sentence.
    protected = _ABBREV.sub(r"\1.m<<DOT>>", text)
    protected = re.sub(r"\b([A-Za-z])\.", r"\1<<DOT>>", protected)
    parts = [p.strip().replace("<<DOT>>", ".") for p in _SENTENCE_SPLIT.split(protected) if p.strip()]
    return parts or [text.strip()]


def _expand(tokens: list[str]) -> set[str]:
    out = set(tokens)
    for token in tokens:
        out.update(_SYNONYMS.get(token, ()))
    return out


def _sentence_score(question_tokens: list[str], sentence: str) -> float:
    sent_tokens = _content_tokens(sentence)
    if not question_tokens or not sent_tokens:
        return 0.0
    qset = _expand(question_tokens)
    sset = _expand(sent_tokens)
    overlap = qset & sset
    if not overlap:
        return 0.0
    # Jaccard, plus a small boost when distinctive numbers/ids match.
    jaccard = len(overlap) / len(qset | sset)
    distinctive = {t for t in overlap if any(ch.isdigit() for ch in t) or t.startswith("$") or len(t) >= 8}
    money = 0.2 if re.search(r"\$\d", sentence) and any(t in qset for t in ("pay", "salary", "profit", "reserve", "gross", "bonus", "compensation", "earnings")) else 0.0
    return jaccard + 0.15 * len(distinctive) + money


def extractive_from_chunks(
    question: str,
    scored: list[ScoredChunk],
    max_sentences: int = 3,
) -> Answer:
    if not scored:
        return Answer(
            text=(
                "I don't have any documents you are allowed to see that answer "
                "this question."
            ),
            citations=[],
            refusal=True,
            source="none",
        )

    question_tokens = _content_tokens(question)
    top_score = max(item.score for item in scored)
    min_for_answer = max(0.15, 0.6 * top_score)
    pool = [item for item in scored if item.score >= min_for_answer] or scored[:1]
    candidates: list[tuple[float, int, str, ScoredChunk]] = []
    for item in pool:
        for sentence in _sentences(item.chunk.text):
            score = _sentence_score(question_tokens, sentence)
            # Blend in the retrieval score so a clearly on-topic passage wins
            # ties against a weak lexical overlap in a less relevant chunk.
            blended = score + 0.25 * item.score
            candidates.append((blended, item.chunk.index, sentence, item))

    candidates.sort(key=lambda row: row[0], reverse=True)
    chosen: list[tuple[str, ScoredChunk]] = []
    used_sentences: set[str] = set()
    min_keep = 0.08
    for blended, _idx, sentence, item in candidates:
        if len(chosen) >= max_sentences:
            break
        if sentence in used_sentences:
            continue
        if blended < min_keep and chosen:
            break
        chosen.append((sentence, item))
        used_sentences.add(sentence)

    if not chosen or (chosen and candidates and candidates[0][0] < 0.08):
        # Very weak match overall — refuse rather than stretch a bad sentence.
        return Answer(
            text=(
                "I don't have any documents you are allowed to see that answer "
                "this question."
            ),
            citations=[],
            refusal=True,
            source="extractive",
        )

    citations: list[Citation] = []
    citation_for_chunk: dict[str, int] = {}
    sentences_out: list[str] = []
    for sentence, item in chosen:
        cid = item.chunk.id
        if cid not in citation_for_chunk:
            number = len(citations) + 1
            citation_for_chunk[cid] = number
            citations.append(
                Citation(
                    number=number,
                    chunk_id=cid,
                    doc_id=item.chunk.doc_id,
                    title=item.chunk.title,
                    sensitivity=item.chunk.sensitivity,
                )
            )
        mark = citation_for_chunk[cid]
        if not sentence.endswith((".", "!", "?")):
            sentence = sentence + "."
        sentences_out.append(f"{sentence} [{mark}]")

    return Answer(
        text=" ".join(sentences_out),
        citations=citations,
        refusal=False,
        source="extractive",
    )


def answer_question(
    question: str,
    retrieval: RetrievalResult,
    use_llm: bool = True,
) -> Answer:
    flagged = injection_flagged(question)
    extractive = extractive_from_chunks(question, retrieval.chunks)
    extractive.retrieval = retrieval
    extractive.injection_flagged = flagged
    if extractive.refusal:
        if flagged and retrieval.mode == "secure":
            extractive.note = (
                "The question looks like an attempt to bypass access rules. "
                "The defense is the retrieval filter, not a polite refusal: "
                "unauthorized chunks were never in the context."
            )
        return extractive

    if use_llm and llm_config():
        passages = [
            f"[{i+1}] {item.chunk.title}: {item.chunk.text}"
            for i, item in enumerate(retrieval.chunks)
        ]
        rewritten, used, note = maybe_rewrite_answer(question, extractive.text, passages)
        if used:
            extractive.text = rewritten
            extractive.source = "llm"
        extractive.note = note
    return extractive
