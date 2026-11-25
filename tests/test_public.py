from io import BytesIO
from itertools import product
from zipfile import ZipFile

import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont

from codex_fonts import build


PUBLIC = build.DIST / "public"


def shape(font, text, **features):
    data = BytesIO()
    font.save(data)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb.Font(hb.Face(data.getvalue())), buf, features)
    return [font.getGlyphName(g.codepoint) for g in buf.glyph_infos]


def outline(font, name):
    return font["glyf"][name].getCoordinates(font["glyf"])


@pytest.fixture(scope="module", params=product(build.FAMILIES, build.STYLES), ids=lambda p: "-".join(p))
def cut(request):
    kind, style = request.param
    spec = build.load_lock()["ibm_plex"][kind]
    with ZipFile(build.CACHE / f"ibm-plex-{kind}-{spec['version']}.zip") as bundle:
        original = TTFont(BytesIO(bundle.read(
            f"{spec['archive_root']}/fonts/complete/ttf/{spec['source_prefix']}-{style}.ttf"
        )))
        assert bundle.read(f"{spec['archive_root']}/LICENSE.txt") == (
            PUBLIC / "licenses" / "IBM-Plex-OFL-1.1.txt"
        ).read_bytes()
    stem = f"Codex{kind.title()}-{style}"
    return kind, style, original, TTFont(PUBLIC / "ttf" / f"{stem}.ttf"), TTFont(PUBLIC / "web" / f"{stem}.woff2")


def test_public_edition_matches_licensed_source(cut):
    kind, style, original, font, web = cut
    cmap, source = font.getBestCmap(), original.getBestCmap()
    assert cmap.keys() == source.keys()
    assert font.getGlyphOrder() == original.getGlyphOrder()
    assert {0xE0A0, 0xE0B0, 0xF09B}.isdisjoint(cmap)
    assert web.flavor == "woff2" and web.getBestCmap() == cmap
    assert web["hmtx"].metrics == font["hmtx"].metrics
    assert all(font["hmtx"][name][0] == original["hmtx"][source[cp]][0] for cp, name in cmap.items())
    for binary in (font, web):
        names = binary["name"]
        family = f"Codex {kind.title()}"
        medium = "Medium" in style
        label = style.replace("Italic", " Italic").strip()
        assert names.getDebugName(1) == (family + " Medium" if medium else family)
        assert names.getDebugName(2) == (("Italic" if "Italic" in style else "Regular") if medium else label)
        assert names.getDebugName(16) == family and names.getDebugName(17) == label
        assert names.getDebugName(6) == f"Codex{kind.title()}-{style}"
        assert names.getDebugName(3) == "2.200;CDX2;" + names.getDebugName(6)
        for name_id in (0, 8, 9):
            assert names.getDebugName(name_id) == original["name"].getDebugName(name_id)
        assert "SIL Open Font License" in names.getDebugName(13)
        assert names.getDebugName(5) == "Version 2.200"
        assert not any(r.platformID == 1 for r in names.names)
        assert abs(binary["head"].fontRevision - 2.2) < 0.0001
        assert binary["OS/2"].usWeightClass == (500 if medium else 700 if "Bold" in style else 400)
        assert binary["head"].macStyle == original["head"].macStyle
        assert binary["post"].italicAngle == original["post"].italicAngle
        assert bool(binary["OS/2"].fsSelection & (1 << 5)) == ("Bold" in style)
        assert bool(binary["OS/2"].fsSelection & 1) == ("Italic" in style)
        assert bool(binary["OS/2"].fsSelection & (1 << 6)) == (style in ("Regular", "Medium"))
        assert "fvar" not in binary
        stat = binary["STAT"].table
        assert [axis.AxisTag for axis in stat.DesignAxisRecord.Axis] == ["wght", "ital"]
        axis_values = stat.AxisValueArray.AxisValue
        assert [v.Value for v in axis_values] == [binary["OS/2"].usWeightClass, int("Italic" in style)]
        if "Italic" not in style:
            assert axis_values[1].LinkedValue == 1 and axis_values[1].Flags == 2
        assert bool(binary["post"].isFixedPitch) == (kind == "mono")
        assert (binary["post"].underlinePosition, binary["post"].underlineThickness) == {
            "mono": (-140, 60), "sans": (-95, 60), "serif": (-78, 44),
        }[kind]
        assert binary["prep"].program.getBytecode().startswith(original["prep"].program.getBytecode())
        os2 = binary["OS/2"]
        assert (os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap) == (1025, -275, 0)
        assert (binary["hhea"].ascent, binary["hhea"].descent, binary["hhea"].lineGap) == (1025, -275, 0)
        assert os2.fsSelection & (1 << 7)
        assert os2.usWinAscent >= binary["head"].yMax and os2.usWinDescent >= -binary["head"].yMin
        if kind == "mono":
            assert os2.panose.bProportion == 9 and binary["hhea"].advanceWidthMax == 600
            assert {binary["hmtx"][name][0] for name in cmap.values()} == {0, 600}


def test_screen_details_and_alternates_survive_packaging(cut):
    kind, style, original, font, _ = cut
    if kind == "sans":
        for name in ("c", "e"):
            tip = original["glyf"][name].endPtsOfContours[0] - 3
            assert outline(font, name)[0][tip][1] < outline(original, name)[0][tip][1]
        for name in ("c", "e", "ccedilla", "eogonek", "ae", "oe"):
            assert outline(font, name) != outline(original, name)
            assert font["glyf"][name].program.getBytecode() == original["glyf"][name].program.getBytecode()
        if style == "MediumItalic":
            assert font["glyf"]["ccedilla"].coordinates[20] == (428, 93)
            assert font["glyf"]["oe"].coordinates[76] == (729, 132)
        if style == "Regular":
            assert font["glyf"]["ae"].coordinates[27] == (730, 123)
        assert outline(font, "a") == outline(original, "a")
    elif kind == "serif":
        sample = "1934/580"
        assert shape(font, sample) == shape(original, sample, onum=True)
        assert shape(font, sample, lnum=True) == shape(original, sample)
        for feature in ("frac", "numr", "dnom", "sups", "subs", "sinf"):
            assert shape(font, sample, **{feature: True}) == shape(original, sample, **{feature: True})
        assert shape(font, "0", zero=True) == shape(original, "0", onum=True, zero=True)
        for alternate in (1, 2):
            assert shape(font, "010", lnum=True, aalt=alternate) == shape(original, "010", lnum=True, aalt=alternate)
    else:
        weight = font["OS/2"].usWeightClass
        lift, retreat = {400: (78, 32), 500: (88, 36), 700: (100, 40)}[weight]
        assert font["glyf"]["r"].xMax == original["glyf"]["r"].xMax - retreat
        for name in ("racute", "rcaron", "rcommaaccent"):
            components = [c.getComponentInfo() for c in font["glyf"][name].components]
            assert components == [c.getComponentInfo() for c in original["glyf"][name].components]
            assert ("r", (1, 0, 0, 1, 0, 0)) in components
            assert font["glyf"][name].xMax == max(x for x, _ in outline(font, name)[0])
        for name in ("m", "uni1E41", "uni1E43"):
            coords = outline(font, name)[0]
            assert sum(y == -12 + lift for _, y in coords) == 2
            assert sum(y == -12 for _, y in coords) == 4
        assert font["glyf"]["uni0442" if "Italic" in style else "uni0442.loclBGR"].getComponentNames(font["glyf"]) == ["m"]
        sample = ",;‘’“”‚„"
        for before, after in (({"ss09": True}, {}), ({}, {"ss09": True})):
            source = [outline(original, name) for name in shape(original, sample, **before)]
            assert [outline(font, name) for name in shape(font, sample, **after)] == source
        assert outline(font, "zero") != outline(original, "zero")
        for name in ("zero", "zero.tosf"):
            assert font["glyf"][name].program.getBytecode() == original["glyf"][name].program.getBytecode()
        assert outline(font, "O") == outline(original, "O")
        assert (outline(font, "l") == outline(original, "l")) == ("Italic" in style)
        if "Italic" not in style:
            assert outline(font, shape(font, "l", ss08=True)[0]) == outline(original, "l")
        assert outline(font, "hyphen") != outline(original, "hyphen")
        assert font["glyf"]["hyphen"].program.getBytecode() == original["glyf"]["minus"].program.getBytecode()
        for cp in range(0x2500, 0x25A0):
            name = font.getBestCmap()[cp]
            before = outline(original, name)[0]
            expected = [(x, 1100 if y == 950 else y) for x, y in before] if (
                cp < 0x2580 and original["glyf"][name].yMax == 950
            ) else list(before)
            assert list(outline(font, name)[0]) == expected


def test_packagers_replace_only_their_own_outputs(tmp_path, monkeypatch):
    inputs = {"mono": sorted((PUBLIC / "ttf").glob("CodexMono-*.ttf"))}
    assert len(inputs["mono"]) == 6
    monkeypatch.setattr(build, "DIST", tmp_path / "dist")
    build.package_public(inputs)
    public = build.DIST / "public"
    public_files = {p: build.sha256(p) for p in public.rglob("*") if p.is_file()}
    private_files = build.package_fonts(inputs, "3.5.1")
    assert {p: build.sha256(p) for p in public.rglob("*") if p.is_file()} == public_files
    private_hashes = {p: build.sha256(p) for p in private_files}
    stray = public / "ttf" / "stale.ttf"
    stray.touch()
    build.package_public(inputs)
    assert not stray.exists()
    assert {p: build.sha256(p) for p in private_files} == private_hashes
