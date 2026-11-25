"""Run FontBakery on each complete static family, including its style-link groups."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from .build import FAMILIES
from .release import STYLES


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", action="store_true", help="Check the OFL-only text edition")
    args = parser.parse_args()
    reports = ROOT / "build" / "fontbakery"
    reports.mkdir(parents=True, exist_ok=True)
    failed = False
    for family in FAMILIES.values():
        prefix = family["base_ps" if args.public else "final_ps"]
        folder = ROOT / "dist" / ("public/ttf" if args.public else family["slug"])
        fonts = [folder / f"{prefix}-{style}.ttf" for style in STYLES]
        report = reports / f"{prefix}.txt"
        result = subprocess.run(
            ["fontbakery", "check-universal", "--succinct", "--loglevel", "WARN", *map(str, fonts)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        report.write_text(result.stdout)
        print(f"FontBakery {prefix}: exit {result.returncode}; report {report.relative_to(ROOT)}", flush=True)
        failed |= result.returncode != 0
    if failed:
        raise SystemExit("FontBakery reported one or more production failures")


if __name__ == "__main__":
    main()
