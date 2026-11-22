"""Speldosa: put a card on the box and its music plays through Music Assistant."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import area_registry as ar, device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.translation import async_get_translations

from .const import (
    CONF_DEVICE_ID,
    CONF_PLAYER,
    CONF_RESUME_WINDOW,
    CONF_SOLO,
    CONF_START_VOLUME,
    DEFAULT_RESUME_WINDOW_MIN,
    DEFAULT_SOLO,
    DEFAULT_START_VOLUME,
    DOMAIN,
    SIGNAL_CHANGED,
)
from .controller import BoxController
from .helpers import find_box_entities
from .image import ImageProxy, ImageView
from .music import SearchCache
from .panel import async_register_panel, async_remove_panel
from .store import CardStore
from .websocket import async_refresh_stale_episodes, async_register


@dataclass
class SpeldosaData:
    """Shared by every box: the card links, the search cache, the image proxy and the boxes."""

    store: CardStore
    images: ImageProxy
    search_cache: SearchCache = field(default_factory=SearchCache)
    controllers: dict[str, BoxController] = field(default_factory=dict)


async def async_get_data(hass: HomeAssistant) -> SpeldosaData:
    # Boxes are set up concurrently at startup: one lock, so they all share one store (found 2026-11-20).
    lock: asyncio.Lock = hass.data.setdefault(f"{DOMAIN}_lock", asyncio.Lock())
    async with lock:
        return await _async_create_data(hass)


async def _async_create_data(hass: HomeAssistant) -> SpeldosaData:
    data: SpeldosaData | None = hass.data.get(DOMAIN)
    if data is None:
        store = CardStore(hass)
        await store.async_load()
        images = ImageProxy(hass)
        hass.http.register_view(ImageView(images))
        data = SpeldosaData(store=store, images=images)
        hass.data[DOMAIN] = data
        async_register(hass)

        @callback
        def changed() -> None:
            async_dispatcher_send(hass, SIGNAL_CHANGED)

        store.async_add_listener(changed)
    return data


def _translator(hass: HomeAssistant):
    async def translate(key: str, placeholders: dict[str, str]) -> tuple[str, str]:
        strings = await async_get_translations(hass, hass.config.language, "exceptions", {DOMAIN})
        title = strings.get(f"component.{DOMAIN}.exceptions.{key}_title.message", "Speldosa")
        message = strings.get(f"component.{DOMAIN}.exceptions.{key}.message", key)
        try:
            message = message.format(**placeholders)
        except (KeyError, IndexError, ValueError):
            pass
        return title, message

    return translate


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = await async_get_data(hass)
    device_id = entry.data[CONF_DEVICE_ID]
    entities = find_box_entities(hass, device_id)
    if entities is None:
        raise ConfigEntryNotReady("The box's Card sensor is not in Home Assistant yet")
    device = dr.async_get(hass).async_get(device_id)
    name = (device.name_by_user or device.name) if device else entry.title
    area = None
    if device and device.area_id and (area_entry := ar.async_get(hass).async_get_area(device.area_id)):
        area = area_entry.name
    player = entry.options.get(CONF_PLAYER, entry.data[CONF_PLAYER])
    window_min = entry.options.get(CONF_RESUME_WINDOW, DEFAULT_RESUME_WINDOW_MIN)
    volume_pct = entry.options.get(CONF_START_VOLUME, DEFAULT_START_VOLUME)
    controller = BoxController(
        hass,
        entry_id=entry.entry_id,
        name=name or entry.title,
        area=area,
        card_entity=entities.card,
        status_entity=entities.status,
        reader_problem_entity=entities.reader_problem,
        player=player,
        store=data.store,
        resume_window_s=float(window_min) * 60,
        start_volume=float(volume_pct) / 100 if volume_pct else None,
        solo=bool(entry.options.get(CONF_SOLO, DEFAULT_SOLO)),
        translate=_translator(hass),
        on_change=lambda: async_dispatcher_send(hass, SIGNAL_CHANGED),
    )
    controller.async_start()
    data.controllers[entry.entry_id] = controller
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    await async_register_panel(hass)
    async_refresh_stale_episodes(hass, player)
    async_dispatcher_send(hass, SIGNAL_CHANGED)
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data: SpeldosaData | None = hass.data.get(DOMAIN)
    if data is not None and (controller := data.controllers.pop(entry.entry_id, None)):
        controller.async_stop()
        if not data.controllers:
            async_remove_panel(hass)
        async_dispatcher_send(hass, SIGNAL_CHANGED)
    return True
