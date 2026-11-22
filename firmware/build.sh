#!/usr/bin/env bash
# Validate (default) or compile every board config with the pinned ESPHome version.
#   ./build.sh            validate all boards
#   ./build.sh compile    compile all boards, firmware in .esphome/build/<name>/
#   ./build.sh compile speldosa-phase2-pn532   one board
set -euo pipefail
cd "$(dirname "$0")"
ESPHOME_VERSION="$(cat ESPHOME_VERSION)"
mode="${1:-config}"
shift || true
boards=("$@")
if [ ${#boards[@]} -eq 0 ]; then
  boards=(speldosa-phase1-d1mini speldosa-phase2-pn532 speldosa-phase2-pn7160 speldosa-phase3)
fi
esphome() {
  if command -v uvx >/dev/null; then
    uvx --from "esphome==${ESPHOME_VERSION}" esphome "$@"
  else
    python -m esphome "$@"
  fi
}
status=0
for b in "${boards[@]}"; do
  if esphome "$mode" "$b.yaml" > ".log-$b.txt" 2>&1; then
    echo "$b: $mode OK"
    if [ "$mode" = compile ]; then
      # Each board builds in .esphome/build/<board_id> (core.yaml build_path).
      id="${b#speldosa-}"
      out="../dist/$id"
      mkdir -p "$out"
      # ESP-IDF builds (ESP32-C6) land in build/, PlatformIO builds (ESP8266) in .pioenvs/speldosa/.
      img=".esphome/build/$id/build"
      [ -f "$img/firmware.factory.bin" ] || img=".esphome/build/$id/.pioenvs/speldosa"
      cp "$img/firmware.factory.bin" "$out/speldosa.factory.bin"
      cp "$img/firmware.ota.bin" "$out/speldosa.ota.bin"
    fi
  else
    echo "$b: $mode FAILED (last lines of .log-$b.txt)"
    sed 's/\x1b\[[0-9;]*m//g' ".log-$b.txt" | tail -25
    status=1
  fi
done
exit $status
