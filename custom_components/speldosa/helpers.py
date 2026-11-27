"""Finding a box's entities in Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import ESPHOME_DOMAIN, LEGACY_TAG_ENTITY_NAME, READER_PROBLEM_NAME, STATUS_ENTITY_NAME, TAG_ENTITY_NAME


@dataclass
class BoxEntities:
    """The box entities the integration reads and writes."""

    tag: str
    status: str | None
    reader_problem: str | None = None


def find_box_entities(hass: HomeAssistant, device_id: str) -> BoxEntities | None:
    """Find the Tag sensor ('Card' on firmware before 0.2.0), Status select and Reader problem sensor by their firmware names."""
    registry = er.async_get(hass)
    tag = legacy_tag = status = problem = None
    for entry in er.async_entries_for_device(registry, device_id, include_disabled_entities=False):
        if entry.platform != ESPHOME_DOMAIN:
            continue
        name = entry.original_name
        if entry.domain == "sensor" and (name == TAG_ENTITY_NAME or entry.entity_id.endswith("_tag")):
            tag = entry.entity_id
        elif entry.domain == "sensor" and (name == LEGACY_TAG_ENTITY_NAME or entry.entity_id.endswith("_card")):
            legacy_tag = entry.entity_id
        elif entry.domain == "select" and (name == STATUS_ENTITY_NAME or entry.entity_id.endswith("_status")):
            status = entry.entity_id
        elif entry.domain == "binary_sensor" and (
            name == READER_PROBLEM_NAME or entry.entity_id.endswith("_reader_problem")
        ):
            problem = entry.entity_id
    tag = tag or legacy_tag
    if tag is None:
        return None
    return BoxEntities(tag=tag, status=status, reader_problem=problem)
