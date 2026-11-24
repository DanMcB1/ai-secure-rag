"""High-level ask / compare helpers used by the app, CLI, and tests."""

from __future__ import annotations

from dataclasses import dataclass

from .answer import answer_question
from .audit import AuditEntry, AuditLog
from .index import DEFAULT_TOP_K, VectorIndex, build_index
from .models import Answer, Document, RetrievalResult, User
from .users import get_user


@dataclass
class AskResult:
    user: User
    question: str
    retrieval: RetrievalResult
    answer: Answer
    audit: AuditEntry


class SecureRagEngine:
    def __init__(self, index: VectorIndex | None = None, audit: AuditLog | None = None) -> None:
        self.index = index or build_index()
        self.audit = audit or AuditLog()

    @property
    def documents(self) -> list[Document]:
        return list(self.index.documents)

    @property
    def backend_name(self) -> str:
        return self.index.backend_name

    def ask(
        self,
        user: User | str,
        question: str,
        naive: bool = False,
        top_k: int = DEFAULT_TOP_K,
        use_llm: bool = True,
        record: bool = True,
    ) -> AskResult:
        person = get_user(user) if isinstance(user, str) else user
        retrieval = self.index.search(question, person, top_k=top_k, naive=naive)
        answer = answer_question(question, retrieval, use_llm=use_llm)
        entry = self.audit.record(person, question, retrieval, answer) if record else None
        if entry is None:
            # Tests sometimes skip the log; build a throwaway entry-less result.
            from .audit import AuditLog as _AL

            entry = _AL().record(person, question, retrieval, answer)
        return AskResult(user=person, question=question, retrieval=retrieval, answer=answer, audit=entry)

    def compare(
        self,
        left: User | str,
        right: User | str,
        question: str,
        naive: bool = False,
        top_k: int = DEFAULT_TOP_K,
        use_llm: bool = True,
    ) -> tuple[AskResult, AskResult]:
        a = self.ask(left, question, naive=naive, top_k=top_k, use_llm=use_llm)
        b = self.ask(right, question, naive=naive, top_k=top_k, use_llm=use_llm)
        return a, b


def format_ask(result: AskResult) -> str:
    """Plain-text rendering for the CLI and saved examples."""
    user = result.user
    retrieval = result.retrieval
    answer = result.answer
    lines = [
        f"User: {user.display}",
        f"Role / store / clearance: {user.role_label} · {user.store_label} · {user.max_sensitivity}",
        f"Mode: {retrieval.mode}",
        f"Question: {result.question}",
        "",
        "Answer:",
        answer.text,
    ]
    if answer.note:
        lines.append(f"Note: {answer.note}")
    if answer.citations:
        lines.append("")
        lines.append("Citations:")
        for cite in answer.citations:
            lines.append(f"  [{cite.number}] {cite.title} ({cite.sensitivity}, {cite.doc_id})")
    lines.append("")
    lines.append(
        f"Retrieved {len(retrieval.chunks)} chunk(s) from {retrieval.candidates_considered} "
        f"candidates after the filter."
    )
    if retrieval.mode == "secure":
        breakdown = ", ".join(
            f"{count} {name}" for name, count in sorted(retrieval.filtered_out_by_sensitivity.items())
        ) or "none"
        lines.append(
            f"Filtered out before ranking: {retrieval.filtered_out_count} chunk(s) ({breakdown}). "
            "Their content is not shown."
        )
    else:
        lines.append(
            f"Naive mode: the ACL filter was off. {retrieval.unauthorized_corpus_count} "
            "chunk(s) in the corpus would have been blocked in secure mode."
        )
        if retrieval.leaked_chunks:
            titles = ", ".join(dict.fromkeys(item.chunk.title for item in retrieval.leaked_chunks))
            lines.append(f"LEAK — unauthorized chunks in the context: {titles}")
    if answer.injection_flagged:
        lines.append("Injection-style wording was flagged. The retrieval filter is still the control.")
    if retrieval.chunks:
        lines.append("")
        lines.append("Retrieved chunks (with ACL tags):")
        for item in retrieval.chunks:
            chunk = item.chunk
            leak = "  [UNAUTHORIZED]" if not item.allowed else ""
            lines.append(
                f"  - {chunk.title}  score={item.score:.3f}  "
                f"sensitivity={chunk.sensitivity}  roles={','.join(chunk.roles)}  "
                f"stores={','.join(chunk.store_ids)}{leak}"
            )
            lines.append(f"    {chunk.text[:280].replace(chr(10), ' ')}")
    return "\n".join(lines) + "\n"
