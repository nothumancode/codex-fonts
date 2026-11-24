"""Build readable Codex Sans, Serif, and Mono Nerd Font derivatives.

The letterforms come from version-pinned IBM Plex releases under SIL OFL 1.1.
They are renamed before modification because ``Plex`` is a Reserved Font Name.
Nerd Fonts v3.5.1 is applied through its digest-pinned Docker patcher.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.ttProgram import Program

from .screen import apply_screen_cut

ROOT = Path(__file__).resolve().parents[2]
LOCK_PATH = ROOT / "sources.lock.json"
CACHE = ROOT / ".cache" / "font-sources"
BUILD = ROOT / "build" / "readable"
DIST = ROOT / "dist"
LICENSES = ROOT / "vendor" / "licenses"
STYLES = ("Regular", "Italic", "Bold", "BoldItalic")
FAMILIES = {
    "sans": {"base_family": "Codex Sans", "base_ps": "CodexSans", "final_family": "Codex Sans Nerd Font Propo", "final_ps": "CodexSansNerdFontPropo", "slug": "codex-sans-nf-propo"},
    "serif": {"base_family": "Codex Serif", "base_ps": "CodexSerif", "final_family": "Codex Serif Nerd Font Propo", "final_ps": "CodexSerifNerdFontPropo", "slug": "codex-serif-nf-propo"},
    "mono": {"base_family": "Codex Mono", "base_ps": "CodexMono", "final_family": "Codex Mono Nerd Font Mono", "final_ps": "CodexMonoNerdFontMono", "slug": "codex-mono-nf-mono"},
}
FIXED_UNIX_EPOCH = int(os.environ.get("SOURCE_DATE_EPOCH", "1787875200"))
FIXED_MAC_EPOCH = FIXED_UNIX_EPOCH + 2_082_844_800
WEB_ICON_CODEPOINTS = {ord(character) for character in "󰉋󰊢󰆍✓"}
WEB_CODEPOINTS = (
    set(range(0x20, 0x250))
    | set(range(0x2000, 0x2150))
    | set(range(0x2500, 0x2600))
    | set(range(0x2800, 0x2900))
    | WEB_ICON_CODEPOINTS
)
MONO_X_HEIGHT_LETTERS = "acemnorsuvwxz"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_lock() -> dict:
    return json.loads(LOCK_PATH.read_text())


def download(url: str, destination: Path, expected_sha256: str | None = None) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and (expected_sha256 is None or sha256(destination) == expected_sha256):
        return destination
    temporary = destination.with_suffix(destination.suffix + ".part")
    if temporary.exists():
        temporary.unlink()
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, temporary)
    if expected_sha256 and sha256(temporary) != expected_sha256:
        temporary.unlink()
        raise ValueError(f"Checksum mismatch for {url}")
    temporary.replace(destination)
    return destination


def set_name(font: TTFont, name_id: int, value: str) -> None:
    name_table = font["name"]
    name_table.names = [record for record in name_table.names if record.nameID != name_id]
    name_table.setName(value, name_id, 3, 1, 0x409)


def finish_binary(font: TTFont, win_ascent: int, win_descent: int) -> None:
    font["name"].names = [record for record in font["name"].names if record.platformID != 1]
    for private_table in ("PfEd", "FFTM", "DSIG"):
        if private_table in font:
            del font[private_table]
    os2, hhea = font["OS/2"], font["hhea"]
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = hhea.ascent, hhea.descent, hhea.lineGap
    os2.fsSelection |= 1 << 7
    os2.usWinAscent, os2.usWinDescent = win_ascent, win_descent
    prep = font["prep"].program
    smart_dropout = bytes.fromhex("B8 01 FF 85 B0 04 8D")
    original = prep.getBytecode()
    if not original.endswith(smart_dropout):
        prep.fromBytecode(original + smart_dropout)


def finalize_nerd_binary(font: TTFont) -> None:
    glyf = font["glyf"]
    minimum_y = 0
    maximum_y = 0
    for glyph_name in font.getGlyphOrder():
        glyph = glyf[glyph_name]
        if glyph.numberOfContours == 0:
            continue
        glyph.recalcBounds(glyf)
        minimum_y = min(minimum_y, glyph.yMin)
        maximum_y = max(maximum_y, glyph.yMax)
    finish_binary(font, maximum_y, -minimum_y)

    font["post"].formatType = 3.0
    font["post"].extraNames = []
    font["post"].mapping = {}


def normalize_names(font: TTFont, family: str, ps_family: str, style: str, *, nerd_version: str | None = None) -> None:
    label = "Bold Italic" if style == "BoldItalic" and not nerd_version else style
    full_name = family if style == "Regular" else f"{family} {label}"
    ps_name = f"{ps_family}-{style}"
    version = "Version 2.100"
    license_note = "This Font Software is licensed under the SIL Open Font License, Version 1.1."
    if nerd_version:
        version += f"; Nerd Fonts {nerd_version}"
        license_note += " See the bundled font and icon license notices."
    for name_id, value in {
        1: family,
        2: label,
        3: f"2.100;CDX2;{ps_name}",
        4: full_name,
        5: version,
        6: ps_name,
        13: license_note,
        14: "https://openfontlicense.org/open-font-license-official-text/",
        16: family,
        17: label,
    }.items():
        set_name(font, name_id, value)
    font["OS/2"].achVendID = "CDX2"
    font.recalcTimestamp = False
    font["head"].fontRevision = 2.100
    font["head"].created = FIXED_MAC_EPOCH
    font["head"].modified = FIXED_MAC_EPOCH
    if nerd_version:
        finalize_nerd_binary(font)


def align_mono_x_height(font: TTFont) -> None:
    """Give ordinary lowercase Mono letters one shared visual envelope.

    IBM Plex Mono uses optical overshoot on rounded lowercase outlines: for
    example, ``e`` spans -12..528 units while the flat-sided ``r`` spans
    0..516 units.  Codex Mono deliberately favors strict cell alignment, so
    enlarge every non-ascending, non-descending lowercase outline to the
    largest shared envelope instead of making rounded letters smaller.

    The source hints describe the original coordinates and can grid-fit the
    resized flat glyphs back to their old height.  Clear those glyph-local
    programs so rasterizers honor the normalized outlines at ordinary UI and
    terminal sizes.
    """
    glyf = font["glyf"]
    cmap = font.getBestCmap()
    x_height = font["OS/2"].sxHeight
    if not x_height:
        raise ValueError("Mono source font has no declared x-height")

    glyphs = []
    for character in MONO_X_HEIGHT_LETTERS:
        glyph_name = cmap[ord(character)]
        glyph = glyf[glyph_name]
        if glyph.isComposite() or glyph.numberOfContours <= 0:
            raise ValueError(f"Expected a simple outline for Mono {character!r}")
        glyph.expand(glyf)
        glyph.recalcBounds(glyf)
        glyphs.append((character, glyph))

    target_min = min(glyph.yMin for _, glyph in glyphs)
    target_max = max(glyph.yMax for _, glyph in glyphs)
    if not target_min < 0 < x_height < target_max:
        raise ValueError(
            f"Unexpected Mono lowercase envelope {target_min}..{target_max} "
            f"around x-height {x_height}"
        )
    target_height = target_max - target_min

    for character, glyph in glyphs:
        source_min = glyph.yMin
        source_max = glyph.yMax
        source_height = glyph.yMax - glyph.yMin
        if source_height <= 0:
            raise ValueError(f"Mono {character!r} has an empty vertical outline")
        if (source_min, source_max) != (target_min, target_max):
            scale = target_height / source_height
            for index, (x, y) in enumerate(glyph.coordinates):
                glyph.coordinates[index] = (
                    x,
                    round(target_min + (y - source_min) * scale),
                )
        glyph.program = Program()
        glyph.recalcBounds(glyf)
        if (glyph.yMin, glyph.yMax) != (target_min, target_max):
            raise ValueError(
                f"Could not align Mono {character!r}: "
                f"got {glyph.yMin}..{glyph.yMax}, "
                f"expected {target_min}..{target_max}"
            )


def fetch_and_prepare(lock: dict) -> dict[str, list[Path]]:
    prepared: dict[str, list[Path]] = {}
    LICENSES.mkdir(parents=True, exist_ok=True)
    for kind, source in lock["ibm_plex"].items():
        archive = download(source["url"], CACHE / f"ibm-plex-{kind}-{source['version']}.zip", source["sha256"])
        family = FAMILIES[kind]
        output_dir = BUILD / "unpatched" / kind
        output_dir.mkdir(parents=True, exist_ok=True)
        outputs: list[Path] = []
        with zipfile.ZipFile(archive) as bundle:
            license_data = bundle.read(f"{source['archive_root']}/LICENSE.txt")
            license_path = LICENSES / "IBM-Plex-OFL-1.1.txt"
            if not license_path.exists():
                license_path.write_bytes(license_data)
            for style in STYLES:
                member = f"{source['archive_root']}/fonts/complete/ttf/{source['source_prefix']}-{style}.ttf"
                font = TTFont(io.BytesIO(bundle.read(member)))
                normalize_names(font, family["base_family"], family["base_ps"], style)
                if kind == "mono":
                    align_mono_x_height(font)
                apply_screen_cut(font, kind, style)
                output = output_dir / f"{family['base_ps']}-{style}.ttf"
                font.save(output, reorderTables=True)
                outputs.append(output)
        prepared[kind] = outputs

    return prepared


def patch_stamp(inputs: list[Path], image: str, arguments: list[str]) -> str:
    material = "\n".join([image, *arguments, *(sha256(path) for path in inputs)])
    return hashlib.sha256(material.encode()).hexdigest()


def run_patcher(kind: str, inputs: list[Path], nerd: dict) -> list[Path]:
    output_dir = BUILD / "patched" / kind
    stamp_path = output_dir / ".stamp"
    arguments = ["--complete", "--careful", "--makegroups", "1"]
    arguments.append("--mono" if kind == "mono" else "--variable-width-glyphs")
    expected_stamp = patch_stamp(inputs, nerd["docker_image"], arguments)
    existing = sorted(output_dir.glob("*.ttf"))
    if stamp_path.exists() and stamp_path.read_text().strip() == expected_stamp and len(existing) == len(inputs):
        print(f"Reusing cached Nerd Font patch outputs for {kind}")
        return existing

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    input_dir = BUILD / "patch-input" / kind
    if input_dir.exists():
        shutil.rmtree(input_dir)
    input_dir.mkdir(parents=True)
    for path in inputs:
        shutil.copy2(path, input_dir / path.name)
    command = [
        "docker", "run", "--rm", "-e", "PN=4",
        "-v", f"{input_dir.resolve()}:/in",
        "-v", f"{output_dir.resolve()}:/out",
        nerd["docker_image"],
        *arguments,
    ]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = result.stdout.decode("utf-8", errors="replace")
    log_path = BUILD / f"font-patcher-{kind}.log"
    log_path.write_text(output)
    version_lines = [line for line in output.splitlines() if "Nerd Fonts Patcher" in line]
    if version_lines:
        print(version_lines[0])
    print(f"Nerd Font patch log: {log_path.relative_to(ROOT)}")
    outputs = sorted(output_dir.glob("*.ttf"))
    if len(outputs) != len(inputs):
        raise RuntimeError(f"Nerd patcher produced {len(outputs)} files for {kind}; expected {len(inputs)}")
    stamp_path.write_text(expected_stamp + "\n")
    return outputs


def font_style(font: TTFont) -> str:
    record = font["name"].getName(17, 3, 1, 0x409) or font["name"].getName(2, 3, 1, 0x409)
    if not record:
        raise ValueError("Patched font has no style name")
    value = record.toUnicode().replace(" ", "")
    aliases = {"Roman": "Regular", "BoldItalic": "BoldItalic", "Italic": "Italic", "Bold": "Bold", "Regular": "Regular"}
    if value not in aliases:
        raise ValueError(f"Unexpected patched font style: {value}")
    return aliases[value]


def save_web_subset(ttf_path: Path, output: Path) -> None:
    font = TTFont(ttf_path, recalcTimestamp=False)
    options = subset.Options()
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.notdef_outline = True
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=WEB_CODEPOINTS)
    subsetter.subset(font)
    font.flavor = "woff2"
    output.parent.mkdir(parents=True, exist_ok=True)
    font.save(output, reorderTables=True)


def fresh_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def package_public(prepared: dict[str, list[Path]]) -> None:
    public = DIST / "public"
    fresh_directory(public)
    for folder in ("ttf", "web", "licenses"):
        (public / folder).mkdir(parents=True, exist_ok=True)
    for paths in prepared.values():
        fonts = [TTFont(source, recalcTimestamp=False) for source in paths]
        win_ascent = max(font["head"].yMax for font in fonts)
        win_descent = max(-font["head"].yMin for font in fonts)
        for source, font in zip(paths, fonts, strict=True):
            finish_binary(font, win_ascent, win_descent)
            font.save(public / "ttf" / source.name)
            font.flavor = "woff2"
            font.save(public / "web" / source.with_suffix(".woff2").name)
    shutil.copy2(LICENSES / "IBM-Plex-OFL-1.1.txt", public / "licenses")
    shutil.copy2(ROOT / "docs" / "PUBLIC-FONTS.txt", public / "README.txt")


def package_fonts(patched: dict[str, list[Path]], nerd_version: str) -> list[Path]:
    DIST.mkdir(exist_ok=True)
    fresh_directory(DIST / "web")
    outputs: list[Path] = []
    for kind, paths in patched.items():
        family = FAMILIES[kind]
        family_dir = DIST / family["slug"]
        fresh_directory(family_dir)
        seen_styles: set[str] = set()
        for patched_path in paths:
            font = TTFont(patched_path)
            style = font_style(font)
            seen_styles.add(style)
            normalize_names(font, family["final_family"], family["final_ps"], style, nerd_version=nerd_version)
            ttf_path = family_dir / f"{family['final_ps']}-{style}.ttf"
            font.save(ttf_path, reorderTables=True)
            outputs.append(ttf_path)

            webfont = TTFont(ttf_path, recalcTimestamp=False)
            webfont.flavor = "woff2"
            woff2_path = ttf_path.with_suffix(".woff2")
            webfont.save(woff2_path, reorderTables=True)
            outputs.append(woff2_path)

            web_subset_path = DIST / "web" / f"{family['base_ps']}-{style}.woff2"
            save_web_subset(ttf_path, web_subset_path)
            outputs.append(web_subset_path)
        if seen_styles != set(STYLES):
            raise RuntimeError(f"Missing packaged styles for {kind}: {set(STYLES) - seen_styles}")

    shutil.copy2(LOCK_PATH, DIST / "sources.lock.json")
    fresh_directory(DIST / "licenses")
    shutil.copytree(LICENSES, DIST / "licenses", dirs_exist_ok=True)
    manifest = DIST / "MANIFEST.txt"
    manifest.write_text("\n".join(f"dist/{path.relative_to(DIST)}" for path in outputs) + "\n")
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", action="store_true", help="Build only the OFL text faces (no icon patch or Docker).")
    args = parser.parse_args()
    lock = load_lock()
    prepared = fetch_and_prepare(lock)
    if args.public:
        package_public(prepared)
        print("Built 12 OFL text faces as TTF and WOFF2 in dist/public")
        return
    nerd = lock["nerd_fonts"]
    download(nerd["license_url"], LICENSES / f"Nerd-Fonts-{nerd['version']}-LICENSE.txt")
    download(nerd["glyph_licenses_url"], LICENSES / f"Nerd-Fonts-{nerd['version']}-GLYPH-LICENSES.md")
    patched = {kind: run_patcher(kind, paths, nerd) for kind, paths in prepared.items()}
    outputs = package_fonts(patched, nerd["version"])
    print(f"Built {len(outputs)} readable font files across 3 families and 4 styles")


if __name__ == "__main__":
    main()
