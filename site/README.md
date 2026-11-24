# Codex screen type specimen

A static, interactive specimen of **Codex Mono, Codex Sans and Codex Serif**. The signal plate samples real Codex Mono Bold outlines. Its first entrance and **Replay signal** compose a glyph from a band of small characters in 1.7 seconds. Choosing another glyph redirects those characters from their last painted positions and velocities, even mid-flight. The new outline settles in 0.85 seconds; reduced motion switches immediately.

The plate pairs like characters in corresponding regions of the three outlines, splitting each region alternately by height and width. Where one outline needs fewer marks, its spare slots share a neighbor's position at zero opacity. This keeps the particle count bounded and lets marks separate or join without changing character or popping into view. The positions follow cubic curves with zero velocity at the destination; opacity and grayscale ease to the new depth.

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

To test interruptions, stage the site, run `python3 -m http.server 8001 --bind 127.0.0.1` at the repository root and open `http://127.0.0.1:8001/site/test_signal.html`. The check uses the built specimen and a controlled frame clock: it compares the painted canvas at identical timestamps across selections, checks the final glyphs and counts pending frames. Reload with reduced motion enabled to check the instant path.
