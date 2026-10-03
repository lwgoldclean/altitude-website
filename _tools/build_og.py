# Builds the 1200x630 social share cards in images/og/, one per page, so a
# shared link shows that page's subject rather than the same photo every time.
# Run from anywhere:  python _tools/build_og.py
# Each page's og:image / twitter:image points at images/og/<page>.jpg; pages
# built by build_pages.py pick theirs up automatically.
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = f"{ROOT}/images/og"
os.makedirs(OUT, exist_ok=True)

NAVY, SKY = (10, 37, 64), (42, 163, 232)
W, H, PANEL = 1200, 630, 640

# page (without .html) -> (headline, photo)
CARDS = {
    "index": ("Commercial drone cleaning on the Gold Coast", "og-card.jpg"),
    "services": ("Drone facade, roof, window and solar cleaning", "curtainwall.jpg"),
    "drone-building-washing-gold-coast": ("Drone building washing on the Gold Coast", "facade.jpg"),
    "drone-window-cleaning-gold-coast": ("Drone window cleaning on the Gold Coast", "curtainwall.jpg"),
    "drone-roof-cleaning-gold-coast": ("Drone roof cleaning on the Gold Coast", "drone.jpg"),
    "drone-solar-panel-cleaning-gold-coast": ("Commercial solar panel cleaning on the Gold Coast", "solar.jpg"),
    "drone-strata-building-cleaning-gold-coast": ("Drone cleaning for strata and body corporate", "tower.jpg"),
    "drone-cleaning-brisbane": ("Commercial drone cleaning in Brisbane", "glasstower.jpg"),
    "compliance": ("Compliance, insurance and safety documentation", "drone.jpg"),
    "contact": ("Request a drone cleaning proposal", "glasstower.jpg"),
    "how-it-works": ("How a drone cleaning engagement runs", "tower.jpg"),
    "capability-statement": ("Capability statement", "facade.jpg"),
    "about": ("A specialist drone cleaning contractor", "drone.jpg"),
    "guides": ("Guides for building and facility managers", "curtainwall.jpg"),
    "guide-drone-building-cleaning-cost": ("What drone building cleaning costs", "facade.jpg"),
    "guide-drone-vs-rope-access-scaffold-ewp": ("Drone, rope access, EWP or scaffold?", "glasstower.jpg"),
    "guide-drone-cleaning-casa-rules": ("Drone cleaning and CASA: what to check", "drone.jpg"),
}


def font(size, weight):
    f = ImageFont.truetype(f"{ROOT}/fonts/ibm-plex-sans.woff2", size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def wrap(draw, text, f, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=f) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def card(slug, headline, photo):
    img = Image.new("RGB", (W, H), NAVY)
    ph = Image.open(f"{ROOT}/images/{photo}").convert("RGB")
    pw, phh = W - PANEL, H
    scale = max(pw / ph.width, phh / ph.height)
    ph = ph.resize((round(ph.width * scale), round(ph.height * scale)), Image.LANCZOS)
    left, top = (ph.width - pw) // 2, (ph.height - phh) // 2
    img.paste(ph.crop((left, top, left + pw, top + phh)), (PANEL, 0))

    d = ImageDraw.Draw(img)
    d.rectangle((PANEL - 6, 0, PANEL, H), fill=SKY)
    x = 64
    d.text((x, 64), "ALTITUDE", font=font(30, 600), fill="white")
    d.text((x, 102), "DRONE EXTERIOR CLEANING", font=font(15, 600), fill=SKY)

    size = 56
    while True:
        f = font(size, 600)
        lines = wrap(d, headline, f, PANEL - x - 56)
        if len(lines) <= 4 or size <= 40:
            break
        size -= 4
    lh = round(size * 1.18)
    y = (H - lh * len(lines)) // 2 + 10
    for line in lines:
        d.text((x, y), line, font=f, fill="white")
        y += lh

    d.text((x, H - 84), "altitudedroneexteriorcleaning.com", font=font(20, 500), fill=(200, 212, 224))
    d.text((x, H - 54), "0432 008 830  |  Gold Coast & Brisbane", font=font(20, 500), fill=(200, 212, 224))
    img.save(f"{OUT}/{slug}.jpg", quality=85, optimize=True, progressive=True)


for slug, (headline, photo) in CARDS.items():
    if os.path.exists(f"{ROOT}/images/{photo}"):
        card(slug, headline, photo)
        print("wrote", f"images/og/{slug}.jpg")
