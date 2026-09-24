"""Local favorites — which automation tools the user has starred."""
from __future__ import annotations

from core import store

_KEY = "favorites"


def get_all() -> list[str]:
    return store.load(_KEY, [])


def is_favorite(tool_slug: str) -> bool:
    return tool_slug in get_all()


def toggle(tool_slug: str) -> bool:
    """Flip favorite status for `tool_slug`. Returns the new state (True = now favorited)."""
    favs = set(get_all())
    if tool_slug in favs:
        favs.discard(tool_slug)
        now_favorited = False
    else:
        favs.add(tool_slug)
        now_favorited = True
    store.save(_KEY, sorted(favs))
    return now_favorited
