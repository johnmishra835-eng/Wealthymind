#!/usr/bin/env python3
"""Static site generator for the Wealthymind Research website.

Composes src/layout.html + src/pages/*.html into plain HTML files at the
project root. No dependencies beyond the Python 3 standard library.

    python3 build.py

------------------------------------------------------------------------------
Business: fundraising and capital advisory — private equity, venture capital,
pre-IPO, IPO and capital market advisory, debt syndication and structured
finance, plus transaction due diligence.

This is an advisory firm, NOT a research analyst or a registered market
intermediary. Do not reintroduce SEBI/exchange registration numbers, an
investor charter, SCORES or ODR grievance routes, subscription plans, or named
Principal/Compliance Officers — none of those apply to this business.
------------------------------------------------------------------------------
"""

import datetime
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent.resolve()
SRC = ROOT / "src"
PAGES_DIR = SRC / "pages"

# ---------------------------------------------------------------------------
# CONFIG — replace any None with the real, verified value.
# Set a field to OMIT to drop it and every block that depends on it.
# ---------------------------------------------------------------------------

OMIT = "OMIT"

CONFIG = {
    # Verified from the Certificate of Incorporation.
    "CIN": "U66190GJ2025PTC170746",
    "GSTIN": "24AAECW3196N1ZS",
    # Public site URL, with a trailing slash.
    "SITE_URL": "https://www.wmrpl.com/",
    # Single office address, as supplied.
    "ADDRESS": (
        "5th Floor, Binori B Square 3, 524, Sindhubhavan Road, Bodakdev, "
        "Ahmedabad, Gujarat 380059"
    ),
    "EMAIL": "info@wmrpl.com",
    "EMAIL_ALT": "office@wmrpl.com",
    "PHONE": "+91 87348 10317",
}

PLACEHOLDER_HINTS = {
    "ADDRESS": "Office address, City, Gujarat – PIN",
    "EMAIL": "info@example.com",
    "EMAIL_ALT": "office@example.com",
    "PHONE": "+91 00000 00000",
    "GSTIN": "24XXXXXXXXXXXZX",
}

# ---------------------------------------------------------------------------
# Page registry: slug -> (title, meta description, noindex?)
# ---------------------------------------------------------------------------

PAGES = {
    "index.html": (
        "Wealthymind Research Private Limited — Fundraising & Capital Advisory",
        "Wealthymind Research Private Limited is a Fundraising and Capital "
        "Advisory firm in Ahmedabad: Private Equity, Venture Capital, Pre-IPO, "
        "IPO and Capital Market Advisory, Debt Syndication and Structured "
        "Finance, with transaction Due Diligence.",
    ),
    "about.html": (
        "About Us — Wealthymind Research Private Limited",
        "Who we are, how we work on a mandate, and the principles behind our "
        "Fundraising and Capital Advisory practice in Ahmedabad.",
    ),
    "services.html": (
        "Services — Wealthymind Research Private Limited",
        "Private Equity and Venture Capital raises, Pre-IPO Placements, IPO and "
        "Capital Market Advisory, Debt Syndication and Structured Finance.",
    ),
    "due-diligence.html": (
        "Due Diligence — Wealthymind Research Private Limited",
        "Buy-side, sell-side and vendor Due Diligence supporting fundraising "
        "and capital market transactions: financial, commercial and tax scope.",
    ),
    "contact.html": (
        "Contact — Wealthymind Research Private Limited",
        "Reach the Wealthymind Research capital advisory team in Ahmedabad to "
        "discuss a fundraising mandate or a Due Diligence engagement.",
    ),
    "disclaimer.html": (
        "Disclaimer — Wealthymind Research Private Limited",
        "The basis on which information on this website is provided, and the "
        "limits of our advisory role.",
    ),
    "privacy-policy.html": (
        "Privacy Policy — Wealthymind Research Private Limited",
        "What personal and business information Wealthymind Research collects, "
        "why, how it is protected, and the choices available to you.",
    ),
    "terms-and-conditions.html": (
        "Terms of Use — Wealthymind Research Private Limited",
        "The terms on which this website may be used, and how an advisory "
        "engagement is actually created.",
    ),
    "thank-you.html": (
        "Thank you — Wealthymind Research Private Limited",
        "Your enquiry has reached the Wealthymind Research desk. Here is what "
        "happens next.",
        True,
    ),
    "404.html": (
        "Page not found — Wealthymind Research Private Limited",
        "The page you requested could not be found.",
        True,
    ),
}


def is_omitted(key: str) -> bool:
    return CONFIG.get(key) == OMIT


def render_conditionals(template: str) -> str:
    """Resolve {{#KEY}}...{{/KEY}} blocks.

    The block is kept when CONFIG[KEY] holds a value or is still an unfilled
    placeholder (so the visible `tbd` marker survives), and dropped entirely
    when CONFIG[KEY] is OMIT. Innermost blocks resolve first, so nesting works.
    """
    pattern = re.compile(
        r"[ \t]*\{\{#([A-Z_]+)\}\}\n?(((?!\{\{#)(?!\{\{/).|\n)*?)[ \t]*\{\{/\1\}\}\n?",
        re.S,
    )

    def resolve(match):
        key, body = match.group(1), match.group(2)
        if key not in CONFIG:
            raise KeyError(f"unknown conditional token {{{{#{key}}}}}")
        return "" if is_omitted(key) else body

    previous = None
    while previous != template:
        previous = template
        template = pattern.sub(resolve, template)

    leftover = re.search(r"\{\{[#/][A-Z_]+\}\}", template)
    if leftover:
        raise ValueError(f"unbalanced conditional block: {leftover.group(0)}")
    return template


def tbd(key: str) -> str:
    """Render a config value, or a visible placeholder if it is unset."""
    value = CONFIG.get(key)
    if value == OMIT:
        return ""
    if value:
        return html.escape(str(value))
    hint = PLACEHOLDER_HINTS.get(key, key)
    return f'<span class="tbd">{html.escape(hint)}</span>'


def mailto(key: str) -> str:
    value = CONFIG.get(key)
    if value == OMIT:
        return ""
    if value:
        safe = html.escape(value)
        return f'<a href="mailto:{safe}">{safe}</a>'
    return tbd(key)


def tel(key: str) -> str:
    value = CONFIG.get(key)
    if value == OMIT:
        return ""
    if value:
        safe = html.escape(value)
        digits = re.sub(r"[^\d+]", "", value)
        return f'<a href="tel:{digits}">{safe}</a>'
    return tbd(key)


def tokens() -> dict:
    return {
        "YEAR": str(datetime.date.today().year),
        "CIN": tbd("CIN"),
        "GSTIN": tbd("GSTIN"),
        "SITE_URL": html.escape(CONFIG["SITE_URL"]),
        "ADDRESS": tbd("ADDRESS"),
        "EMAIL": tbd("EMAIL"),
        "EMAIL_LINK": mailto("EMAIL"),
        "EMAIL_ALT": tbd("EMAIL_ALT"),
        "EMAIL_ALT_LINK": mailto("EMAIL_ALT"),
        "PHONE": tbd("PHONE"),
        "PHONE_LINK": tel("PHONE"),
    }


def render(template: str, values: dict) -> str:
    def sub(match):
        key = match.group(1)
        if key not in values:
            raise KeyError(f"unknown template token {{{{{key}}}}}")
        return values[key]

    return re.sub(r"\{\{([A-Z_]+)\}\}", sub, template)


def main() -> int:
    layout = render_conditionals((SRC / "layout.html").read_text(encoding="utf-8"))
    base = tokens()

    missing = [k for k, v in CONFIG.items() if v is None]
    omitted = [k for k in CONFIG if is_omitted(k)]
    written = []

    for slug, meta in PAGES.items():
        source = PAGES_DIR / slug
        if not source.exists():
            print(f"  ! missing page source: {source}", file=sys.stderr)
            return 1

        title, description = meta[0], meta[1]
        noindex = len(meta) > 2 and meta[2]

        body = render_conditionals(source.read_text(encoding="utf-8").rstrip("\n"))
        values = dict(base)
        values.update(
            {
                "TITLE": html.escape(title),
                "DESCRIPTION": html.escape(description),
                "SLUG": "" if slug == "index.html" else slug,
                "ROBOTS": '<meta name="robots" content="noindex" />'
                if noindex
                else "",
                "BODY": render(body, base),
            }
        )

        (ROOT / slug).write_text(render(layout, values) + "\n", encoding="utf-8")
        written.append(slug)

    # Nothing on this site should imply a regulated-intermediary status.
    banned = {
        "SEBI": r"\bSEBI\b",
        "SCORES portal": r"scores\.sebi\.gov\.in",
        "Smart ODR": r"smartodr",
        "research analyst": r"research analyst",
        "investor charter": r"investor charter",
        "NISM": r"\bNISM\b",
        "BSE/NSE enlistment": r"\b(BSE|NSE)\b",
        "principal officer": r"principal officer",
        "compliance officer": r"compliance officer",
    }
    leaks = []
    for slug in written:
        text = (ROOT / slug).read_text(encoding="utf-8")
        for label, rx in banned.items():
            if re.search(rx, text, re.I):
                leaks.append(f"{slug}: {label}")

    print(f"Built {len(written)} pages:")
    for slug in written:
        print(f"  · {slug}")

    if missing:
        print(f"\n  {len(missing)} placeholder(s) unset (render as `tbd` markers):")
        for key in missing:
            print(f"    · {key}")
    else:
        print("\n  All placeholders filled.")

    if omitted:
        print(f"\n  {len(omitted)} field(s) set to OMIT:")
        for key in omitted:
            print(f"    · {key}")

    if leaks:
        print(f"\n  !! {len(leaks)} regulated-intermediary reference(s) found:")
        for leak in leaks:
            print(f"    · {leak}")
        print("  This is an advisory firm, not a registered intermediary.")
        return 1

    print("\n  No regulated-intermediary references in output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
