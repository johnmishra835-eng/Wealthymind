# Wealthymind Research Private Limited — website

Static marketing and compliance website for Wealthymind Research Private
Limited (CIN U66190GJ2025PTC170746), a research analyst entity in Gujarat,
India.

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
src/layout.html           the page shell: head, risk bar, header, drawer, footer
src/pages/*.html          one file per page — the <main> content only
assets/css/styles.css     design tokens and all styling
assets/js/main.js         drawer, theme toggle, scroll reveal, form validation
assets/img/               logo mark and favicon (SVG)
*.html                    ← generated output, committed so the site needs no build
```

`build.py` substitutes `{{TOKEN}}` placeholders in both the layout and the page
bodies. Page titles and meta descriptions live in the `PAGES` dict in
`build.py`; shared regulatory and contact details live in `CONFIG`.

To add a page: create `src/pages/new-page.html`, add an entry to `PAGES`, add it
to the nav in `src/layout.html`, and rebuild.

---

## Before you go live

**Read `PLACEHOLDERS.md`.** Every unverified value renders as a visible
highlighted `tbd` marker rather than as invented text, and there are about
thirty of them — registration numbers, address, contact details, officer names,
prices, complaint figures and policy dates.

`python3 build.py` prints the config values still unset on every run.

The most important item: the site describes the firm as a SEBI-registered
research analyst. **If that registration has not been granted, those claims
must be removed before publishing** — see section 4 of `PLACEHOLDERS.md`. The
legal pages are structured drafts, not legal advice; have them reviewed.

---

## Design

The palette and typography come from the brand wordmark rather than from a
generic finance template.

| Token | Value | Source |
| --- | --- | --- |
| `--navy-800` | `#1b2947` | the "Wealthy" half of the wordmark |
| `--wine-700` | `#8b2332` | the "Mind" half, and the two dots in the mark |
| `--bg` | `#f5f6f8` | cool paper ground, chosen over warm cream to read institutional |
| Display | Newsreader | transitional serif with a true italic, matching the wordmark |
| Body / UI | IBM Plex Sans | institutional sans that holds up at small sizes in dense regulatory tables |

The three-slash motif from the logo mark is reused as the section marker
(`.eyebrow::before`) and as the faint diagonal field behind the hero, so the
brand device does structural work instead of appearing once in the header.

Both light and dark themes are defined. The toggle stores one key
(`wm-theme`) in `localStorage`; with no stored value the site follows the
operating system. All colour pairs were measured against WCAG — normal text at
4.5:1 or better, large text at 3:1 or better, in both themes.

### Logo

`assets/img/mark.svg` is a **vector reconstruction** of the supplied logo: the
three slashes and two dots as geometry, on a transparent background — which is
what "remove the white background" needs, since the shapes are now paths rather
than pixels on a white rectangle.

The wordmark is **live text** in the header and footer (`.lockup__word`),
not an image. That keeps it crisp at any size, recolourable per theme, readable
by search engines and screen readers, and free of a background entirely.

Two things to check against your master artwork:

- **Slash direction.** The bars lean top-left to bottom-right (`\\\`). If the
  original leans the other way, mirror the three `path` values in
  `assets/img/mark.svg` and in the inline `<svg class="lockup__mark">` in
  `src/layout.html`.
- **Wordmark typeface.** Newsreader was chosen as the closest available match.
  If your logo uses a licensed face, supply it and the lockup should switch to
  it — or supply the original as an SVG and we can use the real outlines.

`assets/img/favicon.svg` is the mark simplified for small sizes (two bars, not
three, which mush together below 32px).

---

## Accessibility

Verified with a scripted audit across 11 pages × 3 viewport widths × 2 themes:

- no horizontal scrolling at 375 / 768 / 1440 px
- sequential heading levels, exactly one `h1` per page
- measured text contrast in both themes
- pointer targets at 24×24 CSS px or larger (WCAG 2.2 AA), with interactive
  controls at 44×46 px
- visible focus rings on every interactive element; skip link to main content
- keyboard-operable mobile drawer with focus trap, `Escape` to close and focus
  returned to the toggle
- form errors inline **and** in a focusable summary that links to each field,
  validated on blur rather than on keystroke
- `prefers-reduced-motion` respected; scroll reveals render immediately, and
  content is never left invisible when JavaScript does not run

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
`wealthymindresearch.com`.

Two things worth doing at the host level: serve over HTTPS with HSTS, and set a
long `Cache-Control` on `/assets/` while keeping the HTML short-lived.

### Self-hosting the fonts

Both fonts load from Google Fonts. For faster first paint and to avoid a
third-party request on a regulated financial site, download the two families,
drop the `.woff2` files in `assets/fonts/`, and replace the `<link>` in
`src/layout.html` with local `@font-face` rules using `font-display: swap`. The
fallback stacks in `styles.css` already degrade cleanly if the fonts never
arrive.
