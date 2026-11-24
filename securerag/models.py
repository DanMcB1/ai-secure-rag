"""Shared dataclasses for users, documents, chunks, and retrieval results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SENSITIVITY_RANK = {
    "public": 0,
    "internal": 1,
    "confidential": 2,
    "restricted": 3,
}

STORE_LABELS = {
    "honda": "Lakeside Honda",
    "toyota": "Lakeside Toyota",
    "ford": "Lakeside Ford",
    "group": "Group / all stores",
    "any": "All stores",
}

ROLE_LABELS = {
    "service_advisor": "Service Advisor",
    "service_manager": "Service Manager",
    "fi_manager": "F&I Manager",
    "gm": "General Manager",
    "hr_director": "HR Director",
    "cfo": "CFO",
    "controller": "Controller",
    "salesperson": "Salesperson",
    "any": "Any role",
}

DEPT_LABELS = {
    "service": "Service",
    "fi": "F&I",
    "sales": "Sales",
    "management": "Management",
    "hr": "HR",
    "finance": "Finance",
    "legal": "Legal",
    "it": "IT",
    "parts": "Parts",
    "any": "Any department",
}

CATEGORY_LABELS = {
    "policy": "Company policy",
    "hr": "HR",
    "fi": "F&I",
    "pl": "P&L / finance",
    "service": "Service",
    "legal": "Legal",
    "executive": "Executive",
    "store": "Store operations",
}


def label_store(store_id: str) -> str:
    return STORE_LABELS.get(store_id, store_id)


def label_role(role: str) -> str:
    return ROLE_LABELS.get(role, role)


def label_dept(dept: str) -> str:
    return DEPT_LABELS.get(dept, dept)


def label_category(category: str) -> str:
    return CATEGORY_LABELS.get(category, category)


def label_stores(store_ids: tuple[str, ...] | list[str]) -> str:
    if "any" in store_ids:
        return "All stores"
    return ", ".join(label_store(s) for s in store_ids)


def label_roles(roles: tuple[str, ...] | list[str]) -> str:
    if "any" in roles:
        return "Any role"
    return ", ".join(label_role(r) for r in roles)


@dataclass(frozen=True)
class User:
    id: str
    name: str
    title: str
    role: str
    department: str
    store: str  # a store id, or "group" for group-level employees
    max_sensitivity: str

    @property
    def store_label(self) -> str:
        return label_store(self.store)

    @property
    def role_label(self) -> str:
        return label_role(self.role)

    @property
    def department_label(self) -> str:
        return label_dept(self.department)

    @property
    def display(self) -> str:
        return f"{self.name} · {self.title} · {self.store_label}"


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    category: str
    store_ids: tuple[str, ...]
    departments: tuple[str, ...]
    roles: tuple[str, ...]
    sensitivity: str
    body: str


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    title: str
    category: str
    store_ids: tuple[str, ...]
    departments: tuple[str, ...]
    roles: tuple[str, ...]
    sensitivity: str
    text: str
    index: int

    def acl_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "category": self.category,
            "stores": list(self.store_ids),
            "departments": list(self.departments),
            "roles": list(self.roles),
            "sensitivity": self.sensitivity,
        }


@dataclass
class ScoredChunk:
    chunk: Chunk
    score: float
    allowed: bool


@dataclass
class RetrievalResult:
    chunks: list[ScoredChunk]
    filtered_out_count: int
    filtered_out_by_sensitivity: dict[str, int]
    candidates_considered: int
    candidate_ids: tuple[str, ...]
    leaked_chunks: list[ScoredChunk]
    mode: str  # "secure" | "naive"
    query: str
    user_id: str
    # How many corpus chunks this user is not allowed to read, whether
    # or not the filter was applied. Used to describe the leak in naive mode.
    unauthorized_corpus_count: int = 0


@dataclass
class Citation:
    number: int
    chunk_id: str
    doc_id: str
    title: str
    sensitivity: str


@dataclass
class Answer:
    text: str
    citations: list[Citation]
    refusal: bool
    source: str  # "extractive" | "llm" | "none"
    note: str = ""
    retrieval: RetrievalResult | None = None
    injection_flagged: bool = False
    extra: dict[str, Any] = field(default_factory=dict)
