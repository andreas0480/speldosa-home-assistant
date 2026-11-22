"""Fixtures: a fake Speldosa box (ESPHome entities) and a fake Music Assistant player and services."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import device_registry as dr, entity_registry as er

from pytest_homeassistant_custom_component.common import MockConfigEntry

PLAYER = "media_player.kids_room"
CARD = "sensor.speldosa_card"
STATUS = "select.speldosa_status"
PROBLEM = "binary_sensor.speldosa_reader_problem"

SEARCH_RESPONSE = json.loads(
    (Path(__file__).resolve().parent.parent / "core_tests" / "fixtures" / "search_die_drei.json").read_text()
)
SEARCH_RESPONSE.pop("_source")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


class FakeServices:
    """Records calls to the services the integration uses and moves the fake player along."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.calls: list[tuple[str, str, dict[str, Any]]] = []
        self.queue: dict[str, Any] = {"elapsed_time": 0, "current_item": None}
        self.search_response: dict[str, Any] = SEARCH_RESPONSE
        self.fail_play = False

        async def record(call: ServiceCall) -> None:
            self.calls.append((call.domain, call.service, dict(call.data)))
            entity_ids = call.data.get("entity_id")
            if isinstance(entity_ids, str):
                entity_ids = [entity_ids]
            if call.domain == "media_player" and call.service == "media_pause":
                self.set_player("paused")
            if call.domain == "media_player" and call.service == "media_play":
                self.set_player("playing")
            if call.domain == "music_assistant" and call.service == "play_media":
                if self.fail_play:
                    from homeassistant.exceptions import HomeAssistantError

                    raise HomeAssistantError("Spotify has reached its limit of 1 concurrent source streams")
                self.set_player("playing", content=str(call.data["media_id"]))
            if call.domain == "select" and call.service == "select_option":
                for entity_id in entity_ids or [STATUS]:
                    hass.states.async_set(entity_id, call.data["option"])

        async def search(call: ServiceCall) -> dict[str, Any]:
            self.calls.append((call.domain, call.service, dict(call.data)))
            return self.search_response

        async def get_queue(call: ServiceCall) -> dict[str, Any]:
            self.calls.append((call.domain, call.service, dict(call.data)))
            return {PLAYER: self.queue}

        for service in ("media_play", "media_pause", "shuffle_set", "media_seek", "volume_set", "repeat_set", "unjoin"):
            hass.services.async_register("media_player", service, record)
        hass.services.async_register("music_assistant", "play_media", record)
        hass.services.async_register("select", "select_option", record)
        hass.services.async_register("music_assistant", "search", search, supports_response=SupportsResponse.ONLY)
        hass.services.async_register(
            "music_assistant", "get_queue", get_queue, supports_response=SupportsResponse.ONLY
        )

    def set_player(self, state: str, content: str | None = None) -> None:
        old = self.hass.states.get(PLAYER)
        attrs = dict(old.attributes) if old else {}
        if content is not None:
            attrs["media_content_id"] = content
        self.hass.states.async_set(PLAYER, state, attrs)

    def named(self, domain: str, service: str) -> list[dict[str, Any]]:
        return [data for d, s, data in self.calls if d == domain and s == service]


@pytest.fixture
def box(hass: HomeAssistant) -> str:
    """A Speldosa box as ESPHome registers it. Returns the device id."""
    esphome_entry = MockConfigEntry(domain="esphome", data={})
    esphome_entry.add_to_hass(hass)
    device = dr.async_get(hass).async_get_or_create(
        config_entry_id=esphome_entry.entry_id,
        identifiers={("esphome", "aa:bb:cc:dd:ee:ff")},
        manufacturer="anjobe",
        model="speldosa",
        name="Speldosa kids room",
    )
    registry = er.async_get(hass)
    for domain, unique, name, object_id in (
        ("sensor", "card", "Card", "speldosa_card"),
        ("select", "status", "Status", "speldosa_status"),
        ("binary_sensor", "reader_problem", "Reader problem", "speldosa_reader_problem"),
    ):
        registry.async_get_or_create(
            domain, "esphome", f"aabbccddeeff-{unique}", device_id=device.id, config_entry=esphome_entry,
            original_name=name, suggested_object_id=object_id,
        )
    hass.states.async_set(CARD, "none")
    hass.states.async_set(STATUS, "idle")
    hass.states.async_set(PROBLEM, "off")
    return device.id


@pytest.fixture
def player(hass: HomeAssistant) -> str:
    ma_entry = MockConfigEntry(domain="music_assistant", data={})
    ma_entry.add_to_hass(hass)
    er.async_get(hass).async_get_or_create(
        "media_player", "music_assistant", "kids_room", config_entry=ma_entry, suggested_object_id="kids_room"
    )
    hass.states.async_set(PLAYER, "idle", {"friendly_name": "Kids room"})
    return PLAYER


@pytest.fixture
def services(hass: HomeAssistant) -> FakeServices:
    return FakeServices(hass)
