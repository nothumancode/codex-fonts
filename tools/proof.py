"""Render matched size and detail proofs from two built Nerd Font dist directories.

Run with a RAQM-enabled Pillow: python tools/proof.py BEFORE AFTER OUTPUT.
"""

import argparse
from functools import cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, features


@cache
def face(root, family, px, style="Regular"):
    suffix = "Mono" if family == "Mono" else "Propo"
    slug = f"codex-{family.lower()}-nf-{suffix.lower()}"
    path = root / slug / f"Codex{family}NerdFont{suffix}-{style}.ttf"
    return ImageFont.truetype(str(path), px, layout_engine=ImageFont.Layout.RAQM)


class Sheet:
    width = 1152
    columns = (36, 604)

    def __init__(self, roots, title, subtitle, height, dark=False):
        self.roots = roots
        self.ink, self.dim, self.rule, self.paper, self.wash = (
            ("#edf0e7", "#aebbac", "#435349", "#19221e", "#212e26") if dark else
            ("#1c2722", "#536459", "#b8c4ba", "#f7f7ef", "#e9eee6")
        )
        self.image = Image.new("RGB", (self.width, height), self.paper)
        self.d = ImageDraw.Draw(self.image)
        self.label(36, 41, "C O D E X    /    S C R E E N   P R O O F S")
        self.d.text((36, 93), title, font=face(roots[1], "Sans", 41, "Bold"), fill=self.ink, anchor="ls")
        self.d.text((36, 127), subtitle, font=face(roots[1], "Sans", 16), fill=self.dim, anchor="ls")
        self.line(150)
        for x, text in zip(self.columns, ("01   /   BEFORE     2.000", "02   /   AFTER     2.100")):
            self.label(x, 182, text)
        self.d.line((575, 170, 575, height - 59), fill=self.rule)
        self.line(height - 49)
        self.label(36, height - 20, "TTF   /   GRAYSCALE   /   1 IMAGE PIXEL = 1 DEVICE PIXEL AT 100%")

    def line(self, y):
        self.d.line((36, y, self.width - 36, y), fill=self.rule)

    def label(self, x, y, text):
        self.d.text((x, y), text, font=face(self.roots[1], "Sans", 12, "Bold"), fill=self.dim, anchor="ls")

    def text(self, side, y, text, family, px, style="Regular", inset=0, **options):
        self.d.text((self.columns[side] + inset, y), text, font=face(self.roots[side], family, px, style),
                    anchor="ls", fill=self.ink, **options)


def terminal(roots, output, dark):
    sheet = Sheet(roots, "Mono in the terminal",
                  "The same prompt, code and cell grid at 12, 14 and 16 pixels. No ligature or spacing overrides.", 950, dark)
    lines = (
        "\ue0a0 main \ue0b0 rg -n -- '0[xX][0-9a-f]+' src",
        "if (fd != 0 && key[i] <= 1) {",
        '    write(1, "O0", 2);  // 0x10, Il1|',
        "}",
        "┌──────────┬──────┐    rn / m    vv / w",
        "│ mode     │ 0640 │    ()[]{}    != -> --",
        "└──────────┴──────┘    ░▒▓█      │ ┼ ╬",
    )
    y = 212
    for px in (12, 14, 16):
        leading = round(px * 1.3)
        for side, x in enumerate(sheet.columns):
            sheet.label(x, y, f"{px} PX    /    REGULAR    /    {leading} PX BASELINES")
            for row, text in enumerate(lines):
                sheet.text(side, y + 32 + row * leading, text, "Mono", px)
        y += 32 + len(lines) * leading + 32
        sheet.line(y - 17)
    for side, x in enumerate(sheet.columns):
        sheet.label(x, y + 6, "STYLE CHECK    /    14 PX")
        for row, (style, text) in enumerate((
            ("Italic", "// italic: file[0] != null;"),
            ("Bold", "  bold: 0x010f --color=auto"),
            ("BoldItalic", "  bold italic: ls -l ./local"),
        )):
            sheet.text(side, y + 32 + row * 22, text, "Mono", 14, style)
    sheet.image.save(output / ("mono-dark.png" if dark else "mono-light.png"))


def detail(roots, output):
    sheet = Sheet(roots, "Signs inside the cell",
                  "Contour details above; below, a 4× nearest-neighbor enlargement of a 14-pixel raster, not a larger font size.", 570)
    for side, x in enumerate(sheet.columns):
        sheet.text(side, 284, "0O 1Il ,;", "Mono", 72)
        sheet.text(side, 351, "->  --  ==", "Mono", 48, "Bold")
        sheet.label(x, 405, "0O  /  1Il  /  COMMA  /  FLAG     •     REGULAR, 14 PX × 4")
        window = Image.new("RGB", (124, 23), sheet.paper)
        ImageDraw.Draw(window).text((0, 17), "0O 1Il ,; --", font=face(roots[side], "Mono", 14),
                                    fill=sheet.ink, anchor="ls")
        sheet.image.paste(window.resize((496, 92), Image.Resampling.NEAREST), (x, 419))
    sheet.image.save(output / "mono-details.png")


def interface(roots, output):
    sheet = Sheet(roots, "Sans in an interface",
                  "Look at the lower terminals in c and e, especially in small bold labels. All advances stay put.", 722)
    for side, x in enumerate(sheet.columns):
        sheet.label(x, 221, "SETTINGS     /     14–16 PX")
        sheet.text(side, 263, "Recent connections", "Sans", 25, "Bold")
        sheet.text(side, 293, "Choose a service to review its access.", "Sans", 16)
        sheet.d.rounded_rectangle((x, 317, x + 506, 362), 7, fill=sheet.wash, outline=sheet.rule)
        sheet.text(side, 345, "Search connections…", "Sans", 14, inset=15)
        for row, (name, status) in enumerate((("Release centre", "Connected"), ("Receipt service", "Reconnect"))):
            y = 400 + row * 49
            sheet.text(side, y, name, "Sans", 14, "Bold")
            sheet.text(side, y, status, "Sans", 14, inset=366)
            sheet.d.line((x, y + 14, x + 506, y + 14), fill=sheet.rule)
        sheet.text(side, 497, "Last checked at 09:41", "Sans", 12, "Italic")
        sheet.label(x, 548, "DETAIL    /    REGULAR + BOLD ITALIC")
        sheet.text(side, 608, "recède", "Sans", 51)
        sheet.text(side, 608, "accès", "Sans", 44, "BoldItalic", inset=244)
        sheet.text(side, 649, "Service recovered.  Recent records received.", "Sans", 14)
    sheet.image.save(output / "sans-ui.png")


def prose(roots, output):
    sheet = Sheet(roots, "Serif on the page",
                  "The date and folio use the default figures. The last line explicitly requests lining figures in both fonts.", 748)
    for side, x in enumerate(sheet.columns):
        sheet.label(x, 221, "NIGHT REGISTER    /    FOLIO 193")
        sheet.text(side, 275, "Notes from 1908", "Serif", 38)
        for row, text in enumerate((
            "At 9.40 the lamps went out. A clerk recorded 28",
            "names in a hand so small that the figures sat",
            "almost inside the letters. By the time she reached",
            "folio 193, the last light had crossed the sill.",
        )):
            sheet.text(side, 327 + row * 29, text, "Serif", 18)
        sheet.text(side, 473, "“Keep the 3 pages together,” she wrote.", "Serif", 17, "Italic")
        sheet.text(side, 510, "Entry 58.", "Serif", 16, "Bold")
        sheet.text(side, 510, "Revised 6 May.", "Serif", 16, "BoldItalic", inset=93)
        sheet.d.line((x, 539, x + 506, 539), fill=sheet.rule)
        sheet.label(x, 573, "DEFAULT    /    32 PX")
        sheet.text(side, 616, "0123456789", "Serif", 32)
        sheet.text(side, 666, "Lining figures   0123456789", "Serif", 18, features=["lnum"])
    sheet.image.save(output / "serif-prose.png")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("before", "after", "output"):
        parser.add_argument(arg, type=Path)
    args = parser.parse_args()
    if not features.check_feature("raqm"):
        parser.error("Pillow must include RAQM for OpenType feature shaping")
    roots = (args.before, args.after)
    args.output.mkdir(parents=True, exist_ok=True)
    for dark in (False, True):
        terminal(roots, args.output, dark)
    detail(roots, args.output)
    interface(roots, args.output)
    prose(roots, args.output)


if __name__ == "__main__":
    main()
