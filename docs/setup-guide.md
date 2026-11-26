# Speldosa setup guide

Speldosa is a music box for children. Put a card on the box and the music, story or audiobook linked to it plays
on a speaker in the room. Lift the card and it pauses. Put it back and it continues.

On svenska: [setup-guide.sv.md](setup-guide.sv.md).

## Requirements

| | |
|---|---|
| Home Assistant | 2026.10 or later, with HACS installed |
| Music Assistant | Set up in Home Assistant, with your music service (for example Spotify) and your speakers in it |
| A computer | With Chrome or Edge, for the Wi-Fi step. iPhone and iPad do not work for this step |
| A USB-C cable | One that carries data. Many cables only charge |
| Wi-Fi | A 2.4 GHz network. Speldosa does not use 5 GHz |

The box arrives with its software already on it. Setting it up takes about 15 minutes.

## 1. Connect the box to Wi-Fi

1. Plug the box into the computer with the USB-C cable.
2. Open <https://web.esphome.io> in Chrome or Edge and select **Connect**.
3. Pick the box from the list. Its name contains "USB JTAG" or "ESP32".
4. Choose the option to set up Wi-Fi (not Install: the software is already on the box), pick your 2.4 GHz network
   and enter its password.
5. When it says the box is connected, unplug it and plug it into its USB power supply in the child's room.

The light pulses orange while the box has no Wi-Fi and pulses blue while it waits for Home Assistant.

## 2. Add the box to Home Assistant

1. Home Assistant shows **New devices discovered: Speldosa** under Settings, Devices and services. Select **Add**.
2. If nothing shows after a minute: Settings, Devices and services, **Add integration**, ESPHome, and enter the
   box's address from your router.
3. When the box is added, its light turns steady green.

## 3. Install the Speldosa integration

1. In Home Assistant open **HACS**, the menu at the top right, **Custom repositories**.
2. Add `https://github.com/andreas0480/speldosa-home-assistant` with the type **Integration**.
3. Search HACS for **Speldosa**, select **Download**, and restart Home Assistant when it asks.
4. Settings, Devices and services, **Add integration**, **Speldosa**. Pick the box and the speaker it should
   play on.

A **Speldosa** page appears in the sidebar.

## 4. Link the cards

1. Put a new card on the box and leave it there. The light blinks pink and the box gives two short sounds:
   the card has no music yet.
2. Open **Speldosa** in the sidebar. A blue banner says a new card is on the box. Select **Link this card**.
3. Type what the card should play, for example "Bamse" or "Die drei ???". The results come from your music
   service. If nothing comes back, Spotify may be busy: wait half a minute and try again.
4. Pick a result. On the right, choose how it plays (below) and select **Link card**. It starts playing.

Repeat for each card.

## Play choices

| Choice | Best for | What happens |
|---|---|---|
| A random album each time | Audiobook series where each album is one episode (Die drei ???, Bamse, Bibi Blocksberg) | Plays one whole album, in order. Every album you chose is heard once before any repeats |
| The next album each time | Series heard in order | Plays the albums one after another, in episode-number order |
| From the start | Albums, playlists, songs | Starts at the beginning each time |
| In random order | Playlists, albums, an artist's music | Shuffles |
| Continue where it stopped | Audiobooks | Always continues where it was. Heard to the end, it starts over |
| A random or the next episode | Podcasts | Like the album choices, one episode at a time |

For the two album choices the page lists the artist's albums. Advent calendars, soundtracks, minis and similar are
unticked, and when most albums carry an episode number, only numbered ones are ticked. Tick or untick as you like.

Lifted halfway through, an album continues from that spot when the card comes back, however much later. The card
moves on to a new album only when the album has been heard to the end.

## Lifting and putting back

- Lift the card: the music pauses.
- Put it back within 15 minutes: it continues where it was, whatever the card's choice.
- After that the card's choice decides, as in the table above.

The 15 minutes, the start volume (40 %) and whether the box leaves a speaker group first are set per box under
Settings, Devices and services, Speldosa, **Configure**.

## Light and sound

| Light | Meaning |
|---|---|
| Steady green | Ready, no card on it |
| Steady yellow | A card is on it and playing |
| Yellow, half bright | Paused |
| Short white flash | A card was read |
| Pink blink, two sounds | The card has no music yet: link it on the Speldosa page |
| Orange pulse | No Wi-Fi |
| Blue pulse | No connection to Home Assistant |
| Red blink | Something went wrong: Home Assistant shows a notification with the reason |

## Troubleshooting

| What you see | What to do |
|---|---|
| web.esphome.io does not list the box | Try another USB-C cable; many only charge. Use Chrome or Edge on a computer |
| Orange pulse after the Wi-Fi step | The network is 5 GHz only, or the password was wrong. Repeat step 1 |
| Blue pulse | Home Assistant has not added the box yet (step 2) |
| Red blink and "could not play" | The notification says why. Common causes: the speaker is off, or the music service is playing on another speaker. Spotify plays on one speaker at a time |
| Red blink and "Reader problem" on the page | Unplug the box for a few seconds and plug it back in |
| Search is slow or finds nothing | Spotify is limiting Music Assistant's searches ("rate limit"; Music Assistant's log says "Spotify Rate Limiter" or "asked to wait ... seconds"). Wait a minute and search again. For good: create your own free Spotify developer app and enter its Client ID in Music Assistant, Settings, Providers, Spotify; with the shared default ID the limit is reached quickly. This fixed it on our own setup (2026-11-26) |
| The card plays the wrong thing | Speldosa page, the card, **Change** |

## Updates

New versions of the integration show up in HACS. New firmware for the box shows up as an update under the box's
device page in Home Assistant.
