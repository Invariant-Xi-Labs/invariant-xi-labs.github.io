# Invariant-Xi-Labs — site

Static site for I-XI Labs. Served by GitHub Pages at https://invariant-xi-labs.github.io/

Pages: index (Overview), research, notes, tools, log (Lab Log). `build.py` regenerates all
five from one source; editing the HTML directly also works.

## Deferred (add when ready, then rebuild)
- Instagram: add `("Instagram", "https://instagram.com/<handle>", False)` to `SOCIAL` in build.py.
- Contact email / PGP fingerprint: add a row to the contact block on the Overview page.
- Repo links point at github.com/osim-framework/... — correct before and after transferring
  those repos into the org (GitHub redirects transferred repos).

## Lab Log images
Strip EXIF before committing (phone photos carry GPS): `exiftool -all= img/*.jpg`
