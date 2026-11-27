"""Music Assistant through Home Assistant: search, play, queue, episode lists, now playing.

Everything Speldosa asks of Music Assistant goes through this module, so a standalone hub can replace it with
Music Assistant's own API.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from homeassistant.components.media_player.const import DATA_COMPONENT as MEDIA_PLAYER_COMPONENT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .const import (
    BROWSE_TIMEOUT_S,
    EPISODES_MAX,
    MA_DOMAIN,
    SEARCH_CACHE_S,
    SEARCH_LIMIT,
    SEARCH_MIN_CHARS,
)
from .core import rank_results

_LOGGER = logging.getLogger(__name__)


def ma_config_entry_id(hass: HomeAssistant, player: str) -> str | None:
    """The Music Assistant config entry that owns a player."""
    entry = er.async_get(hass).async_get(player)
    if entry is None or entry.platform != MA_DOMAIN:
        return None
    return entry.config_entry_id


def music_accounts(hass: HomeAssistant, player: str) -> list[dict[str, str]]:
    """Music services with more than one account in the player's Music Assistant: [{"id", "domain", "name"}].

    Read from the Music Assistant client the integration keeps (entry.runtime_data.mass). Empty when that is not
    reachable, or when no service has a second account.
    """
    entry_id = ma_config_entry_id(hass, player)
    entry = hass.config_entries.async_get_entry(entry_id) if entry_id else None
    mass = getattr(getattr(entry, "runtime_data", None), "mass", None)
    try:
        providers = list(getattr(mass, "providers", None) or [])
    except Exception:  # noqa: BLE001 - a client we do not own; no accounts is a safe answer
        return []
    music = [p for p in providers if str(getattr(p, "type", "music")).lower().endswith("music")]
    counts: dict[str, int] = {}
    for p in music:
        counts[p.domain] = counts.get(p.domain, 0) + 1
    return [
        {"id": p.instance_id, "domain": p.domain, "name": p.name or p.instance_id}
        for p in sorted(music, key=lambda p: (p.domain, p.name or ""))
        if counts[p.domain] > 1
    ]


class SearchCache:
    """Search answers per query for SEARCH_CACHE_S; empty answers (Spotify busy) are not kept."""

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], tuple[float, dict[str, Any]]] = {}

    def get(self, entry_id: str, query: str) -> dict[str, Any] | None:
        hit = self._entries.get((entry_id, query.casefold()))
        if hit is None or time.monotonic() - hit[0] > SEARCH_CACHE_S:
            return None
        return hit[1]

    def put(self, entry_id: str, query: str, response: dict[str, Any]) -> None:
        if any(response.get(k) for k in response):
            self._entries[(entry_id, query.casefold())] = (time.monotonic(), response)
            if len(self._entries) > 200:
                oldest = min(self._entries, key=lambda k: self._entries[k][0])
                self._entries.pop(oldest, None)


async def async_search(
    hass: HomeAssistant, cache: SearchCache, player: str, query: str, types: list[str] | None = None
) -> dict[str, Any]:
    """Search Music Assistant (all types, library and providers) and rank the answer."""
    query = query.strip()
    if len(query) < SEARCH_MIN_CHARS:
        return {"best": [], "groups": [], "weaker": [], "empty": True, "too_short": True}
    entry_id = ma_config_entry_id(hass, player)
    if entry_id is None:
        raise HomeAssistantError(f"{player} is not a Music Assistant player")
    response = cache.get(entry_id, query)
    if response is None:
        response = await hass.services.async_call(
            MA_DOMAIN,
            "search",
            {"config_entry_id": entry_id, "name": query, "limit": SEARCH_LIMIT},
            blocking=True,
            return_response=True,
        ) or {}
        cache.put(entry_id, query, response)
    return rank_results(query, response, types)


async def async_play(
    hass: HomeAssistant,
    player: str,
    uri: str,
    media_type: str | None,
    *,
    shuffle: bool = False,
    start_item: str | None = None,
) -> None:
    """Replace the player's queue with uri, in order or shuffled, optionally from start_item; repeat off."""
    for service, data in (("shuffle_set", {"shuffle": shuffle}), ("repeat_set", {"repeat": "off"})):
        try:
            await hass.services.async_call("media_player", service, data, target={"entity_id": player}, blocking=True)
        except (HomeAssistantError, ValueError) as err:
            _LOGGER.debug("%s not set on %s: %s", service, player, err)
    data: dict[str, Any] = {"media_id": uri, "enqueue": "replace"}
    if media_type:
        data["media_type"] = media_type
    if start_item:
        data["start_item"] = start_item
    await hass.services.async_call(MA_DOMAIN, "play_media", data, target={"entity_id": player}, blocking=True)


async def async_get_queue(hass: HomeAssistant, player: str) -> dict[str, Any] | None:
    try:
        response = await hass.services.async_call(
            MA_DOMAIN, "get_queue", {}, target={"entity_id": player}, blocking=True, return_response=True
        )
    except HomeAssistantError as err:
        _LOGGER.debug("No queue for %s: %s", player, err)
        return None
    return (response or {}).get(player)


def _image(item: dict[str, Any] | None) -> str | None:
    return (item or {}).get("image")


async def async_now_playing(hass: HomeAssistant, player: str) -> dict[str, Any] | None:
    """The track playing on a player and its album, from the Music Assistant queue."""
    queue = await async_get_queue(hass, player)
    current = (queue or {}).get("current_item") or {}
    media = current.get("media_item") or {}
    if not media.get("uri"):
        return None
    artists = [a.get("name") for a in media.get("artists") or [] if a.get("name")]
    album = media.get("album") or {}
    return {
        "track": {
            "uri": media["uri"],
            "name": media.get("name") or current.get("name"),
            "media_type": media.get("media_type") or "track",
            "image": _image(media) or _image(album),
            "subtitle": ", ".join(artists[:2]) or None,
        },
        "album": {
            "uri": album["uri"],
            "name": album.get("name"),
            "media_type": "album",
            "image": _image(album) or _image(media),
            "subtitle": ", ".join(artists[:2]) or None,
        }
        if album.get("uri")
        else None,
    }


async def async_episodes(hass: HomeAssistant, player: str, uri: str, media_type: str) -> list[dict[str, Any]]:
    """The albums of an artist or the episodes of a podcast, by browsing the player: {"uri", "title", "image"}."""
    component = hass.data.get(MEDIA_PLAYER_COMPONENT)
    entity = component.get_entity(player) if component else None
    if entity is None:
        return []
    try:
        async with asyncio.timeout(BROWSE_TIMEOUT_S):
            result = await entity.async_browse_media(media_type, uri)
    except (HomeAssistantError, TimeoutError, NotImplementedError, ValueError) as err:
        _LOGGER.warning("No episode list for %s: %s", uri, err)
        return []
    items = [
        {"uri": child.media_content_id, "title": child.title, "image": child.thumbnail}
        for child in result.children or []
        if child.media_content_id and child.media_content_id != uri and child.can_play
    ]
    return items[:EPISODES_MAX]


async def async_set_volume(hass: HomeAssistant, player: str, level: float) -> None:
    try:
        await hass.services.async_call(
            "media_player", "volume_set", {"volume_level": level}, target={"entity_id": player}, blocking=True
        )
    except HomeAssistantError as err:
        _LOGGER.debug("Volume not set on %s: %s", player, err)


async def async_leave_group(hass: HomeAssistant, player: str) -> None:
    """Take the player out of a speaker group, so a story plays only in its own room."""
    state = hass.states.get(player)
    members = (state.attributes.get("group_members") if state else None) or []
    if len(members) <= 1:
        return
    try:
        await hass.services.async_call("media_player", "unjoin", {}, target={"entity_id": player}, blocking=True)
    except HomeAssistantError as err:
        _LOGGER.debug("Could not unjoin %s: %s", player, err)
