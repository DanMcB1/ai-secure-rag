"""Split documents into chunks that inherit the parent document's ACL."""

from __future__ import annotations

from .models import Chunk, Document

# Aim for mid-size passages so a citation is readable in the UI.
TARGET_CHARS = 700
MIN_CHARS = 80


def _split_paragraphs(body: str) -> list[str]:
    parts = [p.strip() for p in body.replace("\r\n", "\n").split("\n\n")]
    return [p for p in parts if p]


def _pack(paragraphs: list[str]) -> list[str]:
    packed: list[str] = []
    buf = ""
    for para in paragraphs:
        if not buf:
            buf = para
            continue
        if len(buf) + 2 + len(para) <= TARGET_CHARS:
            buf = buf + "\n\n" + para
        else:
            packed.append(buf)
            buf = para
    if buf:
        packed.append(buf)
    # Merge a trailing stub into the previous chunk when it is very short.
    if len(packed) >= 2 and len(packed[-1]) < MIN_CHARS:
        packed[-2] = packed[-2] + "\n\n" + packed[-1]
        packed.pop()
    return packed


def chunk_document(doc: Document) -> list[Chunk]:
    pieces = _pack(_split_paragraphs(doc.body))
    if not pieces:
        pieces = [doc.body.strip() or doc.title]
    chunks: list[Chunk] = []
    for i, text in enumerate(pieces):
        chunks.append(
            Chunk(
                id=f"{doc.id}::c{i}",
                doc_id=doc.id,
                title=doc.title,
                category=doc.category,
                store_ids=doc.store_ids,
                departments=doc.departments,
                roles=doc.roles,
                sensitivity=doc.sensitivity,
                text=text,
                index=i,
            )
        )
    return chunks


def chunk_all(docs: list[Document]) -> list[Chunk]:
    out: list[Chunk] = []
    for doc in docs:
        out.extend(chunk_document(doc))
    return out
