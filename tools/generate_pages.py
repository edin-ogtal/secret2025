#!/usr/bin/env python3
"""
generate_pages.py
Read data/pages.json and render each entry to /pages/<slug>/index.html
Usage:
  python tools/generate_pages.py
"""
import json, os, html

BASE = os.path.dirname(os.path.dirname(__file__))

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
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
      <div class="slug">/pages/{slug}/</div>
      <h1>{title}</h1>
      <p>{text}</p>
      {media}
      <p><a href="../../">Back to home</a></p>
    </div>
  </main>
</body>
</html>"""

def render_media(image, video_embed):
    if video_embed:
        return f'<div style="margin-top:1rem"><iframe src="{html.escape(video_embed)}" loading="lazy" frameborder="0" allowfullscreen title="video clue"></iframe></div>'
    if image:
        return f'<div style="margin-top:1rem"><img src="../../{html.escape(image)}" alt="clue image"></div>'
    return ""

def main():
    json_path = os.path.join(BASE, "data", "pages.json")
    if not os.path.exists(json_path):
        raise SystemExit("Missing data/pages.json. Create it or run: python tools/slugger.py")
    with open(json_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    out_root = os.path.join(BASE, "pages")
    os.makedirs(out_root, exist_ok=True)
    for p in pages:
        slug = p["slug"].strip("/")
        outdir = os.path.join(out_root, slug)
        os.makedirs(outdir, exist_ok=True)
        media = render_media(p.get("image",""), p.get("video_embed",""))
        html_out = TEMPLATE.format(
            slug=html.escape(slug),
            title=html.escape(p.get("title","")),
            text=html.escape(p.get("text","")),
            media=media
        )
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as outf:
            outf.write(html_out)
    print(f"Generated {len(pages)} pages into /pages/<slug>/index.html")

if __name__ == "__main__":
    main()
