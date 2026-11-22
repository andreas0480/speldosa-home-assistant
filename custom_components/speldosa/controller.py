"""One box in Home Assistant: feeds card events to the core and carries out its actions."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from homeassistant.components import persistent_notification
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_state_change_event

from . import music
from .const import DOMAIN, EVENT_CARD, EVENT_UNKNOWN_CARD, NO_CARD, STATUS_ERROR
from .core import Action, BoxState, Card, is_finished, on_finished, on_lifted, on_placed
from .core.playback import STATUS_IDLE, STATUS_PAUSED, STATUS_PLAYING, position_from_queue
from .store import CardStore

_LOGGER = logging.getLogger(__name__)

EMPTY_STATES = {NO_CARD, STATE_UNKNOWN, STATE_UNAVAILABLE, "", None}
SEEK_WAIT_S = 8
# Music Assistant goes idle for a moment while it replaces the queue; idle right after a play is not an end.
PLAY_SETTLE_S = 10

Translator = Callable[[str, dict[str, str]], Awaitable[tuple[str, str]]]


class BoxController:
    """Reacts to the box's Card sensor and drives one Music Assistant player."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        entry_id: str,
        name: str,
        area: str | None,
        card_entity: str,
        status_entity: str | None,
        reader_problem_entity: str | None,
        player: str,
        store: CardStore,
        resume_window_s: float,
        translate: Translator,
        start_volume: float | None = None,
        solo: bool = True,
        on_change: Callable[[], None],
    ) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.name = name
        self.area = area
        self.card_entity = card_entity
        self.status_entity = status_entity
        self.reader_problem_entity = reader_problem_entity
        self.player = player
        self.store = store
        self.resume_window_s = resume_window_s
        self.start_volume = start_volume
        self.solo = solo
        # The player's last position while playing, to tell "heard to the end" from "stopped".
        self._last_position: tuple[float, float, float] | None = None  # (position, duration, at)
        self._last_play_at = 0.0
        self._translate = translate
        self._on_change = on_change
        self.state = BoxState()
        self._unsubs: list[Callable[[], None]] = []
        self._lock = asyncio.Lock()

    # Lifecycle -------------------------------------------------------------------

    @callback
    def async_start(self) -> None:
        self._unsubs.append(async_track_state_change_event(self.hass, [self.card_entity], self._card_changed))
        self._unsubs.append(async_track_state_change_event(self.hass, [self.player], self._player_changed))
        # After a restart, remember a card already on the box without starting playback.
        if (uid := self.current_card()) is not None:
            self.state = BoxState(active_uid=uid)

    @callback
    def async_stop(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()

    # Reading the box ---------------------------------------------------------------

    def current_card(self) -> str | None:
        state = self.hass.states.get(self.card_entity)
        if state is None or state.state in EMPTY_STATES:
            return None
        return state.state

    def available(self) -> bool:
        state = self.hass.states.get(self.card_entity)
        return state is not None and state.state != STATE_UNAVAILABLE

    def reader_problem(self) -> bool:
        if self.reader_problem_entity is None:
            return False
        state = self.hass.states.get(self.reader_problem_entity)
        return state is not None and state.state == "on"

    def player_state(self) -> str | None:
        state = self.hass.states.get(self.player)
        return state.state if state else None

    def player_name(self) -> str:
        state = self.hass.states.get(self.player)
        return (state.attributes.get("friendly_name") if state else None) or self.player

    def summary(self) -> dict[str, Any]:
        uid = self.current_card()
        return {
            "entry_id": self.entry_id,
            "name": self.name,
            "area": self.area,
            "player": self.player,
            "player_name": self.player_name(),
            "player_state": self.player_state(),
            "available": self.available(),
            "card": uid,
            "card_linked": uid is not None and self.store.get(uid) is not None,
            "reader_problem": self.reader_problem(),
        }

    # Events --------------------------------------------------------------------------

    async def _card_changed(self, event: Event[EventStateChangedData]) -> None:
        new, old = event.data["new_state"], event.data["old_state"]
        new_uid = None if new is None or new.state in EMPTY_STATES else new.state
        old_uid = None if old is None or old.state in EMPTY_STATES else old.state
        if new_uid == old_uid:
            return
        async with self._lock:
            if new_uid is None:
                await self.async_card_lifted()
            else:
                await self.async_card_placed(new_uid)
        self._on_change()

    async def _player_changed(self, event: Event[EventStateChangedData]) -> None:
        """Mirror the player on the box light, and notice when the card's piece was heard to the end."""
        new, old = event.data["new_state"], event.data["old_state"]
        if new is None:
            return
        if new.state == "playing":
            pos = new.attributes.get("media_position")
            duration = new.attributes.get("media_duration")
            updated = new.attributes.get("media_position_updated_at")
            if pos is not None and duration:
                at = updated.timestamp() if hasattr(updated, "timestamp") else time.time()
                self._last_position = (float(pos), float(duration), at)
        if self.state.active_uid is None:
            return
        status = {"playing": STATUS_PLAYING, "paused": STATUS_PAUSED}.get(new.state)
        if status is None and new.state in ("idle", "off", "standby"):
            status = STATUS_IDLE
            if old is not None and old.state == "playing" and time.time() - self._last_play_at > PLAY_SETTLE_S:
                await self._check_finished()
                return
        if status:
            await self._set_status(status)

    async def _check_finished(self) -> None:
        uid = self.state.active_uid
        card = self.store.get(uid) if uid else None
        estimate = duration = None
        if self._last_position is not None:
            pos, duration, at = self._last_position
            estimate = pos + max(0.0, time.time() - at)
        queue = await music.async_get_queue(self.hass, self.player)
        if card is not None and is_finished(queue, estimate, duration):
            _LOGGER.debug("%s: %s heard to the end", self.name, card.name)
            await self._run(on_finished(card).actions, card)
            self._on_change()
        else:
            await self._set_status(STATUS_IDLE)

    async def async_card_placed(self, uid: str) -> None:
        self.hass.bus.async_fire(EVENT_CARD, {"entry_id": self.entry_id, "uid": uid, "placed": True})
        card = self.store.get(uid)
        decision = on_placed(
            card, uid, self.state, self.player_state(), time.time(), resume_window=self.resume_window_s
        )
        self.state = decision.state
        await self._run(decision.actions, card)

    async def async_card_lifted(self) -> None:
        uid = self.state.active_uid
        self.hass.bus.async_fire(EVENT_CARD, {"entry_id": self.entry_id, "uid": uid, "placed": False})
        decision = on_lifted(self.state, self.player_state(), time.time())
        self.state = decision.state
        await self._run(decision.actions, self.store.get(uid) if uid else None)

    async def async_try(self, card: Card) -> None:
        """Play a card's content on this box's player without linking it (the page's Try button)."""
        decision = on_placed(card, card.uid, BoxState(), self.player_state(), time.time())
        actions = [a for a in decision.actions if a.kind in ("play", "seek")]
        await self._run(actions, card, track_state=False)

    # Carrying out actions -----------------------------------------------------------

    async def _run(self, actions: list[Action], card: Card | None, track_state: bool = True) -> None:
        try:
            for action in actions:
                await self._do(action)
        except HomeAssistantError as err:
            await self._error(card.name if card else "", str(err))

    async def _do(self, action: Action) -> None:
        kind = action.kind
        if kind == "play":
            if action.fresh:
                if self.solo:
                    await music.async_leave_group(self.hass, self.player)
                if self.start_volume:
                    await music.async_set_volume(self.hass, self.player, self.start_volume)
            self._last_play_at = time.time()
            self._last_position = None
            await music.async_play(
                self.hass,
                self.player,
                action.uri,
                action.media_type,
                shuffle=bool(action.shuffle),
                start_item=action.start_item,
            )
        elif kind == "seek":
            self.hass.async_create_task(self._seek_when_playing(action.position or 0))
        elif kind == "resume":
            await self._media("media_play")
        elif kind == "pause":
            await self._media("media_pause")
        elif kind == "save_position":
            queue = await music.async_get_queue(self.hass, self.player)
            if (position := position_from_queue(queue, time.time())) is not None:
                self.store.set_position(action.uid, position)
        elif kind == "status":
            await self._set_status(action.status)
        elif kind == "unknown_card":
            await self._unknown_card(action.uid)
        elif kind == "series_started":
            self.store.series_started(action.uid, action.uri, action.order, action.order_pos)
        elif kind == "heard":
            self.store.heard(action.uid)

    async def _media(self, service: str, data: dict[str, Any] | None = None) -> None:
        await self.hass.services.async_call(
            "media_player", service, data or {}, target={"entity_id": self.player}, blocking=True
        )

    async def _seek_when_playing(self, position: int) -> None:
        deadline = time.monotonic() + SEEK_WAIT_S
        while time.monotonic() < deadline:
            if self.player_state() == "playing":
                try:
                    await self._media("media_seek", {"seek_position": position})
                except HomeAssistantError as err:
                    _LOGGER.debug("Seek failed on %s: %s", self.player, err)
                return
            await asyncio.sleep(0.5)

    async def _unknown_card(self, uid: str) -> None:
        self.store.mark_seen(uid, self.name)
        self.hass.bus.async_fire(EVENT_UNKNOWN_CARD, {"entry_id": self.entry_id, "uid": uid})
        title, message = await self._translate("unknown_card", {"box": self.name, "card": uid})
        persistent_notification.async_create(
            self.hass, message, title=title, notification_id=f"{DOMAIN}_unknown_{self.entry_id}"
        )

    async def _error(self, card_name: str, error: str) -> None:
        _LOGGER.warning("%s could not play %s: %s", self.name, card_name, error)
        await self._set_status(STATUS_ERROR)
        title, message = await self._translate("play_failed", {"box": self.name, "card": card_name, "error": error})
        persistent_notification.async_create(
            self.hass, message, title=title, notification_id=f"{DOMAIN}_error_{self.entry_id}"
        )

    async def _set_status(self, status: str | None) -> None:
        if self.status_entity is None or status is None:
            return
        state = self.hass.states.get(self.status_entity)
        if state is None or state.state in (status, STATE_UNAVAILABLE):
            return
        try:
            await self.hass.services.async_call(
                "select", "select_option", {"option": status}, target={"entity_id": self.status_entity}, blocking=True
            )
        except HomeAssistantError as err:
            _LOGGER.debug("Status not set on %s: %s", self.status_entity, err)
