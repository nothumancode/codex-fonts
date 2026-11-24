# Codex Readable Nerd Fonts

A practical three-family type system for ordinary interfaces, long-form text,
and terminals:

- **Codex Sans Nerd Font Propo** — proportional UI and web sans.
- **Codex Serif Nerd Font Propo** — proportional editorial and reading serif.
- **Codex Mono Nerd Font Mono** — true fixed-cell terminal and coding font.

The **2.100 screen cut** also comes as Codex Mono, Codex Sans and Codex Serif
without the icon patch. Both editions have four static styles: Regular,
Italic, Bold and Bold Italic. There is no variable or pixel-display face.

Mono gives the zero a free-standing angled mark, turns the foot of upright
`l` away from `I`, and fits the hyphen to the rest of the operators. Sans opens
the lower lips of `c` and `e` in interface text. Serif sets dates in text
figures by default; choose OpenType `lnum` for lining figures. See the
[cut notes and proof recipe](docs/SCREEN-CUT.md) for measurements.

## Install or embed the public text edition

```sh
mise install
mise run public
mise run check-public
```

Install the files in **dist/public/ttf/** using your operating system's font
installer. For websites, use **dist/public/web/**. For example,
`CodexMono-Regular.woff2` is Codex Mono, weight 400, normal style;
`CodexMono-BoldItalic.woff2` is weight 700, italic. These WOFF2s have the same
repertoire and layout features as the matching TTFs. Include
`dist/public/licenses/IBM-Plex-OFL-1.1.txt` when sharing either format.
This build needs no Docker and imports no Nerd Font icons.

## Build the private terminal edition

```sh
mise install
mise run build
mise run check
```

The full icon build uses the digest-pinned Nerd Fonts 3.5.1 Docker patcher
with `--complete --careful`; Mono uses its single-cell mode. The first
uncached build needs a reachable Docker daemon. Install the TTFs in
`dist/codex-mono-nf-mono/`, `dist/codex-sans-nf-propo/` or
`dist/codex-serif-nf-propo/`. The full WOFF2s are alongside them. The
smaller `dist/web/` subsets and the generated pages in `specimen/` are for
**private Nerd Font QA**, not public web distribution.

The Nerd Fonts glyph audit lists Font Logos as unlicensed. Keep this complete
edition local/private unless the relevant rights are separately cleared.
Only `dist/public/` is the OFL-only release. The two builds replace their own
outputs and neither deletes the other edition.

## Sources and checks

The generating sources are the versioned **complete IBM Plex TTFs**, not
editable UFO or Glyphs files in this repository. [sources.lock.json](sources.lock.json)
pins the IBM release archives and patcher; [build.py](src/codex_fonts/build.py)
renames the bases and owns the build/packaging, and
[screen.py](src/codex_fonts/screen.py) holds the cuts. The original copyright
and designer credits stay in the binaries. “Plex” is a Reserved Font Name;
no derivative family uses it.

Python and uv are pinned in `mise.lock`, Python packages in `uv.lock`. The
archives are verified in `.cache/font-sources/`; prepared and patched TTFs
live under `build/readable/`. Generated fonts in `dist/` are not committed.

`mise run check` checks both editions: style and format inventory, names and
licenses, source coverage, HarfBuzz shaping, advances and Mono cells,
stylistic alternates, hinting and web encodings. It also regenerates the
private specimen and runs FontBakery's universal profile on the six Regular
TTFs. Per-font diagnostics, including warnings, are in `build/fontbakery/`.
`mise run check-public` checks the public edition alone.

Build and test code is [MIT-licensed](LICENSE-CODE.txt); see
[LICENSE.txt](LICENSE.txt) for the separate font and icon terms.
