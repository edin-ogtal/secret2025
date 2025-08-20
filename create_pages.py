# Create a starter GitHub Pages scaffold for a scavenger hunt with unique random links.
import os, json, random, string, zipfile, textwrap, datetime, pathlib

base = "/mnt/data/gh-pages-scavenger-starter"
os.makedirs(base, exist_ok=True)

# Basic files
readme = """# Scavenger Hunt — GitHub Pages Starter

This repo is a minimal static site for a QR scavenger hunt.
Each "secret page" lives in `pages/<random-slug>/index.html`.
Your QR codes should point to: `https://<username>.github.io/<repo-name>/pages/<slug>/`.

## Quick start
1) Push this repo to GitHub (ideally a **public** repo for Pages).
2) Go to **Settings → Pages** and choose **Deploy from a branch**,
   then set **Branch: main** and **Folder: / (root)**. Save.
3) After it builds, your site will be at `https://<username>.github.io/<repo-name>/`.

## Add or change pages
- Edit `data/pages.json` to change text/images/video embeds.
- Run `python tools/generate_pages.py` to regenerate HTML files.
- Commit and push.

## Generate QR codes
Run: `python tools/make_qr.py --base https://<username>.github.io/<repo-name>/ --out qr/`
This writes PNGs in `qr/` for each page slug.

> Note: If you don't have Python, you can also use any online QR generator with the full URLs.
"""

index_html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scavenger Hunt</title>
  <link rel="icon" href="favicon.ico">
  <style>
    body{font-family: system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.5;margin:0;background:#f7f7fb;color:#111}
    header{padding:2.5rem 1rem;text-align:center;background:white;border-bottom:1px solid #eaeaea}
    main{max-width:900px;margin:2rem auto;padding:0 1rem}
    .card{background:white;border:1px solid #eaeaea;border-radius:12px;padding:1rem 1.25rem;margin:1rem 0;box-shadow:0 1px 2px rgba(0,0,0,.03)}
    code{background:#f0f0f5;padding:.2rem .35rem;border-radius:6px}
    footer{padding:2rem 1rem;text-align:center;color:#666}
    a{color:inherit}
  </style>
</head>
<body>
  <header>
    <h1>🏁 Scavenger Hunt</h1>
    <p>Scan a QR code to jump to a secret page. These URLs are intentionally hard to guess.</p>
  </header>
  <main>
    <div class="card">
      <h2>How this works</h2>
      <ol>
        <li>Each secret page lives at <code>/pages/&lt;random-slug&gt;/</code>.</li>
        <li>Print QR codes pointing to those URLs.</li>
        <li>The page can show text, an image, and/or an embedded video.</li>
      </ol>
      <p><strong>Tip:</strong> You can hide this homepage by removing or replacing it.</p>
    </div>
    <div class="card">
      <h2>Example links</h2>
      <ul>
        <li><a href="pages/orchid-silk-7f3b2/">Example page A</a></li>
        <li><a href="pages/nebula-fox-d1a9e/">Example page B</a></li>
      </ul>
    </div>
  </main>
  <footer>Built with ❤️ for GitHub Pages</footer>
</body>
</html>
"""

favicon_bytes = bytes.fromhex(
    # a tiny 16x16 transparent favicon (ICO) - placeholder
    "00000100010010100000010001002801000016000000280000001000000020000000010020000000000000040000"
    "00000000000000000000000000000000000000000000000000000000000000"
)

nojekyll = ""  # presence of file disables Jekyll processing

# Data model
os.makedirs(os.path.join(base, "data"), exist_ok=True)
pages_json = [
    {
        "slug": "orchid-silk-7f3b2",
        "title": "Clue: The Hidden Atrium",
        "text": "Nice find! Look for the tallest window near the old library.",
        "image": "assets/example.jpg",
        "video_embed": ""
    },
    {
        "slug": "nebula-fox-d1a9e",
        "title": "Clue: Echoes in the Stairwell",
        "text": "You’re getting warm. Count 12 steps and check beneath the rail.",
        "image": "",
        "video_embed": "https://www.youtube.com/embed/dQw4w9WgXcQ"
    }
]

# Assets
os.makedirs(os.path.join(base, "assets"), exist_ok=True)
with open(os.path.join(base, "assets", "example.jpg"), "wb") as f:
    # create a tiny placeholder JPG (1x1 white)
    f.write(bytes.fromhex("ffd8ffe000104a46494600010101006000600000ffdb00430003020203020203"
                          "03030304030405080a0a09090808090d0e0c0b0e0d11161415131115131d1a17"
                          "161a1d23201a1a20232a25252a34312c31343f3c3f4c4a4c5e5c6f7e919effd9"))

# Tools scripts
os.makedirs(os.path.join(base, "tools"), exist_ok=True)

generate_pages_py = r"""#!/usr/bin/env python3
import json, os, sys, html

BASE = os.path.dirname(os.path.dirname(__file__))

TEMPLATE = """ + 'r"""' + """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    body{font-family: system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.55;margin:0;background:#0b0b12;color:#f3f3f7}
    main{max-width:760px;margin:0 auto;padding:2rem 1rem 4rem}
    .card{background:#11131a;border:1px solid #22252f;border-radius:14px;padding:1.25rem 1.25rem;box-shadow:0 1px 2px rgba(0,0,0,.3);margin-top:1rem}
    h1{font-size:1.6rem;margin:.2rem 0 0}
    p{margin:.75rem 0}
    img, iframe{width:100%;max-width:100%;border-radius:10px}
    a{color:#9fd1ff}
    .slug{opacity:.65;font-size:.85rem}
  </style>
</head>
<body>
  <main>
    <div class="card">
      <div class="slug">/pages/{slug}/</div>
      <h1>{title}</h1>
      <p>{text}</p>
      {media}
      <p><a href="../../">Back to home</a></p>
    </div>
  </main>
</body>
</html>""" + '"""' 

def render_media(image, video_embed):
    if video_embed:
        return f'<div style="margin-top:1rem"><iframe src="{html.escape(video_embed)}" loading="lazy" frameborder="0" allowfullscreen></iframe></div>'
    if image:
        return f'<div style="margin-top:1rem"><img src="../../{html.escape(image)}" alt="clue image"></div>'
    return ""

def main():
    with open(os.path.join(BASE, "data", "pages.json"), "r", encoding="utf-8") as f:
        pages = json.load(f)
    for p in pages:
        slug = p["slug"]
        outdir = os.path.join(BASE, "pages", slug)
        os.makedirs(outdir, exist_ok=True)
        media = render_media(p.get("image",""), p.get("video_embed",""))
        html_out = TEMPLATE.format(slug=html.escape(slug), title=html.escape(p["title"]), text=html.escape(p["text"]), media=media)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as outf:
            outf.write(html_out)
    print(f"Generated {len(pages)} pages into /pages/<slug>/index.html")

if __name__ == "__main__":
    main()

make_qr_py = r"""#!/usr/bin/env python3
import argparse, json, os, sys
try:
    import qrcode
except ImportError:
    print("This script needs the 'qrcode' package. Install with: pip install qrcode[pil]")
    sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Base site URL like https://user.github.io/repo/")
    ap.add_argument("--out", default="qr", help="Output folder for PNGs")
    ap.add_argument("--prefix", default="pages", help="Path prefix (default: pages)")
    ap.add_argument("--json", default="data/pages.json", help="Path to pages.json")
    args = ap.parse_args()

    with open(args.json, "r", encoding="utf-8") as f:
        pages = json.load(f)

    os.makedirs(args.out, exist_ok=True)
    for p in pages:
        slug = p["slug"].strip("/")
        url = f"{args.base.rstrip('/')}/{args.prefix}/{slug}/"
        img = qrcode.make(url)
        outpath = os.path.join(args.out, f"{slug}.png")
        img.save(outpath)
        print("Wrote", outpath, "->", url)

if __name__ == "__main__":
    main()
"""

slugger_py = r"""#!/usr/bin/env python3
import random, string, json, argparse

WORDS_A = ["orchid","nebula","cobalt","ember","velvet","atlas","raven","quartz","pepper","polar","tiger","delta","echo","lunar","moss","onyx","panda","sable","topaz","ultra","vivid","willow","xenon","yarrow","zephyr"]
WORDS_B = ["silk","fox","sage","kite","glow","wave","trail","mist","flare","drift","harbor","grove","stone","bloom","ridge","vale","spark","meadow","hollow","dawn","dusk","crest","wisp","field","nook"]

def rand_slug():
    return f"{random.choice(WORDS_A)}-{random.choice(WORDS_B)}-" + "".join(random.choices("0123456789abcdef", k=5))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--json", default="data/pages.json")
    args = ap.parse_args()

    pages = []
    for _ in range(args.count):
        slug = rand_slug()
        pages.append({
            "slug": slug,
            "title": f"Clue: {slug.replace('-', ' ').title()}",
            "text": "Your custom message here.",
            "image": "",
            "video_embed": ""
        })
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2)
    print(f"Wrote {args.count} placeholder entries to {args.json}")

if __name__ == "__main__":
    main()
"""

workflow_yaml = """name: github-pages
on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v5
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""

# Write files
with open(os.path.join(base, "README.md"), "w", encoding="utf-8") as f: f.write(readme)
with open(os.path.join(base, "index.html"), "w", encoding="utf-8") as f: f.write(index_html)
with open(os.path.join(base, "data", "pages.json"), "w", encoding="utf-8") as f: json.dump(pages_json, f, indent=2)
with open(os.path.join(base, ".nojekyll"), "w", encoding="utf-8") as f: f.write(nojekyll)
with open(os.path.join(base, "tools", "generate_pages.py"), "w", encoding="utf-8") as f: f.write(generate_pages_py)
with open(os.path.join(base, "tools", "make_qr.py"), "w", encoding="utf-8") as f: f.write(make_qr_py)
with open(os.path.join(base, "tools", "slugger.py"), "w", encoding="utf-8") as f: f.write(slugger_py)
os.makedirs(os.path.join(base, ".github", "workflows"), exist_ok=True)
with open(os.path.join(base, ".github", "workflows", "pages.yml"), "w", encoding="utf-8") as f: f.write(workflow_yaml)
with open(os.path.join(base, "favicon.ico"), "wb") as f: f.write(favicon_bytes)

# Pre-generate pages
os.makedirs(os.path.join(base, "pages"), exist_ok=True)
# simulate running generate_pages.py
import json, html
def render_media(image, video_embed):
    if video_embed:
        return f'<div style="margin-top:1rem"><iframe src="{html.escape(video_embed)}" loading="lazy" frameborder="0" allowfullscreen></iframe></div>'
    if image:
        return f'<div style="margin-top:1rem"><img src="../../{html.escape(image)}" alt="clue image"></div>'
    return ""

for p in pages_json:
    outdir = os.path.join(base, "pages", p["slug"])
    os.makedirs(outdir, exist_ok=True)
    media = render_media(p.get("image",""), p.get("video_embed",""))
    html_out = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{p['title']}</title>
  <style>
    body{{font-family: system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.55;margin:0;background:#0b0b12;color:#f3f3f7}}
    main{{max-width:760px;margin:0 auto;padding:2rem 1rem 4rem}}
    .card{{background:#11131a;border:1px solid #22252f;border-radius:14px;padding:1.25rem 1.25rem;box-shadow:0 1px 2px rgba(0,0,0,.3);margin-top:1rem}}
    h1{{font-size:1.6rem;margin:.2rem 0 0}}
    p{{margin:.75rem 0}}
    img, iframe{{width:100%;max-width:100%;border-radius:10px}}
    a{{color:#9fd1ff}}
    .slug{{opacity:.65;font-size:.85rem}}
  </style>
</head>
<body>
  <main>
    <div class="card">
      <div class="slug">/pages/{p['slug']}/</div>
      <h1>{p['title']}</h1>
      <p>{p['text']}</p>
      {media}
      <p><a href="../../">Back to home</a></p>
    </div>
  </main>
</body>
</html>"""
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_out)

# Zip it
zip_path = "/mnt/data/gh-pages-scavenger-starter.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(base):
        for file in files:
            full = os.path.join(root, file)
            rel = os.path.relpath(full, base)
            z.write(full, arcname=os.path.join("gh-pages-scavenger-starter", rel))

zip_path
