# Preparing a box for a beta family

How a Speldosa box is made ready before it is handed over, so that the family does every step a buyer would:
Wi-Fi, adding the box to Home Assistant, installing the integration, linking cards. The family then follows the
[setup guide](setup-guide.md) ([svenska](setup-guide.sv.md)).

## Base image

A box leaves with the release firmware and nothing else: no Wi-Fi network, no Home Assistant key, no fallback
hotspot. The family's Home Assistant sets its own key when it adds the box.

A new Seeed XIAO ESP32-C6 arrives with Seeed's demo firmware, which drops off USB within seconds. Hold BOOT while
plugging it in so that it stays in the bootloader for flashing.

### Flash it

Build the image for the board (phase 2 carrier with a PN532 reader shown):

```bash
firmware/build.sh compile speldosa-phase2-pn532
# images: dist/phase2-pn532/speldosa.factory.bin (whole flash) and speldosa.ota.bin (updates)
```

Erase the whole flash first, so that no Wi-Fi details or keys from testing remain, then write the factory image:

```bash
esptool.py --port /dev/ttyACM0 erase_flash
esptool.py --port /dev/ttyACM0 write_flash 0x0 dist/phase2-pn532/speldosa.factory.bin
```

### Check it

```bash
python3 installer/improv_serial_test.py /dev/ttyACM0 info
```

Expected: Improv state "ready" (not provisioned), device info `anjobe.speldosa` with the release version and
ESP32-C6. Do not send Wi-Fi: that is the family's first step.

Then put a card on it: the box reads it (white flash and a sound) even without Wi-Fi.

## Box contents

| Item | Note |
|---|---|
| The box | Base image as above |
| USB-C data cable | A charge-only cable makes the Wi-Fi step fail |
| USB power supply | 5 V; any phone charger with USB-C or USB-A |
| Cards | NTAG213 or NTAG215 cards or stickers. Mifare Classic cards also read |
| The setup guide | A link to `docs/setup-guide.sv.md` or the English one |

## Family prerequisites

Home Assistant 2026.10 or later with HACS, Music Assistant with their music service and speakers, a computer
with Chrome or Edge, and a 2.4 GHz Wi-Fi network. See the setup guide.

## Record per box

Keep for each box handed over: its name (`speldosa-` and the last six characters of its MAC), the board, the
firmware version, the date and the family. Feedback is collected in person.
