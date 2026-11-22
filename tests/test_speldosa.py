"""The integration on the Home Assistant test harness: setup, the box's main path, the page's API."""

from __future__ import annotations

from homeassistant.components import persistent_notification
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.speldosa.const import CONF_DEVICE_ID, CONF_PLAYER, CONF_RESUME_WINDOW, DOMAIN
from unittest.mock import patch

from homeassistant.util import dt as dt_util

from custom_components.speldosa.core import Card, Episode, PlayMode, Position

from .conftest import CARD, PLAYER, STATUS


async def _setup(hass: HomeAssistant, device_id: str, options: dict | None = None) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN, title="Speldosa kids room", unique_id=device_id,
        data={CONF_DEVICE_ID: device_id, CONF_PLAYER: PLAYER}, options=options or {},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def _place(hass: HomeAssistant, uid: str) -> None:
    hass.states.async_set(CARD, uid)
    await hass.async_block_till_done()


def _store(hass):
    return hass.data[DOMAIN].store


# Setup -------------------------------------------------------------------------


async def test_config_flow_needs_music_assistant(hass: HomeAssistant, box) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "no_music_assistant"


async def test_config_flow_adds_box(hass: HomeAssistant, box, player, services) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DEVICE_ID: box, CONF_PLAYER: player}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_DEVICE_ID: box, CONF_PLAYER: player}


async def test_options_set_speaker_and_window(hass: HomeAssistant, box, player, services) -> None:
    entry = await _setup(hass, box)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["step_id"] == "init"
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_PLAYER: player, CONF_RESUME_WINDOW: 30}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert hass.data[DOMAIN].controllers[entry.entry_id].resume_window_s == 1800


async def test_panel_registered(hass: HomeAssistant, box, player, services) -> None:
    await _setup(hass, box)
    panel = hass.data["frontend_panels"]["speldosa"]
    assert panel.sidebar_icon == "speldosa:logo"
    from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL

    assert any("speldosa-icons.js" in url for url in hass.data[DATA_EXTRA_MODULE_URL].urls)


async def test_brand_icon_is_served(hass: HomeAssistant, hass_client, box, player, services) -> None:
    """HA 2026.3+ serves a custom integration's brand/ folder; that is where the Speldosa mark comes from."""
    from homeassistant.setup import async_setup_component

    assert await async_setup_component(hass, "brands", {})
    client = await hass_client()
    for image in ("icon.png", "icon@2x.png", "dark_icon.png", "logo.png"):
        resp = await client.get(f"/api/brands/integration/speldosa/{image}")
        assert resp.status == 200, image
        assert (await resp.read())[:8] == b"\x89PNG\r\n\x1a\n"


async def test_two_boxes_set_up_together(hass: HomeAssistant, box, player, services) -> None:
    """Both boxes load at startup at the same time; only one registers the panel (found 2026-11-20)."""
    from homeassistant.helpers import device_registry as dr, entity_registry as er

    second = dr.async_get(hass).async_get_or_create(
        config_entry_id=next(iter(hass.config_entries.async_entries("esphome"))).entry_id,
        identifiers={("esphome", "11:22:33:44:55:66")}, manufacturer="anjobe", model="speldosa", name="Box 2",
    )
    er.async_get(hass).async_get_or_create(
        "sensor", "esphome", "112233445566-card", device_id=second.id, original_name="Card",
        suggested_object_id="box2_card",
    )
    hass.states.async_set("sensor.box2_card", "none")
    entries = []
    for device_id in (box, second.id):
        entry = MockConfigEntry(domain=DOMAIN, title=device_id, unique_id=device_id,
                                data={CONF_DEVICE_ID: device_id, CONF_PLAYER: PLAYER})
        entry.add_to_hass(hass)
        entries.append(entry)
    assert await hass.config_entries.async_setup(entries[0].entry_id)  # sets up both entries of the domain
    await hass.async_block_till_done()
    assert all(e.state.value == "loaded" for e in entries)
    assert len(hass.data[DOMAIN].controllers) == 2


async def test_shared_data_is_created_once_when_concurrent(hass: HomeAssistant, box, player, services) -> None:
    """Two boxes starting together must share one store and one set of controllers (found 2026-11-20)."""
    import asyncio

    from homeassistant.setup import async_setup_component

    from custom_components.speldosa import async_get_data
    from custom_components.speldosa.store import CardStore

    for component in ("http", "websocket_api"):
        assert await async_setup_component(hass, component, {})
    real_load = CardStore.async_load

    async def slow_load(self):
        # On a real system the store file is read in an executor, so loading yields to other tasks.
        await asyncio.sleep(0.01)
        await real_load(self)

    CardStore.async_load = slow_load
    try:
        first, second = await asyncio.gather(async_get_data(hass), async_get_data(hass))
    finally:
        CardStore.async_load = real_load
    assert first is second is hass.data[DOMAIN]


async def test_panel_registration_is_safe_when_concurrent(hass: HomeAssistant, box, player, services) -> None:
    """Two setups registering the panel at once must not both register it."""
    import asyncio

    from homeassistant.setup import async_setup_component

    from custom_components.speldosa.panel import async_register_panel

    for component in ("http", "frontend", "panel_custom"):
        assert await async_setup_component(hass, component, {})
    await asyncio.gather(async_register_panel(hass), async_register_panel(hass))
    assert "speldosa" in hass.data["frontend_panels"]


# Main path ---------------------------------------------------------------------


async def test_unknown_card_is_seen_and_notified(hass: HomeAssistant, box, player, services) -> None:
    entry = await _setup(hass, box)
    await _place(hass, "04-A1")
    assert hass.states.get(STATUS).state == "unknown_card"
    assert [s.uid for s in _store(hass).seen()] == ["04-A1"]
    notes = persistent_notification._async_get_or_create_notifications(hass)
    assert f"speldosa_unknown_{entry.entry_id}" in notes
    assert "04-A1" in notes[f"speldosa_unknown_{entry.entry_id}"]["message"]


async def test_place_lift_put_back(hass: HomeAssistant, box, player, services) -> None:
    await _setup(hass, box)
    _store(hass).set(Card("U1", "Bedtime", "spotify://playlist/p1", "playlist", PlayMode.FROM_START))
    await _place(hass, "U1")
    play = services.named("music_assistant", "play_media")[-1]
    assert play["media_id"] == "spotify://playlist/p1" and play["enqueue"] == "replace" and "start_item" not in play
    assert services.named("media_player", "shuffle_set")[-1]["shuffle"] is False
    assert hass.states.get(STATUS).state == "playing"

    services.queue = {"elapsed_time": 42, "current_item": {"media_item": {"uri": "spotify://track/t2"}}}
    await _place(hass, "none")
    assert len(services.named("media_player", "media_pause")) == 1
    assert _store(hass).get("U1").position.item_uri == "spotify://track/t2"
    assert hass.states.get(STATUS).state == "paused"

    await _place(hass, "U1")
    assert len(services.named("media_player", "media_play")) == 1
    assert len(services.named("music_assistant", "play_media")) == 1


async def test_other_music_in_between_is_not_resumed(hass: HomeAssistant, box, player, services) -> None:
    """Found 2026-11-22: a playlist card put back after a parent played and paused something else in Music
    Assistant resumed that other thing. It must start the card's own playlist again."""
    await _setup(hass, box)
    _store(hass).set(Card("U1", "Bedtime", "spotify://playlist/p1", "playlist", PlayMode.FROM_START))
    await _place(hass, "U1")
    await _place(hass, "none")
    assert hass.states.get(PLAYER).state == "paused"
    services.set_player("playing", content="spotify://album/parents-music")  # played from Music Assistant
    services.set_player("paused")
    await hass.async_block_till_done()
    await _place(hass, "U1")
    assert services.named("media_player", "media_play") == []
    assert services.named("music_assistant", "play_media")[-1]["media_id"] == "spotify://playlist/p1"


async def test_window_zero_restarts_from_start(hass: HomeAssistant, box, player, services) -> None:
    await _setup(hass, box, {CONF_PLAYER: PLAYER, CONF_RESUME_WINDOW: 0})
    _store(hass).set(Card("U1", "Bedtime", "spotify://playlist/p1", "playlist", PlayMode.FROM_START))
    await _place(hass, "U1")
    await _place(hass, "none")
    hass.data[DOMAIN].controllers[next(iter(hass.data[DOMAIN].controllers))].state = (
        hass.data[DOMAIN].controllers[next(iter(hass.data[DOMAIN].controllers))].state.__class__(
            paused_uid="U1", lifted_at=0
        )
    )
    await _place(hass, "U1")
    assert len(services.named("music_assistant", "play_media")) == 2


async def test_resume_mode_continues_from_track(hass: HomeAssistant, box, player, services) -> None:
    await _setup(hass, box)
    _store(hass).set(Card("B", "Bibi", "spotify://album/a", "album", PlayMode.RESUME,
                          position=Position("spotify://track/t7", 95, 0)))
    await _place(hass, "B")
    await hass.async_block_till_done()
    play = services.named("music_assistant", "play_media")[-1]
    assert play["start_item"] == "spotify://track/t7"
    assert services.named("media_player", "media_seek")[-1]["seek_position"] == 95


def _series_card(mode=PlayMode.RANDOM_ALBUM, n=3):
    episodes = [Episode(f"spotify://album/e{i}", f"{i:03d}/Folge", i) for i in range(1, n + 1)]
    return Card("D", "Die drei ???", "spotify://artist/x", "artist", mode, episodes=episodes)


def _play_near_end(hass, position=1290, duration=1300):
    old = hass.states.get(PLAYER)
    attrs = dict(old.attributes) | {"media_position": position, "media_duration": duration,
                                    "media_position_updated_at": dt_util.utcnow()}
    hass.states.async_set(PLAYER, "playing", attrs)


async def test_random_album_plays_whole_album_with_settings(hass: HomeAssistant, box, player, services) -> None:
    hass.states.async_set(PLAYER, "idle", {"friendly_name": "Kids room", "group_members": [PLAYER, "media_player.x"]})
    await _setup(hass, box)
    _store(hass).set(_series_card())
    await _place(hass, "D")
    play = services.named("music_assistant", "play_media")[-1]
    card = _store(hass).get("D")
    assert play["media_id"] == card.current and play["media_type"] == "album" and "start_item" not in play
    assert services.named("media_player", "shuffle_set")[-1]["shuffle"] is False
    assert services.named("media_player", "repeat_set")[-1]["repeat"] == "off"
    assert services.named("media_player", "volume_set")[-1]["volume_level"] == 0.4
    assert len(services.named("media_player", "unjoin")) == 1


async def test_heard_to_the_end_moves_on(hass: HomeAssistant, box, player, services) -> None:
    await _setup(hass, box)
    _store(hass).set(_series_card(PlayMode.NEXT_ALBUM))
    await _place(hass, "D")
    assert _store(hass).get("D").current == "spotify://album/e1"
    controller = next(iter(hass.data[DOMAIN].controllers.values()))
    controller._last_play_at = 0  # the album has been playing for a while
    _play_near_end(hass)
    await hass.async_block_till_done()
    services.queue = {"items": 12, "current_index": 11, "elapsed_time": 0}
    hass.states.async_set(PLAYER, "idle", hass.states.get(PLAYER).attributes)
    await hass.async_block_till_done()
    card = _store(hass).get("D")
    assert card.current is None and card.heard == 1 and card.order_pos == 1
    await _place(hass, "none")
    await _place(hass, "D")
    assert services.named("music_assistant", "play_media")[-1]["media_id"] == "spotify://album/e2"


async def test_stopped_halfway_is_not_heard(hass: HomeAssistant, box, player, services) -> None:
    await _setup(hass, box)
    _store(hass).set(_series_card(PlayMode.NEXT_ALBUM))
    await _place(hass, "D")
    controller = next(iter(hass.data[DOMAIN].controllers.values()))
    controller._last_play_at = 0
    _play_near_end(hass, position=300)
    await hass.async_block_till_done()
    services.queue = {"items": 12, "current_index": 4, "elapsed_time": 300}
    hass.states.async_set(PLAYER, "idle", hass.states.get(PLAYER).attributes)
    await hass.async_block_till_done()
    assert _store(hass).get("D").current == "spotify://album/e1" and _store(hass).get("D").heard == 0


async def test_paused_album_continues_the_next_day(hass: HomeAssistant, box, player, services) -> None:
    await _setup(hass, box)
    _store(hass).set(_series_card())
    await _place(hass, "D")
    album = _store(hass).get("D").current
    services.queue = {"elapsed_time": 312, "current_item": {"media_item": {"uri": "spotify://track/chapter7"}}}
    await _place(hass, "none")
    controller = next(iter(hass.data[DOMAIN].controllers.values()))
    controller.state = controller.state.__class__(paused_uid="D", lifted_at=0)  # lifted long ago
    services.set_player("idle")
    volume_calls = len(services.named("media_player", "volume_set"))
    await _place(hass, "D")
    await hass.async_block_till_done()
    play = services.named("music_assistant", "play_media")[-1]
    assert play["media_id"] == album and play["start_item"] == "spotify://track/chapter7"
    assert services.named("media_player", "media_seek")[-1]["seek_position"] == 312
    assert len(services.named("media_player", "volume_set")) == volume_calls  # no volume change on continue


async def test_episodes_command_suggests_and_link_keeps_choice(
    hass: HomeAssistant, hass_ws_client, box, player, services
) -> None:
    await _setup(hass, box)
    items = [{"uri": "a1", "title": "001/Panik im Paradies", "image": None},
             {"uri": "a2", "title": "Adventskalender - 24 Tage", "image": None},
             {"uri": "a3", "title": "002/Spuk", "image": None}]
    client = await hass_ws_client(hass)
    with patch("custom_components.speldosa.music.async_episodes", return_value=items):
        await client.send_json_auto_id({"type": "speldosa/episodes", "uri": "spotify://artist/x", "media_type": "artist"})
        result = (await client.receive_json())["result"]["episodes"]
    assert [(e["uri"], e["included"]) for e in result] == [("a1", True), ("a2", False), ("a3", True)]
    result[2]["included"] = False
    await client.send_json_auto_id({
        "type": "speldosa/card/link", "uid": "D", "uri": "spotify://artist/x", "media_type": "artist",
        "name": "Die drei ??? Kids", "mode": "next_album", "episodes": result,
    })
    msg = await client.receive_json()
    assert msg["success"] and msg["result"]["included"] == 1 and msg["result"]["episodes"] == 3
    await client.send_json_auto_id({"type": "speldosa/card/get", "uid": "D"})
    got = (await client.receive_json())["result"]
    assert [e["included"] for e in got["episode_list"]] == [True, False, False]


async def test_play_failure_sets_error_and_notifies(hass: HomeAssistant, box, player, services) -> None:
    entry = await _setup(hass, box)
    _store(hass).set(Card("U1", "Bedtime", "spotify://playlist/p1", "playlist", PlayMode.FROM_START))
    services.fail_play = True
    await _place(hass, "U1")
    assert hass.states.get(STATUS).state == "error"
    notes = persistent_notification._async_get_or_create_notifications(hass)
    assert "concurrent source streams" in notes[f"speldosa_error_{entry.entry_id}"]["message"]


# Page API ----------------------------------------------------------------------


async def test_overview(hass: HomeAssistant, hass_ws_client, box, player, services) -> None:
    entry = await _setup(hass, box)
    _store(hass).set(Card("U1", "Bedtime", "spotify://playlist/p1", "playlist", PlayMode.FROM_START,
                          image="https://i.scdn.co/image/x"))
    await _place(hass, "NEW")
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "speldosa/overview"})
    msg = await client.receive_json()
    assert msg["success"]
    result = msg["result"]
    assert result["boxes"][0]["entry_id"] == entry.entry_id
    assert result["boxes"][0]["card"] == "NEW" and result["boxes"][0]["card_linked"] is False
    assert result["boxes"][0]["player_name"] == "Kids room" and result["boxes"][0]["reader_problem"] is False
    assert result["cards"][0]["image"] == "https://i.scdn.co/image/x"
    assert result["cards"][0]["modes"] == ["from_start", "shuffle", "resume"]
    assert [s["uid"] for s in result["seen"]] == ["NEW"]


async def test_search_ranks_and_caches(hass: HomeAssistant, hass_ws_client, box, player, services) -> None:
    await _setup(hass, box)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "speldosa/search", "query": "Die drei ???"})
    msg = await client.receive_json()
    assert msg["success"]
    result = msg["result"]
    assert [i["name"] for i in result["best"]] == ["Die drei ???", "Die drei ??? Kids"]
    assert result["best"][0]["mode"] == "random_album"
    assert "media_type" not in services.named("music_assistant", "search")[-1]
    await client.send_json_auto_id({"type": "speldosa/search", "query": "die drei ???", "types": ["album"]})
    msg = await client.receive_json()
    assert [g["media_type"] for g in msg["result"]["groups"]] == ["album"]
    assert len(services.named("music_assistant", "search")) == 1  # served from the cache


async def test_search_short_and_busy(hass: HomeAssistant, hass_ws_client, box, player, services) -> None:
    await _setup(hass, box)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "speldosa/search", "query": "di"})
    assert (await client.receive_json())["result"]["too_short"] is True
    services.search_response = {"artists": [], "albums": []}
    await client.send_json_auto_id({"type": "speldosa/search", "query": "Bamse"})
    assert (await client.receive_json())["result"]["empty"] is True
    await client.send_json_auto_id({"type": "speldosa/search", "query": "Bamse"})
    await client.receive_json()
    assert len(services.named("music_assistant", "search")) == 2  # empty answers are not cached


async def test_link_card_on_box_plays_it(hass: HomeAssistant, hass_ws_client, box, player, services) -> None:
    await _setup(hass, box)
    await _place(hass, "NEW")
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({
        "type": "speldosa/card/link", "uid": "NEW", "uri": "spotify://album/a", "media_type": "album",
        "name": "009/und die rätselhaften Bilder", "image": "https://i.scdn.co/image/c",
    })
    msg = await client.receive_json()
    assert msg["success"] and msg["result"]["mode"] == "from_start"
    await hass.async_block_till_done()
    assert services.named("music_assistant", "play_media")[-1]["media_id"] == "spotify://album/a"
    assert _store(hass).seen() == []


async def test_link_rejects_mode_not_offered(hass: HomeAssistant, hass_ws_client, box, player, services) -> None:
    await _setup(hass, box)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({
        "type": "speldosa/card/link", "uid": "X", "uri": "spotify://album/a", "media_type": "album",
        "name": "A", "mode": "random_episode",
    })
    msg = await client.receive_json()
    assert not msg["success"] and msg["error"]["code"] == "invalid_mode"


async def test_update_and_unlink(hass: HomeAssistant, hass_ws_client, box, player, services) -> None:
    await _setup(hass, box)
    _store(hass).set(Card("U1", "Bedtime", "spotify://playlist/p1", "playlist", PlayMode.FROM_START))
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "speldosa/card/update", "uid": "U1", "mode": "shuffle", "name": "Kväll"})
    msg = await client.receive_json()
    assert msg["result"]["mode"] == "shuffle" and _store(hass).get("U1").name == "Kväll"
    await client.send_json_auto_id({"type": "speldosa/card/unlink", "uid": "U1"})
    assert (await client.receive_json())["success"]
    assert _store(hass).get("U1") is None


async def test_try_plays_without_linking(hass: HomeAssistant, hass_ws_client, box, player, services) -> None:
    await _setup(hass, box)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {"type": "speldosa/card/try", "uri": "spotify://artist/x", "media_type": "artist", "mode": "random_episode"}
    )
    msg = await client.receive_json()
    assert msg["success"] and msg["result"]["player_name"] == "Kids room"
    play = services.named("music_assistant", "play_media")[-1]
    assert play["media_id"] == "spotify://artist/x"
    assert services.named("media_player", "shuffle_set")[-1]["shuffle"] is True
    assert _store(hass).all() == []


async def test_now_playing(hass: HomeAssistant, hass_ws_client, box, player, services) -> None:
    await _setup(hass, box)
    services.queue = {"elapsed_time": 6, "current_item": {"name": "Felicità", "media_item": {
        "uri": "spotify://track/f", "name": "Felicità", "media_type": "track", "image": "https://i.scdn.co/f",
        "artists": [{"name": "Al Bano And Romina Power"}],
        "album": {"uri": "spotify://album/fa", "name": "Felicità (Ariola Express Gold-Serie)",
                  "image": "http://192.168.1.2:8095/imageproxy/abc"},
    }}}
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "speldosa/now_playing"})
    now = (await client.receive_json())["result"]["now"]
    assert now["track"]["name"] == "Felicità" and now["track"]["subtitle"] == "Al Bano And Romina Power"
    assert now["album"]["uri"] == "spotify://album/fa"
    assert now["album"]["image"].startswith("/api/speldosa/image/") and "authSig=" in now["album"]["image"]
    assert now["album"]["source_image"].startswith("http://")


async def test_subscribe_gets_changes(hass: HomeAssistant, hass_ws_client, box, player, services) -> None:
    await _setup(hass, box)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "speldosa/subscribe"})
    assert (await client.receive_json())["success"]
    await _place(hass, "NEW")
    event = await client.receive_json()
    assert event["type"] == "event" and event["event"] == {"changed": True}


async def test_image_proxy_serves_only_signed_known_urls(
    hass: HomeAssistant, hass_ws_client, hass_client_no_auth, aioclient_mock, box, player, services
) -> None:
    await _setup(hass, box)
    url = "http://192.168.1.2:8095/imageproxy/abc"
    aioclient_mock.get(url, content=b"jpegbytes", headers={"Content-Type": "image/jpeg"})
    services.queue = {"current_item": {"media_item": {"uri": "spotify://track/f", "name": "F", "image": url}}}
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "speldosa/now_playing"})
    signed = (await client.receive_json())["result"]["now"]["track"]["image"]
    web = await hass_client_no_auth()
    resp = await web.get(signed)
    assert resp.status == 200 and await resp.read() == b"jpegbytes"
    assert (await web.get(signed.split("?")[0])).status == 401
    other = "/api/speldosa/image/" + "0" * 32 + "?" + signed.split("?")[1]
    assert (await web.get(other)).status in (401, 404)


async def test_migrated_untitled_album_list_is_refetched_with_suggestion(
    hass: HomeAssistant, box, player, services
) -> None:
    """Store version 2 kept bare URIs, all ticked: after setup the list gets titles and the suggested choice."""
    items = [{"uri": "a1", "title": "001/Panik im Paradies", "image": None},
             {"uri": "a2", "title": "Adventskalender - 24 Tage", "image": None}]
    with patch("custom_components.speldosa.music.async_episodes", return_value=items):
        await _setup(hass, box)
        _store(hass).set(Card("D", "Die drei ???", "spotify://artist/x", "artist", PlayMode.RANDOM_ALBUM,
                              episodes=[Episode("a1", "a1"), Episode("a2", "a2")]))
        from custom_components.speldosa.websocket import async_refresh_stale_episodes

        async_refresh_stale_episodes(hass, PLAYER)
        await hass.async_block_till_done()
    card = _store(hass).get("D")
    assert [(e.title, e.included) for e in card.episodes] == [
        ("001/Panik im Paradies", True), ("Adventskalender - 24 Tage", False)]


async def test_prefixed_album_list_is_suggested_again(hass: HomeAssistant, box, player, services) -> None:
    """0.3.0 to 0.3.2 kept "<artist> - " in titles and found no numbers: such a list is suggested again."""
    items = [{"uri": "a1", "title": "Kids - 001/Panik", "image": None},
             {"uri": "a2", "title": "Kids - Magische Fälle", "image": None},
             {"uri": "a3", "title": "Kids - 002/Radio", "image": None}]
    with patch("custom_components.speldosa.music.async_episodes", return_value=items):
        await _setup(hass, box)
        _store(hass).set(Card("D", "Kids", "spotify://artist/x", "artist", PlayMode.RANDOM_ALBUM,
                              episodes=[Episode(i["uri"], i["title"], None, True) for i in items]))
        from custom_components.speldosa.websocket import async_refresh_stale_episodes

        async_refresh_stale_episodes(hass, PLAYER)
        await hass.async_block_till_done()
    card = _store(hass).get("D")
    assert [(e.title, e.number, e.included) for e in card.episodes] == [
        ("001/Panik", 1, True), ("Magische Fälle", None, False), ("002/Radio", 2, True)]


async def test_store_migrates_version_1(hass: HomeAssistant, hass_storage, box, player, services) -> None:
    hass_storage["speldosa.cards"] = {
        "version": 1, "minor_version": 1, "key": "speldosa.cards",
        "data": {"cards": {"04-02": {"uid": "04-02", "name": "BEST OF Italo Pop",
                                     "uri": "spotify://playlist/i", "media_type": "playlist",
                                     "shuffle": False, "resume": None}}},
    }
    await _setup(hass, box)
    card = _store(hass).get("04-02")
    assert card.mode is PlayMode.FROM_START and card.name == "BEST OF Italo Pop"
