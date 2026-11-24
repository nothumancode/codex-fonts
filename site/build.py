"""Stage the static showcase using only the unpatched public font build."""

import argparse
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
STYLES = (
    ("Regular", 400, "normal"),
    ("Italic", 400, "italic"),
    ("Bold", 700, "normal"),
    ("BoldItalic", 700, "italic"),
)


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
        with ZipFile(stage / "Codex-typefaces.zip", "w") as archive:
            archive.writestr(ZipInfo("OFL.txt"), notice, compress_type=ZIP_DEFLATED)
            for family in ("Mono", "Sans", "Serif"):
                for style, weight, slant in STYLES:
                    stem = f"Codex{family}-{style}"
                    web = (public / "web" / f"{stem}.woff2").read_bytes()
                    ttf = (public / "ttf" / f"{stem}.ttf").read_bytes()
                    if web[:4] != b"wOF2" or ttf[:4] != b"\x00\x01\x00\x00":
                        raise ValueError(f"Unexpected font container for {stem} in {public}")
                    (stage / "fonts" / f"{stem}.woff2").write_bytes(web)
                    archive.writestr(ZipInfo(f"{stem}.ttf"), ttf, compress_type=ZIP_DEFLATED)
                    rules.append(
                        f'@font-face {{ font-family: "Codex {family}"; '
                        f'src: url("fonts/{stem}.woff2") format("woff2"); '
                        f'font-style: {slant}; font-weight: {weight}; font-display: swap; }}'
                    )
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
