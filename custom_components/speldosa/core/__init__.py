"""Speldosa core: what a tag does, independent of Home Assistant.

Nothing in this package imports Home Assistant (a test checks it). The Home Assistant integration feeds it events
and carries out the actions it returns; a standalone Speldosa hub can do the same with other connectors.
"""

from .accounts import provider_domain, with_account
from .models import (
    SERIES_MODES,
    Tag,
    Episode,
    PlayMode,
    Position,
    SeenTag,
    default_mode,
    merge_episodes,
    modes_for,
    suggest_episodes,
)
from .playback import Action, BoxState, is_finished, on_finished, on_lifted, on_placed
from .search import rank_results

__all__ = [
    "SERIES_MODES",
    "Action",
    "BoxState",
    "Tag",
    "Episode",
    "PlayMode",
    "Position",
    "SeenTag",
    "default_mode",
    "is_finished",
    "merge_episodes",
    "modes_for",
    "on_finished",
    "on_lifted",
    "on_placed",
    "rank_results",
    "provider_domain",
    "suggest_episodes",
    "with_account",
]
