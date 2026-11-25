"""Stage the static showcase using only the unpatched public font build."""

import argparse
import os
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
sys.path.insert(0, str(ROOT / "src"))
from codex_fonts.release import EPOCH, FAMILY_NAMES, STYLES, style_label, write_archive


def build(public: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as temp:
        stage = Path(temp) / "site"
        shutil.copytree(SITE / "src", stage)
        (stage / "fonts").mkdir()
        notice = (public / "licenses" / "IBM-Plex-OFL-1.1.txt").read_bytes()
        (stage / "OFL.txt").write_bytes(notice)
        shutil.copyfile(ROOT / "LICENSE-CODE.txt", stage / "LICENSE-CODE.txt")
        rules = []
        write_archive(public, stage / "Codex-typefaces.zip", int(os.environ.get("SOURCE_DATE_EPOCH", EPOCH)))
        for family in FAMILY_NAMES:
            for style, (weight, slant) in STYLES.items():
                stem = f"Codex{family}-{style}"
                shutil.copyfile(public / "web" / f"{stem}.woff2", stage / "fonts" / f"{stem}.woff2")
                rules.append(
                    f'@font-face {{ font-family: "Codex {family}"; '
                    f'src: url("fonts/{stem}.woff2") format("woff2"); '
                    f'font-style: {slant}; font-weight: {weight}; font-display: swap; }}'
                )
        options = "".join(
            f'<option value="{style}" data-weight="{weight}" data-slant="{slant}">{style_label(style)}</option>'
            for style, (weight, slant) in STYLES.items()
        )
        index = stage / "index.html"
        index.write_text(index.read_text().replace("<!-- style options -->", options))
        (stage / "fonts.css").write_text("\n".join(rules) + "\n", encoding="utf-8")
        if output.exists():
            shutil.rmtree(output)
        stage.rename(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", type=Path, default=ROOT / "dist/public",
                        help="dist/public from a canonical public build (default: this checkout)")
    args = parser.parse_args()
    try:
        build(args.public, ROOT / "build/showcase")
    except FileNotFoundError as error:
        parser.exit(1, f"Missing {error.filename}. Build the public edition with 'mise run public' first.\n")
    print("Staged build/showcase/ — serve this directory, not the repository or dist/.")
