# Codex Readable Nerd Fonts

[Try the published specimen](https://nothumancode.github.io/codex-fonts/) · [Download the published fonts (ZIP)](https://github.com/nothumancode/codex-fonts/releases/latest/download/Codex-Fonts.zip) · [Build the specimen locally](site/README.md)

A practical three-family type system for ordinary interfaces, long-form text,
and terminals:

- **Codex Sans Nerd Font Propo** — proportional UI and web sans.
- **Codex Serif Nerd Font Propo** — proportional editorial and reading serif.
- **Codex Mono Nerd Font Mono** — true fixed-cell terminal and coding font.

The **2.200 Medium screen cut** comes in both the OFL-only Codex Mono, Sans
and Serif and the private icon editions. Each family has six static faces:
Regular, Medium and Bold, each with a drawn italic. Mono's new 500 weight
fits the same terminal columns as 400 and 700. Its shorter middle stroke in
`m` and clipped `r` flag help separate the one-cell `m` from the two-cell
`rn`. See the [design decisions, specimens and proof recipe](docs/MEDIUM-CUT.md).

Mono gives the zero a free-standing angled mark, turns the foot of upright
`l` away from `I`, and fits the hyphen to the rest of the operators. Sans opens
the lower lips of `c` and `e` in interface text. Serif sets dates in text
figures by default; choose OpenType `lnum` for lining figures. These details
were introduced in the [2.100 screen cut](docs/SCREEN-CUT.md).

## Install or embed the public text edition

The [GitHub Release](https://github.com/nothumancode/codex-fonts/releases/latest) is the published edition. To try the 2.200 candidate from this source tree, use its **Public font download** Actions artifact or build it:

```sh
mise install
mise run public
mise run check-public
mise exec -- python tools/package_public.py
```

The last command writes `build/Codex-Fonts-2.200.zip` with 18 TTFs, 18 WOFF2s,
the OFL/copyright notice, the public source URLs and archive SHA-256 pins in
`sources.json`, and a file manifest. After unzipping, run
`sha256sum --check SHA256SUMS`. The workflow attaches that ZIP to its runs;
run artifacts expire and require GitHub sign-in. It does not publish a Release or Pages.

Install the files in **dist/public/ttf/** using your operating system's font
installer. For websites, use **dist/public/web/**. For example,
`CodexMono-Regular.woff2` is Codex Mono, weight 400, normal style;
`CodexMono-MediumItalic.woff2` is weight 500, italic. Register each file
with its own CSS weight and slant; no faux bold or slant is needed. These WOFF2s have the same
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
private specimen and runs FontBakery's universal profile on each complete
six-style family in both editions. Reports, including warnings, are in `build/fontbakery/`.
`mise run check-public` checks the public edition alone.

Build and test code is [MIT-licensed](LICENSE-CODE.txt); see
[LICENSE.txt](LICENSE.txt) for the separate font and icon terms.
