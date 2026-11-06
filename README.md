# AI Usage Analytics — demo

A working demo of an internal dashboard reporting AI tool adoption and cost across an
organisation. **Fabricated data, for demonstration purposes only.** Every name, department, job
title, project and figure is invented, Ashgrove Press does not exist, and any resemblance to a real
organisation or person is coincidental. The structure mirrors a dashboard built for a real
organisation; none of its data, people, departments or projects appear here. It is published to
show the build.

One button on the way in, then the dashboard. No password.

## What it answers

Most organisations bought AI seats in the last year and cannot say what they got for them. The
data exists but it is split across an admin console, a usage API and a set of invoices, and the
three do not agree with each other. This puts it in one place.

Four views: rankings, monthly adoption, a rolling usage snapshot, and cost.

## Decisions worth explaining

**Rankings are scored out of 100 in five categories, then averaged.** Volume, breadth,
consistency, output and building. No single count describes how deeply someone has taken a tool
on, and any one of them alone crowns the wrong person. The weights are printed on the page so they
can be argued with, and you can rank on a single product to remove the weighting entirely.

**Spend is ranked on its own and has no podium.** Costing the most is not something to win.

**Only the top fifteen are listed.** Nobody appears at the bottom of anything.

**No forecasting.** An early version projected monthly spend from a seven day run rate. The data
was spiky enough that a run rate, a 28 day model and flat arithmetic gave three defensible answers
with a factor of two between them, and the page was showing the highest. It now shows actual
monthly history and lets the reader draw their own line.

**Only complete days are counted**, and the current month states its cutoff on the page. The day
count is derived from the data rather than typed, so it cannot drift.

**Seats and metered usage are never added together.** They are separate charges, invoiced
differently and often reported in different currencies. Quoting either one alone misstates the cost.

**The data is still encrypted at rest** even though it is fictional, because that is how the real
build works and it is part of what the demo demonstrates. PBKDF2-SHA256 at 250,000 iterations,
then AES-256-GCM, decrypted in the browser.

## It keeps itself current

`generate.py` rolls the window to end on the last complete month, keeps the cast of people stable,
and re-rolls the activity with a gentle upward drift. A scheduled job runs it monthly. Because the
data is invented there is no secret to supply, so the whole thing refreshes unattended.

```
python3 generate.py
python3 encrypt.py demo
python3 assemble.py --standalone --nogate demo
```

| File | What it is |
|---|---|
| `tpl.html` | The dashboard template, with placeholders for the font and logo |
| `assemble.py` | Inlines the webfont and logo, writes the page |
| `generate.py` | Rolls the window forward from `template.json` |
| `template.json` | The fictional dataset the generator works from |
| `encrypt.py` | gzip, then AES-256-GCM |
| `preview.html` | Single self contained file, works offline |

## Typeface

Body text uses the system stack. Display numerals use **Redaction 35** by MCKL, under the SIL Open
Font License 1.1, subset to the glyphs actually used.
