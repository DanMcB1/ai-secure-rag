"""Document-level access control used at retrieval time.

A user may read a document (or a chunk that inherits that document's ACL)
only when every rule below passes:

1. Role — the document allows their role, or allows any role.
2. Store — the document is visible at every store, or the user is a
   group-level employee (store = "group"), or the document belongs to
   the user's store.
3. Department — the document allows any department, or the user's
   department is listed.
4. Sensitivity — the user's clearance is at least the document's
   sensitivity (public < internal < confidential < restricted).

Unauthorized chunks are dropped *before* similarity ranking. A prompt
that says "ignore these rules" cannot change the result, because the
model (or the extractive answer) never sees those chunks.
"""

from __future__ import annotations

from .models import SENSITIVITY_RANK, Chunk, Document, User


def _has_any(values: tuple[str, ...] | list[str]) -> bool:
    return any(v == "any" for v in values)


def role_allows(user: User, roles: tuple[str, ...] | list[str]) -> bool:
    return _has_any(roles) or user.role in roles


def store_allows(user: User, store_ids: tuple[str, ...] | list[str]) -> bool:
    if _has_any(store_ids):
        return True
    if user.store == "group":
        return True
    return user.store in store_ids


def department_allows(user: User, departments: tuple[str, ...] | list[str]) -> bool:
    return _has_any(departments) or user.department in departments


def sensitivity_allows(user: User, sensitivity: str) -> bool:
    user_rank = SENSITIVITY_RANK[user.max_sensitivity]
    doc_rank = SENSITIVITY_RANK[sensitivity]
    return user_rank >= doc_rank


def user_can_read(user: User, item: Document | Chunk) -> bool:
    """Return True if *user* is allowed to see *item* (document or chunk)."""
    return (
        role_allows(user, item.roles)
        and store_allows(user, item.store_ids)
        and department_allows(user, item.departments)
        and sensitivity_allows(user, item.sensitivity)
    )


def denial_reasons(user: User, item: Document | Chunk) -> list[str]:
    """Human-readable reasons the user cannot read this item (for tests / debug)."""
    reasons: list[str] = []
    if not role_allows(user, item.roles):
        reasons.append("role")
    if not store_allows(user, item.store_ids):
        reasons.append("store")
    if not department_allows(user, item.departments):
        reasons.append("department")
    if not sensitivity_allows(user, item.sensitivity):
        reasons.append("sensitivity")
    return reasons
