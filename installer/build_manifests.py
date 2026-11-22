"""Write one manifest.json per board next to its images in dist/<board>/.

The same file serves the ESP Web Tools install button (builds[].parts) and the firmware's
`update: platform: http_request` (builds[].ota), as ESPHome documents for managed updates.

    python installer/build_manifests.py 0.1.0
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def main(version: str) -> int:
    boards = sorted(p for p in DIST.iterdir() if (p / "speldosa.factory.bin").exists())
    if not boards:
        print("No images in dist/. Run firmware/build.sh compile first.", file=sys.stderr)
        return 1
    for board in boards:
        manifest = {
            "name": f"Speldosa ({board.name})",
            "version": version,
            "home_assistant_domain": "esphome",
            "new_install_prompt_erase": True,
            "builds": [
                {
                    "chipFamily": "ESP32-C6",
                    "parts": [{"path": "speldosa.factory.bin", "offset": 0}],
                    "ota": {
                        "path": "speldosa.ota.bin",
                        "md5": md5(board / "speldosa.ota.bin"),
                        "summary": f"Speldosa {version}",
                    },
                }
            ],
        }
        (board / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"{board.name}: manifest.json for {version}")
    shutil.copy(ROOT / "installer" / "index.html", DIST / "index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "dev"))
