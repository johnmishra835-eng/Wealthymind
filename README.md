# Wealthymind Research Private Limited — website

Static website for Wealthymind Research Private Limited (CIN
U66190GJ2025PTC170746), a **fundraising and capital advisory firm** in
Ahmedabad: private equity, venture capital, pre-IPO, IPO and capital market
advisory, debt syndication and structured finance, plus transaction due
diligence.

No framework, no bundler, no runtime dependencies. The published site is plain
HTML, one CSS file and one JS file, deployable to any static host.

---

## Quick start

```bash
# Build the HTML pages from src/
python3 build.py

# Preview locally
python3 -m http.server 8000
# → http://localhost:8000
```

Python 3 is the only requirement, and only for the build. The **output** needs
nothing but a web server.

---

## How it works

The root `.html` files are **generated**. Do not edit them directly — your
changes will be overwritten on the next build.

```
build.py                  generator + CONFIG block (all shared facts live here)
src/layout.html           the page shell: head, header, drawer, footer
src/pages/*.html          one file per page — the <main> content only
assets/css/styles.css     design tokens and all styling
assets/js/main.js         drawer, theme toggle, scroll reveal, form validation
assets/img/               logo mark and favicon (SVG)
*.html                    ← generated output, committed so the site needs no build
```

`build.py` substitutes `{{TOKEN}}` placeholders and resolves
`{{#KEY}}…{{/KEY}}` conditional blocks (a field set to `OMIT` removes every
block that names it). Page titles and meta descriptions live in the `PAGES`
dict; company details live in `CONFIG`.

To add a page: create `src/pages/new-page.html`, add an entry to `PAGES`, add
it to the nav in `src/layout.html`, and rebuild.

### The build guard

This site was first built on a wrong premise — as a SEBI-registered research
analyst with subscription plans. That was completely removed. `build.py` now
**fails the build** if `SEBI`, `NSE`, `BSE`, `NISM`, `research analyst`,
`investor charter`, `SCORES`, `Smart ODR`, `principal officer` or `compliance
officer` reappear in the generated HTML.

The firm advises; it does not manage money, deal in securities, hold client
funds, or act as a registered intermediary. If that ever changes, update the
guard list deliberately rather than deleting it.

---

## Before you go live

**Read `PLACEHOLDERS.md`.** All company details are filled in. What remains is
a handful of dates and internal timelines in the legal pages, plus the contact
form endpoint.

The three legal pages are structured drafts for an advisory practice, not legal
advice — have them reviewed. Note especially that the confidentiality
commitments describe what you will actually do on a mandate.

There is deliberately **no team section**, because we had no names or bios. For
an advisory firm that is probably the most valuable thing to add next.

---

## Design

The palette and typography come from the brand wordmark rather than a generic
finance template.

| Token | Value | Source |
| --- | --- | --- |
| `--navy-800` | `#1b2947` | the "Wealthy" half of the wordmark |
| `--wine-700` | `#8b2332` | the "Mind" half, and the two dots in the mark |
| `--bg` | `#f5f6f8` | cool paper ground, chosen over warm cream to read institutional |
| Display | Newsreader | transitional serif with a true italic, matching the wordmark |
| Body / UI | IBM Plex Sans | institutional sans that holds up at small sizes in dense tables |

The three-slash motif from the logo mark is reused as the section marker
(`.eyebrow::before`) and as the faint diagonal field behind the hero, so the
brand device does structural work instead of appearing once in the header.

Both light and dark themes are defined. The toggle stores one key (`wm-theme`)
in `localStorage`; with no stored value the site follows the operating system.

Text colours were measured with a scripted contrast check. On the two page
surfaces — `--surface` `#ffffff` and `--bg` `#f5f6f8` — the light palette
measures `--fg` 17.4:1, `--fg-muted` 7.1:1, `--fg-subtle` 5.4:1 and `--accent`
8.8:1; the dark palette measures 14.2:1, 7.9:1, 5.6:1 and 6.4:1 on `#141e31`.
The lowest value anywhere is 5.0:1, against a 4.5:1 requirement.

### Logo

`assets/img/mark.svg` is a **vector reconstruction** of the supplied logo: the
three slashes and two dots as geometry, on a transparent background — which is
what "remove the white background" needs, since the shapes are now paths rather
than pixels on a white rectangle.

The wordmark is **live text** in the header and footer (`.lockup__word`), not
an image. That keeps it crisp at any size, recolourable per theme, readable by
search engines and screen readers, and free of a background entirely.

The whole lockup scales from one custom property:

```css
.lockup { --lockup-size: 1.5rem; }   /* drives mark and wordmark together */
.lockup--sm { --lockup-size: 1.125rem; }
```

Sizing the mark in plain `em` previously made it shrink wherever the inherited
font-size differed (the footer sets 14px), leaving the mark and wordmark
visibly mismatched between header and footer. The mark also carries an explicit
`aspect-ratio`, because a flex item with `width: auto` can collapse.

Two things to check against your master artwork:

- **Slash direction.** The bars lean top-left to bottom-right (`\\\`). If the
  original leans the other way, mirror the three `path` values in
  `assets/img/mark.svg` and in the inline `<svg class="lockup__mark">` in
  `src/layout.html`.
- **Wordmark typeface.** Newsreader was chosen as the closest available match.
  If your logo uses a licensed face, supply it and the lockup should switch to
  it — or supply the original as an SVG and we can use the real outlines.

`assets/img/favicon.svg` is the mark on a navy tile, with the same three bars
and two dots.

---

## Accessibility

### Checked by script

A Playwright audit runs every page at 375 / 768 / 1440 px in both themes and
asserts four things:

- **no horizontal scrolling** at any of the three widths
- **sequential heading levels** and exactly one `h1` per page
- **text contrast**, compositing translucent backgrounds and resolving both
  `rgb()` and `color(srgb …)` syntax before measuring
- **pointer targets** at 24×24 CSS px or larger (WCAG 2.2 AA), applying the
  inline-link exception only to links genuinely inside running prose

This found three real defects, all fixed: a heading-level skip from
`.callout h3`, `--fg-subtle` at 3.90:1, and `.eyebrow--on-inverse` recolouring
its marker but not its text. It currently reports zero issues.

Be aware it also produced two classes of false positive before the checker
itself was corrected — uncomposited `rgba()` backgrounds, and `color-mix()`
values parsed as 0–255 instead of 0–1. If you re-run it and see a large number
of contrast failures, suspect the checker before the stylesheet.

### Built in, not script-verified

Confirmed by targeted interaction tests rather than the sweep above:

- visible focus rings on every interactive element; skip link to main content
- keyboard-operable mobile drawer with a focus trap, `Escape` to close, and
  focus returned to the toggle
- form errors inline **and** in a focusable summary linking to each field,
  validated on blur rather than on keystroke
- `prefers-reduced-motion` respected; scroll reveals render immediately, and
  content is never left invisible when JavaScript does not run

### Not yet checked

No screen-reader pass, and no automated rule engine (axe, Lighthouse). Worth
doing both before launch — a scripted check catches measurable failures, not
confusing ones.

JavaScript is progressive enhancement throughout. With `main.js` blocked the
site still renders, navigates and reads correctly.

---

## Deployment

The repository root is the web root. Any static host works:

- **Netlify / Cloudflare Pages / Vercel** — no build command, publish
  directory `.`
- **GitHub Pages** — serve from the branch root
- **Any nginx/Apache host** — copy the repo contents to the document root

Point 404 handling at `404.html`. `robots.txt` and `sitemap.xml` are included;
update the domain in both, plus `SITE_URL` in `build.py`, if it is not
`wmrpl.com`.

Two things worth doing at the host level: serve over HTTPS with HSTS, and set a
long `Cache-Control` on `/assets/` while keeping the HTML short-lived.

### Self-hosting the fonts

Both fonts load from Google Fonts. For faster first paint and to avoid a
third-party request, download the two families, drop the `.woff2` files in
`assets/fonts/`, and replace the `<link>` in `src/layout.html` with local
`@font-face` rules using `font-display: swap`. The fallback stacks in
`styles.css` already degrade cleanly if the fonts never arrive.
