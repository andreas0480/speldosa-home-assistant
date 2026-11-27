# Speldosa for Home Assistant

Speldosa is a screen-free music box for children. Put a tag on the box and the music, story or audiobook linked
to it plays on a speaker in the room through Music Assistant. Lift the tag and it pauses. Put it back and it
continues. A tag is a card, coin or sticker with an NFC chip.

This repository holds the box's firmware (ESPHome) and the Home Assistant integration with its page for linking
tags. The box hardware is not part of it.

**Status: beta.** Tested with Home Assistant 2026.11 and Music Assistant 2.10 with Spotify and Sonos speakers.

## Install

The full guide, from Wi-Fi to the first tag: **[setup guide](docs/setup-guide.md)** ·
**[på svenska](docs/setup-guide.sv.md)**.

In short, with Home Assistant 2026.10 or later, HACS and Music Assistant already set up:

1. Set the box's Wi-Fi over USB at <https://web.esphome.io>, then add the box in Home Assistant (ESPHome).
2. HACS, Custom repositories: add `https://github.com/andreas0480/speldosa-home-assistant` as an Integration,
   download **Speldosa**, restart Home Assistant.
3. Settings, Devices and services, Add integration, **Speldosa**: pick the box and its speaker.
4. Open **Speldosa** in the sidebar and link the tags.

## Tag choices

| Choice | For |
|---|---|
| A random album each time | Audiobook series where each album is one episode, such as Die drei ??? or Bamse. Every chosen album once before any repeats |
| The next album each time | The same series, in episode order |
| From the start, In random order | Albums, playlists, songs |
| Continue where it stopped | Audiobooks |
| A random or the next episode | Podcasts |

A tag lifted and put back within 15 minutes always continues. A series album lifted halfway continues from that
spot later, however much later, and the tag moves on only when the album has been heard to the end. The page
lists an artist's albums so you can choose which count as episodes; specials such as advent calendars are left out
by default.

## Privacy

Everything stays in your home. The integration talks to your Home Assistant, your Music Assistant and your box,
and sends nothing anywhere else. Cover images come from your music service.

## For developers

| Path | What it is |
|---|---|
| `custom_components/speldosa/` | The integration. `core/` is plain Python with no Home Assistant import |
| `frontend/` | The sidebar page (Lit), built into `custom_components/speldosa/frontend/speldosa-panel.js` |
| `firmware/` | ESPHome configs per board on shared packages; `ESPHOME_VERSION` pins the version |
| `installer/` | The browser installer page and its manifests; `improv_serial_test.py` for checking a box over USB |
| `core_tests/`, `tests/`, `frontend/test/` | Tests: the core, the integration on the Home Assistant test harness, the page |
| `docs/` | [Architecture](docs/architecture.md), [preparing a box for a beta family](docs/beta-delivery.md), the setup guides |

```bash
# Python: core and integration tests
uv venv -p 3.14 && uv pip install -r requirements-test.txt && python -m pytest

# Page: tests and build
cd frontend && npm ci --legacy-peer-deps && npm test && npm run build

# Firmware: validate every board, or compile one
firmware/build.sh
firmware/build.sh compile speldosa-phase2-pn532
```

### Boards

| Config | Board | Reader |
|---|---|---|
| `speldosa-phase2-pn532.yaml` | Phase 2 carrier, Seeed XIAO ESP32-C6 | PN532 module |
| `speldosa-phase2-pn7160.yaml` | Phase 2 carrier, Seeed XIAO ESP32-C6 | PN7160 module |
| `speldosa-phase3.yaml` | Phase 3 board, ESP32-C6-MINI-1 (draft, not built) | PN7160 on the board |
| `speldosa-phase1-d1mini.yaml` | Test box, Wemos D1 Mini (ESP8266) | PN532 module |

### Security defaults

- The image has no Wi-Fi credentials and no open fallback hotspot. Wi-Fi is set over USB (Improv serial) or
  Bluetooth (Improv BLE, allowed for two minutes after a tag is put on the box).
- The API uses encryption with no key in the image: Home Assistant sets a key for each box when it adds it.
- Open: the ESPHome OTA port has no password, and firmware updates are checked by MD5 only.

## Licence

Apache-2.0, see `LICENSE`. The firmware is built with ESPHome, whose runtime is GPLv3; this repository is the
source of every image we ship.
