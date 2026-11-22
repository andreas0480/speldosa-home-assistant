"""Finding a box's entities in Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import CARD_ENTITY_NAME, ESPHOME_DOMAIN, READER_PROBLEM_NAME, STATUS_ENTITY_NAME


@dataclass
class BoxEntities:
    """The box entities the integration reads and writes."""

    card: str
    status: str | None
    reader_problem: str | None = None


def find_box_entities(hass: HomeAssistant, device_id: str) -> BoxEntities | None:
    """Find the Card sensor, Status select and Reader problem sensor by their firmware names."""
    registry = er.async_get(hass)
    card = status = problem = None
    for entry in er.async_entries_for_device(registry, device_id, include_disabled_entities=False):
        if entry.platform != ESPHOME_DOMAIN:
            continue
        name = entry.original_name
        if entry.domain == "sensor" and (name == CARD_ENTITY_NAME or entry.entity_id.endswith("_card")):
            card = entry.entity_id
        elif entry.domain == "select" and (name == STATUS_ENTITY_NAME or entry.entity_id.endswith("_status")):
            status = entry.entity_id
        elif entry.domain == "binary_sensor" and (
            name == READER_PROBLEM_NAME or entry.entity_id.endswith("_reader_problem")
        ):
            problem = entry.entity_id
    if card is None:
        return None
    return BoxEntities(card=card, status=status, reader_problem=problem)
