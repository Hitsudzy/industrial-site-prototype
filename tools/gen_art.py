#!/usr/bin/env python3
"""Generate the code-drawn SVG artwork of the prototype.

Writes into assets/img/:
  hero-a.svg     first-screen background, concept A: drawing grid, isometric
                 line-up of cabinets, dimension lines and callouts
  hero-b.svg     first-screen background, concept B: soft silhouettes of
                 cabinets on the dark-blue hero
  cabinet-a.svg  isometric electrical cabinet, concept A colours (with dimensions)
  cabinet-b.svg  isometric electrical cabinet, concept B colours (with shadow)

Everything is plain geometry computed here, no raster images and no external
resources. The files are committed, so the site needs no build step; run this
script only after changing the drawings:

    python3 tools/gen_art.py           (from the repository root)
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"

C, S = 0.8660254, 0.5          # isometric axes: cos 30, sin 30
MONO = "IBM Plex Mono, ui-monospace, Menlo, Consolas, monospace"
SANS = "IBM Plex Sans, system-ui, Arial, sans-serif"


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def iso(ox, oy, x, y, z):
    """World point (x right along the front, y into depth, z up) -> screen."""
    return ox + (x + y) * C, oy + (x - y) * S - z


def poly(points, **attrs):
    p = " ".join(f"{f(x)},{f(y)}" for x, y in points)
    return f'<polygon points="{p}"{attrs_str(attrs)}/>'


def attrs_str(attrs):
    return "".join(f' {k.rstrip("_").replace("_", "-")}="{v}"' for k, v in attrs.items())


def face_front(ox, oy, h):
    """Group transform: (u, v) on the front face, u along x, v down from the top."""
    return f"matrix({C} {S} 0 1 {f(ox)} {f(oy - h)})"


def face_side(ox, oy, w, h):
    sx, sy = iso(ox, oy, w, 0, h)
    return f"matrix({C} {-S} 0 1 {f(sx)} {f(sy)})"


def face_top(ox, oy, h):
    return f"matrix({C} {S} {C} {-S} {f(ox)} {f(oy - h)})"


# ---------------------------------------------------------------------------
# Cabinet: corpus, door with HMI, indicator lamps, window on DIN-rail modules
# ---------------------------------------------------------------------------

def cabinet(ox, oy, w, d, h, pal, detail=True):
    """Return SVG markup of one isometric cabinet standing at (ox, oy)."""
    o = []
    plinth = 14
    # corpus faces
    o.append(f'<g transform="{face_front(ox, oy, h)}">')
    o.append(f'<rect width="{w}" height="{h}" fill="{pal["front"]}" stroke="{pal["edge"]}" stroke-width="{pal["sw"]}" vector-effect="non-scaling-stroke"/>')
    o.append(f'<rect y="{h - plinth}" width="{w}" height="{plinth}" fill="{pal["plinth"]}" stroke="{pal["edge"]}" stroke-width="{pal["sw"]}" vector-effect="non-scaling-stroke"/>')
    if detail:
        dw, dh = w - 12, h - plinth - 12
        o.append(f'<rect x="6" y="6" width="{dw}" height="{dh}" fill="{pal["door"]}" stroke="{pal["line"]}" stroke-width="1" vector-effect="non-scaling-stroke"/>')
        # HMI panel
        o.append(f'<rect x="18" y="24" width="{w * 0.5:.0f}" height="38" fill="{pal["screen"]}" stroke="{pal["line"]}" stroke-width="1" vector-effect="non-scaling-stroke"/>')
        for i, ln in enumerate((0.7, 0.45, 0.6)):
            o.append(f'<rect x="24" y="{32 + i * 9}" width="{w * 0.5 * ln - 6:.0f}" height="3" fill="{pal["screen_ink"]}"/>')
        # indicator lamps
        for i, col in enumerate(pal["lamps"]):
            cx = w - 30 + (i % 2) * 14
            cy = 32 + (i // 2) * 16
            o.append(f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="{col}" stroke="{pal["line"]}" stroke-width="0.8" vector-effect="non-scaling-stroke"/>')
        # selector switch and push buttons
        o.append(f'<circle cx="26" cy="84" r="7" fill="none" stroke="{pal["line"]}" stroke-width="1" vector-effect="non-scaling-stroke"/>')
        o.append(f'<rect x="24.5" y="78" width="3" height="12" fill="{pal["line"]}"/>')
        for i in range(3):
            o.append(f'<circle cx="{46 + i * 16}" cy="84" r="5" fill="{pal["button"]}" stroke="{pal["line"]}" stroke-width="0.8" vector-effect="non-scaling-stroke"/>')
        # window onto DIN rails with modules
        wx, wy, ww, wh = 14, 104, w - 28, 92
        o.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="{pal["window"]}" stroke="{pal["line"]}" stroke-width="1" vector-effect="non-scaling-stroke"/>')
        widths = (8, 8, 12, 8, 16, 8, 8, 12, 8)
        for row in range(2):
            ry = wy + 12 + row * 42
            o.append(f'<rect x="{wx + 4}" y="{ry + 12}" width="{ww - 8}" height="4" fill="{pal["rail"]}"/>')
            x = wx + 7
            for k, mw in enumerate(widths):
                mw = mw * (ww - 14) / sum(widths)
                if x + mw > wx + ww - 6:
                    break
                o.append(f'<rect x="{x:.1f}" y="{ry}" width="{mw - 1.2:.1f}" height="28" fill="{pal["module"]}" stroke="{pal["module_edge"]}" stroke-width="0.6" vector-effect="non-scaling-stroke"/>')
                led = pal["lamps"][(k + row) % len(pal["lamps"])]
                o.append(f'<rect x="{x + 1.5:.1f}" y="{ry + 4}" width="2.4" height="2.4" fill="{led}"/>')
                x += mw
        # handle and label plate
        o.append(f'<rect x="{w - 16}" y="{wy + wh + 18}" width="5" height="30" rx="2" fill="{pal["handle"]}"/>')
        o.append(f'<rect x="18" y="{wy + wh + 20}" width="34" height="12" fill="none" stroke="{pal["line"]}" stroke-width="0.8" vector-effect="non-scaling-stroke"/>')
        # louvres at the bottom of the door
        for i in range(5):
            o.append(f'<rect x="18" y="{h - plinth - 48 + i * 7}" width="{w - 44}" height="2.4" fill="{pal["louvre"]}"/>')
    o.append("</g>")

    # side face with louvres
    o.append(f'<g transform="{face_side(ox, oy, w, h)}">')
    o.append(f'<rect width="{d}" height="{h}" fill="{pal["side"]}" stroke="{pal["edge"]}" stroke-width="{pal["sw"]}" vector-effect="non-scaling-stroke"/>')
    o.append(f'<rect y="{h - plinth}" width="{d}" height="{plinth}" fill="{pal["plinth_side"]}" stroke="{pal["edge"]}" stroke-width="{pal["sw"]}" vector-effect="non-scaling-stroke"/>')
    if detail:
        for top in (22, h - plinth - 52):
            for i in range(5):
                o.append(f'<rect x="{d * 0.25:.0f}" y="{top + i * 6}" width="{d * 0.5:.0f}" height="2.2" fill="{pal["louvre_side"]}"/>')
    o.append("</g>")

    # top face with lifting eyes
    o.append(f'<g transform="{face_top(ox, oy, h)}">')
    o.append(f'<rect width="{w}" height="{d}" fill="{pal["top"]}" stroke="{pal["edge"]}" stroke-width="{pal["sw"]}" vector-effect="non-scaling-stroke"/>')
    if detail:
        for x, y in ((10, 10), (w - 10, 10), (10, d - 10), (w - 10, d - 10)):
            o.append(f'<circle cx="{x}" cy="{y}" r="4" fill="none" stroke="{pal["line"]}" stroke-width="1" vector-effect="non-scaling-stroke"/>')
        o.append(f'<rect x="{w * 0.3:.0f}" y="{d * 0.35:.0f}" width="{w * 0.4:.0f}" height="{d * 0.3:.0f}" fill="none" stroke="{pal["line"]}" stroke-width="0.8" stroke-dasharray="3 2" vector-effect="non-scaling-stroke"/>')
    o.append("</g>")
    return "\n".join(o)


def dim_line(p1, p2, label, angle, colour, text_colour, offset=(0, 0), size=9):
    """Dimension line with arrow ticks and a label rotated along it."""
    (x1, y1), (x2, y2) = p1, p2
    mx, my = (x1 + x2) / 2 + offset[0], (y1 + y2) / 2 + offset[1]
    return (
        f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{colour}" stroke-width="0.8" '
        f'marker-start="url(#tick)" marker-end="url(#tick)"/>'
        f'<text x="{f(mx)}" y="{f(my)}" transform="rotate({angle} {f(mx)} {f(my)})" text-anchor="middle" '
        f'fill="{text_colour}" font-family="{MONO}" font-size="{size}" letter-spacing="0.08em">{label}</text>'
    )


def tick_marker(colour, mid="tick"):
    return (
        f'<marker id="{mid}" viewBox="-5 -5 10 10" markerWidth="10" markerHeight="10" orient="auto" markerUnits="userSpaceOnUse">'
        f'<path d="M-3.5 3.5 3.5 -3.5" stroke="{colour}" stroke-width="1.2"/></marker>'
    )


PAL_A = {
    "front": "#11203a", "plinth": "#0a1526", "door": "#132540", "side": "#0c1930",
    "plinth_side": "#08111f", "top": "#1a2f4d", "edge": "#2fd3e0", "sw": 1.3,
    "line": "#2fd3e0", "screen": "#062a36", "screen_ink": "#2fd3e0", "button": "#0b1220",
    "lamps": ("#2fd3e0", "#ffd166", "#5ee6a0", "#ff7a6b"), "window": "#070f1d",
    "rail": "#3d5b7d", "module": "#1d3352", "module_edge": "#5fdde8", "handle": "#74e6ef",
    "louvre": "#26415f", "louvre_side": "#1e3654",
}

PAL_B = {
    "front": "url(#front)", "plinth": "#3a4766", "door": "url(#door)", "side": "url(#side)",
    "plinth_side": "#2b3753", "top": "#f7f9fd", "edge": "#7d8aa8", "sw": 1,
    "line": "#7d8aa8", "screen": "url(#screen)", "screen_ink": "#cfe0ff", "button": "#e3e9f5",
    "lamps": ("#2e9e5b", "#e8590c", "#1f5bd6", "#f2b705"), "window": "#16244f",
    "rail": "#8a97b5", "module": "#eef2f9", "module_edge": "#b5c0d6", "handle": "#47526e",
    "louvre": "#c3cce0", "louvre_side": "#aab6cf",
}


def svg_doc(view_w, view_h, body, label=None, extra_attrs=""):
    a11y = f' role="img" aria-label="{label}"' if label else ' aria-hidden="true"'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" '
        f'width="{view_w}" height="{view_h}"{a11y}{extra_attrs}>\n'
        f"<!-- Generated by tools/gen_art.py - edit the script, not this file. -->\n"
        f"{body}\n</svg>\n"
    )


def cabinet_svg(concept):
    w, d, h = 120, 80, 300
    ox, oy = 46, 390
    vw, vh = 270, 470
    out = []
    if concept == "a":
        pal = PAL_A
        out.append(f"<defs>{tick_marker('#5fdde8')}</defs>")
        out.append(cabinet(ox, oy, w, d, h, pal))
        dc, tc = "#5fdde8", "#c4d2e2"
        # extension lines
        ext = []
        for x, y, z, dx, dy in ((0, 0, 0, 0, -26), (w, 0, 0, 0, -26), (w, 0, 0, 26, 0), (w, d, 0, 26, 0)):
            a = iso(ox, oy, x, y + (-4 if dy else 0), z) if dy else iso(ox, oy, x + 4, y, z)
            b = iso(ox, oy, x + dx, y + dy, z)
            ext.append(f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="{dc}" stroke-width="0.6" opacity="0.7"/>')
        for x, z in ((0, 0), (0, h)):
            a = iso(ox, oy, x - 4, 0, z)
            b = iso(ox, oy, x - 26, 0, z)
            ext.append(f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="{dc}" stroke-width="0.6" opacity="0.7"/>')
        out.extend(ext)
        out.append(dim_line(iso(ox, oy, 0, -20, 0), iso(ox, oy, w, -20, 0), "800", 30, dc, tc, offset=(-5, 12), size=11))
        out.append(dim_line(iso(ox, oy, w + 20, 0, 0), iso(ox, oy, w + 20, d, 0), "600", -30, dc, tc, offset=(5, 12), size=11))
        out.append(dim_line(iso(ox, oy, -20, 0, 0), iso(ox, oy, -20, 0, h), "2000", -90, dc, tc, offset=(-7, 0), size=11))
        out.append(f'<text x="{vw - 8}" y="18" text-anchor="end" fill="{tc}" font-family="{MONO}" font-size="9" letter-spacing="0.12em">ШУ-01 · ИЗОМЕТРИЯ</text>')
        label = "Условная изометрия электротехнического шкафа с размерами"
    else:
        pal = PAL_B
        defs = (
            '<linearGradient id="front" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#e4eaf4"/></linearGradient>'
            '<linearGradient id="door" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f7f9fd"/><stop offset="1" stop-color="#e9eef7"/></linearGradient>'
            '<linearGradient id="side" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c3cde0"/><stop offset="1" stop-color="#a9b6cf"/></linearGradient>'
            '<linearGradient id="screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a62db"/><stop offset="1" stop-color="#142a78"/></linearGradient>'
            '<filter id="blur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>'
        )
        out.append(f"<defs>{defs}</defs>")
        sh = [iso(ox, oy, -6, -6, 0), iso(ox, oy, w + 30, -6, 0), iso(ox, oy, w + 30, d + 14, 0), iso(ox, oy, -6, d + 14, 0)]
        out.append(poly(sh, fill="#0b1640", opacity="0.16", filter="url(#blur)"))
        out.append(cabinet(ox, oy, w, d, h, pal))
        label = "Условная изометрия электротехнического шкафа"
    return svg_doc(vw, vh, "\n".join(out), label=label)


# ---------------------------------------------------------------------------
# Hero backgrounds (1600 x 900, anchored right; the page adds a scrim under text)
# ---------------------------------------------------------------------------

def lineup(ox, oy, n, w, d, h, pal, detail):
    parts = []
    for i in range(n):
        x0, y0 = iso(ox, oy, i * w, 0, 0)
        g = cabinet(x0, y0, w, d, h, pal, detail=detail)
        parts.append(g)
    return "\n".join(parts)


def hero_a():
    vw, vh = 1600, 900
    cyan = "#2fd3e0"
    out = [
        "<defs>",
        '<pattern id="g1" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="#2fd3e0" stroke-opacity="0.06" stroke-width="1"/></pattern>',
        '<pattern id="g2" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M100 0H0V100" fill="none" stroke="#2fd3e0" stroke-opacity="0.11" stroke-width="1"/></pattern>',
        tick_marker(cyan),
        "</defs>",
        f'<rect width="{vw}" height="{vh}" fill="url(#g1)"/>',
        f'<rect width="{vw}" height="{vh}" fill="url(#g2)"/>',
    ]
    # faint construction lines and a crosshair on the left half
    out.append(f'<g stroke="{cyan}" stroke-opacity="0.16" stroke-width="1" fill="none">'
               '<path d="M0 700H1600M120 0V900"/>'
               '<circle cx="320" cy="200" r="60" stroke-dasharray="4 6"/><path d="M240 200h160M320 120v160"/>'
               "</g>")
    # line-up of cabinets on the right: outline drawing, dark translucent faces
    pal = dict(PAL_A)
    pal.update({"front": "#0d1a2e", "door": "#0f1e35", "side": "#0a1526", "top": "#13243d",
                "plinth": "#08111f", "plinth_side": "#060d18", "window": "#070f1d", "edge": "#2fd3e0", "sw": 1})
    w, d, h, n = 100, 70, 240, 4
    ox, oy = 1140, 520
    out.append('<g opacity="0.55">')
    out.append(lineup(ox, oy, n, w, d, h, pal, detail=True))
    out.append("</g>")
    dc, tc = "#2fd3e0", "#9fb0c4"
    out.append('<g opacity="0.6">')
    a, b = iso(ox, oy, 0, -34, 0), iso(ox, oy, n * w, -34, 0)
    out.append(dim_line(a, b, f"{n * 800}", 30, dc, tc, offset=(-7, 15), size=13))
    # height on the far (right) end, clear of the sign that sits over the left part
    a, b = iso(ox, oy, n * w, d + 30, 0), iso(ox, oy, n * w, d + 30, h)
    out.append(dim_line(a, b, "2000", -90, dc, tc, offset=(11, 0), size=13))
    for i in range(n):
        sx, sy = iso(ox, oy, i * w + w * 0.5, 0, h * 0.8)
        # labels start at y ~ 190: a wide hero crops the top ~130 units of the viewBox
        lx, ly = sx - 40 + i * 6, oy - h - 90 + i * 26
        out.append(f'<path d="M{f(sx)} {f(sy)}L{f(sx)} {f(ly + 6)}H{f(lx + 70)}" fill="none" stroke="{dc}" stroke-width="0.8"/>'
                   f'<circle cx="{f(sx)}" cy="{f(sy)}" r="2.5" fill="{dc}"/>'
                   f'<text x="{f(sx + 4)}" y="{f(ly)}" fill="{tc}" font-family="{MONO}" font-size="12" letter-spacing="0.1em">ШУ-0{i + 1}</text>')
    out.append("</g>")
    # floor line
    a, b = iso(ox, oy, -60, 0, 0), iso(ox, oy, n * w + 60, 0, 0)
    out.append(f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="{cyan}" stroke-opacity="0.3" stroke-dasharray="10 6"/>')
    return svg_doc(vw, vh, "\n".join(out), extra_attrs=' preserveAspectRatio="xMaxYMid slice"')


def hero_b():
    vw, vh = 1600, 900
    out = [
        "<defs>",
        '<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fb3ff" stop-opacity="0.14"/><stop offset="1" stop-color="#8fb3ff" stop-opacity="0.02"/></linearGradient>',
        '<linearGradient id="floor" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8fb3ff" stop-opacity="0"/><stop offset="0.6" stop-color="#8fb3ff" stop-opacity="0.35"/><stop offset="1" stop-color="#8fb3ff" stop-opacity="0"/></linearGradient>',
        '<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#5b8cff" stop-opacity="0.25"/><stop offset="1" stop-color="#5b8cff" stop-opacity="0"/></radialGradient>',
        "</defs>",
        '<ellipse cx="1220" cy="430" rx="520" ry="340" fill="url(#glow)"/>',
    ]
    # back row: small, faint; front row: taller, a little brighter
    for row, (y0, hh, ww, gap, op, n) in enumerate(((610, 250, 78, 6, 0.55, 9), (700, 380, 104, 8, 1, 6))):
        x = 1600 - n * (ww + gap) + (40 if row == 0 else -10)
        out.append(f'<g opacity="{op}">')
        for i in range(n):
            hi = hh - (i % 3) * 18
            top = y0 - hi
            out.append(f'<rect x="{x}" y="{top}" width="{ww}" height="{hi}" rx="3" fill="url(#fade)" stroke="#8fb3ff" stroke-opacity="0.16"/>')
            out.append(f'<rect x="{x + 8}" y="{top + 10}" width="{ww - 16}" height="{hi - 30}" rx="2" fill="none" stroke="#8fb3ff" stroke-opacity="0.1"/>')
            out.append(f'<rect x="{x + 16}" y="{top + 22}" width="{ww * 0.42:.0f}" height="16" rx="2" fill="#8fb3ff" fill-opacity="0.12"/>')
            for k in range(3):
                out.append(f'<circle cx="{x + ww - 22 + (k % 2) * 8}" cy="{top + 26 + (k // 2) * 10}" r="2.4" fill="#b9cfff" fill-opacity="0.3"/>')
            x += ww + gap
        out.append("</g>")
    out.append('<rect x="500" y="700" width="1100" height="2" fill="url(#floor)"/>')
    return svg_doc(vw, vh, "\n".join(out), extra_attrs=' preserveAspectRatio="xMaxYMid slice"')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "hero-a.svg": hero_a(),
        "hero-b.svg": hero_b(),
        "cabinet-a.svg": cabinet_svg("a"),
        "cabinet-b.svg": cabinet_svg("b"),
    }
    for name, text in files.items():
        (OUT / name).write_text(text, encoding="utf-8")
        print(f"wrote assets/img/{name} ({len(text)} bytes)")


if __name__ == "__main__":
    main()
