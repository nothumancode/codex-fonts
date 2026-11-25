"""Proof the published 2.100 and candidate 2.200 public editions at matched sizes."""

import argparse
import os
import subprocess
import time
from functools import cache
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageGrab, features


STYLES = ("Regular", "Italic", "Medium", "MediumItalic", "Bold", "BoldItalic")
COLS = (32, 600)


@cache
def face(root, family, style, size):
    return ImageFont.truetype(str(root / "ttf" / f"Codex{family}-{style}.ttf"), size,
                              layout_engine=ImageFont.Layout.RAQM)


class Sheet:
    def __init__(self, root, title, caption, height, dark=False):
        self.paper, self.ink, self.dim, self.rule = (
            ("#17191b", "#efefea", "#b8bdc2", "#4c5055") if dark else
            ("#fbfaf6", "#18191a", "#54585b", "#c4c4bd")
        )
        self.root = root
        self.im = Image.new("RGB", (1160, height), self.paper)
        self.d = ImageDraw.Draw(self.im)
        self.label(32, 28, "CODEX     /     SCREEN STUDIES     /     2.200")
        self.d.text((32, 77), title, font=face(root, "Sans", "Medium", 36), fill=self.ink, anchor="ls")
        self.d.text((32, 106), caption, font=face(root, "Sans", "Regular", 16), fill=self.dim, anchor="ls")
        self.line(127)

    def label(self, x, y, text):
        self.d.text((x, y), text, font=face(self.root, "Sans", "Medium", 13), fill=self.dim, anchor="ls")

    def line(self, y):
        self.d.line((32, y, 1128, y), fill=self.rule)

    def text(self, x, y, root, family, style, size, text, **options):
        self.d.text((x, y), text, font=face(root, family, style, size), fill=self.ink, anchor="ls", **options)


def details(before, after, output):
    s = Sheet(after, "The space under the shoulder",
              "Same 600-unit cell. Compare the end of r and the middle foot of m; n and o are controls.", 641)
    for x, root, title in zip(COLS, (before, after), ("2.100   /   RELEASED", "2.200   /   CANDIDATE")):
        s.label(x, 158, title)
        s.text(x, 261, root, "Mono", "Regular", 86, "rn m ṁ ř")
        s.text(x, 327, root, "Mono", "BoldItalic", 54, "return m")
        s.label(x, 376, "14 PX REGULAR   /   6× NEAREST PIXEL")
        tiny = Image.new("RGB", (83, 23), s.paper)
        ImageDraw.Draw(tiny).text((0, 16), "rn m ṁ ř", font=face(root, "Mono", "Regular", 14),
                                  fill=s.ink, anchor="ls")
        s.im.paste(tiny.resize((498, 138), Image.Resampling.NEAREST), (x, 387))
        s.text(x, 551, root, "Mono", "Regular", 14, "noononno  nron  ommo  runner  memory  ṁ  ṃ")
        s.text(x, 577, root, "Mono", "Italic", 14, "normal_form(rn, m)  rń  ŕ  ŗ  vv / w")
    s.line(600)
    s.label(32, 625, "TTF   /   FREETYPE + RAQM   /   THE LOWER TWO LINES ARE NATIVE 14 PX")
    s.im.save(output / "joins.png")


def reading(before, after, output):
    s = Sheet(after, "A quieter selected label",
              "Both panels use the same control sizes and copy. The right-hand selection uses a real 500 instead of 700.", 503)
    for i, (x, root) in enumerate(zip(COLS, (before, after))):
        selected, emphasis = ("Medium", "MediumItalic") if i else ("Bold", "BoldItalic")
        s.label(x, 159, ("2.100    /    400 + 700", "2.200    /    400 + 500 + 700")[i])
        s.text(x, 220, root, "Sans", "Bold", 30, "Recent connections")
        s.text(x, 250, root, "Sans", "Regular", 15, "Choose a workspace to review its access.")
        for j, (row, value) in enumerate((("Cœur de service", "Selected"), ("Centre de calcul", "Available"))):
            y = 302 + j * 48
            s.text(x + 12, y, root, "Sans", selected if not j else "Regular", 15, row)
            s.text(x + 381, y, root, "Sans", selected if not j else "Regular", 14, value)
            s.d.line((x, y + 16, x + 506, y + 16), fill=s.rule)
        s.text(x, 408, root, "Sans", emphasis, 15, "Accès vérifié.  Dernière révision à 09:41.")
        s.label(x, 444, f"Selection: {selected}   /   Note: {emphasis.replace('Italic', ' Italic')}   /   Body: Regular")
    s.im.save(output / "sans-ui.png")

    s = Sheet(after, "Keep the paragraph; change the voice",
              "The body on both sides is 18 px Regular on 26 px baselines. Only the subhead and italic note change weight.", 660)
    for i, (x, root) in enumerate(zip(COLS, (before, after))):
        s.label(x, 159, ("2.100    /    BOLD SUBHEAD", "2.200    /    MEDIUM SUBHEAD")[i])
        s.text(x, 211, root, "Serif", "Regular", 31, "The night register")
        s.text(x, 251, root, "Serif", "Medium" if i else "Bold", 18, "A note in the margin, 1908")
        for j, line in enumerate((
            "At nine the printer opened the register. A page dated",
            "1908 had slipped behind the binding; the last two",
            "figures lay almost level with the edge of the paper.",
            "She turned it towards the light and read it again.",
            "",
            "There were 28 entries for the crossing, each in a",
            "slightly different hand. Beside number 193 someone",
            "had left a note small enough to miss on a first reading.",
        )):
            s.text(x, 292 + 26 * j, root, "Serif", "Regular", 18, line)
        s.text(x, 521, root, "Serif", "MediumItalic" if i else "Italic", 17, "“Keep these three leaves together.”")
        s.d.line((x, 552, x + 502, 552), fill=s.rule)
        s.text(x, 589, root, "Serif", "Regular", 18, "Folio 193   /   0123456789")
        s.text(x, 620, root, "Serif", "Regular", 18, "Table 193   /   0123456789", features=["lnum"])
    s.im.save(output / "serif-prose.png")


def capture(root, style, px, paper, ink, temp):
    conf = temp / "fonts.conf"
    conf.write_text(f"<fontconfig><dir>{escape(str(root.resolve() / 'ttf'))}</dir>"
                    f"<cachedir>{escape(str(temp / 'cache'))}</cachedir></fontconfig>")
    (temp / "memory.rs").write_text("fn f() {\n    return normal_form(ṁ, ř) != 0x01;\n}\n")
    ready, done = temp / "ready", temp / "done"
    ready.unlink(missing_ok=True)
    done.unlink(missing_ok=True)
    cmd = ["xterm", "-u8", "-report-fonts", "-fa", "Codex Mono:style=" + style.replace("Italic", " Italic").strip(),
           "-fs", str(px), "+sb", "-bw", "0", "-b", "0", "-geometry", "43x2+0+0",
           "-xrm", "Xft.dpi: 72", "-bg", paper, "-fg", ink, "-e", "sh", "-c",
           """printf '\\033[?25l$ grep -nE '\\''rn|m|vv|w'\\'' memory.rs\\n'
printf '%s' "$(grep -nE 'rn|m|vv|w' memory.rs)"
touch ready; while [ ! -f done ]; do sleep 0.05; done"""]
    with (temp / "log").open("w+") as log:
        proc = subprocess.Popen(cmd, cwd=temp, env=dict(os.environ, FONTCONFIG_FILE=str(conf), LC_ALL="C.UTF-8"),
                                stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(150):
                time.sleep(.04)
                if proc.poll() is not None:
                    raise RuntimeError("XTerm exited before drawing")
                if ready.exists():
                    frame = ImageGrab.grab(xdisplay=os.environ["DISPLAY"]).convert("RGB")
                    box = ImageChops.difference(frame, Image.new("RGB", frame.size)).getbbox()
                    if box:
                        strip = frame.crop(box)
                        if len(strip.getcolors(strip.width * strip.height)) > 4:
                            break
            else:
                raise RuntimeError("No terminal text on the dedicated Xvfb screen")
            done.touch()
            proc.wait(timeout=5)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        log.seek(0)
        normal = log.read().split("Loaded XftFonts(", 2)[1]
    expected = (root / "ttf" / f"CodexMono-{style}.ttf").resolve()
    if f"file={expected}\n" not in normal or f"pixelsize={px}\n" not in normal or "embolden=False" not in normal:
        raise ValueError(normal)
    return strip, f"{expected}   {px} px   {strip.width} × {strip.height} px"


def xterm(before, after, output):
    logs = []
    with TemporaryDirectory() as scratch:
        for dark in (False, True):
            s = Sheet(after, "The shell at reading size",
                      "Unscaled XTerm/Xft captures of a real grep. Each row requests the named TTF as its primary face.", 1144, dark)
            s.label(191, 155, "2.100    /    RELEASED")
            s.label(654, 155, "2.200    /    CANDIDATE")
            y = 177
            for px in (12, 14, 16):
                s.label(32, y + 8, f"{px} PX   /   72 DPI")
                y += 23
                for style in STYLES:
                    s.label(32, y + 16, style.replace("Italic", " Italic").strip())
                    for x, root in zip((191, 654), (before, after)):
                        if root == before and "Medium" in style:
                            s.label(x, y + 16, "—   No 500 face")
                            continue
                        strip, log = capture(root, style, px, s.paper, s.ink, Path(scratch))
                        logs.append(log)
                        s.im.paste(strip, (x, y))
                    y += strip.height + 7
                s.line(y + 2)
                y += 24
            s.im.crop((0, 0, s.im.width, y)).save(output / ("xterm-dark.png" if dark else "xterm-light.png"))
    (output / "xterm-files.txt").write_text("\n".join(logs) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ("before", "after", "output"):
        p.add_argument(arg, type=Path)
    p.add_argument("--xterm", action="store_true", help="Also capture XTerm. Run inside a dedicated 72-dpi Xvfb.")
    a = p.parse_args()
    if not features.check_feature("raqm"):
        p.error("Pillow must have RAQM for shaped, comparable text")
    a.output.mkdir(parents=True, exist_ok=True)
    details(a.before, a.after, a.output)
    reading(a.before, a.after, a.output)
    if a.xterm:
        xterm(a.before, a.after, a.output)


if __name__ == "__main__":
    main()
