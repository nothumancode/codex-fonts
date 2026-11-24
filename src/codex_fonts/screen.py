"""The screen cut, applied to the versioned TrueType masters before icon patching."""

from functools import cache

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables.ttProgram import Program


def cut_mono(font):
    """Lengthen the zero mark, match the operator strokes and give upright l a turned foot."""
    glyf = font["glyf"]
    bold = font["OS/2"].usWeightClass == 700
    italic = bool(font["post"].italicAngle)
    changed = set()
    fitted = {"zero", "zero.tosf", "hyphen"}

    for name in ("zero", "zero.tosf"):
        glyph = glyf[name]
        starts = [0, *(end + 1 for end in glyph.endPtsOfContours[:-1])]
        contours = [range(start, end + 1) for start, end in zip(starts, glyph.endPtsOfContours)]
        mark = min(contours, key=lambda c: max(glyph.coordinates[i][1] for i in c)
                   - min(glyph.coordinates[i][1] for i in c))
        xs, ys = zip(*(glyph.coordinates[i] for i in mark))
        cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
        height = (168 if bold else 184) if name.endswith(".tosf") else (218 if bold else 236)
        for i in mark:
            x, y = glyph.coordinates[i]
            dy = (y - cy) * height / (max(ys) - min(ys))
            glyph.coordinates[i] = (round(cx + (x - cx) * (0.70 if bold else 0.82)
                                          + dy * (0.42 if italic else 0.34)), round(cy + dy))

    for i, (x, y) in enumerate(glyf["minus"].coordinates):
        glyf["hyphen"].coordinates[i] = (x + (46 if x < 300 else -46), y)
    glyf["hyphen"].program = glyf["minus"].program

    if not italic:
        for name in ("l", "lslash"):
            pts = glyf[name].coordinates
            left, thickness = pts[1]
            right, _ = pts[-4]
            toe = pts[-3][0]
            bend = 172 if bold else 136
            pen = TTGlyphPen(None)
            pen.moveTo((left, bend))
            for point in pts[2:-4]:
                pen.lineTo(point)
            pen.lineTo((right, bend))
            pen.qCurveTo((right, thickness), (right + 52, thickness))
            pen.lineTo((toe - 12, thickness + 14))
            pen.lineTo((toe, 14))
            pen.qCurveTo((toe - 40, 0), (right + 34, 0))
            pen.qCurveTo((left, 0), (left, bend))
            pen.closePath()
            glyf[name + ".alt01"] = glyf[name]
            fitted.add(name + ".alt01")
            glyf[name] = pen.glyph()
            changed.add(name)

    return changed, fitted


def extend_mono_rails(font):
    """Bleed solid upper rail ends into the next integer row. Leave dash gaps and junctions alone."""
    cmap, glyf = font.getBestCmap(), font["glyf"]
    fitted = set()
    for cp in range(0x2500, 0x2580):
        name = cmap[cp]
        glyph = glyf[name]
        if glyph.yMax != 950:
            continue
        for i, (x, y) in enumerate(glyph.coordinates):
            if y == 950:
                glyph.coordinates[i] = (x, 1100)
        fitted.add(name)
    return fitted


def exchange_mono_punctuation(font):
    """Use round comma heads by default and keep the blade cuts under ss09."""
    glyf = font["glyf"]
    gsub = font["GSUB"].table
    feature = next(f.Feature for f in gsub.FeatureList.FeatureRecord if f.FeatureTag == "ss09")
    pairs = gsub.LookupList.Lookup[feature.LookupListIndex[0]].SubTable[0].mapping
    exchange = pairs | {alt: base for base, alt in pairs.items()}
    original = {name: glyf[name] for name in exchange}
    for name, donor in exchange.items():
        glyph = original[donor]
        if glyph.isComposite():
            for component in glyph.components:
                component.glyphName = exchange.get(component.glyphName, component.glyphName)
        glyf[name] = glyph
    return set(exchange)


def cut_sans(font, style):
    """Lower lip on-curve indices in the pinned masters, including integrated accents and ligatures."""
    names = ("c", "ccedilla", "e", "eogonek", "ae", "oe")
    tips = {
        "Regular": (28, 18, 26, 38, 27, 67),
        "Italic": (29, 19, 25, 34, 74, 76),
        "Bold": (27, 17, 24, 36, 23, 59),
        "BoldItalic": (32, 22, 27, 34, 72, 75),
    }
    for name, inner in zip(names, tips[style], strict=True):
        points = font["glyf"][name].coordinates
        for tip, handle in ((inner, inner - 1), (inner + 1, inner + 2)):
            x, y = points[tip]
            hx, hy = points[handle]
            points[tip] = (round(x + (hx - x) * 0.54), round(y + (hy - y) * 0.54))
    return set(names)


def serif_text_figures(font):
    """Use the source's text figures in prose; retain explicit lining and fraction settings."""
    cmap = font.getBestCmap()
    encoding = {ord(c): cmap[ord(c)] + ".tosf" for c in "0123456789"}
    figures = {cmap[cp]: oldstyle for cp, oldstyle in encoding.items()}
    for table in font["cmap"].tables:
        table.cmap.update({cp: name for cp, name in encoding.items() if cp in table.cmap})

    gsub = font["GSUB"].table
    fraction_tags = {"dnom", "frac", "numr", "sinf", "subs", "sups"}
    lookups = {i for f in gsub.FeatureList.FeatureRecord if f.FeatureTag in fraction_tags
               for i in f.Feature.LookupListIndex}
    for index in lookups:
        lookup = gsub.LookupList.Lookup[index]
        if lookup.LookupType == 1:
            for sub in lookup.SubTable:
                sub.mapping.update({old: sub.mapping[lining] for lining, old in figures.items()
                                    if lining in sub.mapping})
    lining = next(f.Feature for f in gsub.FeatureList.FeatureRecord if f.FeatureTag == "lnum")
    for index in lining.LookupListIndex:
        for sub in gsub.LookupList.Lookup[index].SubTable:
            sub.mapping.update({"zero.tosf.alt01": "zero.alt01", "zero.tosf.alt02": "zero.alt02"})
    for lookup in gsub.LookupList.Lookup:
        if lookup.LookupType == 3:
            for sub in lookup.SubTable:
                if "zero" in sub.alternates:
                    sub.alternates["zero.tosf"] = [name.replace("zero.", "zero.tosf.")
                                                   for name in sub.alternates["zero"]]


def apply_screen_cut(font, kind, style):
    if kind == "serif":
        serif_text_figures(font)
        return
    if kind == "sans":
        redrawn, fitted = set(), cut_sans(font, style)
    else:
        redrawn, fitted = cut_mono(font)
        fitted |= exchange_mono_punctuation(font) | extend_mono_rails(font)

    glyf = font["glyf"]

    @cache
    def affected(name):
        return (name in redrawn or name in fitted
                or any(affected(component) for component in glyf[name].getComponentNames(glyf)))

    for name in font.getGlyphOrder():
        if not affected(name):
            continue
        glyph = glyf[name]
        if hasattr(glyph, "program") and name not in fitted:
            glyph.program = Program()
        glyph.recalcBounds(glyf)
        advance, _ = font["hmtx"][name]
        font["hmtx"][name] = (advance, glyph.xMin)
