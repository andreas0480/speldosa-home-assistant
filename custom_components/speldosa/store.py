"""Tag links and seen tags, shared by every box in the home: a tag plays the same on any box."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .core import Tag, Episode, Position, SeenTag
from .core.playback import apply_heard, apply_series_started

STORAGE_VERSION = 4
# The file keeps its first name (.storage/speldosa.cards); the data inside says "tags" since version 4.
STORAGE_KEY = f"{DOMAIN}.cards"
SEEN_MAX = 50


class _VersionedStore(Store[dict[str, Any]]):
    async def _async_migrate_func(self, old_major_version, old_minor_version, old_data):
        # Version 1: {"cards": {uid: {uid, name, uri, media_type, shuffle, resume}}}.
        # Version 2: modes and plain episode URI lists. Tag.from_dict reads both.
        # Version 3: as 2, still under "cards". Version 4: the same under "tags" (cards renamed to tags, 0.4.0).
        if old_major_version < 4:
            old = old_data.get("cards") or old_data.get("tags") or {}
            tags = {uid: Tag.from_dict(c).to_dict() for uid, c in old.items()}
            return {"tags": tags, "seen": old_data.get("seen") or {}}
        return old_data


class TagStore:
    """Persistent tag links in .storage/speldosa.cards (the file keeps its first name)."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store = _VersionedStore(hass, STORAGE_VERSION, STORAGE_KEY)
        self._tags: dict[str, Tag] = {}
        self._seen: dict[str, SeenTag] = {}
        self._listeners: list[Callable[[], None]] = []

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        self._tags = {uid: Tag.from_dict(c) for uid, c in (data.get("tags") or {}).items()}
        self._seen = {uid: SeenTag(**s) for uid, s in (data.get("seen") or {}).items()}

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener)

    def _changed(self) -> None:
        self._store.async_delay_save(self._data, 1)
        for listener in list(self._listeners):
            listener()

    def _data(self) -> dict[str, Any]:
        return {
            "tags": {uid: c.to_dict() for uid, c in self._tags.items()},
            "seen": {uid: s.to_dict() for uid, s in self._seen.items()},
        }

    def get(self, uid: str) -> Tag | None:
        return self._tags.get(uid)

    def all(self) -> list[Tag]:
        return sorted(self._tags.values(), key=lambda c: c.name.casefold())

    def set(self, tag: Tag) -> None:
        self._tags[tag.uid] = tag
        self._seen.pop(tag.uid, None)
        self._changed()

    def remove(self, uid: str) -> None:
        if self._tags.pop(uid, None) is not None:
            self._changed()

    def set_position(self, uid: str, position: Position | None) -> None:
        if (tag := self._tags.get(uid)) is not None:
            tag.position = position
            self._store.async_delay_save(self._data, 1)

    def series_started(self, uid: str, uri: str, order: tuple[str, ...], order_pos: int) -> None:
        if (tag := self._tags.get(uid)) is not None:
            apply_series_started(tag, uri, order, order_pos)
            self._store.async_delay_save(self._data, 1)

    def heard(self, uid: str) -> None:
        if (tag := self._tags.get(uid)) is not None:
            apply_heard(tag)
            self._changed()

    def set_episodes(self, uid: str, episodes: list[Episode]) -> None:
        if (tag := self._tags.get(uid)) is not None:
            tag.episodes = episodes
            tag.episodes_updated = time.time()
            self._changed()

    def mark_seen(self, uid: str, box: str | None) -> None:
        self._seen[uid] = SeenTag(uid=uid, last_seen=time.time(), box=box)
        if len(self._seen) > SEEN_MAX:
            oldest = sorted(self._seen.values(), key=lambda s: s.last_seen)[: len(self._seen) - SEEN_MAX]
            for s in oldest:
                self._seen.pop(s.uid, None)
        self._changed()

    def forget_seen(self, uid: str) -> None:
        if self._seen.pop(uid, None) is not None:
            self._changed()

    def seen(self) -> list[SeenTag]:
        return sorted(self._seen.values(), key=lambda s: -s.last_seen)
