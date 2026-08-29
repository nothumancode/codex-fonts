"""Run broad FontBakery checks on the regular face of each final family."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    reports = ROOT / "build" / "fontbakery"
    reports.mkdir(parents=True, exist_ok=True)
    fonts = sorted((ROOT / "dist").glob("*/*-Regular.ttf"))
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
