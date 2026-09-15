# Hosting on Hostinger

The site is plain static HTML — no PHP, no database, no Node. Total size is
**288 KB**. Any Hostinger plan runs it comfortably, and a one-website limit is
no constraint: this is one website.

hPanel's menu labels move around between redesigns, so below I name the
*feature* to look for rather than promising an exact click path.

---

## Before you start

You need three things:

1. **The domain.** The site declares `https://www.wmrpl.com/` as its canonical
   address in every page, in `robots.txt` and in `sitemap.xml`. Either register
   or point `wmrpl.com` at Hostinger, or tell me a different domain and I will
   change it in one place (`SITE_URL` in `build.py`) and rebuild. Do not just
   upload it under a different domain — the canonical tags would then point
   somewhere the site does not live, which confuses search engines.
2. **The upload bundle** — `wealthymind-site.zip`, 64 KB, 20 files. It contains
   only what a web server needs. The build sources (`src/`, `build.py`) and the
   project notes are deliberately excluded.
3. **About 20 minutes.**

---

## Step 1 — Point the domain at Hostinger

**If you registered the domain with Hostinger** (Premium includes one free for
the first year): nothing to do, it is already connected.

**If you registered it elsewhere** (GoDaddy, BigRock, Namecheap…): in hPanel
find the nameservers for your plan — they look like

```
ns1.dns-parking.com
ns2.dns-parking.com
```

Set those as the nameservers at your current registrar, replacing what is
there. Propagation usually takes 30 minutes to a few hours, occasionally up to
24. You can keep working while it propagates.

## Step 2 — Attach the domain to the hosting plan

In hPanel, under **Websites**, make sure `wmrpl.com` is the site attached to
your plan. On a one-website plan, spend the slot on the real domain — don't
burn it on a test subdomain.

## Step 3 — Clear out the placeholder site

Open the **File Manager** and go into **`public_html`**. This folder is the web
root: whatever sits here is what visitors see.

Hostinger usually pre-fills it with a `default.php` or a parking page. **Delete
everything inside `public_html`** (the folder itself stays). If anything looks
like it might matter, download it first — but on a fresh plan it will not.

## Step 4 — Upload and extract

Still in `public_html`:

1. **Upload** `wealthymind-site.zip`
2. Right-click it → **Extract** (extract *here*, into `public_html`, not into a
   subfolder)
3. **Delete the .zip** once extracted

You should end up with this, directly inside `public_html`:

```
public_html/
├── index.html
├── about.html
├── services.html
├── due-diligence.html
├── contact.html
├── disclaimer.html
├── privacy-policy.html
├── terms-and-conditions.html
├── 404.html
├── robots.txt
├── sitemap.xml
├── .htaccess
└── assets/
    ├── css/styles.css
    ├── js/main.js
    └── img/{mark.svg, favicon.svg}
```

Two things to check:

- **`index.html` must sit directly in `public_html`**, not in a subfolder. If
  extracting produced `public_html/deploy/index.html`, move the contents up one
  level or the site will 404.
- **`.htaccess` must be there.** It starts with a dot, so the File Manager may
  hide it — look for a "show hidden files" toggle. Without it you lose the
  custom 404 page, the HTTPS redirect and the security headers.

## Step 5 — Install the SSL certificate

Find **SSL** in hPanel (under Security, or on the website's overview) and issue
the **free Let's Encrypt certificate** for `wmrpl.com` and `www.wmrpl.com`.

**Do this before testing.** The `.htaccess` redirects all traffic to `https://`,
so if the certificate is not installed yet, visitors get a browser security
warning instead of the site. Issuing takes a few minutes.

If hPanel also offers a **Force HTTPS** toggle, turning it on is harmless —
`.htaccess` already does it, and the two do not conflict.

## Step 6 — Set up the two mailboxes

The site publishes **`info@wmrpl.com`** and **`office@wmrpl.com`** in the
footer, on the contact page and throughout the legal pages. Those addresses
need to actually receive mail, or the site is inviting people to write into a
void.

In hPanel find **Emails → Email Accounts** and create both. Hostinger includes
free mailboxes on its shared plans; if your plan allows only one, create
`info@` and set `office@` as a forwarder to it — the addresses stay valid
either way.

## Step 7 — Test properly

Open each of these and confirm it loads over `https://` with a padlock:

| Check | What to look for |
| --- | --- |
| `https://www.wmrpl.com` | Home page, navy/wine styling, fonts rendering as serif headings |
| `http://wmrpl.com` | Should **redirect** to `https://www.wmrpl.com` |
| Every nav link | About, Services, Due Diligence, Contact |
| Every footer link | Disclaimer, Privacy, Terms |
| `https://www.wmrpl.com/nonsense` | Should show **your** 404 page, not Hostinger's |
| The light bulb on the home page | Hover the four stages — it should brighten and read "Funded" at stage 4 |
| On a phone | Tap the menu icon, check the drawer opens and closes |

If styling is missing, the `assets/` folder did not upload correctly. If the
404 page is Hostinger's, `.htaccess` is missing or hidden.

## Step 8 — Tell Google it exists

Once live, add the site to [Google Search Console](https://search.google.com/search-console),
verify ownership (the DNS TXT method is easiest on Hostinger), and submit
`https://www.wmrpl.com/sitemap.xml`. Nothing on the site blocks indexing except
the 404 page, which is correct.

---

## Updating the site later

The generated `.html` files are committed to the repository, so you have two
routes.

**Manual (simplest).** Edit the page source under `src/pages/`, run
`python3 build.py`, then upload the changed `.html` files through the File
Manager, overwriting the old ones.

**Git deployment.** hPanel has a **GIT** section on shared hosting that can
clone this repository into `public_html` and pull updates on demand. It is
convenient, but note that it deploys the *whole* repository — `src/` and
`build.py` land in the web root too. The `.htaccess` already blocks those paths
from being served, so it is safe, just untidy. Your call.

Either way, if a CSS or JS change does not appear, it is the cache: assets are
set to cache for a year. Purge the cache in hPanel, or hard-reload with
Ctrl+Shift+R / Cmd+Shift+R.

---

## Two things that are not done yet

**The contact form does not submit.** It validates properly and then shows a
message pointing people at the email address, because there is no endpoint
behind it. That is honest behaviour rather than a silent failure, but it is not
a working form. Hostinger shared hosting runs PHP, so a small handler that
emails submissions to `info@wmrpl.com` is about thirty lines and needs no
third-party service. Say the word and I will add it.

**Five dates and timelines in the legal pages** are still placeholders, shown
as highlighted boxes. They are listed in `PLACEHOLDERS.md`. They will be
visible to anyone reading those pages, so worth filling before you publicise
the site — though nothing stops you going live now and editing them after.

Also still worth adding, though neither blocks launch: a **team section** (for
an advisory firm, who does the work is what clients most want to know), and a
**legal review** of the disclaimer, terms and privacy policy.
