"""Build the Westerly Metals logo set from Barlow Condensed outlines.

Outputs SVGs (pure paths, no font dependency) and PNGs into brand/out/.
"""
import os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

INK = "#111417"
STEEL = "#5B656E"
BONE = "#F2EFE9"
AMBER = "#F4A12E"
AMBER_DEEP = "#B86E0B"


def text_path(font_file, text, size, x=0, y=0, tracking=0.0):
    """Return (svg path d, width, (xmin,ymin,xmax,ymax)) for text set at `size` px, baseline y."""
    f = TTFont(os.path.join(FONTS, font_file))
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    upm = f["head"].unitsPerEm
    s = size / upm
    kern = {}
    if "GPOS" not in f and "kern" in f:
        pass
    pen = SVGPathPen(gs)
    bp = BoundsPen(gs)
    cx = 0.0
    prev = None
    for ch in text:
        g = cmap[ord(ch)]
        t = (s, 0, 0, -s, x + cx, y)
        gs[g].draw(TransformPen(pen, t))
        gs[g].draw(TransformPen(bp, t))
        cx += gs[g].width * s + tracking * size
        prev = g
    width = cx - tracking * size
    return pen.getCommands(), width, bp.bounds


def mark_svg(size=120, badge=True, plate=INK, ground=AMBER, wind=INK, radius=0.16, winds_on=True):
    """Square badge: a W cut into three stacked plates, wind lines entering from the west."""
    S = 120.0
    d, w, b = text_path("BarlowCondensed-ExtraBold.ttf", "W", 104)
    xmin, ymin, xmax, ymax = b
    gw, gh = xmax - xmin, ymax - ymin
    # place W right of centre so the wind lines have room on the left
    ox = (S - 16 - gw - xmin) if winds_on else ((S - gw) / 2 - xmin)
    oy = (S - gh) / 2 - ymin
    # horizontal cuts through the W (plate gaps)
    top = (S - gh) / 2
    cut_h = 6.0
    cuts = [top + gh * 0.36, top + gh * 0.66]
    wx0, wx1 = ox + xmin - 1, ox + xmax + 1
    cut_rects = "".join(
        f'<rect x="{wx0:.2f}" y="{c - cut_h/2:.2f}" width="{wx1 - wx0:.2f}" height="{cut_h}" fill="{ground}"/>' for c in cuts
    )
    # wind lines: three tapering bars, centred on each plate, entering from the left edge
    plate_mid = [top + gh * 0.18, top + gh * 0.51, top + gh * 0.83]
    lens = [20, 26, 15]
    winds = ""
    for ym, L in zip(plate_mid, lens):
        x1 = ox + xmin - 5
        x0 = x1 - L
        h = 5.2
        # tapered: thin at the far west end, full height near the W
        winds += (
            f'<path d="M{x0:.2f} {ym:.2f} L{x1:.2f} {ym - h/2:.2f} L{x1:.2f} {ym + h/2:.2f} Z" fill="{wind}"/>'
        )
    r = S * radius
    bg = f'<rect width="{S}" height="{S}" rx="{r:.1f}" fill="{ground}"/>' if badge else ""
    body = (
        f"{bg}"
        f'<path transform="translate({ox:.2f} {oy:.2f})" d="{d}" fill="{plate}"/>'
        f"{cut_rects}{winds if winds_on else ''}"
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S:.0f} {S:.0f}" width="{size}" height="{size}">'
        f"{body}</svg>"
    )


def lockup_svg(theme="dark", stacked=True):
    """Mark + wordmark. theme=dark means for dark backgrounds."""
    word = BONE if theme == "dark" else INK
    sub = AMBER if theme == "dark" else AMBER_DEEP
    mark = mark_svg(badge=True)
    inner = mark[mark.index(">") + 1 : mark.rindex("</svg>")]
    if stacked:
        d1, w1, b1 = text_path("BarlowCondensed-ExtraBold.ttf", "WESTERLY", 78, tracking=0.01)
        d2, w2, b2 = text_path("BarlowCondensed-Bold.ttf", "METALS", 44, tracking=0.16)
        cap1 = b1[3] - b1[1]
        gap = 22
        tx = 120 + gap
        y1 = 10 - b1[1]  # top of caps at y=10
        y2 = 120 - 8 - b2[3]  # bottom of METALS at y=112
        # amber rule before METALS
        rule_y = 120 - 8 - (b2[3] - b2[1]) / 2
        width = tx + max(w1, w2 + 0) + 4
        cy = y2 + (b2[1] + b2[3]) / 2
        lx0 = tx + w2 + 16
        lx1 = tx + w1
        h = 7.0
        wind_tail = f'<path d="M{lx0:.2f} {cy - h/2:.2f} L{lx1:.2f} {cy:.2f} L{lx0:.2f} {cy + h/2:.2f} Z" fill="{sub}"/>'
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} 120">'
            f'<g>{inner}</g>'
            f'<path transform="translate({tx} {y1:.2f})" d="{d1}" fill="{word}"/>'
            f'<path transform="translate({tx} {y2:.2f})" d="{d2}" fill="{sub}"/>'
            f'{wind_tail}'
            f"</svg>"
        )
    else:
        d1, w1, b1 = text_path("BarlowCondensed-ExtraBold.ttf", "WESTERLY", 74, tracking=0.01)
        d2, w2, b2 = text_path("BarlowCondensed-SemiBold.ttf", "METALS", 74, tracking=0.06)
        gap = 20
        tx = 120 + gap
        cap = b1[3] - b1[1]
        y = (120 - cap) / 2 - b1[1]
        x2 = tx + w1 + 18
        width = x2 + w2 + 4
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} 120">'
            f'<g>{inner}</g>'
            f'<path transform="translate({tx} {y:.2f})" d="{d1}" fill="{word}"/>'
            f'<path transform="translate({x2:.2f} {y:.2f})" d="{d2}" fill="{sub}"/>'
            f"</svg>"
        )
    return svg


def write(name, svg, png_w=None, bg=None):
    p = os.path.join(OUT, name + ".svg")
    open(p, "w").write(svg)
    if png_w:
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(OUT, name + ".png"),
                         output_width=png_w, background_color=bg)
    return p


if __name__ == "__main__":
    write("mark", mark_svg(), 512)
    write("favicon", mark_svg(winds_on=False, radius=0.2), 512)
    write("mark-ink", mark_svg(ground=INK, plate=AMBER, wind=AMBER), 512)
    write("logo-stacked-dark", lockup_svg("dark", True), 1200, INK)
    write("logo-stacked-light", lockup_svg("light", True), 1200, BONE)
    write("logo-line-dark", lockup_svg("dark", False), 1400, INK)
    write("logo-line-light", lockup_svg("light", False), 1400, BONE)
    print("done", sorted(os.listdir(OUT)))
