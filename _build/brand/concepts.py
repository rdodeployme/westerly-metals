"""Three scrap-yard logo directions for Westerly Metals. Pure-path SVGs + PNG previews."""
import math, os
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "concepts")
os.makedirs(OUT, exist_ok=True)

INK, STEEL, STEEL2, BONE, AMBER, RIVET = "#111417", "#2C3338", "#3B444B", "#F2EFE9", "#F4A12E", "#7A848C"

_cache = {}


def font(name, wght=None):
    key = (name, wght)
    if key not in _cache:
        f = TTFont(os.path.join(FONTS, name))
        if wght is not None and "fvar" in f:
            f = instancer.instantiateVariableFont(f, {"wght": wght}, inplace=False)
        _cache[key] = f
    return _cache[key]


def glyphs(fname, text, size, wght=None, tracking=0.0):
    """Yield (glyphset, glyph name, x-offset) and return total width + bounds via run()."""
    f = font(fname, wght)
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    s = size / upm
    out, cx = [], 0.0
    for ch in text:
        g = cmap[ord(ch)]
        out.append((g, cx))
        cx += gs[g].width * s + tracking * size
    return gs, s, out, cx - tracking * size


def text_path(fname, text, size, x=0, y=0, wght=None, tracking=0.0, anchor="start"):
    gs, s, run, width = glyphs(fname, text, size, wght, tracking)
    if anchor == "middle":
        x -= width / 2
    pen, bp = SVGPathPen(gs), BoundsPen(gs)
    for g, cx in run:
        t = (s, 0, 0, -s, x + cx, y)
        gs[g].draw(TransformPen(pen, t)); gs[g].draw(TransformPen(bp, t))
    return pen.getCommands(), width, bp.bounds


def text_on_arc(fname, text, size, cx, cy, r, mid_deg, wght=None, tracking=0.0, outside=True):
    """Glyphs set around a circle, centred on angle mid_deg (0 = top, clockwise). outside=True reads
    clockwise along the top; False reads counter-clockwise along the bottom (upright)."""
    gs, s, run, width = glyphs(fname, text, size, wght, tracking)
    total_ang = width / r  # radians
    pen = SVGPathPen(gs)
    for g, gx in run:
        adv = gs[g].width * s
        centre_off = gx + adv / 2 - width / 2
        if outside:
            ang = math.radians(mid_deg) + centre_off / r
            px, py = cx + r * math.sin(ang), cy - r * math.cos(ang)
            rot = ang
        else:
            ang = math.radians(mid_deg) - centre_off / r
            px, py = cx + r * math.sin(ang), cy - r * math.cos(ang)
            rot = ang + math.pi
        c, sn = math.cos(rot), math.sin(rot)
        # glyph local: centre horizontally on (px,py), baseline at radius
        # local point (u,v) in font units -> (u*s - adv/2, -v*s)
        a, b = c * s, sn * s
        cc, d = sn * s, -c * s
        e = px + c * (-adv / 2)
        f_ = py + sn * (-adv / 2)
        gs[g].draw(TransformPen(pen, (a, b, cc, d, e, f_)))
    return pen.getCommands()


def save(name, svg, w):
    open(os.path.join(OUT, name + ".svg"), "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(OUT, name + ".png"), output_width=w)


STENCIL = "BigShouldersStencilDisplay[wght].ttf"
ANTON = "Anton-Regular.ttf"


# ---------- A: riveted yard plate --------------------------------------------------------
def plate():
    W, H = 640, 300
    rivets = "".join(
        f'<circle cx="{x}" cy="{y}" r="8" fill="{RIVET}"/><circle cx="{x-2}" cy="{y-2}" r="3" fill="#A9B2B9"/>'
        for x, y in [(26, 26), (W - 26, 26), (26, H - 26), (W - 26, H - 26)]
    )
    d1, w1, b1 = text_path(ANTON, "WESTERLY", 120, W / 2, 0, tracking=0.03, anchor="middle")
    y1 = 40 - b1[1]
    d1, w1, b1 = text_path(ANTON, "WESTERLY", 120, W / 2, y1, tracking=0.03, anchor="middle")
    d2, w2, b2 = text_path(ANTON, "METALS", 48, W / 2, 0, tracking=0.5, anchor="middle")
    y2 = b1[3] + 16 - b2[1]
    d2, w2, b2 = text_path(ANTON, "METALS", 48, W / 2, y2, tracking=0.5, anchor="middle")
    # hazard band
    band_y, band_h = H - 62, 32
    stripes = "".join(
        f'<path d="M{x} {band_y+band_h} L{x+band_h} {band_y} L{x+band_h+18} {band_y} L{x+18} {band_y+band_h} Z" fill="{INK}"/>'
        for x in range(30, W - 30, 36)
    )
    clip = f'<clipPath id="band"><rect x="44" y="{band_y}" width="{W-88}" height="{band_h}"/></clipPath>'
    d3, w3, b3 = text_path(ANTON, "SCRAP METAL RECYCLING", 19, W / 2, 0, tracking=0.12, anchor="middle")
    lab_w = w3 + 34
    y3 = band_y + band_h / 2 - (b3[1] + b3[3]) / 2
    d3, w3, b3 = text_path(ANTON, "SCRAP METAL RECYCLING", 19, W / 2, y3, tracking=0.12, anchor="middle")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><defs>{clip}'
        f'<linearGradient id="pl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{STEEL2}"/><stop offset="1" stop-color="{STEEL}"/></linearGradient></defs>'
        f'<rect width="{W}" height="{H}" rx="14" fill="url(#pl)"/>'
        f'<rect x="10" y="10" width="{W-20}" height="{H-20}" rx="8" fill="none" stroke="#4E585F" stroke-width="2"/>'
        f"{rivets}"
        f'<path d="{d1}" fill="{BONE}"/>'
        f'<path d="{d2}" fill="{AMBER}"/>'
        f'<rect x="44" y="{band_y}" width="{W-88}" height="{band_h}" fill="{AMBER}"/>'
        f'<g clip-path="url(#band)">{stripes}</g>'
        f'<rect x="{W/2 - lab_w/2:.1f}" y="{band_y}" width="{lab_w:.1f}" height="{band_h}" fill="{AMBER}"/>'
        f'<path d="{d3}" fill="{INK}"/>'
        f"</svg>"
    )
    save("A-yard-plate", svg, 1280)


# ---------- B: scrap grab claw -----------------------------------------------------------
def grab_icon(col=AMBER, line=BONE):
    """Orange-peel scrap grab on a cable, tines open. viewBox 0 0 120 150."""
    t = 11
    tines = [
        "M43 62 C 20 78, 14 108, 30 134",
        "M53 64 C 44 90, 44 112, 52 134",
        "M67 64 C 76 90, 76 112, 68 134",
        "M77 62 C 100 78, 106 108, 90 134",
    ]
    tine_svg = "".join(f'<path d="{p}" fill="none" stroke="{col}" stroke-width="{t}" stroke-linecap="butt"/>' for p in tines)
    tips = (
        f'<path d="M24 132 L38 136 L28 146 Z" fill="{col}"/>'
        f'<path d="M96 132 L82 136 L92 146 Z" fill="{col}"/>'
        f'<path d="M46.5 133 L57.5 133 L52 145 Z" fill="{col}"/>'
        f'<path d="M62.5 133 L73.5 133 L68 145 Z" fill="{col}"/>'
    )
    return (
        f'<rect x="58.5" y="0" width="3" height="20" fill="{line}"/>'
        f'<circle cx="60" cy="22" r="6" fill="none" stroke="{line}" stroke-width="3"/>'
        f'<rect x="46" y="27" width="28" height="9" rx="2" fill="{col}"/>'
        f'<rect x="36" y="35" width="48" height="30" rx="5" fill="{col}"/>'
        f'<rect x="42" y="42" width="36" height="5" rx="2" fill="{INK}" opacity=".35"/>'
        f"{tine_svg}{tips}"
    )


def grab(theme="dark"):
    word = BONE if theme == "dark" else INK
    bg = INK if theme == "dark" else BONE
    icon = grab_icon(AMBER, word)
    d1, w1, b1 = text_path(ANTON, "WESTERLY", 96, 0, 0, tracking=0.02)
    y1 = 18 - b1[1]
    tx = 150
    d1, w1, b1 = text_path(ANTON, "WESTERLY", 96, tx, y1, tracking=0.02)
    d2, w2, b2 = text_path(ANTON, "METALS", 52, 0, 0, tracking=0.14)
    y2 = b1[3] + 14 - b2[1]
    d2, w2, b2 = text_path(ANTON, "METALS", 52, tx, y2, tracking=0.14)
    hx0, hx1 = tx + w2 + 16, tx + w1
    hy0, hy1 = b2[1] + 6, b2[3] - 6
    hh = hy1 - hy0
    haz = f'<clipPath id="hz"><rect x="{hx0:.1f}" y="{hy0:.1f}" width="{hx1-hx0:.1f}" height="{hh:.1f}"/></clipPath>'
    haz += f'<rect x="{hx0:.1f}" y="{hy0:.1f}" width="{hx1-hx0:.1f}" height="{hh:.1f}" fill="{AMBER}"/><g clip-path="url(#hz)">'
    x = hx0 - hh
    while x < hx1:
        haz += f'<path d="M{x:.1f} {hy1:.1f} L{x+hh:.1f} {hy0:.1f} L{x+hh+11:.1f} {hy0:.1f} L{x+11:.1f} {hy1:.1f} Z" fill="{INK if theme=="dark" else INK}"/>'
        x += 22
    haz += "</g>"
    H = max(b2[3] + 18, 160)
    W = tx + w1 + 24
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}">'
        f'<rect width="{W:.0f}" height="{H:.0f}" fill="{bg}"/>'
        f'<g transform="translate(14 {(H-150)/2:.1f})">{icon}</g>'
        f'<path d="{d1}" fill="{word}"/><path d="{d2}" fill="{AMBER}"/>{haz}</svg>'
    )
    save(f"B-grab-{theme}", svg, 1280)
    sq = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-15 -5 150 160"><rect x="-15" y="-5" width="150" height="160" rx="24" fill="{INK}"/>{grab_icon(AMBER, BONE)}</svg>'
    save("B-grab-icon", sq, 512)


# ---------- C: round yard stamp with crane hook -----------------------------------------
def stamp():
    S, c = 400, 200
    ring_o, ring_i = 192, 132
    top = text_on_arc(ANTON, "WESTERLY METALS", 33, c, c, 146, 0, tracking=0.12, outside=True)
    bot = text_on_arc(ANTON, "SCRAP METAL RECYCLING", 22, c, c, 174, 180, tracking=0.14, outside=False)
    # crane block + hook
    hook = (
        f'<rect x="{c-3}" y="70" width="6" height="34" fill="{BONE}"/>'
        f'<rect x="{c-26}" y="100" width="52" height="40" rx="7" fill="{AMBER}"/>'
        f'<circle cx="{c-10}" cy="114" r="5" fill="{INK}"/><circle cx="{c+10}" cy="114" r="5" fill="{INK}"/>'
        f'<rect x="{c-8}" y="138" width="16" height="22" fill="{AMBER}"/>'
        f'<path d="M{c} 158 L{c} 196 A 34 34 0 1 1 {c-62} 214 L{c-42} 214 A 16 16 0 1 0 {c-16} 200 L{c-16} 158 Z" '
        f'transform="translate(8 0)" fill="{AMBER}"/>'
        f'<path d="M{c-48} 214 L{c-30} 192 L{c-26} 216 Z" fill="{AMBER}" transform="translate(8 0)"/>'
    )
    stars = "".join(
        f'<circle cx="{c + 152*math.sin(math.radians(a))}" cy="{c - 152*math.cos(math.radians(a))}" r="5" fill="{AMBER}"/>'
        for a in (90, 270)
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}">'
        f'<circle cx="{c}" cy="{c}" r="{ring_o}" fill="{INK}"/>'
        f'<circle cx="{c}" cy="{c}" r="{ring_o-8}" fill="none" stroke="{AMBER}" stroke-width="4"/>'
        f'<circle cx="{c}" cy="{c}" r="{ring_i}" fill="{STEEL}" stroke="{AMBER}" stroke-width="4"/>'
        f'<path d="{top}" fill="{BONE}"/><path d="{bot}" fill="{AMBER}"/>{stars}'
        f'<g transform="translate(0 6)">{hook}</g>'
        f"</svg>"
    )
    save("C-stamp", svg, 1000)


if __name__ == "__main__":
    plate(); grab("dark"); grab("light"); stamp()
    print(sorted(os.listdir(OUT)))
