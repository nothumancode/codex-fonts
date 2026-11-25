"""Package the OFL text edition from `mise run public` for download."""

import os
import time
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "dist/public"
OUTPUT = ROOT / "build/Codex-Fonts.zip"


if __name__ == "__main__":
    members = ["README.txt", "licenses/IBM-Plex-OFL-1.1.txt"]
    for family in ("Mono", "Sans", "Serif"):
        for style in ("Regular", "Italic", "Bold", "BoldItalic"):
            stem = f"Codex{family}-{style}"
            members.extend((f"ttf/{stem}.ttf", f"web/{stem}.woff2"))

    timestamp = time.gmtime(int(os.environ["SOURCE_DATE_EPOCH"]))[:6]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(OUTPUT, "w") as archive:
        for name in sorted(members):
            entry = ZipInfo(name, timestamp)
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, (PUBLIC / name).read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=6)
    print(OUTPUT)
