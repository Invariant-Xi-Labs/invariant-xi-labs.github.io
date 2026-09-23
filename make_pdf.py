#!/usr/bin/env python3
"""Print site/cv.html to site/Alec_Sanchez_CV.pdf using the page's own print stylesheet.

Run after build.py whenever the CV changes:  python3 make_pdf.py
Needs Playwright:  pip install playwright && playwright install chromium
"""
import asyncio, pathlib
from playwright.async_api import async_playwright

SRC = pathlib.Path("site/cv.html").resolve()
OUT = pathlib.Path("site/Alec_Sanchez_CV.pdf")

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page()
        await pg.emulate_media(media="print", color_scheme="light")
        await pg.goto(SRC.as_uri(), wait_until="networkidle")
        await pg.evaluate("document.fonts.ready")
        await pg.pdf(path=str(OUT), format="Letter", print_background=True,
                     prefer_css_page_size=True, tagged=True, outline=True)
        await b.close()
    print(f"wrote {OUT}")

asyncio.run(main())
