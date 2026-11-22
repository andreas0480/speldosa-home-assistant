"""The API the Speldosa page talks to (Home Assistant websocket commands, prefix speldosa/)."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

import voluptuous as vol

from homeassistant.components import persistent_notification, websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import music
from .const import DOMAIN, EPISODES_MAX_AGE_S, SIGNAL_CHANGED
from .core import SERIES_MODES, Card, Episode, PlayMode, default_mode, merge_episodes, modes_for, suggest_episodes
from .core.models import MEDIA_TYPES

if TYPE_CHECKING:
    from . import SpeldosaData


def _data(hass: HomeAssistant) -> SpeldosaData:
    return hass.data[DOMAIN]


def _controller(hass: HomeAssistant, box_id: str | None):
    controllers = _data(hass).controllers
    if box_id:
        if box_id not in controllers:
            raise HomeAssistantError(f"Unknown box {box_id}")
        return controllers[box_id]
    if not controllers:
        raise HomeAssistantError("No Speldosa box is set up")
    return next(iter(controllers.values()))


def _card_json(data: SpeldosaData, card: Card, token_id: str | None) -> dict[str, Any]:
    return {
        "uid": card.uid,
        "name": card.name,
        "uri": card.uri,
        "media_type": card.media_type,
        "mode": card.mode.value,
        "modes": [m.value for m in modes_for(card.media_type)],
        "image": data.images.page_url(card.image, token_id),
        "subtitle": card.subtitle,
        "episodes": len(card.episodes),
        "included": len(card.included()),
        "heard": card.heard,
        "current": _episode_title(card, card.current),
        "has_position": card.position is not None,
    }


def _episode_title(card: Card, uri: str | None) -> str | None:
    if uri is None:
        return None
    return next((e.title for e in card.episodes if e.uri == uri), None)


def _episodes_json(data: SpeldosaData, episodes: list[Episode], token_id: str | None) -> list[dict[str, Any]]:
    return [
        {"uri": e.uri, "title": e.title, "number": e.number, "included": e.included,
         "image": data.images.page_url(e.image, token_id)}
        for e in episodes
    ]


EPISODES_SCHEMA = [
    vol.Schema(
        {
            vol.Required("uri"): str,
            vol.Required("title"): str,
            vol.Optional("number"): vol.Any(None, int),
            vol.Required("included"): bool,
        },
        extra=vol.REMOVE_EXTRA,
    )
]


def _episodes_from_msg(items: list[dict[str, Any]], old: list[Episode]) -> list[Episode]:
    images = {e.uri: e.image for e in old}
    return [
        Episode(uri=i["uri"], title=i["title"], number=i.get("number"), included=i["included"],
                image=images.get(i["uri"]))
        for i in items
    ]


def _items_with_images(data: SpeldosaData, items: list[dict[str, Any]], token_id: str | None) -> list[dict[str, Any]]:
    out = []
    for item in items:
        item = dict(item)
        item["source_image"] = item.get("image")
        item["image"] = data.images.page_url(item.get("image"), token_id)
        item["modes"] = [m.value for m in modes_for(item["media_type"])]
        item["mode"] = default_mode(item["media_type"]).value
        out.append(item)
    return out


@callback
def async_register(hass: HomeAssistant) -> None:
    for handler in (
        ws_overview,
        ws_search,
        ws_now_playing,
        ws_link,
        ws_update,
        ws_unlink,
        ws_try,
        ws_forget_seen,
        ws_subscribe,
        ws_episodes,
        ws_card_get,
    ):
        websocket_api.async_register_command(hass, handler)


@websocket_api.websocket_command({vol.Required("type"): "speldosa/overview"})
@callback
def ws_overview(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    data = _data(hass)
    token_id = connection.refresh_token_id
    connection.send_result(
        msg["id"],
        {
            "boxes": [c.summary() for c in data.controllers.values()],
            "cards": [_card_json(data, c, token_id) for c in data.store.all()],
            "seen": [s.to_dict() for s in data.store.seen() if data.store.get(s.uid) is None],
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "speldosa/search",
        vol.Required("query"): str,
        vol.Optional("box_id"): str,
        vol.Optional("types"): [vol.In(MEDIA_TYPES)],
    }
)
@websocket_api.async_response
async def ws_search(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    data = _data(hass)
    controller = _controller(hass, msg.get("box_id"))
    try:
        result = await music.async_search(hass, data.search_cache, controller.player, msg["query"], msg.get("types"))
    except HomeAssistantError as err:
        connection.send_error(msg["id"], "search_failed", str(err))
        return
    token_id = connection.refresh_token_id
    result["best"] = _items_with_images(data, result["best"], token_id)
    result["weaker"] = _items_with_images(data, result["weaker"], token_id)
    for group in result["groups"]:
        group["items"] = _items_with_images(data, group["items"], token_id)
    connection.send_result(msg["id"], result)


@websocket_api.websocket_command({vol.Required("type"): "speldosa/now_playing", vol.Optional("box_id"): str})
@websocket_api.async_response
async def ws_now_playing(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    data = _data(hass)
    controller = _controller(hass, msg.get("box_id"))
    now = await music.async_now_playing(hass, controller.player)
    if now is not None:
        token_id = connection.refresh_token_id
        for key in ("track", "album"):
            if now.get(key):
                now[key]["source_image"] = now[key].get("image")
                now[key]["image"] = data.images.page_url(now[key].get("image"), token_id)
                now[key]["modes"] = [m.value for m in modes_for(now[key]["media_type"])]
                now[key]["mode"] = default_mode(now[key]["media_type"]).value
    connection.send_result(msg["id"], {"player_name": controller.player_name(), "now": now})


async def _refresh_episodes(hass: HomeAssistant, uid: str, player: str) -> None:
    data = _data(hass)
    card = data.store.get(uid)
    if card is None or card.mode not in SERIES_MODES:
        return
    items = await music.async_episodes(hass, player, card.uri, card.media_type)
    if items:
        fresh = suggest_episodes(items)
        # A list migrated from store version 2 has no titles and no real choice: take the suggestion instead.
        chosen_by_parent = not _untitled(card.episodes)
        data.store.set_episodes(uid, merge_episodes(card.episodes, fresh) if chosen_by_parent else fresh)


def _untitled(episodes: list[Episode]) -> bool:
    return bool(episodes) and all(e.title == e.uri for e in episodes)


def async_refresh_stale_episodes(hass: HomeAssistant, player: str) -> None:
    """Refresh episode lists older than EPISODES_MAX_AGE_S in the background."""
    for card in _data(hass).store.all():
        if card.mode in SERIES_MODES and (
            not card.episodes
            or _untitled(card.episodes)
            or (time.time() - (card.episodes_updated or 0)) > EPISODES_MAX_AGE_S
        ):
            hass.async_create_background_task(
                _refresh_episodes(hass, card.uid, player), f"speldosa episodes {card.uid}"
            )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "speldosa/card/link",
        vol.Required("uid"): str,
        vol.Required("uri"): str,
        vol.Required("media_type"): vol.In(MEDIA_TYPES),
        vol.Required("name"): str,
        vol.Optional("mode"): vol.In([m.value for m in PlayMode]),
        vol.Optional("image"): vol.Any(None, str),
        vol.Optional("subtitle"): vol.Any(None, str),
        vol.Optional("box_id"): str,
        vol.Optional("episodes"): EPISODES_SCHEMA,
    }
)
@websocket_api.async_response
async def ws_link(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    data = _data(hass)
    media_type = msg["media_type"]
    mode = PlayMode(msg.get("mode") or default_mode(media_type))
    if mode not in modes_for(media_type):
        connection.send_error(msg["id"], "invalid_mode", f"{mode} is not offered for {media_type}")
        return
    old = data.store.get(msg["uid"])
    same_content = old is not None and old.uri == msg["uri"]
    old_episodes = old.episodes if same_content else []
    episodes = _episodes_from_msg(msg["episodes"], old_episodes) if "episodes" in msg else old_episodes
    card = Card(
        uid=msg["uid"],
        name=msg["name"].strip() or msg["uri"],
        uri=msg["uri"],
        media_type=media_type,
        mode=mode,
        image=msg.get("image"),
        subtitle=msg.get("subtitle"),
        episodes=episodes,
        episodes_updated=time.time() if "episodes" in msg else (old.episodes_updated if same_content else None),
        order=old.order if same_content and old.mode == mode else [],
        order_pos=old.order_pos if same_content and old.mode == mode else 0,
        current=old.current if same_content else None,
        heard=old.heard if same_content else 0,
        position=old.position if same_content else None,
        linked_at=time.time(),
    )
    data.store.set(card)
    for controller in data.controllers.values():
        persistent_notification.async_dismiss(hass, f"{DOMAIN}_unknown_{controller.entry_id}")
    controller = _controller(hass, msg.get("box_id"))
    if mode in SERIES_MODES and not card.episodes:
        hass.async_create_background_task(
            _refresh_episodes(hass, card.uid, controller.player), f"speldosa episodes {card.uid}"
        )
    # The card is on a box right now: start it there, as if it had just been put on.
    for box in data.controllers.values():
        if box.current_card() == card.uid:
            hass.async_create_task(box.async_card_placed(card.uid))
    connection.send_result(msg["id"], _card_json(data, card, connection.refresh_token_id))


@websocket_api.websocket_command(
    {
        vol.Required("type"): "speldosa/card/update",
        vol.Required("uid"): str,
        vol.Optional("name"): str,
        vol.Optional("mode"): vol.In([m.value for m in PlayMode]),
        vol.Optional("episodes"): EPISODES_SCHEMA,
    }
)
@websocket_api.async_response
async def ws_update(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    data = _data(hass)
    card = data.store.get(msg["uid"])
    if card is None:
        connection.send_error(msg["id"], "not_found", "No such card")
        return
    if "mode" in msg:
        mode = PlayMode(msg["mode"])
        if mode not in modes_for(card.media_type):
            connection.send_error(msg["id"], "invalid_mode", f"{mode} is not offered for {card.media_type}")
            return
        if mode != card.mode:
            # A new order for the new mode; an album being listened to is kept.
            card.order, card.order_pos = [], 0
        card.mode = mode
    if msg.get("name", "").strip():
        card.name = msg["name"].strip()
    if "episodes" in msg:
        card.episodes = _episodes_from_msg(msg["episodes"], card.episodes)
        card.episodes_updated = time.time()
    data.store.set(card)
    if card.mode in SERIES_MODES and not card.episodes:
        player = _controller(hass, None).player
        hass.async_create_background_task(_refresh_episodes(hass, card.uid, player), f"speldosa episodes {card.uid}")
    connection.send_result(msg["id"], _card_json(data, card, connection.refresh_token_id))


@websocket_api.websocket_command({vol.Required("type"): "speldosa/card/unlink", vol.Required("uid"): str})
@callback
def ws_unlink(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    _data(hass).store.remove(msg["uid"])
    connection.send_result(msg["id"], {})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "speldosa/card/try",
        vol.Required("uri"): str,
        vol.Required("media_type"): vol.In(MEDIA_TYPES),
        vol.Optional("mode"): vol.In([m.value for m in PlayMode]),
        vol.Optional("box_id"): str,
    }
)
@websocket_api.async_response
async def ws_try(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    controller = _controller(hass, msg.get("box_id"))
    media_type = msg["media_type"]
    mode = PlayMode(msg.get("mode") or default_mode(media_type))
    if mode in SERIES_MODES:
        # Trying a series: shuffle it rather than wait for its album list.
        mode = PlayMode.SHUFFLE
    if mode not in modes_for(media_type):
        mode = default_mode(media_type)
    trial = Card(uid="try", name=msg["uri"], uri=msg["uri"], media_type=media_type, mode=mode)
    try:
        await controller.async_try(trial)
    except HomeAssistantError as err:
        connection.send_error(msg["id"], "play_failed", str(err))
        return
    connection.send_result(msg["id"], {"player_name": controller.player_name()})


@websocket_api.websocket_command({vol.Required("type"): "speldosa/seen/forget", vol.Required("uid"): str})
@callback
def ws_forget_seen(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    _data(hass).store.forget_seen(msg["uid"])
    connection.send_result(msg["id"], {})


@websocket_api.websocket_command({vol.Required("type"): "speldosa/subscribe"})
@callback
def ws_subscribe(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """Sends {"changed": true} whenever cards, seen cards or a box's card change; the page then refetches."""

    @callback
    def forward() -> None:
        connection.send_message(websocket_api.event_message(msg["id"], {"changed": True}))

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(hass, SIGNAL_CHANGED, forward)
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): "speldosa/episodes",
        vol.Required("uri"): str,
        vol.Required("media_type"): vol.In(["artist", "podcast"]),
        vol.Optional("uid"): str,
        vol.Optional("box_id"): str,
    }
)
@websocket_api.async_response
async def ws_episodes(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    """The albums of an artist (or episodes of a podcast) with the suggested choice, for the page's list."""
    data = _data(hass)
    controller = _controller(hass, msg.get("box_id"))
    items = await music.async_episodes(hass, controller.player, msg["uri"], msg["media_type"])
    episodes = suggest_episodes(items)
    old = data.store.get(msg["uid"]) if msg.get("uid") else None
    if old is not None and old.uri == msg["uri"]:
        if not _untitled(old.episodes):
            episodes = merge_episodes(old.episodes, episodes)
    connection.send_result(msg["id"], {"episodes": _episodes_json(data, episodes, connection.refresh_token_id)})


@websocket_api.websocket_command({vol.Required("type"): "speldosa/card/get", vol.Required("uid"): str})
@callback
def ws_card_get(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]) -> None:
    data = _data(hass)
    card = data.store.get(msg["uid"])
    if card is None:
        connection.send_error(msg["id"], "not_found", "No such card")
        return
    token_id = connection.refresh_token_id
    result = _card_json(data, card, token_id)
    result["episode_list"] = _episodes_json(data, card.episodes, token_id)
    connection.send_result(msg["id"], result)
