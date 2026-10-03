# Builds the guide articles (guide-*.html) and the guides index (guides.html)
# from the content below, using services.html as the template for <head>,
# header and footer. Run from anywhere:  python _tools/build_guides.py
# then:  python _tools/build_og.py  (share cards)  and  npm run build:css
#
# Regenerating OVERWRITES these pages, so edit copy here, not in the HTML.
# Article text is plain h2/h3/p/ul/table inside <div class="guide">; the
# styling for that lives in tailwind.src.css under "Guide articles".
import json, os, re, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://altitudedroneexteriorcleaning.com/"
UPDATED, UPDATED_ISO = "3 October 2026", "2026-10-03"

tpl = open(f"{ROOT}/services.html", encoding="utf-8").read()
head_tpl = tpl.split("</head>")[0]
head_tpl = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', "", head_tpl, flags=re.S)
head_tpl = head_tpl.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="article">')
header_html = tpl[tpl.index("</head>"):tpl.index("<!-- ═══════════════ BANNER")]
# Guides sit outside the main nav, so nothing is highlighted.
header_html = (header_html
               .replace('<a href="services.html" class="text-accent">Capability</a>',
                        '<a href="services.html" class="hover:text-accent transition-colors">Capability</a>')
               .replace('<a href="services.html" class="py-3 border-b border-line text-accent">Capability</a>',
                        '<a href="services.html" class="py-3 border-b border-line">Capability</a>'))
footer_html = tpl[tpl.index("<!-- ═══════════════ FOOTER"):]

CASA = {
    "hiring": "https://www.casa.gov.au/operations-safety-and-travel/consumer-and-passenger-advice/hiring-drone-operator",
    "near": "https://www.casa.gov.au/drones/flight-authorisations/flying-over-and-near-people",
    "populous": "https://www.casa.gov.au/drones/drone-rules/flying-populous-areas",
    "rego": "https://www.casa.gov.au/drones/drone-registration/registration-requirements",
    "reoc": "https://www.casa.gov.au/drones/remotely-piloted-aircraft-operators-certificate/get-your-reoc",
}


def plain(s):
    return " ".join(H.unescape(re.sub(r"<[^>]+>", "", s)).split())


def a(href, text):
    return f'<a href="{href}">{text}</a>'


def faq_html(faqs):
    out = []
    for i, (q, ans) in enumerate(faqs):
        out.append(f'''      <details class="group"{" open" if i == 0 else ""}>
        <summary class="font-heading font-semibold text-navy cursor-pointer list-none flex justify-between items-center gap-4 px-6 py-5 hover:bg-mist transition-colors">
          {q}
          <span class="text-accent text-xl group-open:rotate-45 transition-transform shrink-0">+</span>
        </summary>
        <div class="px-6 pb-6 -mt-1">
          <p class="leading-relaxed">{ans}</p>
        </div>
      </details>''')
    return "\n\n".join(out)


def make_head(slug, title, desc, alt, schema):
    url = BASE + slug
    head = head_tpl
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + desc, head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, head)
    og = f"{BASE}images/og/{slug[:-5]}.jpg"
    for k, val in (("og:title", plain(title)), ("twitter:title", plain(title)),
                   ("og:description", desc), ("twitter:description", desc),
                   ("og:image", og), ("twitter:image", og), ("og:image:alt", alt)):
        attr = "property" if k.startswith("og") else "name"
        head = re.sub(rf'(<meta {attr}="{k}" content=")[^"]*', lambda m: m.group(1) + val, head)
    for s in schema:
        head += ('  <script type="application/ld+json">\n  '
                 + json.dumps(s, indent=2, ensure_ascii=False).replace("\n", "\n  ") + "\n  </script>\n")
    return head


def banner(eyebrow, h1, intro, dated=True):
    date = (f'\n    <p class="mt-6 text-[14px] text-white/60">Updated {UPDATED} &middot; '
            f'Altitude Drone Exterior Cleaning</p>') if dated else ""
    return f'''<!-- ═══════════════ BANNER ═══════════════ -->
<section class="page-banner pt-24 pb-10 sm:pt-32 sm:pb-14 lg:pt-48 lg:pb-20 text-white">
  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <p class="text-sky text-[13px] font-semibold tracking-[0.14em] uppercase mb-4">{eyebrow}</p>
    <h1 class="font-heading font-semibold max-sm:text-[1.75rem] text-3xl lg:text-5xl tracking-tight max-w-3xl leading-tight">
      {h1}
    </h1>
    <p class="max-sm:mt-4 max-sm:text-[16.5px] mt-5 text-lg text-white/75 max-w-2xl leading-relaxed">
      {intro}
    </p>{date}
  </div>
</section>
'''


def cta(h2, p):
    return f'''
<!-- ═══════════════ CTA ═══════════════ -->
<section class="hero-bg py-12 sm:py-16 lg:py-24 text-white">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 text-center">
    <h2 class="font-heading font-semibold max-sm:text-[1.6rem] text-3xl lg:text-[2.5rem] tracking-tight">
      {h2}
    </h2>
    <p class="max-sm:mt-4 max-sm:text-[16.5px] mt-5 text-lg text-white/75 leading-relaxed">
      {p}
    </p>
    <div class="mt-9 flex flex-wrap justify-center gap-3">
      <a href="contact.html" class="r-md bg-white px-7 py-3.5 font-heading font-semibold text-navy hover:bg-mist transition-colors">
        Request a Proposal
      </a>
      <a href="tel:+61432008830" class="inline-flex items-center gap-2 r-md border border-white/40 px-7 py-3.5 font-heading font-semibold text-white hover:bg-white/10 transition-colors">
        0432 008 830
      </a>
    </div>
  </div>
</section>

'''


def build_guide(g):
    slug, url = g["slug"], BASE + g["slug"]
    schema = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": BASE + "guides.html"},
            {"@type": "ListItem", "position": 3, "name": g["crumb"], "item": url}]},
        {"@context": "https://schema.org", "@type": "Article",
         "headline": plain(g["h1"]), "description": g["desc"], "url": url,
         "mainEntityOfPage": url, "image": f"{BASE}images/og/{slug[:-5]}.jpg",
         "datePublished": UPDATED_ISO, "dateModified": UPDATED_ISO, "inLanguage": "en-AU",
         "author": {"@type": "Organization", "@id": BASE + "#business", "name": "Altitude Drone Exterior Cleaning"},
         "publisher": {"@type": "Organization", "@id": BASE + "#business", "name": "Altitude Drone Exterior Cleaning"}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(ans)}}
            for q, ans in g["faqs"]]},
    ]
    head = make_head(slug, g["title"], g["desc"], plain(g["h1"]), schema)
    related = "\n".join(f'          <li><a href="{h}" class="text-accent font-semibold hover:underline">{t}</a></li>'
                        for h, t in g["related"])
    body = banner(f'Guide &middot; {g["eyebrow"]}', g["h1"], g["intro"]) + f'''
<!-- ═══════════════ ARTICLE ═══════════════ -->
<section class="py-12 sm:py-16 lg:py-20">
  <div class="max-w-3xl mx-auto px-4 sm:px-6">
    <div class="guide">
{g["body"].strip()}
    </div>

    <div class="mt-14 bg-mist border border-line p-5 sm:p-7">
      <h2 class="font-heading font-semibold text-navy">Related</h2>
      <ul class="mt-4 space-y-2 text-[15px]">
{related}
      </ul>
    </div>
  </div>
</section>

<!-- ═══════════════ FAQ ═══════════════ -->
<section class="py-12 sm:py-16 lg:py-24 bg-mist border-y border-line">
  <div class="max-w-3xl mx-auto px-4 sm:px-6">
    <h2 class="font-heading font-semibold text-3xl text-navy tracking-tight">Questions</h2>
    <div class="mt-10 bg-white border border-line divide-y divide-line">
{faq_html(g["faqs"])}
    </div>
  </div>
</section>
''' + cta(g["cta_h2"], g["cta_p"])
    out = head + header_html + body + footer_html
    open(f"{ROOT}/{slug}", "w", encoding="utf-8", newline="\n").write(out)
    print("wrote", slug, len(out))


def build_index(guides):
    slug = "guides.html"
    schema = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": BASE + slug}]},
        {"@context": "https://schema.org", "@type": "ItemList", "name": "Drone cleaning guides",
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": BASE + g["slug"],
                              "name": plain(g["h1"])} for i, g in enumerate(guides)]},
    ]
    title = "Drone Cleaning Guides for Building Managers | Altitude"
    desc = ("Practical guides on drone building cleaning for facility managers, strata committees and "
            "procurement teams: pricing, access methods and CASA requirements.")
    head = make_head(slug, title, desc, "Guides for building and facility managers", schema)
    cards = "\n".join(f'''      <a href="{g["slug"]}" class="group bg-white p-5 sm:p-7 hover:bg-navy transition-colors">
        <p class="text-accent group-hover:text-sky text-[13px] font-semibold tracking-[0.14em] uppercase transition-colors">{g["eyebrow"]}</p>
        <h2 class="mt-3 font-heading font-semibold text-xl text-navy group-hover:text-white transition-colors leading-snug">{g["h1"]}</h2>
        <p class="mt-3 text-[15px] leading-relaxed group-hover:text-white/75 transition-colors">{g["card"]}</p>
      </a>''' for g in guides)
    body = banner("Guides", "Guides for building and facility managers",
                  "Plain answers to the questions we are asked most often by facility managers, strata "
                  "committees and procurement teams.", dated=False) + f'''
<!-- ═══════════════ GUIDES ═══════════════ -->
<section class="py-12 sm:py-16 lg:py-24">
  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <div class="grid lg:grid-cols-3 gap-px bg-line border border-line">
{cards}
    </div>
    <p class="mt-8 text-[15px]"><a href="services.html" class="text-accent font-semibold hover:underline">View our full capability →</a></p>
  </div>
</section>
''' + cta("Have a building in mind?",
          "Send us the address and what needs cleaning, and we will tell you whether drone delivery suits it.")
    out = head + header_html + body + footer_html
    open(f"{ROOT}/{slug}", "w", encoding="utf-8", newline="\n").write(out)
    print("wrote", slug, len(out))


GUIDES = []

# ───────────────────────────────────────────────────────────────────────────
GUIDES.append(dict(
    slug="guide-drone-building-cleaning-cost.html",
    title="Drone Building Cleaning Cost: What Drives the Price | Altitude",
    desc="What sets the price of drone building, window and roof cleaning, which costs drop out compared "
         "with scaffold or rope access, and how to compare quotes.",
    crumb="Drone building cleaning cost",
    eyebrow="Pricing",
    h1="What drone building cleaning costs, and what drives the price",
    intro="There is no honest rate card for exterior cleaning, because no two buildings cost the same to "
          "reach. What is predictable is where the money goes. This guide explains what sets the price of a "
          "drone clean, which costs drop out compared with conventional access, and how to compare quotes.",
    card="What sets the price of a drone clean, which access costs drop out, and how to compare quotes like "
         "for like.",
    body=f"""
<h2>Why access, not cleaning, sets most of the price</h2>
<p>On a conventional exterior clean, the cleaning itself is often the smaller part of the bill. The larger part is getting people to the surface: hiring, delivering and erecting scaffold, bringing in an elevated work platform, rigging a swing stage, or inspecting and certifying roof anchors for a rope access crew. Each carries its own mobilisation cost, lead time and time on site.</p>
<p>Access also brings costs that never appear as a cleaning line item: road occupancy permits and traffic control when equipment stands on a footpath or lane, lost car parking or trading frontage, and the hours building managers spend coordinating it all.</p>
<p>Drone delivery removes most of that. The crew works from the ground, so the price is driven by the building and the job rather than by the equipment needed to reach it.</p>

<h2>What sets the price of a drone clean</h2>
<h3>Surface area and number of elevations</h3>
<p>The total area to be treated is the starting point. A building with four exposed elevations costs more than one with two exposed and two built against its neighbours. We measure areas from aerial imagery and drawings, so the scope reflects the actual building rather than an estimate from the street.</p>
<h3>Surface type and soiling</h3>
<p>Render, painted concrete and cladding are soft washed; glass and frames are cleaned with purified water. Light organic growth and salt film clear readily, while heavy, long-established growth takes more treatment. Heavy mechanical staining, graffiti and coating removal are not suited to the method at all, and we say so at scoping.</p>
<h3>Building shape</h3>
<p>Deep balconies, setbacks, awnings and overhangs take more flying time than a flat curtain wall, because the aircraft has to work around them. Simple, repetitive elevations are the most efficient to clean.</p>
<h3>Airspace and approvals</h3>
<p>Sites inside controlled airspace, such as parts of the southern Gold Coast near Gold Coast Airport, or inner Brisbane near Brisbane Airport and Archerfield, can need a CASA approval before works. Sites near hospital helipads need their own coordination. Approvals add lead time and occasionally rule the method out, so we check airspace for every site at scoping. Our {a("guide-drone-cleaning-casa-rules.html", "CASA guide")} explains what is involved.</p>
<h3>The ground around the building</h3>
<p>CASA rules keep a drone a set distance from people who are not part of the operation, so the crew needs a ground exclusion zone below the work. On a quiet site that is simple. Beside a busy footpath, a pool deck or a car park it can mean starting early, sequencing elevations around foot traffic, or arranging notice through building management.</p>
<h3>One-off clean or scheduled program</h3>
<p>A one-off clean is priced on its own. A scheduled program over several cycles, or across several buildings in a portfolio, is priced as a fixed amount per cycle so it can be budgeted rather than approved each time.</p>

<h2>Costs that usually drop out</h2>
<ul>
<li>Scaffold hire, delivery, erection and dismantling</li>
<li>Elevated work platform hire, and the hardstand or ground protection it needs</li>
<li>Swing stage rigging and building maintenance unit certification</li>
<li>Roof anchor inspection and certification for rope access</li>
<li>Road occupancy permits for equipment standing on a footpath or lane</li>
<li>Weeks of program, and the disruption to tenants or residents that comes with it</li>
</ul>
<p>Not every site loses every item. A site on a busy road may still need traffic control around the exclusion zone, and some work has to be scheduled outside trading hours. A proper scope tells you which costs remain.</p>

<h2>Comparing quotes like for like</h2>
<p>Exterior cleaning quotes vary widely in what they include. Before comparing prices, check that each one covers:</p>
<ul>
<li>The same elevations, surfaces and roof areas, measured the same way</li>
<li>Glass and frames, or glass only</li>
<li>The cleaning products, with Safety Data Sheets</li>
<li>Any CASA approvals the site needs, and who obtains them</li>
<li>Public liability and aviation liability insurance, with certificates of currency</li>
<li>A site-specific SWMS and risk assessment</li>
<li>What happens if weather stops work, and whether rescheduling costs extra</li>
<li>A completion report with photographs of each elevation</li>
</ul>
<p>A low price that leaves out approvals, insurance or documentation stops being low once those are added back.</p>

<h2>How to get an accurate price</h2>
<p>Send the site address and tell us what needs cleaning: facades, glass, roof, solar or a combination. Drawings, recent photos and any constraints, such as trading hours, a pool deck or a shared driveway, all help. In most cases we can scope and price the site remotely from aerial imagery and drawings, with no attendance fee. You receive a fixed-price proposal with the methodology, SWMS, insurance certificates and program.</p>
""",
    faqs=[
        ("How much does drone building washing cost on the Gold Coast?",
         "It depends on the area to be cleaned, the surfaces, the shape of the building and its airspace, so "
         "every site is priced individually. On most multi-storey buildings the saving comes from removing "
         "scaffold, EWP or rope access from the job, which is usually the largest cost in a conventional clean."),
        ("Is a drone always cheaper than rope access?",
         "No. On low buildings with easy ground access, or for small areas, conventional methods can be "
         "competitive. The gap widens with height, area and the cost of access equipment, and a scope will show "
         "which applies to your building."),
        ("Do you charge to quote?",
         "Most sites are quoted without an attendance fee, because the scope can be measured from aerial imagery "
         "and drawings. If a visit is genuinely needed, we tell you before arranging it."),
    ],
    related=[("drone-building-washing-gold-coast.html", "Drone building washing on the Gold Coast"),
             ("drone-window-cleaning-gold-coast.html", "Drone window cleaning on the Gold Coast"),
             ("drone-strata-building-cleaning-gold-coast.html", "Strata and body corporate building cleaning"),
             ("guide-drone-vs-rope-access-scaffold-ewp.html", "Guide: drone, rope access, EWP or scaffold?")],
    cta_h2="Get a fixed price for your building",
    cta_p="Send the address and what needs cleaning, and we will come back with a fixed-scope proposal.",
))

# ───────────────────────────────────────────────────────────────────────────
GUIDES.append(dict(
    slug="guide-drone-vs-rope-access-scaffold-ewp.html",
    title="Drone vs Rope Access, EWP &amp; Scaffold Cleaning | Altitude",
    desc="How drone cleaning compares with rope access, swing stage, EWP and scaffold for exterior building "
         "cleaning: what each suits and where each falls short.",
    crumb="Drone vs rope access, EWP and scaffold",
    eyebrow="Access methods",
    h1="Drone, rope access, EWP or scaffold: choosing an access method for exterior cleaning",
    intro="The access method decides most of the cost, the program and the safety risk of an exterior clean. "
          "Each method has its place. This guide sets out what each one suits, where it falls short, and how to "
          "choose for your building.",
    card="What scaffold, EWPs, rope access, swing stages and drones each suit, where each falls short, and how "
         "to choose.",
    body=f"""
<h2>The methods at a glance</h2>
<div class="table-wrap">
<table>
<thead><tr><th>Method</th><th>People at height</th><th>Set-up</th><th>Ground footprint</th><th>Best suited to</th></tr></thead>
<tbody>
<tr><th>Scaffold</th><td>Yes</td><td>Days to weeks</td><td>Large, often a footpath or lane</td><td>Cleaning combined with repairs or repainting</td></tr>
<tr><th>Elevated work platform</th><td>Yes, in the basket</td><td>Hours</td><td>Machine plus hardstand</td><td>Low to mid-rise with good ground access</td></tr>
<tr><th>Rope access</th><td>Yes, on ropes</td><td>Anchor inspection, then drop by drop</td><td>Exclusion below each drop</td><td>Tall elevations needing hands-on work</td></tr>
<tr><th>Swing stage or BMU</th><td>Yes, in the cradle</td><td>Rigging and certification</td><td>Exclusion below the cradle</td><td>Towers designed around a maintenance unit</td></tr>
<tr><th>Drone</th><td>No, crew on the ground</td><td>Hours</td><td>Moving ground exclusion zone</td><td>Multi-storey facades, glass, roofs and solar</td></tr>
</tbody>
</table>
</div>

<h2>Scaffold</h2>
<p>Scaffold gives a stable working platform across a whole elevation, which is why it remains the right choice when cleaning is part of a larger job such as facade repairs, sealant replacement or repainting. For cleaning alone it is rarely economic. Hire, erection and dismantling dominate the cost, the building is wrapped for weeks, and balconies, windows and frontages are blocked for the duration.</p>

<h2>Elevated work platforms</h2>
<p>Boom lifts and scissor lifts are quick to set up and suit low to mid-rise buildings with firm, level ground beside each elevation. Their limits are reach, ground conditions and footprint. The machine needs hardstand, often occupies car parking or a footpath, and setbacks, landscaping or basement slabs can stop it getting close enough. Boom-type platforms with a boom of 11 metres or more also need an operator who holds a high risk work licence.</p>

<h2>Rope access</h2>
<p>Abseil technicians can reach almost any elevation and can do hands-on work that a drone cannot, such as scrubbing heavy staining, resealing or inspecting at arm's length. The trade-offs are that people work at height on every drop, roof anchors must be inspected and certified before use, the area below each drop is closed off, and progress is one drop at a time. Specialist crews can also carry booking lead times.</p>

<h2>Swing stages and building maintenance units</h2>
<p>Some towers were designed with a permanent building maintenance unit or davit system. Where one is installed and certified, it is a practical way to reach glazing. Where there is none, rigging a temporary swing stage adds engineering, certification and time. Either way, people still work in a suspended cradle beside the facade.</p>

<h2>Drones</h2>
<p>A cleaning drone carries the spray to the surface while a two-person crew controls it from the ground. Nobody works at height, nothing is fixed to or loaded against the building, and most buildings are finished in days rather than weeks.</p>
<p>The method has clear limits. It does not suit heavy mechanical staining, graffiti or coating removal, ground-level hardstand, internal atria, or sites in airspace where approval cannot be obtained. Wind sets an operating limit on every flight, and CASA's separation rules mean the ground below the work has to be managed. Our {a("guide-drone-cleaning-casa-rules.html", "CASA guide")} covers those rules.</p>

<h2>Combining methods</h2>
<p>Sometimes the best answer is a mix. A drone can clean the upper elevations, roof and glazing while a ground-level crew cleans shopfronts, awnings and paving. On a building due for repairs, a drone clean beforehand shows the true condition of the facade before anyone commits to scaffold.</p>

<h2>How to choose</h2>
<ul>
<li>Is the job cleaning only, or cleaning plus repairs? Repairs usually need hands-on access.</li>
<li>How tall is the building, and how much ground is there beside each elevation?</li>
<li>Is the building occupied or trading, and how much disruption can it take?</li>
<li>Is the soiling organic growth and salt film, or heavy staining and graffiti?</li>
<li>Is the site near an airport, a helipad or other controlled airspace?</li>
<li>How often does it need cleaning? Recurring cleans multiply the cost of access.</li>
</ul>
<p>If you are not sure, send us the address. We will tell you at scoping whether a drone suits the building and, if it does not, which trade does. The {a("guide-drone-building-cleaning-cost.html", "cost guide")} explains how each choice affects the price.</p>
""",
    faqs=[
        ("Is drone cleaning safer than rope access?",
         "It removes the main hazard. With the crew on the ground, nobody is exposed to a fall from height, which "
         "is the risk that dominates rope access, swing stage and EWP work. The remaining risks, such as the "
         "aircraft itself and the area below it, are managed through CASA requirements, a site-specific SWMS and a "
         "ground exclusion zone."),
        ("When is scaffold still the better option?",
         "When cleaning is combined with repairs, repainting or sealant replacement across a whole elevation, or "
         "when hands-on work is needed at every level. For cleaning alone, scaffold is rarely the economic choice."),
        ("Does a drone need anything fixed to the building?",
         "No. Nothing is anchored, propped or rigged against the structure, so there is no facade loading and no "
         "anchor certification for the cleaning task."),
    ],
    related=[("drone-window-cleaning-gold-coast.html", "Drone window cleaning on the Gold Coast"),
             ("drone-roof-cleaning-gold-coast.html", "Drone roof cleaning on the Gold Coast"),
             ("services.html", "Where drone delivery is, and isn't, the right method"),
             ("guide-drone-building-cleaning-cost.html", "Guide: what drone building cleaning costs")],
    cta_h2="Not sure which method suits your building?",
    cta_p="Send us the address. We will tell you at scoping whether a drone is the right fit.",
))

# ───────────────────────────────────────────────────────────────────────────
GUIDES.append(dict(
    slug="guide-drone-cleaning-casa-rules.html",
    title="Drone Cleaning and CASA Rules: What to Check | Altitude",
    desc="The CASA registration, licence, ReOC, airspace approval and insurance checks to make before hiring "
         "a commercial drone cleaning contractor in Australia.",
    crumb="Drone cleaning and CASA rules",
    eyebrow="Compliance",
    h1="Hiring a drone cleaning contractor: the CASA rules and what to check",
    intro="Commercial drone work in Australia is regulated by the Civil Aviation Safety Authority (CASA). For a "
          "building owner or manager, an unlicensed operator is more than a regulatory problem: CASA warns that "
          "illegal operations could void the operator's insurance. These are the checks worth making before "
          "anyone flies at your building.",
    card="The registration, licence, ReOC, approval and insurance checks to make before a drone flies at your "
         "building.",
    body=f"""
<h2>1. The drone is registered</h2>
<p>CASA requires every drone used for business to be registered, whatever its weight, and flying an unregistered drone for a commercial purpose is an offence. Ask for proof of registration for the aircraft that will be used on your site.</p>

<h2>2. The pilot is licensed for that drone</h2>
<p>A remote pilot licence (RePL) shows the type and weight category of drone the pilot may fly. Cleaning drones are far heavier than camera drones, so check that the licence covers the aircraft actually being used, not just a smaller one. You can ask to see the paper or digital licence.</p>

<h2>3. The business holds a ReOC</h2>
<p>Licensed pilots flying commercially must operate for a business that holds a remotely piloted aircraft operator's certificate (ReOC). CASA publishes a directory of ReOC holders, so you can confirm the certificate and the operations it covers.</p>

<h2>4. Any approvals the site needs are current</h2>
<p>Some sites need a specific CASA authorisation before work can start. Flying within 5.5 kilometres of a controlled airport, for example, needs an approval to fly in controlled airspace. On the Gold Coast that affects parts of the southern suburbs near Gold Coast Airport; in Brisbane, areas around Brisbane Airport and Archerfield.</p>
<p>An approval lists the operations allowed, the conditions and the approved period. Ask to see any approval the job relies on, and check that it has not expired.</p>

<h2>5. The insurance covers drone work</h2>
<p>Ask for certificates of currency for public liability and for aviation liability. General liability policies often exclude aircraft, so a public liability certificate on its own may not respond to a drone incident. Check that the cover applies to the services being provided.</p>

<h2>The 30 metre rule, and what it means on your site</h2>
<p>Under CASA's standard operating conditions, a drone must stay at least 30 metres from people who are not part of the operation, and must never fly over a person. An operator working under a ReOC may fly between 30 and 15 metres from a person who consents, with documented procedures in place. Anything closer needs a specific CASA approval.</p>
<p>Flying a drone that is not certified over a populous area, which includes residential areas, roads, footpaths and city areas, needs an exemption that ReOC holders can apply to CASA for. In practice, this is why a professional drone clean comes with a ground exclusion zone, notice to occupants before each elevation and, where needed, site-specific approvals. A contractor proposing to fly above a busy footpath with none of that in place is a warning sign.</p>

<h2>Safety and environmental documents</h2>
<p>CASA covers the aviation side. Your site rules and workplace health and safety duties still apply, so expect the same documents you would ask of any contractor: a site-specific SWMS and risk assessment, Safety Data Sheets for the cleaning products, and an agreed approach to runoff where the site drains to stormwater.</p>

<h2>Checklist</h2>
<ul>
<li>Proof of registration for the drone being used</li>
<li>A remote pilot licence covering that drone's type and weight category</li>
<li>The operator's ReOC, checked against CASA's directory</li>
<li>Any site-specific CASA approvals, with current dates</li>
<li>Certificates of currency for public liability and aviation liability</li>
<li>A site-specific SWMS, risk assessment and Safety Data Sheets</li>
<li>A plan for the ground exclusion zone and notice to occupants</li>
</ul>
<p>Altitude supplies its credentials, insurance certificates and site documentation with tender responses or on request. Our {a("compliance.html", "compliance page")} sets out what we hold.</p>
<p>Sources: CASA, {a(CASA["hiring"], "Hiring a drone operator")}, {a(CASA["rego"], "Registration requirements")}, {a(CASA["reoc"], "Get your ReOC")}, {a(CASA["near"], "Flying over and near people")} and {a(CASA["populous"], "Flying in populous areas")}. CASA's rules change from time to time, so check its website for the current position.</p>
""",
    faqs=[
        ("Is drone building cleaning legal in Australia?",
         "Yes, when it is done by an operator with the right CASA credentials: a registered drone, a remote pilot "
         "licence covering that drone, a ReOC, and any approvals the specific site needs."),
        ("Can a drone fly close to people while cleaning?",
         "Only within limits. The standard rule is 30 metres from anyone not involved in the operation, and never "
         "over a person. ReOC operators can work between 30 and 15 metres from people who consent, and closer only "
         "with a CASA approval. That is why the area below the work is kept clear."),
        ("Who is responsible for getting airspace approval?",
         "The drone operator. Approvals are issued to the operator, so the contractor should identify what the "
         "site needs at scoping and hold the approval before works start."),
    ],
    related=[("compliance.html", "Our compliance, insurance and safety documentation"),
             ("how-it-works.html", "How an engagement runs, from scope to completion report"),
             ("guide-drone-vs-rope-access-scaffold-ewp.html", "Guide: drone, rope access, EWP or scaffold?")],
    cta_h2="Need our documentation first?",
    cta_p="Ask for our credentials and certificates of currency with your proposal, or ahead of a tender.",
))

for g in GUIDES:
    build_guide(g)
build_index(GUIDES)
