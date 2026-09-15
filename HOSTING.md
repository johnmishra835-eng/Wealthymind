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

## The contact form

The form posts to **`contact.php`**, which validates the submission and emails
it to `info@wmrpl.com`. Plain PHP, no third-party service, no monthly fee.

For it to work you need **one thing**: the `info@wmrpl.com` mailbox must
actually exist on this hosting (Step 6 above). The message is sent *from* that
address, because a server may only send as a domain it is authorised for — if
the visitor's own address were used as the sender, most providers would reject
it or file it as spam. The visitor's address goes in **Reply-To**, so hitting
reply in your mail client still writes back to them.

What happens on submit:

| Outcome | What the visitor sees |
| --- | --- |
| Success | Redirected to `thank-you.html`, which explains what happens next |
| A field is wrong | Back to the form with a specific message above it |
| Too many attempts | "Please wait a little, or email us directly" |
| Mail server refuses | An error, **and** the enquiry is written to a log so it is not lost |

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
page and receive the email at `info@wmrpl.com` within a minute or two. **Check
the spam folder** — the first message from a new domain often lands there.

If nothing arrives:

1. Confirm the `info@wmrpl.com` mailbox exists in hPanel.
2. Look for `wm-contact-failed.log` **one level above `public_html`**. If it is
   there, PHP could not hand the mail off and the log holds the enquiries.
3. If Hostinger's `mail()` is unreliable on your plan, the handler can be
   switched to authenticated SMTP through your own mailbox. Ask me and it is a
   small change.

Consider adding an **SPF record** in hPanel's DNS zone if one is not already
there — it markedly improves whether your mail reaches the inbox.

---

## Still outstanding

**Five dates and timelines in the legal pages** are placeholders, shown as
highlighted boxes and listed in `PLACEHOLDERS.md`. They are visible to anyone
reading those pages, so worth filling before you publicise the site — though
nothing stops you going live now and editing them after.

Neither of these blocks launch, but both are worth doing: a **team section**
(for an advisory firm, who does the work is what clients most want to know),
and a **legal review** of the disclaimer, terms and privacy policy.
