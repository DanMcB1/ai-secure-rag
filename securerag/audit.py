"""In-memory access audit log (optional JSONL append)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .models import Answer, RetrievalResult, User

# America/New_York is the user's zone; store UTC in the file and format ET in the UI.
try:
    from zoneinfo import ZoneInfo
    DISPLAY_TZ = ZoneInfo("America/New_York")
except Exception:  # pragma: no cover
    DISPLAY_TZ = timezone(datetime.now().astimezone().utcoffset() or timezone.utc.utcoffset(None))  # type: ignore[arg-type]


@dataclass
class AuditEntry:
    id: str
    ts_utc: str
    user_id: str
    user_name: str
    role: str
    store: str
    question: str
    mode: str
    retrieved_chunk_ids: list[str]
    retrieved_doc_ids: list[str]
    citation_doc_ids: list[str]
    filtered_out_count: int
    filtered_out_by_sensitivity: dict[str, int]
    unauthorized_corpus_count: int
    leaked_chunk_ids: list[str]
    leaked_doc_ids: list[str]
    injection_flagged: bool
    refusal: bool
    answer_preview: str
    answer_source: str
    candidates_considered: int

    def display_time(self) -> str:
        dt = datetime.fromisoformat(self.ts_utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local = dt.astimezone(DISPLAY_TZ)
        return local.strftime("%Y-%m-%d %I:%M:%S %p") + " ET"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _preview(text: str, limit: int = 220) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


class AuditLog:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self.entries: list[AuditEntry] = []

    def record(
        self,
        user: User,
        question: str,
        retrieval: RetrievalResult,
        answer: Answer,
    ) -> AuditEntry:
        leaked_chunks = [item.chunk for item in retrieval.leaked_chunks]
        entry = AuditEntry(
            id=str(uuid4())[:8],
            ts_utc=_now_utc().isoformat(),
            user_id=user.id,
            user_name=user.name,
            role=user.role,
            store=user.store,
            question=question,
            mode=retrieval.mode,
            retrieved_chunk_ids=[item.chunk.id for item in retrieval.chunks],
            retrieved_doc_ids=list(dict.fromkeys(item.chunk.doc_id for item in retrieval.chunks)),
            citation_doc_ids=list(dict.fromkeys(c.doc_id for c in answer.citations)),
            filtered_out_count=retrieval.filtered_out_count,
            filtered_out_by_sensitivity=dict(retrieval.filtered_out_by_sensitivity),
            unauthorized_corpus_count=retrieval.unauthorized_corpus_count,
            leaked_chunk_ids=[c.id for c in leaked_chunks],
            leaked_doc_ids=list(dict.fromkeys(c.doc_id for c in leaked_chunks)),
            injection_flagged=answer.injection_flagged,
            refusal=answer.refusal,
            answer_preview=_preview(answer.text),
            answer_source=answer.source,
            candidates_considered=retrieval.candidates_considered,
        )
        self.entries.append(entry)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
        return entry

    def clear(self) -> None:
        self.entries.clear()

    def as_rows(self) -> list[dict[str, Any]]:
        rows = []
        for entry in reversed(self.entries):
            rows.append(
                {
                    "when (ET)": entry.display_time(),
                    "user": entry.user_name,
                    "role": entry.role,
                    "store": entry.store,
                    "mode": entry.mode,
                    "question": entry.question,
                    "retrieved docs": ", ".join(entry.retrieved_doc_ids) or "—",
                    "filtered out": entry.filtered_out_count,
                    "leaked docs": ", ".join(entry.leaked_doc_ids) or "—",
                    "injection flagged": "yes" if entry.injection_flagged else "no",
                    "refusal": "yes" if entry.refusal else "no",
                    "answer preview": entry.answer_preview,
                }
            )
        return rows

    def dumps(self) -> str:
        return json.dumps([asdict(e) for e in self.entries], indent=2, ensure_ascii=False)
