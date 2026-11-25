from pathlib import Path
from hashlib import sha256

import uharfbuzz as hb
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
STYLES = ("Regular", "Italic", "Medium", "MediumItalic", "Bold", "BoldItalic")
FAMILIES = {
    "sans": ("codex-sans-nf-propo", "CodexSansNerdFontPropo", "Codex Sans Nerd Font Propo"),
    "serif": ("codex-serif-nf-propo", "CodexSerifNerdFontPropo", "Codex Serif Nerd Font Propo"),
    "mono": ("codex-mono-nf-mono", "CodexMonoNerdFontMono", "Codex Mono Nerd Font Mono"),
}
NERD_PROBES = {0xE0A0, 0xE0B0, 0xE5FF, 0xEA85, 0xF09B, 0xF024B}
SHAPING_TEXT = "0O 1Il| 5S 2Z 8B rn m vv w office affinity ÀÉÖ æ œ ß ñ — ‘quotes’ … € ™ Á ë"
MONO_X_HEIGHT_LETTERS = "acemnorsuvwxz"


def font_path(kind: str, style: str = "Regular", extension: str = "ttf") -> Path:
    slug, ps_family, _ = FAMILIES[kind]
    return ROOT / "dist" / slug / f"{ps_family}-{style}.{extension}"


def shape(path: Path, text: str):
    face = hb.Face(path.read_bytes())
    font = hb.Font(face)
    font.scale = (face.upem, face.upem)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer, {"kern": True, "liga": True})
    return buffer.glyph_infos, buffer.glyph_positions


def english_name(font: TTFont, name_id: int) -> str:
    record = font["name"].getName(name_id, 3, 1, 0x409)
    assert record is not None
    return record.toUnicode()


def test_all_styles_and_formats_exist():
    for kind in FAMILIES:
        for style in STYLES:
            assert font_path(kind, style).exists()
            assert font_path(kind, style, "woff2").exists()


def test_names_versions_and_license_are_collision_safe():
    for kind, (_, _, family_name) in FAMILIES.items():
        for style in STYLES:
            font = TTFont(font_path(kind, style))
            medium = "Medium" in style
            label = style.replace("Italic", " Italic").strip()
            assert english_name(font, 1) == (family_name + " Med" if medium else family_name)
            assert english_name(font, 2) == (("Italic" if "Italic" in style else "Regular") if medium else label)
            assert english_name(font, 16) == family_name and english_name(font, 17) == label
            assert english_name(font, 5).startswith("Version 2.200;")
            assert font["OS/2"].usWeightClass == (500 if medium else 700 if "Bold" in style else 400)
            assert bool(font["head"].macStyle & 2) == ("Italic" in style)
            assert (font["post"].underlinePosition, font["post"].underlineThickness) == {
                "mono": (-140, 60), "sans": (-95, 60), "serif": (-78, 44),
            }[kind]
            assert "Nerd Fonts 3.5.1" in english_name(font, 5)
            assert "SIL Open Font License" in english_name(font, 13)
            user_facing = " ".join(english_name(font, name_id) for name_id in (1, 4, 6, 16))
            assert "Plex" not in user_facing
            assert "IBM" not in user_facing


def test_readable_unicode_and_nerd_icon_coverage():
    required_text = set(range(0x20, 0x7F)) | {0xA0, 0xC0, 0xC9, 0xD6, 0xDF, 0xE6, 0xF1, 0x153, 0x2014, 0x2026, 0x20AC}
    for kind in FAMILIES:
        cmap = TTFont(font_path(kind)).getBestCmap()
        assert required_text | NERD_PROBES <= set(cmap)


def test_harfbuzz_shapes_prose_without_notdef():
    for kind in FAMILIES:
        for style in STYLES:
            infos, _ = shape(font_path(kind, style), SHAPING_TEXT)
            assert infos
            assert all(info.codepoint != 0 for info in infos)


def test_sans_and_serif_are_proportional():
    for kind in ("sans", "serif"):
        font = TTFont(font_path(kind))
        cmap = font.getBestCmap()
        widths = {font["hmtx"][cmap[ord(character)]][0] for character in "ilMW0m"}
        assert len(widths) >= 3
        assert font["post"].isFixedPitch == 0


def test_mono_ascii_boxes_and_nerd_icons_share_one_cell():
    for style in STYLES:
        font = TTFont(font_path("mono", style))
        cmap = font.getBestCmap()
        codepoints = set(range(0x20, 0x7F)) | set(range(0x2500, 0x2580)) | set(range(0x2580, 0x25A0)) | NERD_PROBES
        widths = {font["hmtx"][cmap[codepoint]][0] for codepoint in codepoints}
        assert len(widths) == 1
        cell_width = widths.pop()
        assert font["post"].isFixedPitch != 0
        assert font["OS/2"].panose.bProportion == 9
        assert font["OS/2"].xAvgCharWidth == cell_width
        assert font["hhea"].advanceWidthMax == cell_width


def test_mono_lowercase_x_height_is_exactly_aligned_in_every_style():
    for style in STYLES:
        paths = (
            font_path("mono", style),
            font_path("mono", style, "woff2"),
            ROOT / "dist" / "web" / f"CodexMono-{style}.woff2",
        )
        for path in paths:
            font = TTFont(path)
            cmap = font.getBestCmap()
            glyf = font["glyf"]
            expected_bounds = (-12, font["OS/2"].sxHeight + 12)
            bounds = set()
            for character in MONO_X_HEIGHT_LETTERS:
                glyph = glyf[cmap[ord(character)]]
                glyph.recalcBounds(glyf)
                bounds.add((glyph.yMin, glyph.yMax))
                assert not glyph.program.getBytecode(), (path, character)
            assert bounds == {expected_bounds}, path


def test_mono_shaped_advances_stay_on_cell_grid():
    text = "0O 1Il| rn m │  main  ✓ 42"
    for style in STYLES:
        infos, positions = shape(font_path("mono", style), text)
        font = TTFont(font_path("mono", style))
        cmap = font.getBestCmap()
        cell_width = font["hmtx"][cmap[ord("M")]][0]
        assert all(info.codepoint != 0 for info in infos)
        assert sum(position.x_advance for position in positions) == len(text) * cell_width


def test_woff2_has_cmap_and_name_parity():
    for kind in FAMILIES:
        ttf = TTFont(font_path(kind))
        woff2 = TTFont(font_path(kind, extension="woff2"))
        assert ttf.getBestCmap() == woff2.getBestCmap()
        assert english_name(ttf, 1) == english_name(woff2, 1)


def test_showcase_web_subsets_are_small_and_usable():
    for kind, (_, _, family_name) in FAMILIES.items():
        filename = {"sans": "CodexSans", "serif": "CodexSerif", "mono": "CodexMono"}[kind]
        path = ROOT / "dist" / "web" / f"{filename}-Regular.woff2"
        assert path.exists()
        assert path.stat().st_size < 150_000
        font = TTFont(path)
        assert set(range(0x20, 0x7F)) | NERD_PROBES <= set(font.getBestCmap())
        assert english_name(font, 1) == family_name


def test_every_private_cut_keeps_its_full_repertoire_and_real_woff2s():
    coverage = {
        "mono": "ffe159d30343232c15007450a1a6cbb4d1d3520a110eaa6fadbcffcbd63c72af",
        "sans": "235b4244c28861fb8f28ede035cb5f6bcbce3f22ec3a17ed19fcc5def5747f05",
        "serif": "e54e12a6f3798801b3156b77d073df7c1f12cc6e02c77210d7d22358e690ffa8",
    }
    for kind in FAMILIES:
        for style in STYLES:
            font = TTFont(font_path(kind, style))
            cmap = font.getBestCmap()
            assert sha256(b"".join(cp.to_bytes(4, "big") for cp in sorted(cmap))).hexdigest() == coverage[kind]
            full = TTFont(font_path(kind, style, "woff2"))
            subset = TTFont(ROOT / "dist" / "web" / f"Codex{kind.title()}-{style}.woff2")
            assert full.flavor == subset.flavor == "woff2"
            assert cmap == full.getBestCmap()
            assert NERD_PROBES <= set(subset.getBestCmap()) <= set(cmap)
            master = TTFont(ROOT / "build" / "readable" / "unpatched" / kind / f"Codex{kind.title()}-{style}.ttf")
            assert font["prep"].program.getBytecode().startswith(master["prep"].program.getBytecode())
            assert (font["hhea"].ascent, font["hhea"].descent, font["hhea"].lineGap) == (1025, -275, 0)
            if kind == "mono":
                assert all(font["hmtx"][name][0] == 600 for name in cmap.values())
                _, positions = shape(font_path(kind, style), "q\u0323")
                assert [p.x_advance for p in positions] == [600, 0]
