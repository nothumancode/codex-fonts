"""Package the OFL text edition from 'mise run public' without extra dependencies."""

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from codex_fonts.release import ARCHIVE_NAME, EPOCH, write_archive


if __name__ == "__main__":
    output = ROOT / "build" / ARCHIVE_NAME
    write_archive(ROOT / "dist/public", output, int(os.environ.get("SOURCE_DATE_EPOCH", EPOCH)))
    print(output)
