# Architecture

Speldosa is three layers. The box reads cards; Home Assistant decides what to play; Music Assistant plays it.

| Layer | Where | Depends on |
|---|---|---|
| Box firmware | `firmware/` (ESPHome) | Nothing but the box. Reports the card on it and shows a status |
| Core | `custom_components/speldosa/core/` | Nothing: plain Python, no Home Assistant import (a test checks it) |
| Home Assistant integration | `custom_components/speldosa/` | Home Assistant and Music Assistant |
| Page in the sidebar | `frontend/`, built into `custom_components/speldosa/frontend/` | The integration's websocket API |

## Box

The box tells Home Assistant one thing: the `Card` sensor holds the UID of the card on it, or `none`. A card counts
as lifted only after the box's lift delay, so a short misread does not pause the music. Home Assistant sets the
box's `Status` select (idle, playing, paused, unknown_card, error) and the box shows it with its light and sound.

## Core

`core/` decides what a card does, as pure functions over plain data:

- `models.py`: cards, play modes per media type and their defaults, album and episode lists with episode numbers
  read from titles and a suggested selection.
- `playback.py`: `on_placed`, `on_lifted` and `on_finished` return a list of actions (play, resume, pause, seek,
  save the position, set the status, start the next album, mark heard). A card put back within the resume window
  continues; after it the card's mode decides. A series album continues until it has been heard to the end.
- `search.py`: ranks and groups Music Assistant search results.

A connector feeds it events and carries out the actions. Today that is the Home Assistant integration.

## Integration

- `controller.py`: one per box. Listens to the box's Card sensor and the speaker, runs the core, carries out its
  actions, and notices when a piece was heard to the end (the speaker stopped at the last queue item near its end).
- `music.py`: every Music Assistant call (search with a cache, play, queue, now playing, album lists).
- `websocket.py`: the API the page uses (`speldosa/overview`, `search`, `episodes`, `card/link`, `card/update`,
  `card/get`, `card/unlink`, `card/try`, `now_playing`, `seen/forget`, `subscribe`).
- `store.py`: cards in `.storage/speldosa.cards`, shared by every box in the home.
- `image.py`: Music Assistant's plain-http cover images through a signed view for the https page.
- `panel.py`: registers the Speldosa page in the sidebar.

## Standalone hub

The core has no Home Assistant import, so a standalone Speldosa hub can reuse it with two other connectors: the
box over the ESPHome native API (`aioesphomeapi`) and Music Assistant over its own API
(`music-assistant-client`). The page talks only to the websocket API above, so a hub that serves the same API can
serve the same page.
