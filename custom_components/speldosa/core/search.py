"""Rank and group Music Assistant search results for the card screen.

Spotify returns loose matches for a series name ("Die drei ???" also finds "Die drei kleinen Schweinchen").
Results are scored against the query, grouped by type, and loose matches go to a separate list.
"""

from __future__ import annotations

import re
from typing import Any

# Response keys of music_assistant.search, in the order the page shows the groups.
GROUP_ORDER = (
    ("artist", "artists"),
    ("playlist", "playlists"),
    ("album", "albums"),
    ("audiobook", "audiobooks"),
    ("podcast", "podcasts"),
    ("track", "tracks"),
    ("radio", "radio"),
)

SCORE_EXACT = 100
SCORE_PREFIX = 85
SCORE_ALL_IN_NAME = 70
SCORE_ALL_WITH_ARTIST = 55
WEAK_BELOW = SCORE_ALL_WITH_ARTIST
BEST_MATCH_MIN = SCORE_PREFIX
BEST_MATCH_MAX = 3

_TOKEN = re.compile(r"\w+|\?+|!+", re.UNICODE)


def tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.casefold())


def score(query: str, name: str, artists: list[str] | None = None) -> int:
    """How well a result matches the query, 0 to 100."""
    q = tokens(query)
    if not q:
        return 0
    n = tokens(name)
    if n == q:
        return SCORE_EXACT
    if n[: len(q)] == q:
        return SCORE_PREFIX
    name_set = set(n)
    if all(t in name_set for t in q):
        return SCORE_ALL_IN_NAME
    full = name_set | {t for a in artists or [] for t in tokens(a)}
    if all(t in full for t in q):
        return SCORE_ALL_WITH_ARTIST
    hits = sum(1 for t in q if t in full)
    return int(40 * hits / len(q))


def _item(media_type: str, raw: dict[str, Any], query: str) -> dict[str, Any] | None:
    uri = raw.get("uri")
    name = raw.get("name")
    if not uri or not name:
        return None
    artists = [a.get("name") for a in raw.get("artists") or [] if a.get("name")]
    album = (raw.get("album") or {}).get("name")
    subtitle = ", ".join(artists[:2]) or album or None
    return {
        "uri": uri,
        "name": name,
        "media_type": raw.get("media_type") or media_type,
        "image": raw.get("image"),
        "subtitle": subtitle,
        "score": score(query, name, artists),
    }


def rank_results(query: str, response: dict[str, Any] | None, types: list[str] | None = None) -> dict[str, Any]:
    """Group a music_assistant.search response.

    Returns {"best": [...], "groups": [{"media_type", "items"}], "weaker": [...], "empty": bool}.
    `types` limits the groups (filtering here, not in the search call).
    """
    response = response or {}
    best: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []
    weaker: list[dict[str, Any]] = []
    total = 0
    for media_type, key in GROUP_ORDER:
        raw_items = response.get(key) or []
        total += len(raw_items)
        if types and media_type not in types:
            continue
        items = [i for i in (_item(media_type, r, query) for r in raw_items) if i]
        items.sort(key=lambda i: -i["score"])
        strong = [i for i in items if i["score"] >= WEAK_BELOW]
        weaker.extend(i for i in items if i["score"] < WEAK_BELOW)
        if media_type == "artist":
            best = [i for i in strong if i["score"] >= BEST_MATCH_MIN][:BEST_MATCH_MAX]
            strong = [i for i in strong if i not in best]
        if strong:
            groups.append({"media_type": media_type, "items": strong})
    weaker.sort(key=lambda i: -i["score"])
    return {"best": best, "groups": groups, "weaker": weaker, "empty": total == 0}
