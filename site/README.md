# Codex screen type specimen

A static, interactive specimen of **Codex Mono, Codex Sans and Codex Serif**. The signal plate samples the actual outline of the chosen Codex Mono Bold glyph and composes it out of smaller letters. Each signal ends in 1.7 seconds; reduced motion renders the finished glyph immediately. The terminal, editable proof and reading plate also work without animation.

## Build and view

From the repository root, with [mise](https://mise.jdx.dev/) installed:

```sh
mise install
mise run public
python3 site/build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory build/showcase
```

Open `http://127.0.0.1:8000/`. Edit the files in `site/src/` and rerun `python3 site/build.py` to restage them. To use a public build from another checkout, pass its directory: `python3 site/build.py --public /path/to/dist/public`. The site build needs only Python's standard library; the finished page has no framework, CDN, analytics or server-side code.

Only **`build/showcase/`** is the deployable directory. All URLs are relative, so the same tree works at a domain root or a subpath. It contains the twelve public WOFF2s, the font and code notices, and one downloadable ZIP with the matching twelve installable TTFs and their OFL notice. It does not copy private Nerd Font outputs. Do not substitute `dist/web/`, the patched family directories or the old `specimen/` proof sheets for the public build.

Run the packaging regression checks with `python3 -m unittest discover -s site`.
