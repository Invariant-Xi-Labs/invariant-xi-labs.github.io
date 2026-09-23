# Invariant-Xi-Labs — site

Static site for I-XI Labs, served by GitHub Pages.

Pages: index (Overview), research, notes, tools, log (Lab Log), cv (CV).

## Editing
- Content, nav, and styles live in `build.py`. Run `python3 build.py` → writes `site/`.
  Copy `site/*` to the repo root (or edit the HTML directly; nothing depends on the generator).
- The CV PDF is `cv.html` printed with its own print stylesheet, so the page and the PDF
  cannot disagree. After any CV change: `python3 make_pdf.py`
  (needs `pip install playwright && playwright install chromium`, and IBM Plex Serif/Mono
  installed locally so the PDF doesn't fall back to other fonts).

## Deferred
- Instagram: add `("Instagram", "https://instagram.com/<handle>", False)` to `SOCIAL`.
- OPNsense / TheHive reports: add public links when available; they also fill the
  Disclosure section on the Research page.
- Repo links point at github.com/osim-framework/... — correct before and after transferring
  those repos into the org (GitHub redirects transferred repos).

## Lab Log images
Strip EXIF before committing (phone photos carry GPS): `exiftool -all= img/*.jpg`
