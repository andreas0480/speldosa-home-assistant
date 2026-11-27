"""Add a box (which Speldosa device, which Music Assistant speaker) and its two settings.

Tags are linked on the Speldosa page in the sidebar, not here.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.selector import (
    BooleanSelector,
    DeviceSelector,
    DeviceSelectorConfig,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    ACCOUNT_AS_LINKED,
    CONF_ACCOUNT,
    CONF_DEVICE_ID,
    CONF_PLAYER,
    CONF_RESUME_WINDOW,
    CONF_SOLO,
    CONF_START_VOLUME,
    DEFAULT_RESUME_WINDOW_MIN,
    DEFAULT_SOLO,
    DEFAULT_START_VOLUME,
    DOMAIN,
    ESPHOME_DOMAIN,
    MA_DOMAIN,
    MANUFACTURER,
)
from .helpers import find_box_entities
from .music import ma_config_entry_id, music_accounts


# The select's first choice; the accounts themselves are named by Music Assistant.
AS_LINKED_LABEL = {"en": "The account each tag was linked with", "sv": "Kontot som varje bricka kopplades med"}


def _player_selector() -> EntitySelector:
    return EntitySelector(EntitySelectorConfig(domain="media_player", integration=MA_DOMAIN))


class SpeldosaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add one box."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if not self.hass.config_entries.async_entries(MA_DOMAIN):
            return self.async_abort(reason="no_music_assistant")
        errors: dict[str, str] = {}
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            player = user_input[CONF_PLAYER]
            if find_box_entities(self.hass, device_id) is None:
                errors[CONF_DEVICE_ID] = "not_a_box"
            elif ma_config_entry_id(self.hass, player) is None:
                errors[CONF_PLAYER] = "not_ma_player"
            else:
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()
                device = dr.async_get(self.hass).async_get(device_id)
                title = (device.name_by_user or device.name) if device else None
                return self.async_create_entry(
                    title=title or "Speldosa", data={CONF_DEVICE_ID: device_id, CONF_PLAYER: player}
                )
        schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): DeviceSelector(
                    DeviceSelectorConfig(integration=ESPHOME_DOMAIN, manufacturer=MANUFACTURER)
                ),
                vol.Required(CONF_PLAYER): _player_selector(),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return SpeldosaOptionsFlow()


class SpeldosaOptionsFlow(OptionsFlow):
    """The box's speaker and how long a lifted tag keeps its place."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        current_player = self.config_entry.options.get(CONF_PLAYER, self.config_entry.data[CONF_PLAYER])
        options_account = self.config_entry.options.get(CONF_ACCOUNT, ACCOUNT_AS_LINKED)
        if user_input is not None:
            if ma_config_entry_id(self.hass, user_input[CONF_PLAYER]) is None:
                errors[CONF_PLAYER] = "not_ma_player"
            else:
                return self.async_create_entry(
                    data={
                        CONF_PLAYER: user_input[CONF_PLAYER],
                        CONF_RESUME_WINDOW: int(user_input[CONF_RESUME_WINDOW]),
                        CONF_START_VOLUME: int(user_input[CONF_START_VOLUME]),
                        CONF_SOLO: bool(user_input[CONF_SOLO]),
                        CONF_ACCOUNT: user_input.get(CONF_ACCOUNT, options_account),
                    }
                )
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(CONF_PLAYER, default=current_player): _player_selector(),
                vol.Required(
                    CONF_RESUME_WINDOW, default=options.get(CONF_RESUME_WINDOW, DEFAULT_RESUME_WINDOW_MIN)
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=0, max=240, step=1, unit_of_measurement="min", mode=NumberSelectorMode.BOX
                    )
                ),
                vol.Required(
                    CONF_START_VOLUME, default=options.get(CONF_START_VOLUME, DEFAULT_START_VOLUME)
                ): NumberSelector(
                    NumberSelectorConfig(min=0, max=100, step=5, unit_of_measurement="%", mode=NumberSelectorMode.SLIDER)
                ),
                vol.Required(CONF_SOLO, default=options.get(CONF_SOLO, DEFAULT_SOLO)): BooleanSelector(),
            }
        )
        # Only when a music service has more than one account in Music Assistant (two Spotify family members)
        accounts = music_accounts(self.hass, current_player)
        if accounts:
            as_linked = AS_LINKED_LABEL.get(self.hass.config.language, AS_LINKED_LABEL["en"])
            choices = [SelectOptionDict(value=ACCOUNT_AS_LINKED, label=as_linked)] + [
                SelectOptionDict(value=a["id"], label=f"{a['domain'].capitalize()}: {a['name']}") for a in accounts
            ]
            if options_account and options_account not in {a["id"] for a in accounts}:
                choices.append(SelectOptionDict(value=options_account, label=options_account))
            schema = schema.extend(
                {
                    vol.Required(CONF_ACCOUNT, default=options_account): SelectSelector(
                        SelectSelectorConfig(options=choices, mode=SelectSelectorMode.DROPDOWN)
                    )
                }
            )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
