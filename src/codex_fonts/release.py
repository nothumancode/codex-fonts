"""Public release contract. Kept stdlib-only for the standalone site and ZIP builders."""

from hashlib import sha256
from pathlib import Path
from time import gmtime
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


FONT_VERSION = "2.200"
ARCHIVE_NAME = f"Codex-Fonts-{FONT_VERSION}.zip"
EPOCH = 1787875200
FAMILY_NAMES = ("Mono", "Sans", "Serif")
STYLES = {
    "Regular": (400, "normal"),
    "Italic": (400, "italic"),
    "Medium": (500, "normal"),
    "MediumItalic": (500, "italic"),
    "Bold": (700, "normal"),
    "BoldItalic": (700, "italic"),
}


def style_label(style):
    return style.replace("Italic", " Italic").strip()


def write_archive(public: Path, output: Path, epoch: int = EPOCH) -> None:
    members = ["README.txt", "licenses/IBM-Plex-OFL-1.1.txt", "sources.json"]
    for family in FAMILY_NAMES:
        for style in STYLES:
            stem = f"Codex{family}-{style}"
            members.extend((f"ttf/{stem}.ttf", f"web/{stem}.woff2"))

    def entry(name):
        info = ZipInfo(name, gmtime(epoch)[:6])
        info.create_system = 3
        info.external_attr = 0o100644 << 16
        return info

    checksums = []
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w") as archive:
        for name in sorted(members):
            data = (public / name).read_bytes()
            magic = {".ttf": b"\x00\x01\x00\x00", ".woff2": b"wOF2"}.get(Path(name).suffix)
            if magic and not data.startswith(magic):
                raise ValueError(f"Unexpected font container for {name} in {public}")
            archive.writestr(entry(name), data, compress_type=ZIP_DEFLATED, compresslevel=6)
            checksums.append(f"{sha256(data).hexdigest()}  {name}\n")
        archive.writestr(entry("SHA256SUMS"), "".join(checksums), compress_type=ZIP_DEFLATED, compresslevel=6)
