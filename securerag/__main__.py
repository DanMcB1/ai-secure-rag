"""Command-line entry point: ask, compare, or list the catalog.

Examples:
  python -m securerag ask --user maya --question "What is the holiday schedule?"
  python -m securerag compare --left maya --right jonathan --question "What is the Honda GM pay plan?"
  python -m securerag catalog
"""

from __future__ import annotations

import argparse
import sys

from . import COMPANY
from .engine import SecureRagEngine, format_ask
from .models import label_roles, label_stores
from .users import USERS, all_users


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"Row-Level Secure RAG Engine for {COMPANY}. Offline demo, no API key required."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    ask = sub.add_parser("ask", help="Ask a question as one user")
    ask.add_argument("--user", required=True, choices=sorted(USERS))
    ask.add_argument("--question", required=True)
    ask.add_argument("--naive", action="store_true", help="Disable the ACL filter (demonstrates the leak)")
    ask.add_argument("--no-llm", action="store_true")
    ask.add_argument("--out", default="")

    cmp_ = sub.add_parser("compare", help="Ask the same question as two users")
    cmp_.add_argument("--left", required=True, choices=sorted(USERS))
    cmp_.add_argument("--right", required=True, choices=sorted(USERS))
    cmp_.add_argument("--question", required=True)
    cmp_.add_argument("--naive", action="store_true")
    cmp_.add_argument("--no-llm", action="store_true")
    cmp_.add_argument("--out", default="")

    sub.add_parser("catalog", help="List documents and their ACL tags")
    sub.add_parser("users", help="List sample users")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.cmd == "users":
        for user in all_users():
            print(f"{user.id:10}  {user.display}  clearance={user.max_sensitivity}")
        return 0

    engine = SecureRagEngine()
    if args.cmd == "catalog":
        print(f"{COMPANY} — {len(engine.documents)} documents, {len(engine.index.chunks)} chunks, backend={engine.backend_name}")
        print(f"{'id':32} {'sens':14} {'stores':28} roles")
        for doc in engine.documents:
            print(
                f"{doc.id:32} {doc.sensitivity:14} {label_stores(doc.store_ids):28} {label_roles(doc.roles)}"
            )
        return 0

    if args.cmd == "ask":
        result = engine.ask(args.user, args.question, naive=args.naive, use_llm=not args.no_llm)
        text = format_ask(result)
    else:
        left, right = engine.compare(
            args.left,
            args.right,
            args.question,
            naive=args.naive,
            use_llm=not args.no_llm,
        )
        text = (
            f"Same question, two users. Mode: {'naive' if args.naive else 'secure'}.\n"
            + "=" * 72
            + "\nLEFT\n"
            + format_ask(left)
            + "\n"
            + "=" * 72
            + "\nRIGHT\n"
            + format_ask(right)
        )

    print(text)
    if getattr(args, "out", ""):
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
