"""Constants for the Speldosa integration."""

from __future__ import annotations

DOMAIN = "speldosa"
MA_DOMAIN = "music_assistant"
ESPHOME_DOMAIN = "esphome"

# ESPHome sets the device manufacturer from the firmware's project name "anjobe.speldosa".
MANUFACTURER = "anjobe"

CONF_DEVICE_ID = "device_id"
CONF_PLAYER = "player"
CONF_RESUME_WINDOW = "resume_window_min"
DEFAULT_RESUME_WINDOW_MIN = 15
# Start volume in percent when a new piece starts (0: leave the volume alone), and whether to leave a group.
CONF_START_VOLUME = "start_volume"
DEFAULT_START_VOLUME = 40
CONF_SOLO = "solo"
DEFAULT_SOLO = True

# Entity names in the firmware (firmware/packages/core.yaml).
CARD_ENTITY_NAME = "Card"
STATUS_ENTITY_NAME = "Status"
READER_PROBLEM_NAME = "Reader problem"
NO_CARD = "none"

STATUS_ERROR = "error"

# Search: wait for this many characters, keep answers this long, ask for this many per type.
SEARCH_MIN_CHARS = 3
SEARCH_CACHE_S = 600
SEARCH_LIMIT = 8

# Episode lists for "a random episode each time" are refreshed after this long.
EPISODES_MAX_AGE_S = 7 * 24 * 3600
EPISODES_MAX = 300
BROWSE_TIMEOUT_S = 60

PANEL_URL_PATH = "speldosa"
PANEL_COMPONENT = "speldosa-panel"
STATIC_URL = "/speldosa_static"
IMAGE_URL = "/api/speldosa/image"

EVENT_UNKNOWN_CARD = f"{DOMAIN}_unknown_card"
EVENT_CARD = f"{DOMAIN}_card"
SIGNAL_CHANGED = f"{DOMAIN}_changed"
