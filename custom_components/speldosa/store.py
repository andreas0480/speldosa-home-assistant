"""Card links and seen cards, shared by every box in the home: a card plays the same on any box."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .core import Card, Episode, Position, SeenCard
from .core.playback import apply_heard, apply_series_started

STORAGE_VERSION = 3
STORAGE_KEY = f"{DOMAIN}.cards"
SEEN_MAX = 50


class _VersionedStore(Store[dict[str, Any]]):
    async def _async_migrate_func(self, old_major_version, old_minor_version, old_data):
        # Version 1: {"cards": {uid: {uid, name, uri, media_type, shuffle, resume}}}.
        # Version 2: modes and plain episode URI lists. Card.from_dict reads both.
        if old_major_version < 3:
            cards = {uid: Card.from_dict(c).to_dict() for uid, c in (old_data.get("cards") or {}).items()}
            return {"cards": cards, "seen": old_data.get("seen") or {}}
        return old_data


class CardStore:
    """Persistent card links in .storage/speldosa.cards."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store = _VersionedStore(hass, STORAGE_VERSION, STORAGE_KEY)
        self._cards: dict[str, Card] = {}
        self._seen: dict[str, SeenCard] = {}
        self._listeners: list[Callable[[], None]] = []

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        self._cards = {uid: Card.from_dict(c) for uid, c in (data.get("cards") or {}).items()}
        self._seen = {uid: SeenCard(**s) for uid, s in (data.get("seen") or {}).items()}

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
            "cards": {uid: c.to_dict() for uid, c in self._cards.items()},
            "seen": {uid: s.to_dict() for uid, s in self._seen.items()},
        }

    def get(self, uid: str) -> Card | None:
        return self._cards.get(uid)

    def all(self) -> list[Card]:
        return sorted(self._cards.values(), key=lambda c: c.name.casefold())

    def set(self, card: Card) -> None:
        self._cards[card.uid] = card
        self._seen.pop(card.uid, None)
        self._changed()

    def remove(self, uid: str) -> None:
        if self._cards.pop(uid, None) is not None:
            self._changed()

    def set_position(self, uid: str, position: Position | None) -> None:
        if (card := self._cards.get(uid)) is not None:
            card.position = position
            self._store.async_delay_save(self._data, 1)

    def series_started(self, uid: str, uri: str, order: tuple[str, ...], order_pos: int) -> None:
        if (card := self._cards.get(uid)) is not None:
            apply_series_started(card, uri, order, order_pos)
            self._store.async_delay_save(self._data, 1)

    def heard(self, uid: str) -> None:
        if (card := self._cards.get(uid)) is not None:
            apply_heard(card)
            self._changed()

    def set_episodes(self, uid: str, episodes: list[Episode]) -> None:
        if (card := self._cards.get(uid)) is not None:
            card.episodes = episodes
            card.episodes_updated = time.time()
            self._changed()

    def mark_seen(self, uid: str, box: str | None) -> None:
        self._seen[uid] = SeenCard(uid=uid, last_seen=time.time(), box=box)
        if len(self._seen) > SEEN_MAX:
            oldest = sorted(self._seen.values(), key=lambda s: s.last_seen)[: len(self._seen) - SEEN_MAX]
            for s in oldest:
                self._seen.pop(s.uid, None)
        self._changed()

    def forget_seen(self, uid: str) -> None:
        if self._seen.pop(uid, None) is not None:
            self._changed()

    def seen(self) -> list[SeenCard]:
        return sorted(self._seen.values(), key=lambda s: -s.last_seen)
