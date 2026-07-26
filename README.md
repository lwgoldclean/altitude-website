# Altitude Drone Exterior Cleaning — website

Static site served by GitHub Pages from the repository root at
**altitudedroneexteriorcleaning.com**.

## Important: the CSS is compiled

`css/site.css` is **generated** — do not edit it directly, your changes will be
overwritten. It is built from `tailwind.src.css` plus the Tailwind classes found
in the HTML.

If you add or change any class in an HTML file (for example `text-navy`,
`px-6`, `lg:grid-cols-2`), you must rebuild or that style will be missing from
the live site:

```bash
npm install      # first time only
npm run build:css
```

`npm run watch:css` rebuilds automatically while you work.

The site previously loaded Tailwind from a CDN, which shipped roughly 400 KB of
JavaScript and delayed rendering until it ran. The compiled stylesheet is about
22 KB and needs no JavaScript, which is materially better for search ranking and
for visitors on mobile data.

## Pages

| File | Purpose |
| --- | --- |
| `index.html` | Home |
| `services.html` | Capability — the six delivery scopes |
| `how-it-works.html` | Process, plus the FAQ (carries FAQ structured data) |
| `compliance.html` | Insurance, CASA, WHS and environmental documentation |
| `about.html` | Company, aircraft and governance |
| `contact.html` | Enquiry form and direct contact |
| `capability-statement.html` | Print-to-PDF one-pager for tender submissions |
| `faq.html` | Redirect stub — keeps the old indexed URL alive |
| `404.html` | Not-found page (GitHub Pages serves this automatically) |

## The enquiry forms (Resend via a Cloudflare Worker)

A static site cannot hold a Resend API key — anything in the page source is
public, and a leaked key lets a stranger send email as your domain. So the form
posts to a small Cloudflare Worker in `worker/`, which holds the key and calls
Resend. It is free on Cloudflare's plan and is about 60 lines of code.

**Deploy it once:**

```bash
cd worker
npx wrangler login                      # opens your browser
npx wrangler deploy                     # prints your Worker URL
npx wrangler secret put RESEND_API_KEY  # paste your Resend key when prompted
```

Then take the URL wrangler prints — something like
`https://altitude-enquiry.<your-subdomain>.workers.dev` — and paste it over
`REPLACE_WITH_WORKER_URL.workers.dev` in the `<form action="...">` of both
`index.html` and `contact.html`. Commit and push.

**Sender address.** `worker/wrangler.toml` sets `FROM_EMAIL` to
`enquiries@altitudedroneexteriorcleaning.com`. Resend will refuse to send from
that until you verify the domain in the Resend dashboard (a few DNS records at
your registrar). To test before verifying, temporarily change it to
`Altitude Website <onboarding@resend.dev>`.

Enquiries arrive as a formatted table, and the reply-to is set to the
enquirer's address so replying in your mail client goes straight back to them.

Until the Worker URL is pasted in, the form tells visitors to phone instead of
failing silently.

## Outstanding
- Placeholders marked `TODO (William)` cover the ABN, insurance sums, CASA
  certificate details, aircraft specifications and past-project references.
  None of these were invented — each needs your real detail before publishing.
- Roof and industrial photography is still a grey placeholder on
  `services.html`, and the home page wants a sample completion-report page.

## After deploying

- Submit `sitemap.xml` in [Google Search Console](https://search.google.com/search-console).
- Create a **Google Business Profile** — for a local service business this
  moves the needle more than anything on the site itself.
- HTTPS: if `https://` fails, re-add the custom domain under
  Settings → Pages to trigger certificate provisioning, then tick
  "Enforce HTTPS".
