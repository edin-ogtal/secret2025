#!/usr/bin/env python3
"""
make_qr.py
Create a PNG QR for each slug in data/pages.json.
Install dependency:
  pip install qrcode[pil]
Usage:
  python tools/make_qr.py --base https://<user>.github.io/<repo>/ --out qr/
"""
import argparse, json, os, sys

try:
    import qrcode
except ImportError:
    print("This script needs the 'qrcode' package. Install with: pip install qrcode[pil]")
    sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Base site URL, e.g. https://user.github.io/repo/")
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


# # 1) Install dependency once
# pip install qrcode[pil]

# # 2) Generate PNGs for all slugs
# python tools/make_qr.py --base https://<username>.github.io/<repo-name>/ --out qr/
