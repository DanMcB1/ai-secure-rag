"""Flag prompt-injection-style wording. This is not the security control.

The real control is the retrieval filter: unauthorized chunks never enter
the candidate set. These patterns are logged so a demo can show that a
"ignore your rules" question was noticed — and still failed, because
there was nothing unauthorized in the context to leak.
"""

from __future__ import annotations

import re

_PATTERNS = [
    r"ignore (all )?(your|the|previous|prior) (rules|instructions|guidelines|policy|policies)",
    r"ignore (all )?rules",
    r"disregard (your |the |previous |prior )+(rules|instructions)",
    r"you are now",
    r"jailbreak",
    r"system prompt",
    r"override (the )?(acl|access|security|permissions?|filter)",
    r"do not (apply|use|follow) (the )?(acl|access|filter|rules|permissions?)",
    r"show (me )?(everything|all documents|all files)",
    r"pretend (you|I) (have|has|are|am) (no |admin|unrestricted|cfo|hr)",
    r"bypass (the )?(filter|acl|access|security|permissions?)",
    r"without (any )?(permission|permissions|acl|access control|filtering)",
    r"act as (the )?(cfo|hr director|administrator|root)",
]


def injection_flagged(question: str) -> bool:
    text = question.lower()
    return any(re.search(pattern, text) for pattern in _PATTERNS)
