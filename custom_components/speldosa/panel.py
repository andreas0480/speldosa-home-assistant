"""The Speldosa page in the Home Assistant sidebar."""

from __future__ import annotations

import json
from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import PANEL_COMPONENT, PANEL_URL_PATH, STATIC_URL

FRONTEND_DIR = Path(__file__).parent / "frontend"
BUNDLE = "speldosa-panel.js"
ICONS = "speldosa-icons.js"
SIDEBAR_ICON = "speldosa:logo"
_STATIC_KEY = "speldosa_static_registered"
_PANEL_KEY = "speldosa_panel_registered"
_ICONS_KEY = "speldosa_icons_url"


def _version() -> str:
    manifest = json.loads((Path(__file__).parent / "manifest.json").read_text())
    return manifest.get("version", "0")


async def async_register_panel(hass: HomeAssistant) -> None:
    # Several boxes set up at the same time: the first claims the panel before any await, the others return.
    if hass.data.get(_PANEL_KEY) or PANEL_URL_PATH in hass.data.get(frontend.DATA_PANELS, {}):
        return
    hass.data[_PANEL_KEY] = True
    if not hass.data.get(_STATIC_KEY):
        # Static paths cannot be removed again, so register them once per Home Assistant run.
        hass.data[_STATIC_KEY] = True
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(FRONTEND_DIR), cache_headers=False)]
        )
    version = await hass.async_add_executor_job(_version)
    # The Speldosa mark as icon "speldosa:logo", loaded on every page so the sidebar can show it.
    icons_url = f"{STATIC_URL}/{ICONS}?v={version}"
    hass.data[_ICONS_KEY] = icons_url
    frontend.add_extra_js_url(hass, icons_url)
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL_PATH,
        webcomponent_name=PANEL_COMPONENT,
        sidebar_title="Speldosa",
        sidebar_icon=SIDEBAR_ICON,
        module_url=f"{STATIC_URL}/{BUNDLE}?v={version}",
        require_admin=False,
        config={},
    )


def async_remove_panel(hass: HomeAssistant) -> None:
    hass.data.pop(_PANEL_KEY, None)
    if (icons_url := hass.data.pop(_ICONS_KEY, None)) is not None:
        frontend.remove_extra_js_url(hass, icons_url)
    if PANEL_URL_PATH in hass.data.get(frontend.DATA_PANELS, {}):
        frontend.async_remove_panel(hass, PANEL_URL_PATH)
