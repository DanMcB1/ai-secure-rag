"""Sample employees of Lakeside Auto Group (fictional)."""

from __future__ import annotations

from .models import User

USERS: dict[str, User] = {
    "maya": User(
        id="maya",
        name="Maya Chen",
        title="Service Advisor",
        role="service_advisor",
        department="service",
        store="honda",
        max_sensitivity="internal",
    ),
    "chris": User(
        id="chris",
        name="Chris Alvarez",
        title="F&I Manager",
        role="fi_manager",
        department="fi",
        store="toyota",
        max_sensitivity="confidential",
    ),
    "patricia": User(
        id="patricia",
        name="Patricia Walsh",
        title="General Manager",
        role="gm",
        department="management",
        store="honda",
        max_sensitivity="confidential",
    ),
    "derek": User(
        id="derek",
        name="Derek Singh",
        title="General Manager",
        role="gm",
        department="management",
        store="toyota",
        max_sensitivity="confidential",
    ),
    "lauren": User(
        id="lauren",
        name="Lauren Brooks",
        title="HR Director",
        role="hr_director",
        department="hr",
        store="group",
        max_sensitivity="restricted",
    ),
    "jonathan": User(
        id="jonathan",
        name="Jonathan Hale",
        title="CFO",
        role="cfo",
        department="finance",
        store="group",
        max_sensitivity="restricted",
    ),
}

DEFAULT_LEFT_USER = "maya"
DEFAULT_RIGHT_USER = "jonathan"


def get_user(user_id: str) -> User:
    try:
        return USERS[user_id]
    except KeyError as exc:
        known = ", ".join(USERS)
        raise KeyError(f"Unknown user '{user_id}'. Known ids: {known}") from exc


def all_users() -> list[User]:
    return list(USERS.values())
