#!/usr/bin/env python3
"""
slugger.py
Create random slugs and write them to data/pages.json (overwriting or creating the file).
Each entry is a stub you can later edit.
Usage:
  python tools/slugger.py --count 10
  python tools/slugger.py --count 5 --append
"""
import argparse, json, os, random

WORDS_A = ["orchid","nebula","cobalt","ember","velvet","atlas","raven","quartz","pepper","polar",
           "tiger","delta","echo","lunar","moss","onyx","panda","sable","topaz","ultra",
           "vivid","willow","xenon","yarrow","zephyr"]
WORDS_B = ["silk","fox","sage","kite","glow","wave","trail","mist","flare","drift",
           "harbor","grove","stone","bloom","ridge","vale","spark","meadow","hollow","dawn",
           "dusk","crest","wisp","field","nook"]

def rand_slug():
    return f"{random.choice(WORDS_A)}-{random.choice(WORDS_B)}-" + "".join(random.choices("0123456789abcdef", k=5))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=5, help="How many slugs to create")
    ap.add_argument("--json", default="data/pages.json", help="Path to pages.json")
    ap.add_argument("--append", action="store_true", help="Append instead of overwrite")
    args = ap.parse_args()

    pages = []
    if args.append and os.path.exists(args.json):
        with open(args.json, "r", encoding="utf-8") as f:
            pages = json.load(f)

    existing = {p["slug"] for p in pages}
    added = 0
    while added < args.count:
        s = rand_slug()
        if s in existing:
            continue
        pages.append({
            "slug": s,
            "title": f"Clue: {s.replace('-', ' ').title()}",
            "text": "Your custom message here.",
            "image": "",
            "video_embed": ""
        })
        existing.add(s)
        added += 1

    os.makedirs(os.path.dirname(args.json), exist_ok=True)
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2)
    print(f"Wrote {len(pages)} entries to {args.json} (added {added}).")

if __name__ == "__main__":
    main()


# # Make 10 brand new entries (overwrites data/pages.json)
# python tools/slugger.py --count 10

# # Add 5 more entries to the existing file
# python tools/slugger.py --count 5 --append
