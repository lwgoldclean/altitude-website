# Builds the service and location landing pages (drone-*.html) from the
# content below, using services.html as the template for <head>, header and
# footer. Run from anywhere:  python _tools/build_pages.py
# then:  npm run build:css
#
# Regenerating OVERWRITES every drone-*.html page, so make copy changes to
# those pages here rather than in the HTML. Folders starting with "_" are not
# published by GitHub Pages, so this script never appears on the live site.
import json, re, html as H

import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://altitudedroneexteriorcleaning.com/"

tpl = open(f"{ROOT}/services.html", encoding="utf-8").read()
head_tpl = tpl.split("</head>")[0]
# Strip page-specific structured data from the template head.
head_tpl = re.sub(r'\s*<script type="application/ld\+json">.*?</script>', "", head_tpl, flags=re.S)
body_start = tpl.index("</head>")
header_html = tpl[body_start:tpl.index("<!-- ═══════════════ BANNER")]
footer_html = tpl[tpl.index("<!-- ═══════════════ FOOTER"):]

SUBURBS = ["Surfers Paradise", "Broadbeach", "Main Beach", "Southport", "Labrador",
           "Runaway Bay", "Hope Island", "Coomera", "Helensvale", "Nerang", "Robina",
           "Varsity Lakes", "Burleigh Heads", "Palm Beach", "Coolangatta", "Mermaid Beach"]

PAGES = {}

def li(items, mark="—", cls="text-accent font-semibold"):
    return "\n".join(f'          <li class="flex gap-3"><span class="{cls}">{mark}</span> {i}</li>' for i in items)

def media(img):
    if img.get("src"):
        wrap = "border border-line bg-mist p-4" if img.get("pad") else "border border-line overflow-hidden"
        return (f'<div class="{wrap}">\n        <img src="{img["src"]}" alt="{img["alt"]}" class="w-full h-auto" '
                f'width="{img["w"]}" height="{img["h"]}" loading="lazy" decoding="async">\n      </div>')
    return ('<div class="img-ph border border-line min-h-[300px] lg:min-h-[360px] flex items-center justify-center">\n'
            f'        <p class="text-navy/40 font-medium text-sm px-6 text-center">{img["placeholder"]}</p>\n      </div>')

def faq_html(faqs):
    out = []
    for i, (q, a) in enumerate(faqs):
        out.append(f'''      <details class="group"{" open" if i == 0 else ""}>
        <summary class="font-heading font-semibold text-navy cursor-pointer list-none flex justify-between items-center gap-4 px-6 py-5 hover:bg-mist transition-colors">
          {q}
          <span class="text-accent text-xl group-open:rotate-45 transition-transform shrink-0">+</span>
        </summary>
        <div class="px-6 pb-6 -mt-1">
          <p class="leading-relaxed">{a}</p>
        </div>
      </details>''')
    return "\n\n".join(out)

def plain(s):
    return H.unescape(re.sub(r"<[^>]+>", "", s))

def build(slug, p):
    url = BASE + slug
    head = head_tpl
    t, d = p["title"], p["desc"]
    head = re.sub(r"<title>.*?</title>", f"<title>{t}</title>", head)
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + d, head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, head)
    for k in ("og:title", "twitter:title"):
        attr = "property" if k.startswith("og") else "name"
        head = re.sub(rf'(<meta {attr}="{k}" content=")[^"]*', lambda m: m.group(1) + plain(t), head)
    for k in ("og:description", "twitter:description"):
        attr = "property" if k.startswith("og") else "name"
        head = re.sub(rf'(<meta {attr}="{k}" content=")[^"]*', lambda m: m.group(1) + d, head)

    schema = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
            {"@type": "ListItem", "position": 2, "name": "Capability", "item": BASE + "services.html"},
            {"@type": "ListItem", "position": 3, "name": p["crumb"], "item": url}]},
        {"@context": "https://schema.org", "@type": "Service",
         "name": p["service_name"], "serviceType": p["service_name"],
         "description": plain(p["intro"]), "url": url,
         "provider": {"@type": "ProfessionalService", "@id": BASE + "#business",
                      "name": "Altitude Drone Exterior Cleaning", "url": BASE,
                      "telephone": "+61432008830"},
         "areaServed": p.get("area_served", [{"@type": "City", "name": "Gold Coast"},
                        {"@type": "AdministrativeArea", "name": "South East Queensland"}])},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": plain(q),
             "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in p["faqs"]]},
    ]
    for s in schema:
        head += ('  <script type="application/ld+json">\n  '
                 + json.dumps(s, indent=2, ensure_ascii=False).replace("\n", "\n  ") + "\n  </script>\n")

    hdr = header_html  # nav keeps "Capability" highlighted, as these sit under it

    s1 = p["s1"]
    img_first = s1.get("img_first", False)
    text_block = f'''<div>
        <h2 class="font-heading font-semibold text-2xl lg:text-3xl text-navy tracking-tight">{s1["h2"]}</h2>
{"".join(f'        <p class="{"mt-5" if i == 0 else "mt-4"} leading-relaxed">{para}</p>{chr(10)}' for i, para in enumerate(s1["paras"]))}        <ul class="mt-6 space-y-2.5 text-[15px]">
{li(s1["bullets"])}
        </ul>
      </div>'''
    m = media(s1["img"])
    if img_first:
        m = m.replace('class="', 'class="order-last lg:order-first ', 1)
    cols = f"{m}\n      {text_block}" if img_first else f"{text_block}\n      {m}"

    extra = ""
    for sec in p.get("extra", []):
        extra += f'''
<!-- ═══════════════ {sec["h2"].upper()[:40]} ═══════════════ -->
<section class="py-12 sm:py-16 lg:py-24">
  <div class="max-w-4xl mx-auto px-4 sm:px-6">
    <h2 class="font-heading font-semibold text-3xl text-navy tracking-tight">{sec["h2"]}</h2>
{"".join(f'    <p class="mt-5 text-lg leading-relaxed max-sm:text-[16.5px]">{para}</p>{chr(10)}' for para in sec["paras"])}    <ul class="mt-6 space-y-2.5 text-[15px]">
{li(sec["bullets"])}
    </ul>
  </div>
</section>
'''

    conv, drone = p["compare"]
    suburbs = "\n".join(f'          <li>{s}</li>' for s in p.get("suburbs", SUBURBS))
    suburbs_h3 = p.get("suburbs_h3", "Gold Coast suburbs we service")
    also = p.get("also", "We also deliver across Brisbane, Logan, Ipswich, the Scenic Rim and Northern New South\n"
                         "        Wales, with the Sunshine Coast by arrangement.")
    related_h2 = p.get("related_h2", "Other drone cleaning services on the Gold Coast")
    related = "\n".join(f'''      <a href="{href}" class="group bg-white p-5 sm:p-7 hover:bg-navy transition-colors">
        <h3 class="font-heading font-semibold text-lg text-navy group-hover:text-white transition-colors">{name}</h3>
        <p class="mt-3 text-[15px] leading-relaxed group-hover:text-white/75 transition-colors">{blurb}</p>
      </a>''' for href, name, blurb in [r for r in RELATED if r[0] != slug][:3])

    body = f'''<!-- ═══════════════ BANNER ═══════════════ -->
<section class="page-banner pt-24 pb-10 sm:pt-32 sm:pb-14 lg:pt-48 lg:pb-20 text-white">
  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <p class="text-sky text-[13px] font-semibold tracking-[0.14em] uppercase mb-4">{p["eyebrow"]}</p>
    <h1 class="font-heading font-semibold max-sm:text-[1.75rem] text-3xl lg:text-5xl tracking-tight max-w-3xl leading-tight">
      {p["h1"]}
    </h1>
    <p class="max-sm:mt-4 max-sm:text-[16.5px] mt-5 text-lg text-white/75 max-w-2xl leading-relaxed">
      {p["intro"]}
    </p>
    <div class="mt-8 flex flex-wrap gap-3">
      <a href="contact.html" class="r-md bg-white px-7 py-3.5 font-heading font-semibold text-navy hover:bg-mist transition-colors">Request a Proposal</a>
      <a href="tel:+61432008830" class="inline-flex items-center gap-2 r-md border border-white/40 px-7 py-3.5 font-heading font-semibold text-white hover:bg-white/10 transition-colors">0432 008 830</a>
    </div>
  </div>
</section>

<!-- ═══════════════ SERVICE ═══════════════ -->
<section class="py-12 sm:py-16 lg:py-24">
  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <article class="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
      {cols}
    </article>
  </div>
</section>

<!-- ═══════════════ COMPARISON ═══════════════ -->
<section class="py-12 sm:py-16 lg:py-24 bg-mist border-y border-line">
  <div class="max-w-4xl mx-auto px-4 sm:px-6">
    <h2 class="font-heading font-semibold text-3xl text-navy tracking-tight">{p["compare_h2"]}</h2>
    <p class="max-sm:mt-4 max-sm:text-[16.5px] mt-5 text-lg leading-relaxed">{p["compare_intro"]}</p>
    <div class="mt-10 grid sm:grid-cols-2 gap-px bg-line border border-line">
      <div class="bg-white p-5 sm:p-7">
        <h3 class="font-heading font-semibold text-navy">{conv[0]}</h3>
        <ul class="mt-4 space-y-2.5 text-[15px]">
{li(conv[1], "×", "text-steel/50")}
        </ul>
      </div>
      <div class="bg-white p-5 sm:p-7">
        <h3 class="font-heading font-semibold text-navy">{drone[0]}</h3>
        <ul class="mt-4 space-y-2.5 text-[15px]">
{li(drone[1], "✓", "text-accent")}
        </ul>
      </div>
    </div>
  </div>
</section>
{extra}
<!-- ═══════════════ GOLD COAST ═══════════════ -->
<section class="py-12 sm:py-16 lg:py-24 bg-mist border-y border-line">
  <div class="max-w-4xl mx-auto px-4 sm:px-6">
    <h2 class="font-heading font-semibold text-3xl text-navy tracking-tight">{p["local_h2"]}</h2>
{"".join(f'    <p class="mt-5 text-lg leading-relaxed max-sm:text-[16.5px]">{para}</p>{chr(10)}' for para in p["local"])}    <div class="mt-8 bg-white border border-line p-5 sm:p-7">
      <h3 class="font-heading font-semibold text-navy">{suburbs_h3}</h3>
      <ul class="mt-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-2 text-[15px]">
{suburbs}
      </ul>
      <p class="mt-5 text-[15px] leading-relaxed">
        {also}
      </p>
    </div>
  </div>
</section>

<!-- ═══════════════ FAQ ═══════════════ -->
<section class="py-12 sm:py-16 lg:py-24">
  <div class="max-w-4xl mx-auto px-4 sm:px-6">
    <h2 class="font-heading font-semibold text-3xl text-navy tracking-tight">{p["faq_h2"]}</h2>
    <div class="mt-10 border border-line divide-y divide-line">
{faq_html(p["faqs"])}
    </div>
    <p class="mt-8 text-[15px] leading-relaxed">
      More detail on scoping, documentation and delivery is on our
      <a href="how-it-works.html" class="text-accent font-semibold hover:underline">process page</a>, and our
      insurance and safety documentation is outlined on the
      <a href="compliance.html" class="text-accent font-semibold hover:underline">compliance page</a>.
    </p>
  </div>
</section>

<!-- ═══════════════ RELATED ═══════════════ -->
<section class="py-12 sm:py-16 lg:py-24 bg-mist border-y border-line">
  <div class="max-w-7xl mx-auto px-4 sm:px-6">
    <h2 class="font-heading font-semibold text-3xl text-navy tracking-tight mb-8 sm:mb-12">{related_h2}</h2>
    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-px bg-line border border-line">
{related}
    </div>
    <p class="mt-8 text-[15px]"><a href="services.html" class="text-accent font-semibold hover:underline">View our full capability →</a></p>
  </div>
</section>

<!-- ═══════════════ CTA ═══════════════ -->
<section class="hero-bg py-12 sm:py-16 lg:py-24 text-white">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 text-center">
    <h2 class="font-heading font-semibold max-sm:text-[1.6rem] text-3xl lg:text-[2.5rem] tracking-tight">
      {p["cta_h2"]}
    </h2>
    <p class="max-sm:mt-4 max-sm:text-[16.5px] mt-5 text-lg text-white/75 leading-relaxed">
      Most sites can be scoped and priced from aerial imagery and drawings, without an attendance
      fee or a sales visit.
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
    out = head + hdr + body + footer_html
    open(f"{ROOT}/{slug}", "w", encoding="utf-8", newline="\n").write(out)
    print("wrote", slug, len(out))


RELATED = [
    ("drone-building-washing-gold-coast.html", "Building &amp; facade washing",
     "Low-pressure soft washing of render, concrete, cladding and painted facades, with no scaffold or EWP."),
    ("drone-window-cleaning-gold-coast.html", "Window &amp; curtain wall cleaning",
     "Purified-water cleaning of high-rise glass without swing stage, rope access or anchor certification."),
    ("drone-roof-cleaning-gold-coast.html", "Roof cleaning",
     "Tile, metal and membrane roofs soft washed with no foot traffic, no roof loading and no fall risk."),
    ("drone-solar-panel-cleaning-gold-coast.html", "Solar panel cleaning",
     "Commercial rooftop, ground-mount and carport arrays cleaned with purified water and no module loading."),
]

OCCUPIED_Q = ("Can you work while the building is occupied or trading?",
              "Yes. There is no scaffold erection period, no elevated work platform occupying car parking or "
              "footpath, and no loss of trading frontage. We establish a modest ground exclusion zone that "
              "moves with the work, and schedule around peak occupancy or trading hours.")
AIRSPACE_Q = ("Can you fly anywhere on the Gold Coast?",
              "Not always without approval. Parts of the southern Gold Coast sit within controlled airspace "
              "around Gold Coast Airport, and some sites are close to hospital helipads. These can require "
              "authorisation or occasionally rule the method out. We assess airspace at scoping, before you "
              "commit to anything.")
WEATHER_Q = ("What happens if the weather turns?",
             "Wind, rain and visibility limits are set before each flight. If conditions fall outside them we "
             "reschedule at no cost, and we will not attempt a partial job to hold a booking.")
DOCS_Q = ("What documentation do we receive?",
          "Before works: a site-specific SWMS, risk assessment, insurance certificates of currency and Safety "
          "Data Sheets. After works: a photographic completion report per elevation with condition observations.")

GROUND_CREW = "Two-person crew working from ground level"

PAGES["drone-building-washing-gold-coast.html"] = dict(
    title="Drone Building Washing Gold Coast | Facade Soft Wash | Altitude",
    desc="Drone building washing and facade soft washing for Gold Coast commercial, strata and government "
         "buildings. No scaffold, EWP or rope access. Request a proposal.",
    crumb="Building Washing Gold Coast",
    service_name="Drone building washing",
    eyebrow="Gold Coast &middot; Facade &amp; cladding",
    h1="Drone building washing on the Gold Coast",
    intro="Low-pressure soft washing of render, concrete, cladding and painted facades on commercial, strata "
          "and government buildings, delivered by drone from ground level. No scaffold, no EWP and nobody "
          "working at height.",
    s1=dict(
        h2="Facade cleaning without touching the building",
        paras=[
            "Render, precast concrete, composite panel, brick and painted surfaces. Low-pressure soft-wash "
            "chemistry lifts mould, algae, salt deposit and traffic film without driving water into control "
            "joints, window seals or cladding cavities.",
            "Because nothing is anchored, propped or rigged against the structure, there is no facade loading, "
            "no anchor point certification and no reinstatement of fixings afterwards. Treating the growth "
            "itself, rather than blasting away the surface layer, also lengthens the interval before the next "
            "wash is needed.",
        ],
        bullets=["No scaffold, EWP or swing stage mobilisation",
                 "No road occupancy or footpath closure permits",
                 "Suitable for occupied and trading buildings",
                 "Photographic completion report for every elevation"],
        img=dict(src="images/facade.jpg", alt="Drone soft washing the upper elevation of a commercial building",
                 w=399, h=501, pad=True),
    ),
    compare_h2="Drone washing compared with conventional access",
    compare_intro="On most buildings, getting to the surface costs more than cleaning it. Removing the access "
                  "equipment changes the cost, the program and the risk profile of the job.",
    compare=(("Scaffold, EWP or rope access", [
                 "Access equipment hire, delivery and erection",
                 "Road occupancy or footpath closure permits",
                 "Personnel working at height under fall-arrest",
                 "Weeks on site for a mid-rise building",
                 "Lost car parking and trading frontage"]),
             ("Drone delivery", [
                 GROUND_CREW,
                 "A small exclusion zone that moves with the work",
                 "Days on site, not weeks",
                 "No anchor point certification",
                 "Every elevation photo-documented"])),
    local_h2="Built for coastal conditions",
    local=[
        "Buildings along the Gold Coast strip take salt-laden onshore wind, high humidity and long warm, wet "
        "summers. Those are the conditions mould, algae and lichen thrive in, and salt film dulls render and "
        "coatings well before a repaint is due.",
        "With no access cost to recover, washing can be programmed at the interval each elevation actually "
        "needs. Beachfront aspects facing the weather can be washed more often than sheltered ones, under one "
        "fixed-price program.",
    ],
    faq_h2="Building washing questions",
    faqs=[
        ("How often should a Gold Coast building be washed?",
         "It depends on aspect and exposure. Elevations facing onshore wind and salt soil faster than sheltered "
         "ones, so we set the interval per elevation at scoping rather than applying one blanket frequency."),
        ("Will soft washing damage render, paint or window seals?",
         "Soft washing is low pressure by design. The chemistry lifts organic growth and salt rather than "
         "blasting the surface, so water is not driven into control joints, seals or cladding cavities and "
         "coatings are not stripped."),
        OCCUPIED_Q, AIRSPACE_Q, DOCS_Q,
    ],
    cta_h2="Send us your building",
)

PAGES["drone-window-cleaning-gold-coast.html"] = dict(
    title="Drone Window Cleaning Gold Coast | High-Rise Glass | Altitude",
    desc="High-rise and commercial window cleaning by drone across the Gold Coast. Purified-water curtain wall cleaning with no swing stage or rope access.",
    crumb="Window Cleaning Gold Coast",
    service_name="Drone window and curtain wall cleaning",
    eyebrow="Gold Coast &middot; Windows &amp; curtain wall",
    h1="Drone window cleaning on the Gold Coast",
    intro="Purified-water cleaning of window banks and curtain wall on high-rise, commercial and strata "
          "buildings, delivered from the ground with no swing stage, rope access crew or EWP.",
    s1=dict(
        h2="High-rise glass without rope access",
        paras=[
            "Window banks and curtain wall systems are cleaned and rinsed with purified water to a spot-free "
            "finish. Purified water has had its dissolved minerals removed, so it dries without the spotting "
            "tap water leaves and with no detergent residue on glass or frames.",
            "The conventional alternatives are swing stage, abseil crews or an EWP in the loading zone. Each "
            "carries mobilisation cost, lead time and a work-at-height exposure that this method does not.",
        ],
        bullets=["No building maintenance unit or anchor certification",
                 "No exclusion of pedestrian frontage below",
                 "Shorter site duration than rope access equivalents",
                 "Suitable for residential strata towers and commercial glazing"],
        img=dict(src="images/curtainwall.jpg", alt="Drone rinsing a glazed curtain wall on a Gold Coast commercial building",
                 w=1200, h=800),
    ),
    compare_h2="Drone window cleaning compared with rope access",
    compare_intro="For tall glazed elevations, the access method sets most of the price and most of the risk.",
    compare=(("Rope access or swing stage", [
                 "Roof anchor inspection and certification",
                 "Abseil crew exposed to a fall hazard",
                 "Footpath and frontage exclusion below the drop",
                 "Longer program, one drop at a time",
                 "Booking lead times for specialist crews"]),
             ("Drone delivery", [
                 GROUND_CREW,
                 "No anchor certification needed",
                 "Moving ground exclusion zone",
                 "Large glazed areas covered quickly",
                 "Photo-documented completion report"])),
    local_h2="Glass in a salt-air environment",
    local=[
        "Beachfront towers in Surfers Paradise, Broadbeach and Main Beach collect salt spray that builds into a "
        "hazy film on the glass. For body corporate committees and building managers, glass cleaning is a "
        "recurring cost driven largely by access, not by the cleaning itself.",
        "Taking rope access out of the scope lowers the cost of each clean. That makes a regular program "
        "practical on elevations that would otherwise be left until they are noticeably dirty.",
    ],
    faq_h2="Window cleaning questions",
    faqs=[
        ("Can a drone clean high-rise windows on the Gold Coast?",
         "Yes. High-rise glazed elevations are cleaned with the crew on the ground, provided the site's airspace "
         "allows it. We check airspace for every site at scoping, before anything is booked."),
        ("Is drone window cleaning as good as a rope access clean?",
         "For salt film, dust and atmospheric soiling, purified-water cleaning gives a spot-free finish. Heavy "
         "mechanical staining, graffiti or coating removal is not suited to the method, and we will tell you so "
         "at scoping rather than mobilise to a job we cannot finish properly."),
        OCCUPIED_Q, WEATHER_Q, AIRSPACE_Q,
    ],
    cta_h2="Send us your elevations",
)

PAGES["drone-roof-cleaning-gold-coast.html"] = dict(
    title="Drone Roof Cleaning Gold Coast | Commercial & Strata | Altitude",
    desc="Commercial, strata and industrial roof cleaning by drone on the Gold Coast. Tile, metal and "
         "membrane roofs soft washed with no foot traffic or fall risk.",
    crumb="Roof Cleaning Gold Coast",
    service_name="Drone roof cleaning",
    eyebrow="Gold Coast &middot; Roofs",
    h1="Drone roof cleaning on the Gold Coast",
    intro="Tile, metal sheet and membrane roofs on commercial, strata, government and industrial property, "
          "soft washed by drone with no foot traffic on the roof, no roof loading and nobody exposed to a fall.",
    s1=dict(
        img_first=True,
        h2="Roofs cleaned with nobody on them",
        paras=[
            "Beyond the fall hazard, keeping people off the roof removes the trafficking damage that drives a "
            "meaningful share of post-maintenance roof defects: cracked tiles, deformed sheeting and punctured "
            "membrane.",
            "Soft-wash treatment addresses the biological growth itself rather than blasting away the surface "
            "layer. That protects the roof material and extends the interval before the next clean is required.",
        ],
        bullets=["No roof access permit or fall-arrest system required",
                 "No trafficking damage to tiles, sheeting or membrane",
                 "Suitable for brittle and heritage roof materials",
                 "Works scheduled around operating hours"],
        img=dict(src="images/drone.jpg", alt="Altitude's six-rotor spray drone used for roof soft washing", w=1000, h=1000, pad=True),
    ),
    extra=[dict(
        h2="Industrial and warehouse roofs",
        paras=[
            "Distribution centres, manufacturing facilities and warehouse estates across the Gold Coast's "
            "industrial areas. Large roof and wall areas are covered in a single mobilisation and scheduled "
            "around production and despatch windows.",
            "Where roof entry triggers a permit process, a height safety review and often a production pause, "
            "removing roof access from the scope is frequently the largest saving in the job.",
        ],
        bullets=["No height safety mobilisation", "Multi-building estates handled under one program",
                 "Wall cladding cleaned in the same visit"],
    )],
    compare_h2="Drone roof cleaning compared with walking the roof",
    compare_intro="Conventional roof cleaning puts people on the surface being cleaned. That is where most of "
                  "the risk and much of the damage comes from.",
    compare=(("Crew on the roof", [
                 "Fall-arrest systems and roof access permits",
                 "Foot traffic cracking tiles and denting sheeting",
                 "High-pressure cleaning that erodes the surface",
                 "Production pauses on operational sites"]),
             ("Drone delivery", [
                 GROUND_CREW,
                 "No load or foot traffic on the roof",
                 "Low-pressure soft wash that treats the cause",
                 "Scheduled around operating hours"])),
    local_h2="Roofs in a subtropical climate",
    local=[
        "Warm, humid Gold Coast summers suit the algae and lichen that cause dark streaking on tile and metal "
        "roofs. Left untreated, that growth holds moisture against the roof surface and shortens the life of "
        "coatings.",
        "Treating the growth at the cause, without walking on the roof, keeps the roof in condition between "
        "planned maintenance cycles.",
    ],
    faq_h2="Roof cleaning questions",
    faqs=[
        ("Is drone roof cleaning suitable for old or brittle tiles?",
         "Yes. Nothing and nobody walks on the roof, so there is no trafficking load on the tiles. That makes "
         "the method suitable for brittle and heritage roof materials."),
        ("Do you need a roof access permit?",
         "Not for the cleaning task. The crew works from the ground, so roof entry, fall-arrest and the permits "
         "that go with them are removed from the scope."),
        ("Does soft washing just remove the stain, or the growth?",
         "Soft washing treats the biological growth itself rather than blasting away the surface layer. That "
         "extends the interval before the next clean."),
        WEATHER_Q, AIRSPACE_Q,
    ],
    cta_h2="Send us your roof",
)

PAGES["drone-solar-panel-cleaning-gold-coast.html"] = dict(
    title="Solar Panel Cleaning Gold Coast | Commercial Drone | Altitude",
    desc="Commercial solar panel cleaning by drone on the Gold Coast. Purified water, no module loading, nobody on the roof. Rooftop, ground and carport arrays.",
    crumb="Solar Panel Cleaning Gold Coast",
    service_name="Commercial solar panel cleaning",
    eyebrow="Gold Coast &middot; Solar arrays",
    h1="Commercial solar panel cleaning on the Gold Coast",
    intro="Purified-water cleaning of commercial rooftop, ground-mount and carport solar arrays, delivered by "
          "drone with no module loading and no technicians traversing the array.",
    s1=dict(
        img_first=True,
        h2="Recovering soiling losses without anyone on the array",
        paras=[
            "Dust, salt deposition, bird fouling and organic film reduce array output over time. Purified-water "
            "cleaning restores transmission without detergents, abrasives or module loading, and without "
            "technicians working across an energised array on a roof.",
            "Large arrays are covered in a single mobilisation, and cleaning intervals can be aligned to your "
            "generation reporting so cleans happen when the data says they pay for themselves.",
        ],
        bullets=["No module or roof loading",
                 "Purified water with no detergent residue",
                 "Large arrays covered in a single mobilisation",
                 "Rooftop, ground-mount and carport structures"],
        img=dict(src="images/solar.jpg", alt="Drone rinsing a commercial solar array with purified water",
                 w=447, h=447, pad=True),
    ),
    compare_h2="Drone cleaning compared with manual panel cleaning",
    compare_intro="Manual cleaning of a commercial array means people, brushes and water on a roof full of "
                  "energised equipment.",
    compare=(("Technicians on the roof", [
                 "Roof access, fall-arrest and permits",
                 "Personnel working among energised modules",
                 "Foot traffic and kneeling loads near modules",
                 "Slow progress across large arrays"]),
             ("Drone delivery", [
                 GROUND_CREW,
                 "No load on modules or roof",
                 "Purified water, no abrasives",
                 "Large arrays in one mobilisation"])),
    local_h2="Why Gold Coast arrays soil quickly",
    local=[
        "Coastal arrays collect salt deposition carried on onshore wind, along with bird fouling and dust from "
        "the region's ongoing construction. A thin film across a large commercial array adds up to a "
        "measurable loss in generation.",
        "Because there is no roof access to arrange, cleans can be scheduled when your generation data shows "
        "soiling losses, rather than on a fixed calendar.",
    ],
    faq_h2="Solar cleaning questions",
    faqs=[
        ("Will drone cleaning affect our panel warranty?",
         "Cleaning uses purified water only, with no detergents, abrasives or load on the modules. We recommend "
         "checking your manufacturer's cleaning guidance, and we will work to it."),
        ("How often should commercial solar panels be cleaned?",
         "It depends on location and soiling. Coastal and dusty sites soil faster. We recommend aligning cleans "
         "to your generation reporting so each clean is justified by the recovered output."),
        ("Can you clean ground-mount and carport arrays?",
         "Yes. The method applies to commercial rooftop installations, ground-mount arrays and carport "
         "structures."),
        WEATHER_Q, AIRSPACE_Q,
    ],
    cta_h2="Send us your array",
)

PAGES["drone-strata-building-cleaning-gold-coast.html"] = dict(
    title="Strata &amp; Body Corporate Building Cleaning Gold Coast | Altitude",
    desc="Drone building and window cleaning for Gold Coast strata and body corporate. No scaffold, residents stay put, fixed pricing and committee-ready documents.",
    crumb="Strata &amp; Body Corporate",
    service_name="Strata and body corporate building cleaning",
    eyebrow="Gold Coast &middot; Strata &amp; body corporate",
    h1="Drone building cleaning for Gold Coast strata and body corporate",
    intro="Facade washing, window cleaning and roof cleaning for residential towers and strata complexes, "
          "delivered by drone with no scaffold on the balconies, no swing stage past the windows and nobody "
          "working at height.",
    s1=dict(
        h2="Exterior cleaning residents barely notice",
        paras=[
            "Scaffold and rope access are disruptive in a residential building. Balconies are blocked, privacy "
            "is lost for weeks, and the pool deck or car park is fenced off. Drone delivery removes all of that. "
            "A small ground exclusion zone moves with the work, and each elevation is finished in a fraction of "
            "the time.",
            "For building managers and committees, the bigger change is cost. Access equipment is usually the "
            "largest line in an exterior clean. Removing it makes regular cleaning affordable enough to plan "
            "rather than defer.",
        ],
        bullets=["No scaffold or swing stage past balconies and windows",
                 "Residents stay in their apartments",
                 "No anchor point certification required",
                 "Fixed pricing per cleaning cycle"],
        img=dict(src="images/tower.jpg", alt="Drone cleaning the upper elevations of a glazed residential tower",
                 w=783, h=391),
    ),
    extra=[dict(
        h2="What the committee receives",
        paras=[
            "Committees need to approve the works, and building managers need a record that stands up later. "
            "Every engagement is documented before and after, so you can table it at the next meeting without "
            "chasing the contractor.",
        ],
        bullets=["A fixed-scope, fixed-price proposal for the committee",
                 "Site-specific SWMS and risk assessment before works",
                 "Certificates of currency for public liability and aviation cover",
                 "A photographic completion report for every elevation",
                 "Condition observations to feed your maintenance plan"],
    )],
    compare_h2="Drone cleaning compared with scaffold and rope access",
    compare_intro="For a residential tower, the access method decides how long residents are disrupted and "
                  "how much of the budget goes on equipment rather than cleaning.",
    compare=(("Scaffold, swing stage or rope access", [
                 "Balconies blocked and privacy lost for weeks",
                 "Pool decks, driveways or car parks fenced off",
                 "Roof anchor inspection and certification",
                 "Access hire as the largest cost line"]),
             ("Drone delivery", [
                 GROUND_CREW,
                 "Days on site, not weeks",
                 "A small exclusion zone that moves with the work",
                 "Budget spent on cleaning, not access"])),
    local_h2="Strata buildings on the Gold Coast",
    local=[
        "Beachfront and canal-front towers take salt spray, humidity and wind-driven rain that stain render, "
        "dull glass and grow mould on shaded elevations. Most strata buildings on the Gold Coast need exterior "
        "cleaning more often than their maintenance plans allow for.",
        "We set cleaning intervals per elevation rather than one frequency for the whole building, and price "
        "each cycle as a fixed amount the committee can budget for.",
    ],
    faq_h2="Strata and body corporate questions",
    faqs=[
        ("Do residents need to leave their apartments?",
         "No. The crew works from the ground and a small exclusion zone moves around the building with the "
         "work. We coordinate notice with building management for each elevation before it is cleaned."),
        ("Can the committee budget for it as a recurring cost?",
         "Yes. Scheduled programs are priced as a fixed amount per cleaning cycle, so the cost can be planned "
         "for rather than approved as a one-off each time."),
        ("What documents do you provide for the committee?",
         "A fixed-scope proposal before approval. Then a site-specific SWMS, risk assessment, insurance "
         "certificates of currency and Safety Data Sheets before works, and a photographic completion report "
         "per elevation afterwards."),
        OCCUPIED_Q, AIRSPACE_Q,
    ],
    cta_h2="Send us your building",
)

PAGES["drone-cleaning-brisbane.html"] = dict(
    title="Drone Cleaning Brisbane | Facade, Window &amp; Roof | Altitude",
    desc="Commercial drone cleaning across Brisbane, Logan and Ipswich. Facade, window, roof and solar cleaning for commercial, strata and government property.",
    crumb="Drone Cleaning Brisbane",
    service_name="Commercial drone cleaning",
    eyebrow="Brisbane &middot; Logan &middot; Ipswich",
    h1="Commercial drone cleaning in Brisbane",
    intro="Facade, roof, window and solar cleaning by drone for commercial, strata and government property "
          "across Brisbane, Logan and Ipswich. No scaffold, no EWP and nobody working at height.",
    area_served=[{"@type": "City", "name": "Brisbane"}, {"@type": "City", "name": "Logan"},
                 {"@type": "City", "name": "Ipswich"}],
    s1=dict(
        h2="One contractor for the whole exterior",
        paras=[
            "Altitude is a South East Queensland drone cleaning contractor based on the Gold Coast. Brisbane, "
            "Logan and Ipswich are part of our regular service area, not an occasional trip.",
            "Every scope is delivered the same way: from ground level by a two-person crew, with a site-specific "
            "SWMS before works and a photographic completion report afterwards.",
        ],
        bullets=['<a href="drone-building-washing-gold-coast.html" class="text-accent font-semibold hover:underline">Facade and building washing</a>',
                 '<a href="drone-window-cleaning-gold-coast.html" class="text-accent font-semibold hover:underline">Window and curtain wall cleaning</a>',
                 '<a href="drone-roof-cleaning-gold-coast.html" class="text-accent font-semibold hover:underline">Roof and industrial roof cleaning</a>',
                 '<a href="drone-solar-panel-cleaning-gold-coast.html" class="text-accent font-semibold hover:underline">Commercial solar panel cleaning</a>'],
        img=dict(src="images/glasstower.jpg", alt="Drone soft washing the glazed elevation of a high-rise tower",
                 w=800, h=486),
    ),
    compare_h2="Drone cleaning compared with conventional access",
    compare_intro="On most buildings, getting to the surface costs more than cleaning it.",
    compare=(("Scaffold, EWP or rope access", [
                 "Access equipment hire, delivery and erection",
                 "Road occupancy or footpath closure permits",
                 "Personnel working at height under fall-arrest",
                 "Weeks on site for a mid-rise building"]),
             ("Drone delivery", [
                 GROUND_CREW,
                 "A small exclusion zone that moves with the work",
                 "Days on site, not weeks",
                 "Every elevation photo-documented"])),
    local_h2="Working across Brisbane",
    local=[
        "Brisbane's warm, humid summers suit the mould, algae and lichen that stain facades and roofs, and "
        "traffic film builds up quickly on buildings near main roads. Industrial estates in Brisbane's south "
        "and west carry large roof areas where roof access is the biggest cost in the job.",
        "Parts of inner Brisbane sit within controlled airspace around Brisbane Airport and Archerfield, or "
        "close to hospital helipads. We assess airspace for every site at scoping, before you commit to "
        "anything.",
    ],
    suburbs_h3="Areas we service",
    suburbs=["Brisbane CBD", "Fortitude Valley", "South Brisbane", "Newstead", "Bowen Hills", "Milton",
             "Woolloongabba", "Eight Mile Plains", "Rocklea", "Acacia Ridge", "Springwood", "Logan Central",
             "Beenleigh", "Yatala", "Ipswich", "Springfield"],
    also="Our base is the Gold Coast, and we also cover the Scenic Rim and Northern New South Wales, with the "
         "Sunshine Coast by arrangement.",
    faq_h2="Brisbane questions",
    faqs=[
        ("Do you service Brisbane from the Gold Coast?",
         "Yes. Brisbane, Logan and Ipswich are part of our regular service area across South East Queensland."),
        ("Can you fly in the Brisbane CBD?",
         "Sometimes. Parts of inner Brisbane sit within controlled airspace or near hospital helipads, which can "
         "require authorisation or occasionally rule the method out. We assess this at scoping, before you "
         "commit to anything."),
        ("Do you need to visit the site to quote?",
         "Usually not. Most sites can be scoped and priced from aerial imagery and drawings, without an "
         "attendance fee or a sales visit."),
        OCCUPIED_Q, DOCS_Q,
    ],
    related_h2="Our drone cleaning services",
    cta_h2="Send us your Brisbane site",
)

for slug, p in PAGES.items():
    build(slug, p)
