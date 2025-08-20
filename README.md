# secret2025


# A) Create 15 new clues
python tools/slugger.py --count 15

# (optional) Edit data/pages.json to customize title/text/image/video for each

# B) Build all pages
python tools/generate_pages.py

# C) Commit & push so GitHub Pages deploys
git add .
git commit -m "Add 15 clues and build pages"
git push

# D) Make QR codes for printing
python tools/make_qr.py --base https://<username>.github.io/<repo-name>/ --out qr/
