"""What happens when a card is put on a box, lifted, or heard to the end: pure decisions, carried out by a connector.

The connector (the Home Assistant controller, later a standalone hub) passes in the card, the box's state, the
player's state and the time, and carries out the returned actions in order.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .models import RANDOM_SERIES_MODES, SERIES_MODES, Card, PlayMode, Position, number_order

# A card lifted and put back within this many seconds continues where it was, whatever its mode.
DEFAULT_RESUME_WINDOW_S = 15 * 60

STATUS_IDLE = "idle"
STATUS_PLAYING = "playing"
STATUS_PAUSED = "paused"
STATUS_UNKNOWN_CARD = "unknown_card"

# Heard to the end: the player stopped at the last queue item within this many seconds of its end.
END_TOLERANCE_S = 20


@dataclass(frozen=True)
class Action:
    """One thing for the connector to do.

    kind: "play" (uri, media_type, start_item, shuffle, fresh), "resume", "pause", "seek" (position),
    "save_position" (uid), "status" (status), "unknown_card" (uid), "series_started" (uid, uri, order, order_pos),
    "heard" (uid).
    `fresh` is true when a new piece starts (the connector then applies the box's start volume).
    """

    kind: str
    uri: str | None = None
    media_type: str | None = None
    start_item: str | None = None
    shuffle: bool | None = None
    fresh: bool = False
    position: int | None = None
    status: str | None = None
    uid: str | None = None
    order: tuple[str, ...] | None = None
    order_pos: int | None = None


@dataclass(frozen=True)
class BoxState:
    """What a box remembers between events."""

    active_uid: str | None = None
    paused_uid: str | None = None
    lifted_at: float | None = None


@dataclass
class Decision:
    actions: list[Action] = field(default_factory=list)
    state: BoxState = field(default_factory=BoxState)


def _within_window(state: BoxState, uid: str, now: float, window: float) -> bool:
    return state.paused_uid == uid and state.lifted_at is not None and now - state.lifted_at <= window


def _play(uri: str, media_type: str | None, *, position: Position | None = None, shuffle: bool = False,
          fresh: bool = True) -> list[Action]:
    """Play uri, from a saved position when there is one."""
    if position is None:
        return [Action("play", uri=uri, media_type=media_type, shuffle=shuffle, fresh=fresh)]
    actions = [Action("play", uri=uri, media_type=media_type, start_item=position.item_uri, shuffle=False)]
    if position.elapsed > 0:
        actions.append(Action("seek", position=position.elapsed))
    return actions


def _episode_type(card: Card) -> str | None:
    return "album" if card.media_type == "artist" else None


def build_order(card: Card, rng: random.Random) -> list[str]:
    """The play order through the included albums or episodes: shuffled, or in number order."""
    if card.mode in RANDOM_SERIES_MODES:
        order = card.included()
        rng.shuffle(order)
        return order
    return number_order(card.episodes)


def _next_in_series(card: Card, rng: random.Random) -> tuple[str | None, tuple[str, ...], int]:
    """The next album or episode, and the order and step it comes from."""
    included = set(card.included())
    order = [u for u in card.order if u in included]
    pos = card.order_pos
    if not order or len(order) != len(included):
        order, pos = build_order(card, rng), 0
    if not order:
        return None, (), 0
    if pos >= len(order):
        # The whole series has been heard: a new round, reshuffled for random modes.
        order = build_order(card, rng) if card.mode in RANDOM_SERIES_MODES else order
        pos = 0
    return order[pos], tuple(order), pos


def on_placed(
    card: Card | None,
    uid: str,
    state: BoxState,
    player_state: str | None,
    now: float,
    *,
    resume_window: float = DEFAULT_RESUME_WINDOW_S,
    rng: random.Random | None = None,
) -> Decision:
    """A card was put on the box."""
    rng = rng or random.Random()
    if card is None:
        return Decision(
            [Action("status", status=STATUS_UNKNOWN_CARD), Action("unknown_card", uid=uid)],
            BoxState(),
        )
    new_state = BoxState(active_uid=uid)
    playing = [Action("status", status=STATUS_PLAYING)]
    if _within_window(state, uid, now, resume_window):
        if player_state == "paused":
            return Decision([Action("resume")] + playing, new_state)
        if card.position is not None and card.mode not in SERIES_MODES:
            return Decision(_play(card.uri, card.media_type, position=card.position) + playing, new_state)

    if card.mode in SERIES_MODES:
        if card.current is not None:
            # An album not yet heard to the end continues from where it stopped, however long ago.
            return Decision(_play(card.current, _episode_type(card), position=card.position) + playing, new_state)
        episode, order, pos = _next_in_series(card, rng)
        if episode is None:
            # No albums chosen or fetched yet: shuffling the whole series is the nearest thing.
            return Decision(_play(card.uri, card.media_type, shuffle=True) + playing, new_state)
        actions = [Action("series_started", uid=uid, uri=episode, order=order, order_pos=pos)]
        return Decision(actions + _play(episode, _episode_type(card)) + playing, new_state)

    if card.mode is PlayMode.SHUFFLE:
        actions = _play(card.uri, card.media_type, shuffle=True)
    elif card.mode is PlayMode.RESUME:
        actions = _play(card.uri, card.media_type, position=card.position)
    else:
        actions = _play(card.uri, card.media_type)
    return Decision(actions + playing, new_state)


def on_lifted(state: BoxState, player_state: str | None, now: float) -> Decision:
    """The card was lifted off the box."""
    uid = state.active_uid
    if uid is None or player_state not in ("playing", "paused"):
        return Decision([Action("status", status=STATUS_IDLE)], BoxState())
    actions = [Action("save_position", uid=uid)]
    if player_state == "playing":
        actions.append(Action("pause"))
    return Decision(
        actions + [Action("status", status=STATUS_PAUSED)],
        BoxState(active_uid=None, paused_uid=uid, lifted_at=now),
    )


def is_finished(queue: dict | None, last_position: float | None, last_duration: float | None) -> bool:
    """Whether the player stopped because the queue was heard to the end.

    queue is music_assistant.get_queue's entry after the player went idle; last_position and last_duration are
    the player's position and the item's length just before (estimated to the moment it stopped).
    """
    if not queue:
        return False
    items = int(queue.get("items") or 0)
    index = queue.get("current_index")
    if items and index is not None and index < items - 1:
        return False
    if last_position is None or not last_duration:
        return False
    return last_duration - last_position <= END_TOLERANCE_S


def on_finished(card: Card | None) -> Decision:
    """The card's album, episode or audiobook was heard to the end while it lay on the box."""
    if card is None:
        return Decision([Action("status", status=STATUS_IDLE)])
    return Decision([Action("heard", uid=card.uid), Action("status", status=STATUS_IDLE)])


def apply_heard(card: Card) -> None:
    """Move a card on after its piece was heard to the end."""
    if card.mode in SERIES_MODES:
        card.current = None
        card.order_pos += 1
        card.heard += 1
    card.position = None


def apply_series_started(card: Card, uri: str, order: tuple[str, ...], order_pos: int) -> None:
    card.order = list(order)
    card.order_pos = order_pos
    card.current = uri
    card.position = None


def position_from_queue(queue: dict | None, now: float) -> Position | None:
    """Turn a music_assistant.get_queue entry into a Position."""
    if not queue:
        return None
    elapsed = int(queue.get("elapsed_time") or 0)
    item = queue.get("current_item") or {}
    media_item = item.get("media_item") or {}
    item_uri = media_item.get("uri")
    if not item_uri and not elapsed:
        return None
    return Position(item_uri=item_uri, elapsed=elapsed, at=now)
