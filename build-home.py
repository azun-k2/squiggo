#!/usr/bin/env python3
"""Squiggo's richer home page: one template, strings in home/<lang>.json (en = the source of truth).
Rewrites the tagline and everything from the first family:shot marker to family:apps in <lang>/index.html.
Run `../_tools/site-family.py apply` + `lint` afterwards (it refreshes badges, nav, the shot images and More apps)."""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
e = lambda s: html.escape(s, quote=False)


def dev(up, n, cls):
    return f'<div class="dev {cls}"><img src="{up}img/play-{n}.jpg" alt="" width="1100" height="768" loading="lazy"></div>'


def section(s):
    chips = "".join(f"<li>{e(c)}</li>" for c in s.get("chips", []))
    chips = f'\n  <ul class="sq-chips">{chips}</ul>' if chips else ""
    return (f'<section class="card sq-sec"><span class="sq-ico" aria-hidden="true">{s["icon"]}</span>\n  <h2>{e(s["h"])}</h2>\n'
            f'  <p>{e(s["p"])}</p>{chips}\n</section>\n')


def page_html(d, up):
    stats = "".join(f'<li><b>{e(n)}</b><span>{e(l)}</span></li>' for n, l in d["stats"])
    s = d["sections"]
    p, m, f = d["privacy"], d["mac"], d["faq"]
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>\n" for q, a in f["items"])
    return f'''<!-- squiggo:home -->
<p class="sq-sub">{e(d["sub"])}</p>
<p class="sq-note">{e(d["note"])}</p>
<ul class="sq-stats">{stats}</ul>

<!-- family:shot --><div class="gallery">{dev(up, 2, "c")}{dev(up, 1, "l")}{dev(up, 4, "r")}</div>
{section(s[0])}
{section(s[1])}
{section(s[2])}
<!-- family:shot2 --><div class="pair">{dev(up, 3, "")}{dev(up, 5, "")}</div>

{section(s[3])}
{section(s[4])}
{section(s[5])}
<section class="card sq-sec sq-band"><span class="sq-ico" aria-hidden="true">{p["icon"]}</span>
  <h2>{e(p["h"])}</h2>
  <p>{p["pHtml"]}</p>
</section>

<section class="card sq-sec"><span class="sq-ico" aria-hidden="true">{m["icon"]}</span>
  <h2>{e(m["h"])}</h2>
  <p>{e(m["p"])}</p>
  <p class="note">{e(d["requires"])}</p>
</section>

<section class="card sq-faq">
  <h2>{e(f["h"])}</h2>
{faq}</section>

<section class="sq-final">
  <h2>{e(d["final"]["h"])}</h2>
  <a class="sq-cta" href="#">{e(d["final"]["cta"])}</a>
</section>
<!-- /squiggo:home -->

'''


def build(lang):
    src = ROOT / "home" / f"{lang}.json"
    page = ROOT / ("index.html" if lang == "en" else f"{lang}/index.html")
    if not src.exists() or not page.exists():
        print(f"{lang}: skipped (no strings or no page)"); return False
    d = json.loads(src.read_text())
    up = "" if lang == "en" else "../"
    t = page.read_text()
    t = re.sub(r'<p class="tagline">.*?</p>', lambda _: f'<p class="tagline">{e(d["tagline"])}</p>', t, count=1, flags=re.S)
    a = t.find("<!-- squiggo:home -->")
    if a < 0: a = t.index("<!-- family:shot -->")
    b = t.index("<!-- /squiggo:home -->") + len("<!-- /squiggo:home -->") if "<!-- /squiggo:home -->" in t else t.index("<!-- family:apps -->")
    t = t[:a] + page_html(d, up).rstrip("\n") + "\n\n" + t[b:].lstrip("\n")
    page.write_text(t)
    return True


if __name__ == "__main__":
    langs = sys.argv[1:] or ["en"] + sorted(p.parent.name for p in ROOT.glob("*/index.html") if (ROOT / "home" / f"{p.parent.name}.json").exists())
    print(sum(build(l) for l in langs), "pages written")
