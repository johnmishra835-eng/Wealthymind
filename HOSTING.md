# Hosting on Hostinger

The site is static HTML plus one small PHP file for the contact form — no
database, no Node, no build step on the server. Total size is **292 KB**. Any
Hostinger plan runs it comfortably, and a one-website limit is no constraint:
this is one website.

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
2. **The upload bundle** — `wealthymind-site.zip`, 22 files. It contains only
   what a web server needs. The build sources (`src/`, `build.py`) and the
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
├── thank-you.html
├── contact.php          ← the contact form handler
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

## Step 6 — Protect your Google Workspace email

**`info@wmrpl.com` is already on Google Workspace, so there is nothing to
create — but there is something to protect.**

> ### ⚠️ Read this before attaching the domain
>
> When you point `wmrpl.com` at Hostinger, Hostinger writes its own DNS zone.
> Its default zone includes **its own MX records**, which would replace
> Google's. The moment that propagates, mail to `info@wmrpl.com` stops
> reaching your Workspace inbox.
>
> **Before** or immediately after attaching the domain, open the DNS zone in
> hPanel and make sure the MX records are Google's, not Hostinger's.

### Getting the MX records right

Do not copy MX records from me or from a blog post — Google changes its
recommended set, and yours may differ. Open **Google Admin → Account →
Domains → Manage domains → your domain**, and Google shows you the exact
records it wants. Copy those into hPanel's DNS zone, and **delete any Hostinger
MX records** that are there.

Keep these Google records intact as well:

| Type | Purpose | Where it comes from |
| --- | --- | --- |
| **MX** | Routes mail to Google | Google Admin |
| **TXT (SPF)** | Says which servers may send as your domain | Usually `v=spf1 include:_spf.google.com ~all` |
| **TXT (DKIM)** | Signs your outgoing mail | Google Admin → Apps → Gmail → Authenticate email |

After the change, send yourself a test message from an outside account and
confirm it still arrives in Workspace. Do that **before** you tell anyone the
site is live.

### `office@wmrpl.com`

The site publishes this too. If it is not already a Workspace mailbox or alias,
add it in Google Admin (an alias on the same account is free and enough).

---

## Step 6b — Point the contact form at Workspace

This matters because your mailbox is not on Hostinger.

PHP's built-in `mail()` is unreliable in exactly your situation, for two
reasons:

1. **Local delivery.** Hostinger's server may decide it handles mail for
   `wmrpl.com` itself and deliver to a local mailbox that does not exist,
   instead of routing out to Google. The message then disappears with no error.
2. **SPF failure.** Your SPF record authorises Google to send as `wmrpl.com`.
   A message sent directly from Hostinger's server is not from Google, fails
   SPF, and gets spam-filed or rejected — by your own Workspace, ironically.

**The fix is to relay through Workspace**, so the mail genuinely originates
from Google and passes SPF and DKIM. `contact.php` supports this; it just needs
credentials.

1. On the Google account for `info@wmrpl.com`, turn on **2-Step Verification**
   if it is not already on (App passwords are unavailable without it).
2. Go to **Google Account → Security → 2-Step Verification → App passwords**
   and create one. Google shows a **16-character password** once — copy it.
3. Open `contact.php` and fill in the SMTP block near the top:

```php
const SMTP_HOST = 'smtp.gmail.com';
const SMTP_PORT = 587;
const SMTP_USER = 'info@wmrpl.com';
const SMTP_PASS = 'xxxxxxxxxxxxxxxx';   // the 16-character app password
const SMTP_TLS  = true;
```

4. Re-upload `contact.php`.

Leaving `SMTP_HOST` empty makes the handler fall back to `mail()`. That may
work on your plan — but if enquiries go missing, this is the first thing to
change.

**The app password is a credential.** It sits in `contact.php` on the server,
which is normal for this kind of handler, but: never commit it to the
repository, and if you ever suspect it has leaked, revoke it in the same Google
screen and generate a new one. It grants mail access to that mailbox and
nothing else, and revoking it does not affect your normal sign-in.

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

## The contact form

The form posts to **`contact.php`**, which validates the submission and emails
it to `info@wmrpl.com`. Plain PHP, no third-party service, no monthly fee.

It sends either through **Workspace SMTP** (recommended — see Step 6b) or
through PHP's `mail()` if the SMTP block is left empty.

Mail is sent **from** `info@wmrpl.com` with the enquirer in **Reply-To**, so
hitting reply in Gmail writes back to them. It is deliberately not sent *as*
the visitor: a server may only send as a domain it is authorised for, and doing
otherwise fails SPF.

| Outcome | What the visitor sees |
| --- | --- |
| Success | Redirected to `thank-you.html`, which explains what happens next |
| A field is wrong | Back to the form with a specific message above it |
| Too many attempts | "Please wait a little, or email us directly" |
| Mail refused | An error, **and** the enquiry is written to a log so it is not lost |

Built-in protections:

- **Honeypot field** — invisible to people, so anything that fills it is a bot.
  Bots get a fake success page so they do not retry.
- **Time trap** — a submission arriving within three seconds of page load is
  treated as automated.
- **Rate limit** — five submissions per IP per hour.
- **Header-injection defence** — newlines are stripped from every single-line
  field, so a crafted name cannot add a `Bcc:` and turn your form into a spam
  relay. This was tested explicitly.
- **Server-side validation** — every rule is re-checked in PHP, never trusting
  the browser.

### Testing it after you go live

Submit the form yourself with a real message. You should land on the thank-you
page and receive the email in Workspace within a minute or two. **Check spam**
— the first message from a new sender often lands there.

If nothing arrives:

1. Confirm the MX records still point to Google (Step 6). This is the most
   likely cause, and it would also mean *all* your mail is failing.
2. Switch to Workspace SMTP if you have not (Step 6b). This is the second most
   likely cause.
3. Look for `wm-contact-failed.log` **one level above `public_html`**. If it is
   there, the send failed and the log holds both the enquiries and the reason —
   nothing has been lost.

---

## Still outstanding

**Five dates and timelines in the legal pages** are placeholders, shown as
highlighted boxes and listed in `PLACEHOLDERS.md`. They are visible to anyone
reading those pages, so worth filling before you publicise the site — though
nothing stops you going live now and editing them after.

Neither of these blocks launch, but both are worth doing: a **team section**
(for an advisory firm, who does the work is what clients most want to know),
and a **legal review** of the disclaimer, terms and privacy policy.
