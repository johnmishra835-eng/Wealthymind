# Placeholders to fill before going live

Everything on the site that we could not verify renders as a **highlighted
`tbd` marker** — a pink/dashed box — so nothing invented can ship silently.

There are two kinds:

1. **Config placeholders** — set once in the `CONFIG` block at the top of
   `build.py`, then run `python3 build.py`. They propagate to every page.
2. **Inline placeholders** — hard-coded `<span class="tbd">` in a specific page
   under `src/pages/`. Edit the page, then rebuild.

Run `python3 build.py` at any time: it prints which config values are still
unset. To find every remaining inline one:

```bash
grep -rn 'class="tbd"' src/pages/
```

---

## 1. Config placeholders (`build.py`)

| Key | What it is | Where it shows |
| --- | --- | --- |
| `SEBI_RA` | SEBI Research Analyst registration number (`INH…`) | Hero, registration strip, footer, about, charter, disclaimer |
| `BSE_ENL` | BSE enlistment number for research analysts | Registration strip, footer, disclaimer |
| `VALIDITY` | Registration validity period | Footer, disclaimer |
| `GSTIN` | GST identification number | Registration strip, footer |
| `ADDRESS` | Full registered office address with PIN | Footer, about, contact, privacy, terms |
| `EMAIL` | General/subscriptions email | Footer, contact, terms, privacy |
| `PHONE` | Telephone number | Footer, contact |
| `GRIEVANCE_EMAIL` | Dedicated grievance email | Footer, contact, grievance, pricing |
| `PRINCIPAL_OFFICER` | Name, email and phone | Footer, contact, grievance |
| `COMPLIANCE_OFFICER` | Name, email and phone | Footer, contact, grievance, disclaimer |

`CIN` and `SITE_URL` are already set. Change `SITE_URL` if the domain differs —
it drives the canonical and Open Graph URLs.

---

## 2. Inline placeholders, by page

### `src/pages/pricing.html`
- **Three plan prices** (`₹0,000`). Also review the plan names, the inclusion
  lists and the billing period — these are a sensible starting structure, not
  your commercial decisions.
- **Regulatory fee ceiling.** The per-annum-per-family cap on fees charged to
  individual and HUF clients must be quoted from the SEBI circular in force on
  the day you publish. Do not copy a figure from another firm's website.

### `src/pages/grievance-redressal.html`
- **Escalation matrix** — the two `Name` cells for customer care and the
  grievance desk.
- **Complaints disclosure tables** — every figure, plus the month and financial
  year labels. These must be updated monthly (by the 7th of the following
  month) even when all values are nil.

### `src/pages/investor-charter.html`
- **Refund processing timeline** (`N` working days) — keep consistent with the
  refund policy.

### `src/pages/terms-and-conditions.html`
- **Last updated** date.
- **Cancellation window** and **refund decision/credit timelines** (`N` days).
- **Jurisdiction city** in Gujarat.

### `src/pages/privacy-policy.html`
- **Last updated** date.
- **Record retention period** — confirm against the regulation in force.
- **Response time** for a data-rights request.

### `src/pages/disclaimer.html`
- **Disciplinary action** row — must be answered truthfully, not left blank.
- **Jurisdiction city** in Gujarat.

### `src/pages/contact.html`
- **Working hours.**

---

## 3. Not placeholders, but decide before launch

- **Contact form endpoint.** The form has no `action`, so `assets/js/main.js`
  blocks submission and shows a message pointing at the email address. Wire it
  to a form service or your own handler, then set `action` and
  `method="post"` on the `<form>` in `src/pages/contact.html`.
- **Logo fidelity.** `assets/img/mark.svg` and the header wordmark are a vector
  reconstruction from the supplied image, not your original file. Compare them
  against your master artwork before launch — see "Logo" in `README.md`.
- **Sample note.** Several pages offer a "redacted sample note" on request.
  Either prepare one or remove those references.
- **Every factual claim about the firm.** The copy describes a research process
  (six steps, second-reader review, fixed publication windows, closure notices).
  It is written to be true of a disciplined research desk — but it describes
  *your* operations, so read it as a commitment and change anything you will
  not actually do.

---

## 4. Do not publish until this is true

The site states in several places that the firm is a SEBI-registered research
analyst. **If that registration has not been granted, this is a
misrepresentation** and the claim must be removed, not merely left as a
placeholder. Until the certificate is in hand, delete or reword:

- the hero eyebrow "Research Analyst · Gujarat, India" (`src/pages/index.html`)
- the `SEBI_RA` / `BSE_ENL` rows in the registration strip and footer
- the "Registration" section of `src/pages/disclaimer.html`
- `src/pages/investor-charter.html` in full — the Investor Charter is a
  registered-intermediary obligation
- the references to being "bound by" the SEBI (Research Analysts) Regulations

Have the legal and compliance pages reviewed by a lawyer or compliance
consultant familiar with those regulations before launch. The drafts here are a
structured starting point, not legal advice.
