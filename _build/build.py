#!/usr/bin/env python3
"""Build the Westerly Metals static site: src/pages/*.html -> site/*.html."""
import json, math, os, re, shutil, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC, SITE = os.path.join(ROOT, "src"), os.path.dirname(ROOT)  # _build/ -> repo root
SITE_URL = "https://rdodeployme.github.io/westerly-metals/"
PHONE, PHONE_TEL, EMAIL = "0418 524 602", "0418524602", "sean@nunjara.com"
ADDRESS_Q = "Atkinsons Road, Moorabool VIC 3213"
LAT, LON = -38.0322, 144.2577
MAPS_DIR = "https://www.google.com/maps/dir/?api=1&destination=Atkinsons+Road%2C+Moorabool+VIC+3213"
MAP_IFRAME = (
    '<iframe title="Map: Atkinsons Road, Moorabool" loading="lazy" referrerpolicy="no-referrer" '
    'src="https://www.openstreetmap.org/export/embed.html?bbox=144.205%2C-38.062%2C144.31%2C-38.002&amp;layer=mapnik&amp;marker=-38.0322%2C144.2577"></iframe>'
    f'<a class="map-open btn btn-amber" href="{MAPS_DIR}" target="_blank" rel="noopener">Open in Google Maps</a>'
)

NAV = [("savings", "savings.html", "Savings"), ("prices", "prices.html", "Prices"), ("take", "what-we-take.html", "What we take"),
       ("pickups", "pickups.html", "Pickups"), ("find", "find-us.html", "Find us")]

PHONE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.6a1 1 0 0 1-.25 1z"/></svg>'
PIN_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>'

# ---------------------------------------------------------------- data
EXCLUDE = {"Ararat", "Beaufort"}  # quicker to Melbourne via the Western Freeway
towns = [t for t in json.load(open(os.path.join(ROOT, "data", "towns.json"))) if t["town"] not in EXCLUDE]



def _ver():
    """Short content hash of the CSS, JS and town data, added to asset links so browsers fetch new versions."""
    import hashlib
    h = hashlib.sha1()
    for f in (os.path.join(SRC, "css", "main.css"), os.path.join(SRC, "js", "main.js"), os.path.join(ROOT, "data", "towns.json")):
        h.update(open(f, "rb").read())
    return h.hexdigest()[:8]
VER = _ver()

def X(h):  # hours chart: 4am to 8pm window
    return (h - 4) / 16 * 100


def hours_chart():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    rows = []
    for i, d in enumerate(days):
        us = f'<span class="hbar us" style="left:{X(6):.3f}%;width:{X(18)-X(6):.3f}%"></span>'
        them = (f'<span class="hbar them" style="left:{X(7.5):.3f}%;width:{X(16)-X(7.5):.3f}%"></span>' if i < 5 else "")
        rows.append(f'<div class="hday">{d}</div><div class="htrack" role="presentation">{us}{them}</div>')
    ticks = "".join(
        f'<span style="left:{X(h):.3f}%">{lab}</span>' for h, lab in [(6, "6am"), (12, "12pm"), (18, "6pm")]
    )
    return (
        '<figure class="hours" style="margin:0">'
        '<figcaption class="hours-legend"><span><i class="k-us"></i>Westerly Metals, 6am to 6pm</span>'
        '<span><i class="k-them"></i>A weekday-only yard, 7:30am to 4pm</span></figcaption>'
        f'<div class="hgrid">{"".join(rows)}<div class="haxis" aria-hidden="true">{ticks}</div></div>'
        '<div class="hours-sum"><span><b>84</b>hours a week open here</span><span class="them"><b>42.5</b>at a weekday-only yard</span></div>'
        "</figure>"
    )


def towns_table():
    rows = sorted(towns, key=lambda t: t["yard_km"])
    body = "".join(
        f'<tr><td>{t["town"]}</td><td>{t["yard_km"]} km</td><td>{t["mel_km"]} km</td>'
        f'<td class="save">{2*(t["mel_km"]-t["yard_km"])} km</td><td class="t-time">{fmt_min(max(0, 2*(t["mel_min"]-t["yard_min"])))}</td></tr>'
        for t in rows
    )
    return (
        '<table class="towns"><caption class="sr">Road distance from each town to Westerly Metals and to Laverton North</caption>'
        '<thead><tr><th scope="col">Town</th><th scope="col"><span class="lg">To Westerly</span><span class="sh">To us</span></th>'
        '<th scope="col"><span class="lg">To Laverton North</span><span class="sh">Laverton</span></th>'
        '<th scope="col"><span class="lg">Saved per round trip</span><span class="sh">Saved</span></th><th scope="col" class="t-time">Time back</th></tr></thead>'
        f"<tbody>{body}</tbody></table>"
    )


def fmt_min(m):
    m = int(round(m))
    if m < 5:
        return "about the same"
    if m < 60:
        return f"{m} min"
    h, r = divmod(m, 60)
    return f"{h} hr {r} min" if r else f"{h} hr"


def region_map(mobile=False):
    land = json.load(open(os.path.join(ROOT, "geo", "land_clip.json")))
    lon0, lon1, lat0, lat1 = 141.25, 145.15, -38.72, -37.38
    k = 1000 / ((lon1 - lon0) * math.cos(math.radians(38)))
    W = 1000
    H = (lat1 - lat0) * k

    def P(lon, lat):
        return ((lon - lon0) * math.cos(math.radians(38)) * k, (lat1 - lat) * k)

    paths = ""
    for ring in land:
        pts = [P(x, y) for x, y in ring]
        paths += "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z "
    label_off = {  # town: (dx, dy, anchor)
        "Warrnambool": (0, 26, "middle"), "Port Fairy": (-10, 24, "end"), "Koroit": (-8, -12, "end"),
        "Portland": (0, 26, "middle"), "Hamilton": (0, -14, "middle"), "Heywood": (-10, 5, "end"),
        "Casterton": (0, -14, "middle"), "Coleraine": (10, -10, "start"), "Dunkeld": (10, -8, "start"),
        "Penshurst": (10, 14, "start"), "Mortlake": (10, -8, "start"), "Terang": (-10, -10, "end"),
        "Camperdown": (12, -10, "start"), "Cobden": (8, 20, "start"), "Timboon": (0, 24, "middle"),
        "Colac": (0, 26, "middle"), "Lismore": (10, -8, "start"), "Derrinallum": (-10, -8, "end"),
        "Skipton": (0, -14, "middle"), "Lake Bolac": (0, -14, "middle"), "Willaura": (0, -14, "middle"),
        "Winchelsea": (0, 26, "middle"), "Birregurra": (10, 20, "start"), "Inverleigh": (-10, 5, "end"),
        "Cressy": (0, -14, "middle"), "Bannockburn": (6, -14, "middle"), "Meredith": (0, -14, "middle"),
        "Teesdale": (-10, 5, "end"),
    }
    big = {"Warrnambool", "Hamilton", "Portland", "Colac", "Camperdown"}
    if mobile:
        label_off = {"Warrnambool": (0, 52, "middle"), "Portland": (0, 52, "middle"), "Hamilton": (0, -24, "middle"),
                     "Camperdown": (0, -24, "middle"), "Colac": (0, 52, "middle")}
    dots, labels = "", ""
    for t in towns:
        x, y = P(t["lon"], t["lat"])
        r = (10 if t["town"] in big else 6.5) if mobile else (5.5 if t["town"] in big else 4)
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#F2EFE9"/>'
        if mobile and t["town"] not in label_off:
            continue
        dx, dy, a = label_off.get(t["town"], (8, -8, "start"))
        cls = "tb" if t["town"] in big else "ts"
        labels += f'<text class="{cls}" x="{x+dx:.1f}" y="{y+dy:.1f}" text-anchor="{a}">{t["town"]}</text>'
    yx, yy = P(LON, LAT)
    lx, ly = P(144.7964, -37.8297)
    mx, my = P(144.963, -37.814)
    sfx = "m" if mobile else "d"
    if mobile:
        css = (".tb{font:700 44px 'Barlow Condensed',sans-serif;fill:#F2EFE9;letter-spacing:.02em;paint-order:stroke;stroke:#252C31;stroke-width:12px;stroke-linejoin:round}"
               ".big{font:700 52px 'Barlow Condensed',sans-serif;letter-spacing:.06em;paint-order:stroke;stroke:#252C31;stroke-width:12px;stroke-linejoin:round}"
               ".cap{font:700 36px 'Barlow Condensed',sans-serif;letter-spacing:.04em;paint-order:stroke;stroke:#16232C;stroke-width:10px;stroke-linejoin:round}")
        marks = f'''<line x1="{yx:.1f}" y1="{yy:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" stroke="#F4A12E" stroke-width="6" stroke-dasharray="3 12" stroke-linecap="round"/>
<text class="cap" x="{(yx+lx)/2-10:.1f}" y="{(yy+ly)/2+58:.1f}" text-anchor="start" fill="#F4A12E">+45 KM</text>
<circle cx="{lx:.1f}" cy="{ly:.1f}" r="16" fill="#5B656E" stroke="#111417" stroke-width="5"/>
<text class="cap" x="{lx+20:.1f}" y="{ly-30:.1f}" text-anchor="end" fill="#9AA3AA">LAVERTON</text>
<circle cx="{yx:.1f}" cy="{yy:.1f}" r="40" fill="#F4A12E" opacity=".22"/>
<circle cx="{yx:.1f}" cy="{yy:.1f}" r="19" fill="#F4A12E" stroke="#111417" stroke-width="5"/>
<text class="big" x="{yx-10:.1f}" y="{yy+82:.1f}" text-anchor="middle" fill="#F4A12E">WESTERLY</text>'''
    else:
        css = (".ts{font:600 15px 'Barlow Condensed',sans-serif;fill:#C9CDD0;letter-spacing:.02em}.tb{font:700 19px 'Barlow Condensed',sans-serif;fill:#F2EFE9;letter-spacing:.03em}"
               ".big{font:700 22px 'Barlow Condensed',sans-serif;letter-spacing:.08em}.cap{font:600 15px 'Barlow Condensed',sans-serif;letter-spacing:.06em}")
        marks = f'''<line x1="{yx:.1f}" y1="{yy:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" stroke="#F4A12E" stroke-width="3" stroke-dasharray="2 7" stroke-linecap="round"/>
<text class="cap" x="{(yx+lx)/2-6:.1f}" y="{(yy+ly)/2+28:.1f}" text-anchor="start" fill="#F4A12E">+45 KM EACH WAY</text>
<circle cx="{lx:.1f}" cy="{ly:.1f}" r="9" fill="#5B656E" stroke="#111417" stroke-width="3"/>
<text class="big" x="{lx-4:.1f}" y="{ly-20:.1f}" text-anchor="middle" fill="#9AA3AA">LAVERTON NORTH</text>
<circle cx="{yx:.1f}" cy="{yy:.1f}" r="22" fill="#F4A12E" opacity=".22"/>
<circle cx="{yx:.1f}" cy="{yy:.1f}" r="11" fill="#F4A12E" stroke="#111417" stroke-width="3"/>
<text class="big" x="{yx:.1f}" y="{yy+44:.1f}" text-anchor="middle" fill="#F4A12E">WESTERLY</text>
<text class="cap" x="{yx:.1f}" y="{yy+64:.1f}" text-anchor="middle" fill="#F2EFE9">MOORABOOL</text>'''
    svg = f'''<svg viewBox="0 0 {W} {H:.0f}" role="img" aria-labelledby="rm-t{sfx} rm-d{sfx}" xmlns="http://www.w3.org/2000/svg">
<title id="rm-t{sfx}">Map of western Victoria</title>
<desc id="rm-d{sfx}">Western District towns, Westerly Metals at Moorabool, and the Laverton North yards about 45 km further east.</desc>
<style>{css}</style>
<rect width="{W}" height="{H:.0f}" fill="#16232C"/>
<path d="{paths}" fill="#252C31" stroke="#3B444B" stroke-width="{2.4 if mobile else 1.2}"/>
{dots}{labels}
{marks}
</svg>'''
    return svg


PRICES = json.load(open(os.path.join(ROOT, "data", "prices.json")))


def price_board():
    fams = PRICES["families"]
    tabs = "".join(
        f'<button type="button" role="tab" id="pt-{f["key"]}" aria-controls="pp-{f["key"]}" aria-selected="{"true" if i == 0 else "false"}">'
        f'<i style="background:{f["colour"]}"></i>{f["name"]}</button>' for i, f in enumerate(fams)
    ) + '<button type="button" role="tab" id="pt-fees" aria-controls="pp-fees" aria-selected="false"><i class="fee-dot"></i>Handling fees</button>'
    panes = ""
    for i, f in enumerate(fams):
        rows = "".join(
            f'<div class="grade"><div><b>{n}</b><small>{d}</small></div>'
            f'<div class="price" data-rate="{gid}"><a class="call-rate" href="tel:{PHONE_TEL}">Call</a></div></div>'
            for gid, n, d in f["grades"]
        )
        panes += f'<div class="grades" role="tabpanel" id="pp-{f["key"]}" aria-labelledby="pt-{f["key"]}"{"" if i == 0 else " hidden"}>{rows}</div>'
    rows = "".join(
        f'<div class="grade"><div><b>{n}</b><small>{d}</small></div>'
        f'<div class="price" data-fee="{fid}"><span class="quoted">Quoted</span></div></div>'
        for fid, n, d in PRICES["fees"]
    )
    panes += f'<div class="grades" role="tabpanel" id="pp-fees" aria-labelledby="pt-fees" hidden>{rows}</div>'
    return (
        '<div class="board">'
        '<div class="board-top"><div class="live" id="rates-stamp"><i></i><span>Rates per kg for clean, sorted metal</span></div>'
        f'<div class="mtabs" role="tablist" aria-label="Metal">{tabs}</div></div>'
        f'{panes}'
        '<div class="board-foot"><p>Clean, sorted metal gets the best rate. Mixed or dirty loads are graded on the scale, '
        'and the final price is set when it\'s weighed.</p>'
        '<a class="btn btn-amber" href="#estimate">Estimate my load</a></div>'
        "</div>"
    )


def estimator_rows():
    out = ""
    for f in PRICES["families"]:
        opts = "".join(f'<option value="{gid}">{n}</option>' for gid, n, d in f["grades"])
        out += (
            f'<div class="mrow" data-family="{f["key"]}">'
            f'<span class="sw" style="background:{f["colour"]}"></span>'
            f'<div class="mrow-main"><b>{f["name"]}</b>'
            f'<label class="sr" for="g-{f["key"]}">{f["name"]} grade</label><select id="g-{f["key"]}" class="mgrade">{opts}</select></div>'
            f'<div class="kg"><button type="button" class="kg-minus" aria-label="10 kg less {f["name"].lower()}">\u2212</button>'
            f'<label class="sr" for="kg-{f["key"]}">{f["name"]} kilos</label>'
            f'<input id="kg-{f["key"]}" class="kg-in" type="number" inputmode="numeric" min="0" step="10" value="0">'
            f'<span class="kg-u">kg</span>'
            f'<button type="button" class="kg-plus" aria-label="10 kg more {f["name"].lower()}">+</button></div>'
            "</div>"
        )
    return out


def town_options():
    return "".join(f'<option value="{t["town"]}"{" selected" if t["town"] == "Warrnambool" else ""}>{t["town"]}</option>' for t in sorted(towns, key=lambda t: t["town"]))


def towns_js():
    slim = [{k: t[k] for k in ("town", "yard_km", "mel_km", "yard_min", "mel_min")} for t in towns]
    return "window.WM_TOWNS=" + json.dumps(slim, separators=(",", ":")) + ";\n"


# ---------------------------------------------------------------- layout
def header(nav_key):
    links = (f'<a class="m-only" href="./"{" aria-current=page" if nav_key == "home" else ""}>Home</a>' + "".join(
        f'<a href="{href}"{" aria-current=page" if key == nav_key else ""}>{label}</a>' for key, href, label in NAV
    ) + f'<div class="nav-extra"><a class="btn btn-amber" href="tel:{PHONE_TEL}">{PHONE_SVG}Call Sean {PHONE}</a>'
        '<span class="status" data-status><i></i><span>Open 6am to 6pm, 7 days</span></span>'
        '<p>Atkinsons Road, Moorabool</p></div>')
    return f'''<a class="sr" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
  <a class="brand" href="./" aria-label="Westerly Metals home"><img src="assets/brand/logo-dark.svg" alt="Westerly Metals" width="234" height="60"></a>
  <nav class="nav" id="nav" aria-label="Main">{links}</nav>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
  <div class="top-call"><a class="btn btn-amber" href="tel:{PHONE_TEL}">{PHONE_SVG}<span>Call<span class="long"> {PHONE}</span></span></a></div>
</div></header>'''


def footer():
    year = datetime.date.today().year
    pages = "".join(f'<li><a href="{h}">{l}</a></li>' for _, h, l in NAV)
    return f'''<div class="hazard thin"></div>
<footer class="foot"><div class="wrap">
  <div class="foot-grid">
    <div><img src="assets/brand/logo-dark.svg" alt="Westerly Metals" width="234" height="60"><p style="margin:0;max-width:34ch">Scrap metal drop-off and pickups for the Western District. Closer than Melbourne, open 6am to 6pm, 7&nbsp;days.</p></div>
    <div><h4>Visit</h4><ul><li class="nw">Nunjara Recycling site</li><li>Atkinsons Road</li><li>Moorabool VIC&nbsp;3213</li><li><a href="{MAPS_DIR}" target="_blank" rel="noopener">Directions</a></li></ul></div>
    <div><h4>Call ahead</h4><ul><li>Sean Woods</li><li><a href="tel:{PHONE_TEL}">{PHONE}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li>6am to 6pm, 7&nbsp;days</li></ul></div>
    <div><h4>Pages</h4><ul><li><a href="./">Home</a></li>{pages}</ul></div>
  </div>
  <div class="legal"><p>Distances and drive times: OpenStreetMap routing (OSRM), town centre to gate, without traffic, compared with the scrap yards at Dohertys Road, Laverton North. Map data &copy; OpenStreetMap contributors, Natural Earth.</p><p>&copy; {year} Westerly Metals</p></div>
</div></footer>
<div class="callbar"><a class="btn btn-amber" href="tel:{PHONE_TEL}">{PHONE_SVG}Call</a><a class="btn btn-line" style="color:#F2EFE9" href="{MAPS_DIR}" target="_blank" rel="noopener">{PIN_SVG}Directions</a></div>'''


def glue(html):
    """Keep the last two words of short text blocks together (clean-line-breaks)."""
    return re.sub(r"(?<=[^\s>])[ ]+([^\s<>]{1,12}</(?:p|h3|li|dd|figcaption|summary)>)", "\u00a0\\1", html)


def page(fname):
    raw = open(os.path.join(SRC, "pages", fname)).read()
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", raw[: raw.index("-->")], re.M))
    body = raw[raw.index("-->") + 3 :].strip()
    for key, val in {
        "{{HOURS_CHART}}": hours_chart(), "{{TOWNS_TABLE}}": towns_table(), "{{REGION_MAP}}": '<div class="map-desk">' + region_map() + '</div><div class="map-mob">' + region_map(True) + "</div>",
        "{{CALC}}": open(os.path.join(SRC, "partials", "calc.html")).read().strip(),
        "{{PRICE_BOARD}}": price_board(), "{{EST_ROWS}}": estimator_rows(), "{{TOWN_OPTIONS}}": town_options(),
        "{{PHONE}}": PHONE, "{{PHONE_TEL}}": PHONE_TEL,
        "{{MAPS_DIR}}": MAPS_DIR, "{{MAP_IFRAME}}": MAP_IFRAME,
    }.items():
        body = body.replace(key, val)
    body = glue(body)
    url = SITE_URL + ("" if fname == "index.html" else fname)
    schema = {
        "@context": "https://schema.org", "@type": "RecyclingCenter", "name": "Westerly Metals",
        "description": "Scrap metal drop-off and pickups for the Western District of Victoria.",
        "url": SITE_URL, "telephone": "+61418524602", "email": EMAIL,
        "address": {"@type": "PostalAddress", "streetAddress": "Atkinsons Road", "addressLocality": "Moorabool",
                    "addressRegion": "VIC", "postalCode": "3213", "addressCountry": "AU"},
        "geo": {"@type": "GeoCoordinates", "latitude": LAT, "longitude": LON},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "06:00", "closes": "18:00"}],
        "areaServed": "Western District, Victoria", "image": SITE_URL + "og.jpg",
    }
    scripts = f'<script src="assets/js/towns.js?v={VER}" defer></script>' if fname in ("index.html", "savings.html", "prices.html") else ""
    if fname == "prices.html":
        scripts += '<script src="assets/js/rates.js" defer></script>\n'
    html = f'''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{meta["title"]}</title>
<meta name="description" content="{meta["description"]}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#111417">
<meta property="og:type" content="website"><meta property="og:site_name" content="Westerly Metals">
<meta property="og:title" content="{meta["title"]}"><meta property="og:description" content="{meta["description"]}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="assets/brand/icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="assets/brand/favicon-32.png">
<link rel="apple-touch-icon" href="assets/brand/apple-touch-icon.png">
<link rel="preload" href="assets/fonts/anton-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/main.css?v={VER}">
<script type="application/ld+json">{json.dumps(schema)}</script>
</head>
<body>
{header(meta.get("nav", ""))}
<main id="main">
{body}
</main>
{footer()}
{scripts}<script src="assets/js/main.js?v={VER}" defer></script>
</body>
</html>
'''
    assert "—" not in html and "&mdash;" not in html, f"em dash in {fname}"
    assert not re.search(r"\bfree\b", re.sub(r"<[^>]+>", " ", html), re.I), f"'free' in {fname}"
    open(os.path.join(SITE, fname), "w").write(html)
    return fname


def og_image():
    from PIL import Image
    import cairosvg, io
    W, H = 1200, 630
    bg = Image.open(os.path.join(SITE, "assets/img/hero-weighbridge.webp")).convert("RGB")
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s), int(bg.height * s)))
    bg = bg.crop(((bg.width - W) // 2 + 120, (bg.height - H) // 2, (bg.width - W) // 2 + 120 + W, (bg.height - H) // 2 + H))
    shade = Image.new("RGBA", (W, H))
    for x in range(W):
        a = int(235 * max(0, 1 - x / (W * 0.75)))
        for y in range(0, H, 1):
            pass
    grad = Image.linear_gradient("L").rotate(90).resize((W, H))
    grad = grad.point(lambda v: int(v * 0.92))
    dark = Image.new("RGB", (W, H), (17, 20, 23))
    bg = Image.composite(dark, bg, grad)
    logo = cairosvg.svg2png(url=os.path.join(SITE, "assets/brand/logo-dark.svg"), output_width=560)
    lg = Image.open(io.BytesIO(logo)).convert("RGBA")
    bg.paste(lg, (60, 60), lg)
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(os.path.join(ROOT, "fonts", "Anton-Regular.ttf"), 76)
    f2 = ImageFont.truetype(os.path.join(ROOT, "fonts", "BarlowCondensed-Bold.ttf"), 38)
    d.text((60, 300), "SKIP THE MELBOURNE RUN.", font=f1, fill=(242, 239, 233))
    d.text((60, 410), "SCRAP METAL DROP-OFF, MOORABOOL", font=f2, fill=(244, 161, 46))
    d.text((60, 458), "OPEN 6AM TO 6PM, 7 DAYS", font=f2, fill=(242, 239, 233))
    d.rectangle([0, H - 14, W, H], fill=(244, 161, 46))
    bg.save(os.path.join(SITE, "og.jpg"), quality=86)


def main():
    os.makedirs(os.path.join(SITE, "assets", "css"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "assets", "js"), exist_ok=True)
    shutil.copy(os.path.join(SRC, "css", "main.css"), os.path.join(SITE, "assets", "css", "main.css"))
    shutil.copy(os.path.join(SRC, "js", "main.js"), os.path.join(SITE, "assets", "js", "main.js"))
    open(os.path.join(SITE, "assets", "js", "towns.js"), "w").write(towns_js())
    # rates.js is edited by hand on the live site: only seed it, never overwrite
    rates_out = os.path.join(SITE, "assets", "js", "rates.js")
    if not os.path.exists(rates_out):
        shutil.copy(os.path.join(SRC, "js", "rates.js"), rates_out)
    built = [page(f) for f in sorted(os.listdir(os.path.join(SRC, "pages"))) if f.endswith(".html")]
    today = datetime.date.today().isoformat()
    open(os.path.join(SITE, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE_URL}{'' if f == 'index.html' else f}</loc><lastmod>{today}</lastmod></url>\n" for f in built)
        + "</urlset>\n")
    open(os.path.join(SITE, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n")
    open(os.path.join(SITE, ".nojekyll"), "w").write("")
    og_image()
    print("built", built)


if __name__ == "__main__":
    main()
