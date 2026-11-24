"""Run FontBakery's universal profile on each edition's regular faces."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", action="store_true", help="Check the OFL-only text edition")
    args = parser.parse_args()
    reports = ROOT / "build" / "fontbakery"
    reports.mkdir(parents=True, exist_ok=True)
    pattern = "public/ttf/*-Regular.ttf" if args.public else "codex-*/*-Regular.ttf"
    fonts = sorted((ROOT / "dist").glob(pattern))
    if len(fonts) != 3:
        raise SystemExit(f"Expected 3 regular TTFs, found {len(fonts)}")
    failed = False
    for font in fonts:
        report = reports / f"{font.stem}.txt"
        result = subprocess.run(
            ["fontbakery", "check-universal", "--succinct", "--loglevel", "WARN", str(font)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        report.write_text(result.stdout)
        print(f"FontBakery {font.name}: exit {result.returncode}; report {report.relative_to(ROOT)}")
        failed |= result.returncode != 0
    if failed:
        raise SystemExit("FontBakery reported one or more production failures")


if __name__ == "__main__":
    main()
