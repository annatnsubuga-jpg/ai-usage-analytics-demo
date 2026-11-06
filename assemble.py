#!/usr/bin/env python3
"""Inline the subset webfonts and the logo into index.html.

Fonts are subset to only the glyphs the dashboard uses and converted to WOFF2,
then base64-inlined. That keeps them out of the repo as standalone, installable
font files while still rendering correctly.
"""
import base64, re, os, sys, json
import os as _os
BASE = _os.path.dirname(_os.path.abspath(__file__))
def _p(*parts): return _os.path.join(BASE, *parts)


TPL   = _p('tpl.html')
FONTS = _p('brand')
LOGO  = _p('brand', 'demo-logo.min.svg')
OUT   = _p('index.html')

# --standalone builds a single self-contained file to preview before
# anything is pushed: fonts inlined, and the ENCRYPTED payload embedded so it
# still needs the password and works straight from a Downloads folder with no
# network and no repo involved.
STANDALONE = '--standalone' in sys.argv
if STANDALONE:
    OUT = _p('preview.html')

# Served as separate files from fonts/ rather than base64-inlined: it keeps
# index.html at ~65 KB instead of ~108 KB, and the browser caches the faces
# across visits. Light is deliberately absent — Regular covers the light weights.
FACES = [
    ('Redaction 35', 'Redaction35.woff2',      '400'),
]

css = []
for fam, fn, wt in FACES:
    assert os.path.exists(os.path.join(FONTS, fn)), 'missing font ' + fn
    if STANDALONE:
        b = base64.b64encode(open(os.path.join(FONTS, fn), 'rb').read()).decode()
        src = 'data:font/woff2;base64,%s' % b
    else:
        src = 'fonts/%s' % fn
    css.append(
        '@font-face{font-family:"%s";'
        'src:url(%s) format("woff2");'
        'font-weight:%s;font-style:normal;font-display:swap}' % (fam, src, wt))

logo = open(LOGO, encoding='utf-8').read().strip()

# svgo drops the viewBox, so recover the geometry from width/height before
# removing them, otherwise the SVG has no intrinsic aspect ratio and blows up.
m = re.search(r'<svg[^>]*?width="([\d.]+)"[^>]*?height="([\d.]+)"', logo)
if not m:
    raise SystemExit('logo: could not read width/height to rebuild the viewBox')
vb = '0 0 %s %s' % (m.group(1), m.group(2))
logo = re.sub(r'\s(?:width|height)="[\d.]+"', '', logo, count=2)
logo = logo.replace('<svg', '<svg viewBox="%s" fill="currentColor"' % vb, 1)

# drop the hardcoded ink so the mark follows the theme in dark mode
logo = re.sub(r'\sfill="#1[fF]283[dD]"', ' fill="currentColor"', logo)

html = open(TPL, encoding='utf-8').read()
html = html.replace('/*__FONTS__*/', '\n'.join(css))
html = html.replace('/*__LOGO__*/', logo)

if STANDALONE:
    # swap the network fetch for the ciphertext itself, embedded inline
    enc = open(_p('data.enc')).read().strip()
    old = "  const res = await fetch('data.enc?v=' + Date.now());\n" \
          "  if(!res.ok) throw new Error('Could not load the data file (HTTP ' + res.status + ')');\n" \
          "  const p = await res.json();"
    assert old in html, 'could not find the data.enc fetch block to replace'
    html = html.replace(old, "  const p = PAYLOAD;   /* standalone preview: data embedded */", 1)
    html = html.replace("<script>\n/* \u2550\u2550\u2550 decryption gate",
                        "<script>\nconst PAYLOAD = " + enc + ";\n/* \u2550\u2550\u2550 decryption gate", 1)

open(OUT, 'w', encoding='utf-8').write(html)
print('wrote %s  (%.1f KB)' % (OUT, os.path.getsize(OUT) / 1024))
print('font faces linked: %d  |  logo inlined: %d chars' % (len(FACES), len(logo)))
assert '__FONTS__' not in html and '__LOGO__' not in html, 'placeholder left behind'
