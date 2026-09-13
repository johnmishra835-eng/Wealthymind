#!/usr/bin/env python3
"""Static site generator for the Wealthymind Research website.

Composes src/layout.html + src/pages/*.html into plain HTML files at the
project root. No dependencies beyond the Python 3 standard library.

    python3 build.py

------------------------------------------------------------------------------
FILL IN THE CONFIG BLOCK BELOW BEFORE GOING LIVE.
Any value left as None renders as a visible `tbd` placeholder on every page
that uses it, so nothing silently ships as invented information.
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
# CONFIG — replace each None with the real, verified value.
# ---------------------------------------------------------------------------

# Sentinel: drop this field and any block that depends on it, instead of
# rendering a placeholder. Use it for details that genuinely do not exist yet —
# printing "N.A." on a compliance page looks worse than not having the row.
OMIT = "OMIT"

CONFIG = {
    # Verified from the Certificate of Incorporation.
    "CIN": "U66190GJ2025PTC170746",
    # Public site URL, with a trailing slash.
    "SITE_URL": "https://www.wealthymindresearch.com/",
    # --- Regulatory. Leave as None until the registration is actually granted.
    "SEBI_RA": None,  # e.g. "INH000012345"
    "BSE_ENL": None,  # e.g. "ENL/RA/1234"
    "VALIDITY": None,  # e.g. "12/03/2026 – Perpetual"
    "GSTIN": "24AAECW3196N1ZS",
    # --- Contact.
    "ADDRESS": (
        "A-501, Ratnaakar 2, Prernatirth Derasar Road, Jodhpur Char Rasta, "
        "Satellite, Ahmedabad, Gujarat 380015"
    ),
    "OFFICE_ADDRESS": (
        "5th Floor, Binori B Square 3, 524, Sindhubhavan Road, Bodakdev, "
        "Ahmedabad, Gujarat 380059"
    ),
    "EMAIL": "info@wmrpl.com",
    # NOTE: 1234567890 is the number supplied for the build. It reads as a
    # dummy — replace it with the real line before the site goes public.
    "PHONE": "1234567890",
    "GRIEVANCE_EMAIL": "office@wmrpl.com",
    # --- Named officers.
    # Set to OMIT on instruction: no officer is appointed yet, so every block
    # naming one is removed rather than filled with "N.A.".
    # A registered research analyst MUST name both — see PLACEHOLDERS.md.
    "PRINCIPAL_OFFICER": OMIT,
    "COMPLIANCE_OFFICER": OMIT,
}

PLACEHOLDER_HINTS = {
    "SEBI_RA": "INH000XXXXXX",
    "BSE_ENL": "ENL/RA/XXXX",
    "VALIDITY": "DD/MM/YYYY – Perpetual",
    "GSTIN": "24XXXXXXXXXXXZX",
    "ADDRESS": "Registered office address, City, Gujarat – PIN",
    "OFFICE_ADDRESS": "Office address, City, Gujarat – PIN",
    "EMAIL": "support@example.com",
    "PHONE": "+91 00000 00000",
    "GRIEVANCE_EMAIL": "grievance@example.com",
    "PRINCIPAL_OFFICER": "Name, email, phone",
    "COMPLIANCE_OFFICER": "Name, email, phone",
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

# ---------------------------------------------------------------------------
# Page registry: slug -> (title, meta description, noindex?)
# ---------------------------------------------------------------------------

PAGES = {
    "index.html": (
        "Wealthymind Research Private Limited — Independent Equity Research",
        "Wealthymind Research Private Limited publishes equity, technical and "
        "derivatives research with a written thesis, a defined risk framework "
        "and a stated review point.",
    ),
    "about.html": (
        "About Us — Wealthymind Research Private Limited",
        "Who we are, how we are governed, and the research principles "
        "Wealthymind Research Private Limited operates under.",
    ),
    "services.html": (
        "Research Scope — Wealthymind Research Private Limited",
        "Fundamental equity, technical, derivatives and macro research "
        "coverage, and what each published note contains.",
    ),
    "pricing.html": (
        "Plans & Fees — Wealthymind Research Private Limited",
        "Research subscription plans, fee terms and the regulatory fee limits "
        "that apply to a SEBI research analyst.",
    ),
    "contact.html": (
        "Contact — Wealthymind Research Private Limited",
        "Reach the Wealthymind Research desk in Ahmedabad, ask about research "
        "coverage, or raise a grievance.",
    ),
    "investor-charter.html": (
        "Investor Charter — Wealthymind Research Private Limited",
        "Vision, mission, services, investor rights and timelines, as required "
        "under the SEBI Investor Charter for Research Analysts.",
    ),
    "grievance-redressal.html": (
        "Grievance Redressal — Wealthymind Research Private Limited",
        "How to raise a complaint, our escalation matrix and timelines, monthly "
        "complaints disclosure, and the SEBI SCORES and Smart ODR routes.",
    ),
    "disclaimer.html": (
        "Disclaimer & Disclosures — Wealthymind Research Private Limited",
        "Standard disclaimer, analyst and entity disclosures, and conflict of "
        "interest statements.",
    ),
    "terms-and-conditions.html": (
        "Terms, Conditions & Refund Policy — Wealthymind Research Private Limited",
        "Subscription terms, acceptable use, limitation of liability and the "
        "refund and cancellation policy.",
    ),
    "privacy-policy.html": (
        "Privacy Policy — Wealthymind Research Private Limited",
        "What personal data Wealthymind Research collects, why, how long it is "
        "kept, and the choices available to you.",
    ),
    "404.html": (
        "Page not found — Wealthymind Research Private Limited",
        "The page you requested could not be found.",
        True,
    ),
}


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
    year = datetime.date.today().year
    return {
        "YEAR": str(year),
        "CIN": html.escape(CONFIG["CIN"]),
        "SITE_URL": html.escape(CONFIG["SITE_URL"]),
        "SEBI_RA": tbd("SEBI_RA"),
        "BSE_ENL": tbd("BSE_ENL"),
        "VALIDITY": tbd("VALIDITY"),
        "GSTIN": tbd("GSTIN"),
        "ADDRESS": tbd("ADDRESS"),
        "OFFICE_ADDRESS": tbd("OFFICE_ADDRESS"),
        "EMAIL": tbd("EMAIL"),
        "PHONE": tbd("PHONE"),
        "EMAIL_LINK": mailto("EMAIL"),
        "PHONE_LINK": tel("PHONE"),
        "GRIEVANCE_EMAIL": mailto("GRIEVANCE_EMAIL"),
        "PRINCIPAL_OFFICER": tbd("PRINCIPAL_OFFICER"),
        "COMPLIANCE_OFFICER": tbd("COMPLIANCE_OFFICER"),
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

    print(f"Built {len(written)} pages:")
    for slug in written:
        print(f"  · {slug}")

    if missing:
        print(
            f"\n  {len(missing)} placeholder(s) still unset — these render as "
            f"visible `tbd` markers on the site:"
        )
        for key in missing:
            print(f"    · {key}")
        print("  Fill them in the CONFIG block of build.py and rebuild.")
    else:
        print("\n  All placeholders filled.")

    if omitted:
        print(
            f"\n  {len(omitted)} field(s) set to OMIT — every block naming them "
            f"was removed from the output:"
        )
        for key in omitted:
            print(f"    · {key}")
        print(
            "  A registered research analyst must name a Principal Officer and\n"
            "  a Compliance Officer. Set real values before the registration\n"
            "  goes live. See PLACEHOLDERS.md."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
