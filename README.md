# Codex Readable Nerd Fonts

A practical three-family type system for ordinary interfaces, long-form text,
and terminals:

- **Codex Sans Nerd Font Propo** — proportional UI and web sans.
- **Codex Serif Nerd Font Propo** — proportional editorial and reading serif.
- **Codex Mono Nerd Font Mono** — true fixed-cell terminal and coding font.

Each family ships in Regular, Italic, Bold, and Bold Italic as installable TTF
and browser-ready WOFF2 files. The pixel-display experiment from version 1 has
been superseded and is not included in the final distribution.

## Design and provenance

The readable letterforms are modified derivatives of the matching IBM Plex
Sans, Serif, and Mono branches. They are selected because the three styles were
designed as a coherent professional system with true italics, strong language
coverage, and proven UI/terminal behavior.

The IBM release archives, checksums, versions, and Nerd Fonts v3.5.1 patcher
image digest are pinned in `sources.lock.json`. Because `Plex` is an OFL
Reserved Font Name, every base is renamed to a Codex name before patching. The
upstream copyright, OFL text, patcher notice, and per-icon-set license audit are
packaged under `vendor/licenses/` and copied into `dist/licenses/`.

The complete Nerd Font option includes Font Logos, which upstream lists as
unlicensed. These complete builds are appropriate for local/private use. Before
public redistribution, narrow the patch options to cleared icon sets or obtain
separate permission.

## Reproducible build

```sh
mise install
mise run build
mise run check
```

Python and uv are locked by `mise.lock`; Python dependencies are locked by
`uv.lock`; source archives are checksum-pinned by `sources.lock.json`. The first
uncached build requires a reachable Docker daemon to run the digest-pinned Nerd
Fonts patcher. Patched intermediates are cached under `build/readable/`.

## Verification

`mise run check` performs:

- output and style inventory checks;
- user-facing name and Reserved Font Name checks;
- SIL OFL and Nerd Fonts version metadata checks;
- extended Latin and representative Nerd glyph coverage;
- HarfBuzz shaping across every style;
- proportional Sans/Serif metric checks;
- strict one-cell Mono checks across every style, ASCII, box drawing, block
  elements, and Nerd glyphs;
- one shared visual envelope for ordinary lowercase Mono glyphs in every
  style, without stale outline hinting;
- TTF/WOFF2 cmap and family-name parity;
- FontBakery universal checks on each regular face; and
- practical browser specimen generation.

The live specimen is served from `specimen/index.html` and exercises normal
14–20 px prose, UI controls, italics, weights, terminal grids, ambiguous
character pairs, Powerline separators, and representative Nerd icons.

## Output

```text
dist/
  codex-sans-nf-propo/
  codex-serif-nf-propo/
  codex-mono-nf-mono/
  web/
  licenses/
  MANIFEST.txt
  sources.lock.json
```

Build/test code is MIT-licensed in `LICENSE-CODE.txt`. Generated font binaries
remain under SIL OFL 1.1 plus the bundled icon-source terms described above.
