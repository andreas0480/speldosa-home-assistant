"""Tags, play modes and the defaults per media type."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class PlayMode(StrEnum):
    """How a tag plays when it is put on a box after the resume window."""

    FROM_START = "from_start"
    SHUFFLE = "shuffle"
    RESUME = "resume"
    # Series: one album (artist tags) or one episode (podcast tags) at a time, played whole.
    RANDOM_ALBUM = "random_album"
    NEXT_ALBUM = "next_album"
    RANDOM_EPISODE = "random_episode"
    NEXT_EPISODE = "next_episode"


SERIES_MODES = frozenset(
    {PlayMode.RANDOM_ALBUM, PlayMode.NEXT_ALBUM, PlayMode.RANDOM_EPISODE, PlayMode.NEXT_EPISODE}
)
RANDOM_SERIES_MODES = frozenset({PlayMode.RANDOM_ALBUM, PlayMode.RANDOM_EPISODE})

# Music Assistant media types a tag can link to.
MEDIA_TYPES = ("artist", "album", "playlist", "audiobook", "podcast", "track", "radio", "folder")

_MODES: dict[str, tuple[PlayMode, ...]] = {
    "artist": (PlayMode.RANDOM_ALBUM, PlayMode.NEXT_ALBUM, PlayMode.SHUFFLE, PlayMode.FROM_START),
    "podcast": (PlayMode.RANDOM_EPISODE, PlayMode.NEXT_EPISODE, PlayMode.RESUME, PlayMode.FROM_START),
    "audiobook": (PlayMode.RESUME, PlayMode.FROM_START),
    "album": (PlayMode.FROM_START, PlayMode.SHUFFLE, PlayMode.RESUME),
    "playlist": (PlayMode.FROM_START, PlayMode.SHUFFLE, PlayMode.RESUME),
    "folder": (PlayMode.FROM_START, PlayMode.SHUFFLE, PlayMode.RESUME),
    "track": (PlayMode.FROM_START,),
    "radio": (PlayMode.FROM_START,),
}


def modes_for(media_type: str) -> tuple[PlayMode, ...]:
    """The modes offered for a media type; the first is the default."""
    return _MODES.get(media_type, (PlayMode.FROM_START,))


def default_mode(media_type: str) -> PlayMode:
    return modes_for(media_type)[0]


@dataclass
class Position:
    """Where a tag stopped: the queue item playing and the seconds into it."""

    item_uri: str | None
    elapsed: int
    at: float


# Episode numbers in Spotify album titles: "035/Im Wilden Westen", "Folge 91: Gefahr ...", "Folge 12 - ...".
_NUMBER = re.compile(r"^\s*(?:folge|episode|avsnitt|teil|del)?\s*0*(\d{1,3})\s*(?:[/:.\-–]|\s)", re.IGNORECASE)
# Albums of a series that are not episodes: unticked by default.
_NOT_EPISODE = re.compile(
    r"advent|soundtrack|\bmini|\bminis\b|best of|das beste|die besten|lieder|songs|karaoke|instrumental|"
    r"titelsong|hörbuch-box|sammelbox|box set|\bbox\b|\bcollection\b",
    re.IGNORECASE,
)


def episode_number(title: str) -> int | None:
    match = _NUMBER.match(title or "")
    return int(match.group(1)) if match else None


@dataclass
class Episode:
    """One album of an artist tag, or one episode of a podcast tag."""

    uri: str
    title: str
    number: int | None = None
    included: bool = True
    image: str | None = None


def strip_shared_prefix(titles: list[str]) -> list[str]:
    """Drop a prefix most titles share, such as the artist in "Die drei ??? Kids - 035/Im Wilden Westen".

    Music Assistant's album list names each album "<artist> - <album>" (seen 2026-11-22).
    """
    heads = [t.split(" - ", 1)[0] for t in titles if " - " in t]
    if not heads:
        return titles
    head = max(set(heads), key=heads.count)
    if heads.count(head) * 5 < len(titles) * 3:  # fewer than 60 % share it
        return titles
    prefix = head + " - "
    return [t[len(prefix):] if t.startswith(prefix) else t for t in titles]


def suggest_episodes(items: list[dict[str, Any]]) -> list[Episode]:
    """Episodes with a suggested selection.

    Advent calendars, soundtracks, minis and similar are left out. When most albums carry an episode number,
    only numbered albums are ticked. `items` are {"uri", "title", "image"} in the provider's order.
    """
    items = [i for i in items if i.get("uri")]
    titles = strip_shared_prefix([i.get("title") or i["uri"] for i in items])
    episodes = [
        Episode(uri=i["uri"], title=title, number=episode_number(title), image=i.get("image"))
        for i, title in zip(items, titles)
    ]
    numbered = sum(1 for e in episodes if e.number is not None)
    mostly_numbered = bool(episodes) and numbered * 2 >= len(episodes)
    for e in episodes:
        e.included = not _NOT_EPISODE.search(e.title) and (e.number is not None or not mostly_numbered)
    return episodes


def merge_episodes(old: list[Episode], fresh: list[Episode]) -> list[Episode]:
    """A refreshed list keeps the parent's choices; new albums get the suggestion."""
    chosen = {e.uri: e.included for e in old}
    for e in fresh:
        if e.uri in chosen:
            e.included = chosen[e.uri]
    return fresh


def number_order(episodes: list[Episode]) -> list[str]:
    """Included episodes in number order; unnumbered ones after, in the provider's order."""
    included = [(i, e) for i, e in enumerate(episodes) if e.included]
    included.sort(key=lambda p: (p[1].number is None, p[1].number or 0, p[0]))
    return [e.uri for _, e in included]


@dataclass
class Tag:
    """One linked tag."""

    uid: str
    name: str
    uri: str
    media_type: str
    mode: PlayMode
    image: str | None = None
    subtitle: str | None = None
    # Series modes: the albums or episodes, the play order through the included ones, the step in it, and the
    # album being listened to (set until it has been heard to the end).
    episodes: list[Episode] = field(default_factory=list)
    episodes_updated: float | None = None
    order: list[str] = field(default_factory=list)
    order_pos: int = 0
    current: str | None = None
    heard: int = 0
    position: Position | None = None
    linked_at: float | None = None

    def included(self) -> list[str]:
        return [e.uri for e in self.episodes if e.included]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["mode"] = self.mode.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Tag:
        media_type = data.get("media_type") or "playlist"
        mode = data.get("mode")
        if mode is None:
            # Store version 1 had only a shuffle flag.
            mode = PlayMode.SHUFFLE if data.get("shuffle") else default_mode(media_type)
        if mode == "random_episode" and media_type == "artist":
            # Store version 2 called the artist mode a random episode.
            mode = PlayMode.RANDOM_ALBUM
        mode = PlayMode(mode)
        if mode not in modes_for(media_type):
            mode = default_mode(media_type)
        position = data.get("position")
        if position is None and (resume := data.get("resume")):
            # Store version 1 kept {"elapsed": seconds} for audiobooks.
            position = {"item_uri": None, "elapsed": int(resume.get("elapsed", 0)), "at": 0.0}
        raw_episodes = data.get("episodes") or []
        if raw_episodes and isinstance(raw_episodes[0], str):
            # Store version 2 kept a plain URI list without titles.
            episodes = [Episode(uri=u, title=u) for u in raw_episodes]
        else:
            episodes = [Episode(**e) for e in raw_episodes]
        return cls(
            uid=data["uid"],
            name=data.get("name") or data["uri"],
            uri=data["uri"],
            media_type=media_type,
            mode=mode,
            image=data.get("image"),
            subtitle=data.get("subtitle"),
            episodes=episodes,
            episodes_updated=data.get("episodes_updated"),
            order=list(data.get("order") or []),
            order_pos=int(data.get("order_pos") or 0),
            current=data.get("current"),
            heard=int(data.get("heard") or 0),
            position=Position(**position) if position else None,
            linked_at=data.get("linked_at"),
        )


@dataclass
class SeenTag:
    """A tag a box read that is not linked yet."""

    uid: str
    last_seen: float
    box: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
