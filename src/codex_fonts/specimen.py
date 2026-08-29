"""Generate a practical readability specimen for the three Nerd Font families."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FAMILIES = {
    "Codex Sans": ("Codex Sans Nerd Font Propo", "web/CodexSans"),
    "Codex Serif": ("Codex Serif Nerd Font Propo", "web/CodexSerif"),
    "Codex Mono": ("Codex Mono Nerd Font Mono", "web/CodexMono"),
}


def font_faces() -> str:
    rules = []
    for family, relative in FAMILIES.values():
        for style, weight, italic in (("Regular", 400, "normal"), ("Italic", 400, "italic"), ("Bold", 700, "normal"), ("BoldItalic", 700, "italic")):
            rules.append(f"@font-face{{font-family:'{family}';src:url('../dist/{relative}-{style}.woff2') format('woff2');font-weight:{weight};font-style:{italic};font-display:block}}")
    return "\n".join(rules)


def main() -> None:
    output_dir = ROOT / "specimen"
    output_dir.mkdir(exist_ok=True)
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Codex Readable Nerd Fonts</title><style>
{font_faces()}
:root{{--paper:#f5f2ea;--ink:#17201b;--muted:#657069;--line:#cfd5cf;--accent:#087a4a;--dark:#08120d;--glow:#78f0ac;color-scheme:light}}
*{{box-sizing:border-box}}html{{background:var(--paper);color:var(--ink)}}body{{margin:0;font-family:'Codex Sans Nerd Font Propo',sans-serif;font-synthesis:none}}
header{{min-height:72vh;padding:clamp(32px,8vw,120px);display:grid;align-content:end;background:linear-gradient(135deg,#eef5ee,#f5f2ea 52%,#e4ece5);border-bottom:1px solid var(--line)}}
.eyebrow,.label{{font:700 12px/1.3 'Codex Mono Nerd Font Mono',monospace;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)}}
h1{{max-width:12ch;margin:.25em 0;font:700 clamp(58px,10vw,150px)/.9 'Codex Sans Nerd Font Propo',sans-serif;letter-spacing:-.045em}}header p{{max-width:68ch;margin:0;color:var(--muted);font-size:18px;line-height:1.55}}
main{{padding:clamp(22px,5vw,72px);display:grid;gap:clamp(24px,5vw,72px)}}section{{border-top:1px solid var(--line);padding-top:28px}}
.section-head{{display:flex;justify-content:space-between;align-items:baseline;gap:20px;margin-bottom:28px}}h2{{margin:0;font-size:clamp(36px,6vw,82px);line-height:1}}
.sans{{font-family:'Codex Sans Nerd Font Propo',sans-serif}}.serif{{font-family:'Codex Serif Nerd Font Propo',serif}}.mono{{font-family:'Codex Mono Nerd Font Mono',monospace}}
.prose-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:clamp(28px,5vw,70px)}}.copy{{font-size:16px;line-height:1.62;max-width:68ch}}.copy.large{{font-size:20px;line-height:1.52}}
.copy p:first-child:first-letter{{float:left;font-size:4.4em;line-height:.75;padding:.08em .1em 0 0;color:var(--accent)}}
.ui{{padding:28px;border:1px solid var(--line);border-radius:18px;background:#fff;box-shadow:0 18px 50px #1a39200d}}.ui h3{{font-size:25px;margin:0 0 6px}}.ui p{{color:var(--muted);margin:0 0 24px}}button{{border:0;border-radius:999px;padding:11px 18px;background:var(--accent);color:white;font:700 14px inherit}}.secondary{{background:#e6ede7;color:var(--ink);margin-left:8px}}
.weights{{display:grid;gap:10px;margin-top:28px;font-size:24px}}.weights i{{font-style:italic}}.weights b{{font-weight:700}}
.terminal{{background:var(--dark);color:#dce8df;border-radius:18px;overflow:hidden;box-shadow:0 30px 80px #08120d33}}.termbar{{padding:13px 18px;border-bottom:1px solid #23352a;color:#8ba093;font-size:13px}}
pre{{margin:0;padding:clamp(20px,4vw,48px);overflow:auto;font:400 clamp(12px,1.4vw,16px)/1.55 'Codex Mono Nerd Font Mono',monospace;tab-size:2}}.prompt{{color:var(--glow)}}.icons{{color:#efc65a}}
.pairs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-top:24px}}.pair{{padding:18px;border:1px solid var(--line);border-radius:12px;font:24px/1.45 'Codex Mono Nerd Font Mono',monospace;background:#fff}}.pair small{{display:block;color:var(--muted);font:12px 'Codex Sans Nerd Font Propo',sans-serif}}
.glyphs{{font:clamp(28px,5vw,66px)/1.6 'Codex Mono Nerd Font Mono',monospace;overflow-wrap:anywhere;color:var(--accent)}}footer{{padding:50px;text-align:center;color:var(--muted);font-size:13px}}@media(max-width:620px){{.section-head{{display:block}}header{{min-height:60vh}}.pair{{font-size:20px}}}}
</style></head><body>
<header><div class="eyebrow">Codex Type System / Readable Edition</div><h1>Made to be read.</h1><p>A coherent sans, serif, and true monospaced Nerd Font family for ordinary interfaces, long-form reading, and real terminals. Four styles each: regular, italic, bold, and bold italic.</p></header>
<main>
<section class="sans"><div class="section-head"><h2>Codex Sans</h2><div class="label">UI + everyday web</div></div><div class="prose-grid"><div class="copy large"><p>Good interface typography should disappear into the work. Open counters, distinct silhouettes, and a generous x-height keep instructions clear even when the screen is busy.</p><p><b>Bold establishes structure.</b> <i>Italic adds a quieter second voice.</i> Neither needs to shout.</p><div class="weights">Regular — The quick brown fox, 0123456789<br><i>Italic — Thoughtful emphasis without noise</i><br><b>Bold — Actions, states, and hierarchy</b><br><b><i>Bold Italic — Urgent, but still composed</i></b></div></div><div class="ui"><div class="label">Agent status</div><h3>Ready for review</h3><p>Four checks passed. One visual confirmation remains.</p><button>Open evidence</button><button class="secondary">View diff</button></div></div></section>
<section class="serif"><div class="section-head"><h2>Codex Serif</h2><div class="label">Editorial + long-form</div></div><div class="prose-grid"><article class="copy large"><p>Evidence changes the texture of a decision. What began as a plausible explanation becomes a durable conclusion only after the behavior has been reproduced, observed, and written down.</p><p>The serif face is meant for that slower register: reports, research notes, design narratives, and documentation with enough room to breathe.</p></article><article class="copy"><p><b>Readable at ordinary sizes.</b> This paragraph is set at sixteen pixels, not poster scale. Letterforms remain conventional, punctuation carries its weight, and mixed-case text forms a steady line.</p><p><i>“Clarity is not simplification for its own sake; it is the removal of accidental difficulty.”</i></p><p>Diacritics: À É Ö ñ æ œ ß. Symbols: € £ ¥ © ™. Dashes—short and long—quotes “curved,” ellipses… all present.</p></article></div></section>
<section><div class="section-head"><h2 class="mono">Codex Mono</h2><div class="label">True mono + Nerd icons</div></div><div class="terminal"><div class="termbar mono">● ● ● &nbsp; codex / verification</div><pre><span class="prompt"> main </span> mise run check
<span class="icons">󰊢</span> source   OFL-derived readable letterforms
<span class="icons"></span> terminal one fixed cell for text + icons
<span class="icons">󰉋</span> output   TTF + WOFF2 / four styles

┌──────────────────┬──────────┐
│ 0O  1Il|  rn  m  │ 100% ███ │
├──────────────────┼──────────┤
│  main          │ ✓ 42     │
└──────────────────┴──────────┘
▏▎▍▌▋▊▉█  ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏

const result = await agent.verify({{
  glyphs: "readable",
  widths: "one-cell",
  evidence: true,
}});</pre></div><div class="pairs"><div class="pair">cr ea create<small>baseline + x-height alignment</small></div><div class="pair">0O oO 8B<small>zero / capital O / eight / B</small></div><div class="pair">1Il| !iL<small>one / capital I / lowercase l / bar</small></div><div class="pair">5S 2Z 6G 9g<small>ambiguous terminal pairs</small></div><div class="pair">rn m vv w<small>joined-shape stress test</small></div></div></section>
<section><div class="section-head"><h2>Nerd glyphs</h2><div class="label">v3.5.1 / representative sets</div></div><div class="glyphs">     󰉋 󰊢 󰆍      </div></section>
</main><footer>Codex Sans · Codex Serif · Codex Mono — readable derivatives built under SIL OFL 1.1</footer></body></html>"""
    output = output_dir / "index.html"
    output.write_text(html)
    print(f"Wrote {output.relative_to(ROOT)}")
    proofs = {
        "sans": ("Codex Sans Nerd Font Propo", "CodexSans", "UI + everyday web", "Good interface typography should disappear into the work. Open counters and distinct silhouettes keep instructions clear at ordinary reading sizes."),
        "serif": ("Codex Serif Nerd Font Propo", "CodexSerif", "Editorial + long-form", "Evidence changes the texture of a decision. A plausible explanation becomes durable only after the behavior is reproduced, observed, and written down."),
        "mono": ("Codex Mono Nerd Font Mono", "CodexMono", "True mono + Nerd icons", "cr  ea  create  recreate\n0O  1Il|  rn  m  vv  w\n main         󰉋\n┌────────┬────────┐\n│ 100% █ │ ✓ 42   │\n└────────┴────────┘"),
    }
    for slug, (family, filename, purpose, sample) in proofs.items():
        escaped_sample = sample.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        faces = "".join(
            f"@font-face{{font-family:'Proof';src:url('../dist/web/{filename}-{style}.woff2');font-weight:{weight};font-style:{italic}}}"
            for style, weight, italic in (("Regular", 400, "normal"), ("Italic", 400, "italic"), ("Bold", 700, "normal"), ("BoldItalic", 700, "italic"))
        )
        proof = f"""<!doctype html><html><head><meta charset="utf-8"><style>{faces}
*{{box-sizing:border-box}}body{{margin:0;padding:72px;background:#f5f2ea;color:#17201b;font-family:'Proof';font-synthesis:none}}.meta{{display:flex;justify-content:space-between;color:#087a4a;font:700 13px 'Proof';letter-spacing:.12em;text-transform:uppercase}}h1{{font:700 86px/.95 'Proof';margin:.45em 0}}.sample{{padding-block:34px;border-block:1px solid #cfd5cf;font:400 30px/1.55 'Proof'}}.styles{{margin-top:34px;font:22px/1.7 'Proof'}}i{{font-style:italic}}b{{font-weight:700}}</style></head><body><div class="meta"><span>{family}</span><span>{purpose}</span></div><h1>Made to be read.</h1><div class="sample">{escaped_sample}</div><div class="styles">Regular — ÀÉÖ ñ æ œ ß 0123456789<br><i>Italic — thoughtful emphasis</i><br><b>Bold — structure and hierarchy</b><br><b><i>Bold Italic — composed urgency</i></b></div></body></html>"""
        proof_path = output_dir / f"{slug}.html"
        proof_path.write_text(proof)
        print(f"Wrote {proof_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
