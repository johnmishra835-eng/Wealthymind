# Placeholders to fill before going live

Anything we could not verify renders as a **highlighted `tbd` marker** — a
pink dashed box — so nothing invented ships silently.

All the company details are now filled in. What remains is a short list of
dates and internal timelines only you can decide.

Find every remaining one:

```bash
grep -rn 'class="tbd"' src/pages/
```

Then edit the page under `src/pages/` and run `python3 build.py`.

---

## Remaining placeholders

### `src/pages/contact.html`
- **Working hours.** Currently `Mon–Sat, 10:00 am – 7:00 pm IST`. Confirm or
  change.

### `src/pages/terms-and-conditions.html`
- **Last updated** date.

### `src/pages/privacy-policy.html`
- **Last updated** date.
- **Record retention period** — currently suggests 8 years; confirm with your
  accountant or company secretary.
- **Enquiry deletion period** — how long you keep enquiries that do not become
  engagements.
- **Response time** for a data-rights request.

---

## Config

Company details live in one place: the `CONFIG` block at the top of
`build.py`. All are filled:

| Key | Value |
| --- | --- |
| `CIN` | U66190GJ2025PTC170746 |
| `GSTIN` | 24AAECW3196N1ZS |
| `ADDRESS` | 5th Floor, Binori B Square 3, 524, Sindhubhavan Road, Bodakdev, Ahmedabad, Gujarat 380059 |
| `EMAIL` | info@wmrpl.com |
| `EMAIL_ALT` | office@wmrpl.com |
| `PHONE` | +91 87348 10317 |
| `SITE_URL` | https://www.wmrpl.com/ |

Change `SITE_URL` if the domain differs — it drives the canonical and Open
Graph URLs, and should match `robots.txt` and `sitemap.xml`.

---

## Not placeholders, but decide before launch

- ~~**Contact form endpoint.**~~ Done — the form posts to `contact.php`, which
  emails enquiries to `info@wmrpl.com`. It needs that mailbox to exist on the
  hosting; see "The contact form" in `HOSTING.md`.
- **Legal review.** The disclaimer, terms of use and privacy policy are
  structured drafts written for an advisory practice. They are not legal
  advice. Have a lawyer review them — particularly the limitation of liability
  and the confidentiality commitments, since the latter describe what you will
  actually do on a mandate.
- **Every factual claim about the firm.** The copy commits to specific
  behaviour: a small number of mandates at a time, anonymised first approaches,
  NDAs before detailed materials, data room access withdrawn when a party
  leaves, bad news reported the same week, fees agreed in an engagement letter
  before work starts. Read these as promises and change anything you will not
  actually do.
- **Team page.** There is deliberately no team section, because we have no
  names or bios. For an advisory firm this is the single most useful thing you
  could add — who is doing the work matters more here than in most businesses.
- **Logo fidelity.** `assets/img/mark.svg` and the header wordmark are a vector
  reconstruction of your artwork, not your original file. See "Logo" in
  `README.md` for the two things worth checking.

---

## What this site deliberately does not contain

The business is fundraising and capital advisory, **not** research analysis or
any regulated intermediary activity. The following were removed and should not
be reintroduced:

- SEBI, BSE or NSE registration numbers, or any claim of registration
- an Investor Charter
- SCORES or Smart ODR grievance routes, or any complaints-disclosure table
- named Principal Officer and Compliance Officer
- subscription plans, pricing tiers and a refund policy
- the market-risk banner and NISM certification wording

`build.py` enforces this: the build **fails** if any of those terms reappear in
the generated HTML. If you genuinely become a registered intermediary later,
update the guard list in `build.py` deliberately rather than deleting it.

No client names, client counts, transaction values, success rates or
testimonials appear anywhere, and the copy is written so none are needed.
