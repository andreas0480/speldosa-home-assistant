"""Tests for the Home Assistant-free core: models, playback decisions, series, search ranking."""

from __future__ import annotations

import json
import random
from pathlib import Path

import pytest

from custom_components.speldosa.core import (
    BoxState,
    Card,
    Episode,
    PlayMode,
    Position,
    default_mode,
    is_finished,
    merge_episodes,
    modes_for,
    on_finished,
    on_lifted,
    on_placed,
    rank_results,
    suggest_episodes,
)
from custom_components.speldosa.core.models import episode_number, number_order
from custom_components.speldosa.core.playback import apply_heard, apply_series_started, position_from_queue
from custom_components.speldosa.core.search import score

CORE = Path(__file__).resolve().parent.parent / "custom_components" / "speldosa" / "core"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def kinds(decision):
    return [a.kind for a in decision.actions]


def card(**kw):
    base = dict(uid="U1", name="Card", uri="spotify://playlist/p", media_type="playlist", mode=PlayMode.FROM_START)
    base.update(kw)
    return Card(**base)


def series(mode=PlayMode.RANDOM_ALBUM, n=4, **kw):
    episodes = [Episode(uri=f"spotify://album/e{i}", title=f"{i:03d}/Folge {i}", number=i) for i in range(1, n + 1)]
    return card(uri="spotify://artist/d", media_type="artist", mode=mode, episodes=episodes, **kw)


def run(c, decision):
    """Apply the store-side actions of a decision to the card, as the controller does."""
    for a in decision.actions:
        if a.kind == "series_started":
            apply_series_started(c, a.uri, a.order, a.order_pos)
    return decision


# Models ------------------------------------------------------------------------


def test_core_has_no_home_assistant_imports():
    for path in CORE.glob("*.py"):
        assert "homeassistant" not in path.read_text(), path.name


@pytest.mark.parametrize(
    ("media_type", "mode"),
    [
        ("artist", PlayMode.RANDOM_ALBUM),
        ("podcast", PlayMode.RANDOM_EPISODE),
        ("audiobook", PlayMode.RESUME),
        ("album", PlayMode.FROM_START),
        ("playlist", PlayMode.FROM_START),
        ("track", PlayMode.FROM_START),
        ("radio", PlayMode.FROM_START),
        ("unknown", PlayMode.FROM_START),
    ],
)
def test_default_mode(media_type, mode):
    assert default_mode(media_type) is mode
    assert modes_for(media_type)[0] is mode


def test_series_modes_only_for_artists_and_podcasts():
    assert modes_for("artist")[:2] == (PlayMode.RANDOM_ALBUM, PlayMode.NEXT_ALBUM)
    assert modes_for("podcast")[:2] == (PlayMode.RANDOM_EPISODE, PlayMode.NEXT_EPISODE)
    for media_type in ("album", "playlist", "audiobook", "track", "radio"):
        assert not {PlayMode.RANDOM_ALBUM, PlayMode.RANDOM_EPISODE} & set(modes_for(media_type))


def test_card_round_trip():
    c = series(position=Position("spotify://track/t", 42, 1.0), order=["a", "b"], order_pos=1, current="a", heard=3)
    assert Card.from_dict(c.to_dict()) == c


def test_card_from_store_v1():
    v1 = {"uid": "U", "name": "Bibi", "uri": "x://audiobook/b", "media_type": "audiobook", "shuffle": False,
          "resume": {"elapsed": 754}}
    c = Card.from_dict(v1)
    assert c.mode is PlayMode.RESUME
    assert c.position.elapsed == 754 and c.position.item_uri is None
    shuffled = Card.from_dict({"uid": "S", "name": "S", "uri": "x://playlist/p", "media_type": "playlist",
                               "shuffle": True, "resume": None})
    assert shuffled.mode is PlayMode.SHUFFLE


def test_card_from_store_v2_random_episode_artist():
    v2 = {"uid": "D", "name": "Die drei ??? Kids", "uri": "x://artist/d", "media_type": "artist",
          "mode": "random_episode", "episodes": ["x://album/1", "x://album/2"], "last_episode": "x://album/1"}
    c = Card.from_dict(v2)
    assert c.mode is PlayMode.RANDOM_ALBUM
    assert [e.uri for e in c.episodes] == ["x://album/1", "x://album/2"] and all(e.included for e in c.episodes)


def test_invalid_mode_falls_back_to_default():
    c = Card.from_dict({"uid": "U", "name": "N", "uri": "x://album/a", "media_type": "album",
                        "mode": "random_album"})
    assert c.mode is PlayMode.FROM_START


@pytest.mark.parametrize(
    ("title", "number"),
    [
        ("035/Im Wilden Westen", 35),
        ("Folge 91: Gefahr im Spiegelkabinett", 91),
        ("138/Die geheime Treppe", 138),
        ("Folge 100: 100 Stunden", 100),
        ("009/und die rätselhaften Bilder", 9),
        ("Adventskalender - O Geisterbaum", None),
        ("2024 Hits", None),
        ("Bamses nya sagor", None),
    ],
)
def test_episode_number(title, number):
    assert episode_number(title) == number


def test_suggest_episodes_unticks_specials_and_unnumbered():
    items = [
        {"uri": "a1", "title": "001/Panik im Paradies"},
        {"uri": "a2", "title": "Adventskalender - 24 Tage voller Spannung!"},
        {"uri": "a3", "title": "Folge 91: Gefahr im Spiegelkabinett"},
        {"uri": "a4", "title": "Die drei ??? Kids - Der Soundtrack"},
        {"uri": "a5", "title": "Mini-Fälle 1"},
        {"uri": "a6", "title": "Sonderfolge Weihnachten"},
        {"uri": "a7", "title": "002/Spuk im Dino-Park"},
        {"uri": "a8", "title": "003/Invasion der Fliegen"},
    ]
    chosen = {e.uri: e.included for e in suggest_episodes(items)}
    # Most albums are numbered, so the unnumbered "Sonderfolge" is unticked too.
    assert chosen == {"a1": True, "a2": False, "a3": True, "a4": False, "a5": False, "a6": False,
                      "a7": True, "a8": True}


def test_suggest_episodes_strips_the_artist_prefix():
    """Music Assistant names albums "<artist> - <album>" (Andreas's HA, 2026-11-22)."""
    titles = [
        "Die drei ??? Kids - Adventskalender - 24 Tage voller Spannung!",
        "Die drei ??? Kids - Nacht unter Wölfen / Night among Wolves",
        "Die drei ??? Kids - Folge 104: Teuflische Küche",
        "Die drei ??? Kids - Mini-Fall/Der unsichtbare Dieb (Mini-Fall 09)",
        "Die drei ??? Kids - Magische Fälle",
        "Die drei ??? Kids - 080/Gefährlicher Nebel",
        "Die drei ??? Kids - 001/Panik im Paradies",
        "Die drei ??? Kids - 002/Radio Rocky Beach",
    ]
    episodes = suggest_episodes([{"uri": f"u{i}", "title": t} for i, t in enumerate(titles)])
    assert [e.title for e in episodes][:3] == [
        "Adventskalender - 24 Tage voller Spannung!", "Nacht unter Wölfen / Night among Wolves",
        "Folge 104: Teuflische Küche"]
    assert [e.number for e in episodes] == [None, None, 104, None, None, 80, 1, 2]
    assert [e.included for e in episodes] == [False, False, True, False, False, True, True, True]
    assert number_order(episodes) == ["u6", "u7", "u5", "u2"]


def test_shared_prefix_only_when_most_share_it():
    from custom_components.speldosa.core.models import strip_shared_prefix

    assert strip_shared_prefix(["A - x", "B - y", "C"]) == ["A - x", "B - y", "C"]
    assert strip_shared_prefix(["Bamse - x", "Bamse - y", "z"]) == ["x", "y", "z"]


def test_suggest_episodes_without_numbers_keeps_all_but_specials():
    items = [{"uri": "b1", "title": "Bamses nya sagor"}, {"uri": "b2", "title": "Bamse på skattjakt"},
             {"uri": "b3", "title": "Bamses bästa sånger och lieder"}]
    chosen = {e.uri: e.included for e in suggest_episodes(items)}
    assert chosen == {"b1": True, "b2": True, "b3": False}


def test_merge_keeps_parent_choice():
    old = [Episode("a", "A", 1, included=False), Episode("b", "B", 2, included=True)]
    fresh = [Episode("a", "A", 1, included=True), Episode("b", "B", 2, included=True), Episode("c", "C", 3)]
    merged = {e.uri: e.included for e in merge_episodes(old, fresh)}
    assert merged == {"a": False, "b": True, "c": True}


def test_number_order():
    eps = [Episode("c", "C", 3), Episode("x", "X", None), Episode("a", "A", 1), Episode("b", "B", 2, included=False)]
    assert number_order(eps) == ["a", "c", "x"]


# Playback ----------------------------------------------------------------------


def test_unknown_card():
    d = on_placed(None, "X", BoxState(), "idle", 0)
    assert kinds(d) == ["status", "unknown_card"]
    assert d.state.active_uid is None


def test_from_start_plays_in_order():
    d = on_placed(card(), "U1", BoxState(), "idle", 0)
    assert kinds(d) == ["play", "status"]
    assert d.actions[0].shuffle is False and d.actions[0].fresh is True


def test_shuffle_mode():
    assert on_placed(card(mode=PlayMode.SHUFFLE), "U1", BoxState(), "idle", 0).actions[0].shuffle is True


def test_lift_while_playing_saves_and_pauses():
    d = on_lifted(BoxState(active_uid="U1"), "playing", 100)
    assert kinds(d) == ["save_position", "pause", "status"]
    assert d.state == BoxState(active_uid=None, paused_uid="U1", lifted_at=100)


def test_lift_while_paused_saves_without_pausing():
    """A parent paused from the app, then the child lifts the card: the place is kept."""
    d = on_lifted(BoxState(active_uid="U1"), "paused", 100)
    assert kinds(d) == ["save_position", "status"]


def test_lift_when_idle_goes_idle():
    assert kinds(on_lifted(BoxState(active_uid="U1"), "idle", 100)) == ["status"]
    assert on_lifted(BoxState(), "playing", 100).actions[0].status == "idle"


def test_put_back_within_window_resumes_any_mode():
    for c in (card(), card(mode=PlayMode.SHUFFLE), series(), series(PlayMode.NEXT_ALBUM)):
        state = BoxState(paused_uid="U1", lifted_at=100, paused_content="spotify://track/t1")
        d = on_placed(c, "U1", state, "paused", 160, player_content="spotify://track/t1")
        assert kinds(d) == ["resume", "status"], c.mode


def test_lift_remembers_what_the_speaker_played():
    d = on_lifted(BoxState(active_uid="U1"), "playing", 100, "spotify://track/t1")
    assert d.state.paused_content == "spotify://track/t1"


def test_something_else_played_in_between_is_not_resumed():
    """Found 2026-11-22: a parent played something else in Music Assistant and paused it; putting the card back
    pressed play on that. The card now starts its own content again, from its place."""
    c = card(position=Position("spotify://track/t3", 30, 0))
    state = BoxState(paused_uid="U1", lifted_at=100, paused_content="spotify://track/t3")
    d = on_placed(c, "U1", state, "paused", 160, player_content="spotify://track/other")
    assert kinds(d) == ["play", "seek", "status"]
    assert d.actions[0].uri == "spotify://playlist/p" and d.actions[0].start_item == "spotify://track/t3"


def test_unknown_speaker_content_is_not_resumed():
    state = BoxState(paused_uid="U1", lifted_at=100)
    d = on_placed(card(), "U1", state, "paused", 160, player_content=None)
    assert kinds(d)[0] == "play"


def test_put_back_after_window_from_start_restarts():
    d = on_placed(card(), "U1", BoxState(paused_uid="U1", lifted_at=0), "paused", 3600)
    assert kinds(d) == ["play", "status"] and d.actions[0].start_item is None


def test_within_window_player_stopped_uses_saved_position():
    c = card(position=Position("spotify://track/t3", 30, 0))
    d = on_placed(c, "U1", BoxState(paused_uid="U1", lifted_at=0), "idle", 10)
    assert kinds(d) == ["play", "seek", "status"]
    assert d.actions[0].start_item == "spotify://track/t3" and d.actions[1].position == 30


def test_resume_mode_after_window():
    c = card(mode=PlayMode.RESUME, position=Position("spotify://track/t9", 75, 0))
    d = on_placed(c, "U1", BoxState(), "idle", 10_000)
    assert kinds(d) == ["play", "seek", "status"] and d.actions[0].start_item == "spotify://track/t9"


def test_audiobook_position_without_item_seeks_only():
    c = card(media_type="audiobook", mode=PlayMode.RESUME, position=Position(None, 754, 0))
    d = on_placed(c, "U1", BoxState(), "idle", 0)
    assert d.actions[0].start_item is None and d.actions[1].position == 754


# Series: random and next album --------------------------------------------------


def test_random_album_starts_an_album_from_its_start():
    c = series()
    d = run(c, on_placed(c, "U1", BoxState(), "idle", 0, rng=random.Random(1)))
    assert kinds(d) == ["series_started", "play", "status"]
    play = d.actions[1]
    assert play.media_type == "album" and play.start_item is None and play.shuffle is False and play.fresh
    assert c.current == play.uri and sorted(c.order) == [f"spotify://album/e{i}" for i in range(1, 5)]


def test_paused_album_continues_later_from_its_place():
    """The Die drei ??? case: lifted mid-album, put back the next day, it continues there (decided 2026-11-20)."""
    c = series()
    run(c, on_placed(c, "U1", BoxState(), "idle", 0, rng=random.Random(1)))
    album = c.current
    c.position = Position("spotify://track/chapter7", 312, 100)  # saved on lift
    d = on_placed(c, "U1", BoxState(paused_uid="U1", lifted_at=100), "idle", 100 + 24 * 3600)
    assert kinds(d) == ["play", "seek", "status"]
    assert d.actions[0].uri == album and d.actions[0].start_item == "spotify://track/chapter7"
    assert d.actions[1].position == 312


def test_album_moves_on_only_when_heard_to_the_end():
    c = series(n=3)
    rng = random.Random(7)
    heard = []
    for _ in range(3):
        d = run(c, on_placed(c, "U1", BoxState(), "idle", 0, rng=rng))
        heard.append(c.current)
        # Lifted halfway and put back: still the same album.
        again = on_placed(c, "U1", BoxState(), "idle", 99_999, rng=rng)
        assert again.actions[0].uri == c.current
        apply_heard(c)
    assert sorted(heard) == [f"spotify://album/e{i}" for i in range(1, 4)]  # each once before any repeat
    assert c.heard == 3 and c.current is None


def test_random_album_reshuffles_after_a_full_round():
    c = series(n=3)
    rng = random.Random(3)
    for _ in range(3):
        run(c, on_placed(c, "U1", BoxState(), "idle", 0, rng=rng))
        apply_heard(c)
    d = run(c, on_placed(c, "U1", BoxState(), "idle", 0, rng=rng))
    assert c.order_pos == 0 and kinds(d)[0] == "series_started"


def test_next_album_goes_in_number_order_and_wraps():
    c = series(PlayMode.NEXT_ALBUM, n=3)
    c.episodes.reverse()
    played = []
    for _ in range(4):
        run(c, on_placed(c, "U1", BoxState(), "idle", 0))
        played.append(c.current)
        apply_heard(c)
    assert played == ["spotify://album/e1", "spotify://album/e2", "spotify://album/e3", "spotify://album/e1"]


def test_unticked_albums_are_never_played():
    c = series(n=4)
    for e in c.episodes[1:]:
        e.included = False
    for _ in range(3):
        run(c, on_placed(c, "U1", BoxState(), "idle", 0, rng=random.Random()))
        assert c.current == "spotify://album/e1"
        apply_heard(c)


def test_changed_selection_rebuilds_the_order():
    c = series(n=3)
    run(c, on_placed(c, "U1", BoxState(), "idle", 0, rng=random.Random(2)))
    apply_heard(c)
    c.episodes.append(Episode("spotify://album/e9", "009/Neu", 9))
    run(c, on_placed(c, "U1", BoxState(), "idle", 0, rng=random.Random(2)))
    assert len(c.order) == 4


def test_series_without_albums_shuffles_the_artist():
    c = card(uri="spotify://artist/d", media_type="artist", mode=PlayMode.RANDOM_ALBUM)
    d = on_placed(c, "U1", BoxState(), "idle", 0)
    assert kinds(d) == ["play", "status"] and d.actions[0].shuffle is True


def test_podcast_episode_has_no_media_type():
    c = card(uri="spotify://podcast/p", media_type="podcast", mode=PlayMode.NEXT_EPISODE,
             episodes=[Episode("spotify://episode/1", "Ep 1", 1)])
    d = on_placed(c, "U1", BoxState(), "idle", 0)
    assert d.actions[1].uri == "spotify://episode/1" and d.actions[1].media_type is None


def test_heard_audiobook_starts_from_the_beginning():
    c = card(media_type="audiobook", mode=PlayMode.RESUME, position=Position(None, 7200, 0))
    assert kinds(on_finished(c)) == ["heard", "status"]
    apply_heard(c)
    assert c.position is None
    assert on_placed(c, "U1", BoxState(), "idle", 0).actions[0].start_item is None


def test_is_finished():
    last = {"items": 12, "current_index": 11}
    assert is_finished(last, 1290, 1300) is True
    assert is_finished(last, 600, 1300) is False  # stopped from the app halfway through the last chapter
    assert is_finished({"items": 12, "current_index": 4}, 1299, 1300) is False
    assert is_finished({"items": 1, "current_index": 0}, 3590, 3600) is True  # audiobook in one item
    assert is_finished(last, None, 1300) is False
    assert is_finished(None, 1290, 1300) is False


def test_position_from_queue():
    q = {"elapsed_time": 61, "current_item": {"media_item": {"uri": "spotify://track/x"}}}
    assert position_from_queue(q, 5.0) == Position("spotify://track/x", 61, 5.0)
    assert position_from_queue({}, 0) is None
    assert position_from_queue({"elapsed_time": 0, "current_item": None}, 0) is None


# Search ------------------------------------------------------------------------


def test_score_levels():
    assert score("Die drei ???", "Die drei ???") == 100
    assert score("Die drei ???", "Die drei ??? Alle Folgen (1-240)") == 85
    assert score("bamse", "Jul i Bamses kula") < 55
    assert score("Die drei ???", "138/Die geheime Treppe", ["Die drei ???"]) == 55
    assert score("Die drei ???", "Die drei kleinen Schweinchen") < 55
    assert score("", "x") == 0


def test_rank_real_search():
    response = json.loads((FIXTURES / "search_die_drei.json").read_text())
    r = rank_results("Die drei ???", response)
    assert [i["name"] for i in r["best"]] == ["Die drei ???", "Die drei ??? Kids"]
    groups = {g["media_type"]: [i["name"] for i in g["items"]] for g in r["groups"]}
    assert set(groups["playlist"][:2]) == {"Die drei ??? Alle Folgen (1-240)", "Die drei ??? Kids - Alle Hörspiele"}
    assert "Die drei !!! - Die drei Ausrufezeichen - Alle Hörspiele" not in groups["playlist"]
    assert "Adventskalender - O Geisterbaum" in groups["album"]
    assert groups["podcast"] == ["Die drei ???"]
    weaker = [i["name"] for i in r["weaker"]]
    assert "Die drei kleinen Schweinchen" in weaker and "TKKG" in weaker
    assert "audiobook" not in groups
    assert r["empty"] is False
    order = [g["media_type"] for g in r["groups"]]
    assert order == sorted(order, key=["artist", "playlist", "album", "audiobook", "podcast"].index)


def test_rank_filters_types_locally():
    response = json.loads((FIXTURES / "search_die_drei.json").read_text())
    r = rank_results("Die drei ???", response, types=["album"])
    assert [g["media_type"] for g in r["groups"]] == ["album"] and r["best"] == []


def test_rank_empty_response():
    r = rank_results("x", {"artists": [], "albums": []})
    assert r == {"best": [], "groups": [], "weaker": [], "empty": True}
    assert rank_results("x", None)["empty"] is True


def test_subtitle_from_artists_or_album():
    response = {"tracks": [{"uri": "t", "name": "Bamse", "media_type": "track", "artists": [],
                            "album": {"name": "Blåsbus 2 saxofon"}}]}
    item = rank_results("Bamse", response)["groups"][0]["items"][0]
    assert item["subtitle"] == "Blåsbus 2 saxofon"
