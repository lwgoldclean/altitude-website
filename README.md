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

## Outstanding

- **The enquiry forms do not send yet.** Both `index.html` and `contact.html`
  contain `REPLACE_WITH_WEB3FORMS_ACCESS_KEY`. Get a free key at
  [web3forms.com](https://web3forms.com) and paste it into both files. Until
  then the form shows a message asking the visitor to phone instead.
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
