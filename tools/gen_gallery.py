#!/usr/bin/env python3
"""Generate the code-drawn gallery illustrations of project.html.

The drawings are inline SVG (not files) so that they take their colours from
the page CSS: every element carries a class (.cover__*, .art__*) styled in
assets/css/blocks.css and assets/css/project.css through tokens, and concept B
re-dresses them without touching the markup.

Each drawing is written into project.html between the markers

    <!-- gen:NAME -->  ...  <!-- /gen:NAME -->

NAME is one of: schema, spec, list, assembly, panel. Everything is abstract
geometry: no readable designations, no real documentation. Run only after
changing the drawings:

    python3 tools/gen_gallery.py       (from the repository root)
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "project.html"

C, S = 0.8660254, 0.5          # isometric axes: cos 30, sin 30
INDENT = "                "    # inside .gallery__media


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def path(cls, d):
    return f'<path class="{cls}" d="{d}"/>'


def rect(cls, x, y, w, h, rx=0):
    r = f' rx="{f(rx)}"' if rx else ""
    return f'<rect class="{cls}" x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{r}/>'


def circle(cls, cx, cy, r):
    return f'<circle class="{cls}" cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"/>'


def svg(w, h, label, body):
    lines = [f'<svg class="art" viewBox="0 0 {w} {h}" role="img" aria-label="{label}" focusable="false">']
    lines += ["  " + b for b in body]
    lines.append("</svg>")
    return lines


def bars(x, y, widths, h=4, gap=10, cls="art__bar"):
    """Placeholder "text": grey bars instead of readable words."""
    out = []
    for i, w in enumerate(widths):
        out.append(rect(cls, x, y + i * gap, w, h, 1))
    return out


# ---------------------------------------------------------------------------
# 1. Fragment of a schematic: single-line part + functional blocks
# ---------------------------------------------------------------------------
def schema():
    W, H = 480, 280
    b = [rect("art__sheet", 8, 8, W - 16, H - 16),
         path("cover__thin", "M20 20h440v240H20z")]
    bus_y = 52
    b.append(path("cover__line cover__line--accent", f"M40 {bus_y}h272"))
    feeders = [64, 128, 192, 256]
    for i, x in enumerate(feeders):
        b.append(circle("cover__dot", x, bus_y, 3))
        # breaker
        b.append(path("cover__line", f"M{x} {bus_y}v20M{x} 96v20"))
        b.append(rect("cover__node", x - 8, 72, 16, 24))
        b.append(path("cover__thin", f"M{x - 5} 92l10-16"))
        # contactor
        b.append(path("cover__line", f"M{x - 9} 116h18M{x - 9} 124h18M{x} 124v22"))
        b += bars(x + 12, 78, [14, 9], gap=8)
        # load: transformer for the 2nd feeder, a motor-like circle otherwise
        if i == 1:
            b.append(circle("cover__line", x, 160, 13))
            b.append(circle("cover__line", x, 178, 13))
            b.append(path("cover__line", f"M{x} 191v19"))
        else:
            b.append(circle("cover__line", x, 166, 19))
            b.append(path("cover__thin", f"M{x - 8} 172l8-12 8 12"))
            b.append(path("cover__line", f"M{x} 185v25"))
        # earth
        b.append(path("cover__thin", f"M{x - 9} 210h18M{x - 6} 215h12M{x - 3} 220h6"))
    # functional blocks on the right
    bx, bw, bh = 352, 92, 34
    for j, by in enumerate([40, 100, 160]):
        cls = "cover__node" if j == 1 else "art__module"
        b.append(rect(cls, bx, by, bw, bh))
        b += bars(bx + 10, by + 10, [52, 34][: 2], gap=10)
        if j < 2:
            b.append(path("cover__line", f"M{bx + bw / 2} {by + bh}v26"))
            b.append(path("cover__line", f"M{bx + bw / 2 - 4} {by + bh + 20}l4 6 4-6"))
    b.append(path("cover__axis", f"M312 {bus_y}h40M{bx} 117h-24v60H{feeders[-1] + 30}"))
    # title block corner
    b.append(path("cover__thin", "M340 222h120M340 222v38M392 222v38M340 241h120"))
    b += bars(348, 229, [30], gap=0)
    b += bars(400, 229, [48, 30], gap=19)
    return svg(W, H, "Фрагмент условной однолинейной и функциональной схемы: шина, фидеры с аппаратами защиты, функциональные блоки. Обозначения нечитаемые", b)


# ---------------------------------------------------------------------------
# 2. "Specification": table with placeholder rows, lower part hatched
# ---------------------------------------------------------------------------
def spec():
    W, H = 320, 300
    x0, y0, x1, y1 = 16, 16, 304, 284
    cols = [x0, 44, 168, 224, 262, x1]
    head_h, row_h = 30, 22
    b = [rect("art__sheet", x0, y0, x1 - x0, y1 - y0),
         rect("art__fill", x0, y0, x1 - x0, head_h),
         rect("cover__line", x0, y0, x1 - x0, y1 - y0)]
    b.append(path("cover__thin", "".join(f"M{c} {y0}V{y1}" for c in cols[1:-1])))
    rows = list(range(y0 + head_h, y1, row_h))
    b.append(path("cover__thin", "".join(f"M{x0} {r}H{x1}" for r in rows)))
    # header labels as accent bars
    for c0, c1 in zip(cols, cols[1:]):
        b.append(rect("art__bar art__bar--accent", c0 + 6, y0 + 13, min(c1 - c0 - 12, 40), 4, 1))
    widths = [96, 70, 108, 84, 60, 100, 76, 92, 66, 104, 80]
    clear = 5
    for i, r in enumerate(rows):
        if r + row_h > y1:
            break
        cls = "art__bar" if i < clear else "art__bar art__blur"
        cy = r + 9
        b.append(rect(cls, cols[0] + 6, cy, 14, 4, 1))
        b.append(rect(cls, cols[1] + 6, cy, widths[i % len(widths)], 4, 1))
        b.append(rect(cls, cols[2] + 6, cy, 30 + (i * 7) % 18, 4, 1))
        b.append(rect(cls, cols[3] + 6, cy, 16 + (i * 5) % 10, 4, 1))
        b.append(rect(cls, cols[4] + 6, cy, 22, 4, 1))
    # hatch over the lower rows: the table "fades out"
    top = rows[clear]
    hatch = "".join(f"M{f(x)} {y1 - 2}l36-{y1 - 2 - top}" for x in range(x0 + 4, x1 - 38, 9))
    b.append(path("art__hatch", hatch))
    return svg(W, H, "Условная спецификация: таблица с полосами-заглушками вместо текста, нижняя часть заштрихована", b)


# ---------------------------------------------------------------------------
# 3. "Bill of items": list of placeholder lines
# ---------------------------------------------------------------------------
def items_list():
    W, H = 320, 300
    b = [rect("art__sheet", 16, 16, 288, 268),
         rect("cover__line", 16, 16, 288, 268),
         path("cover__thin", "M16 52h288")]
    b += bars(30, 30, [120], h=6, cls="art__bar art__bar--accent")
    b.append(rect("art__bar", 236, 31, 54, 4, 1))
    widths = [150, 118, 170, 96, 140, 160, 108, 134, 88, 152]
    for i, w in enumerate(widths):
        y = 66 + i * 21
        b.append(rect("art__module", 30, y, 14, 12, 1))
        b.append(rect("art__bar", 54, y + 4, w, 4, 1))
        b.append(rect("art__bar", 276 - (i % 3) * 6, y + 4, 14 + (i % 3) * 6, 4, 1))
        if i % 4 == 1:
            b.append(rect("cover__dot", 33, y + 3, 8, 6, 1))
    return svg(W, H, "Условный перечень: строки-заглушки с номерами позиций без читаемого текста", b)


# ---------------------------------------------------------------------------
# 4. 3D assembly: isometric row of cabinets with a cable tray on top
# ---------------------------------------------------------------------------
def iso(ox, oy, x, y, z):
    return ox + (x + y) * C, oy + (x - y) * S - z


def pts(points):
    return " ".join(f"{f(x)},{f(y)}" for x, y in points)


def poly(cls, points):
    return f'<polygon class="{cls}" points="{pts(points)}"/>'


def assembly():
    W, H = 480, 330
    ox, oy = 100, 176
    n, w, d, h, plinth = 4, 64, 48, 132, 10
    L = n * w
    b = []
    P = lambda x, y, z: iso(ox, oy, x, y, z)  # noqa: E731
    # dimension line in front of the row (offset along -y)
    a, z = P(0, -22, 0), P(L, -22, 0)
    b.append(path("cover__dim", f"M{f(a[0])} {f(a[1])}L{f(z[0])} {f(z[1])}"))
    for x in (0, L):
        p, q = P(x, -16, 0), P(x, -28, 0)
        b.append(path("cover__dim", f"M{f(p[0])} {f(p[1])}L{f(q[0])} {f(q[1])}"))
    for i in range(n):
        x = i * w
        accent = i == 1
        line = "cover__line cover__line--accent" if accent else "cover__line"
        # top
        b.append(poly("art__fill " + line, [P(x, 0, h), P(x + w, 0, h), P(x + w, d, h), P(x, d, h)]))
        # front
        b.append(poly("art__face " + line, [P(x, 0, 0), P(x + w, 0, 0), P(x + w, 0, h), P(x, 0, h)]))
        fx, fy = P(x, 0, h)
        g = [f'<g transform="matrix({C} {S} 0 1 {f(fx)} {f(fy)})">',
             "  " + rect("cover__thin", 4, 4, w - 8, h - plinth - 8),
             "  " + rect("art__fill", 0, h - plinth, w, plinth),
             "  " + rect("cover__line", w - 12, 46, 3, 16)]
        if i == 0:
            g.append("  " + rect("cover__node", 12, 18, 30, 20))
        else:
            g.append("  " + "".join(circle("cover__dot", 14 + k * 9, 24, 2.2) for k in range(3)))
        g.append("  " + path("cover__thin", "".join(f"M14 {h - plinth - 30 + k * 5}h{w - 30}" for k in range(4))))
        g.append("</g>")
        b += g
    # right side of the last cabinet
    b.append(poly("art__side cover__line", [P(L, 0, 0), P(L, d, 0), P(L, d, h), P(L, 0, h)]))
    sx, sy = P(L, 0, h)
    b.append(f'<g transform="matrix({C} {-S} 0 1 {f(sx)} {f(sy)})">')
    b.append("  " + rect("art__fill", 0, h - plinth, d, plinth))
    b.append("  " + path("cover__thin", "".join(f"M10 {20 + k * 6}h{d - 20}" for k in range(4))))
    b.append("</g>")
    # cable tray on top
    t0, t1, th = 10, 34, 8
    b.append(poly("art__face cover__line", [P(0, t0, h), P(L, t0, h), P(L, t0, h + th), P(0, t0, h + th)]))
    b.append(poly("art__fill cover__line", [P(0, t0, h + th), P(L, t0, h + th), P(L, t1, h + th), P(0, t1, h + th)]))
    b.append(poly("art__side cover__line", [P(L, t0, h), P(L, t1, h), P(L, t1, h + th), P(L, t0, h + th)]))
    rungs = "".join(
        f"M{f(P(x, t0, h + th)[0])} {f(P(x, t0, h + th)[1])}L{f(P(x, t1, h + th)[0])} {f(P(x, t1, h + th)[1])}"
        for x in range(16, L, 16))
    b.append(path("cover__thin", rungs))
    # axis through the highlighted cabinet
    a, z = P(w * 1.5, 0, -18), P(w * 1.5, 0, h + 30)
    b.append(path("cover__axis", f"M{f(a[0])} {f(a[1])}L{f(z[0])} {f(z[1])}"))
    return svg(W, H, "Условная 3D-сборка: изометрия ряда из четырёх шкафов с кабельным лотком сверху, один шкаф выделен", b)


# ---------------------------------------------------------------------------
# 5. Mounting panel: modules on DIN rails between cable ducts
# ---------------------------------------------------------------------------
def panel():
    W, H = 360, 300
    px, py, pw, ph = 20, 20, 320, 260
    b = [rect("art__fill", px, py, pw, ph, 3), rect("cover__line", px, py, pw, ph, 3)]
    for cx, cy in ((px + 9, py + 9), (px + pw - 9, py + 9), (px + 9, py + ph - 9), (px + pw - 9, py + ph - 9)):
        b.append(circle("cover__thin", cx, cy, 3.5))
    rx0, rx1 = 36, 284

    def duct(x, y, w, h, vertical=False):
        out = [rect("art__module", x, y, w, h)]
        if vertical:
            out.append(path("cover__thin", "".join(f"M{x} {yy}h{w * 0.3}M{x + w} {yy}h-{w * 0.3}" for yy in range(int(y) + 8, int(y + h), 8))))
        else:
            out.append(path("cover__thin", "".join(f"M{xx} {y}v{h * 0.3}M{xx} {y + h}v-{h * 0.3}" for xx in range(int(x) + 8, int(x + w), 8))))
        return out

    b += duct(rx0, 34, rx1 - rx0, 18)
    b += duct(rx0, 122, rx1 - rx0, 18)
    b += duct(rx0, 210, rx1 - rx0, 18)
    b += duct(296, 34, 20, 232, vertical=True)

    def rail(y):
        return [rect("art__rail", rx0, y - 4, rx1 - rx0, 8),
                path("cover__thin", "".join(f"M{x} {y - 1}h6" for x in range(rx0 + 6, rx1 - 6, 12)))]

    def module(x, y, w, h, cls="art__module", lever=False, leds=0):
        out = [rect(cls, x, y - h / 2, w, h, 1.5)]
        out.append(path("cover__thin", f"M{f(x + 3)} {f(y - h / 2 + 6)}h{f(w - 6)}M{f(x + 3)} {f(y + h / 2 - 6)}h{f(w - 6)}"))
        if lever:
            out.append(rect("cover__line", x + w / 2 - 2, y - 7, 4, 10, 1))
        for k in range(leds):
            out.append(circle("cover__dot", x + 6 + k * 6, y - h / 2 + 12, 1.6))
        return out

    # rail 1: breakers, power supply, relays
    y = 87
    b += rail(y)
    x = 44
    for _ in range(5):
        b += module(x, y, 17, 50, lever=True)
        x += 18
    x += 8
    b += module(x, y, 50, 54, leds=2)
    b += bars(x + 8, y - 2, [30, 20], gap=8)
    x += 58
    for _ in range(8):
        b += module(x, y, 11, 46)
        x += 12
    # rail 2: controller, I/O modules, interface
    y = 175
    b += rail(y)
    x = 44
    b += module(x, y, 42, 58, cls="cover__node", leds=4)
    x += 44
    for _ in range(6):
        b += module(x, y, 22, 58, cls="cover__node", leds=2)
        x += 23
    x += 8
    b += module(x, y, 34, 54, leds=3)
    # rail 3: terminal blocks
    y = 250
    b += rail(y)
    x = 44
    for i in range(30):
        cls = "art__bar--accent art__term" if i % 10 in (3, 4) else "art__module"
        b.append(rect(cls, x, y - 14, 6, 28, 1))
        x += 7
    b.append(rect("cover__line", x + 2, y - 16, 5, 32, 1))
    return svg(W, H, "Условная монтажная панель: автоматы, блок питания, реле, контроллер и модули ввода-вывода на DIN-рейках между кабель-каналами, ряд клемм", b)


DRAWINGS = {
    "schema": schema,
    "spec": spec,
    "list": items_list,
    "assembly": assembly,
    "panel": panel,
}


def main():
    html = PAGE.read_text(encoding="utf-8")
    for name, fn in DRAWINGS.items():
        pat = re.compile(rf"(<!-- gen:{name} -->).*?(\n\s*<!-- /gen:{name} -->)", re.S)
        if not pat.search(html):
            raise SystemExit(f"marker gen:{name} not found in {PAGE.name}")
        body = "\n".join(INDENT + line for line in fn())
        html = pat.sub(lambda m: m.group(1) + "\n" + body + m.group(2), html, count=1)
    PAGE.write_text(html, encoding="utf-8")
    print(f"updated {PAGE.relative_to(ROOT)}: {', '.join(DRAWINGS)}")


if __name__ == "__main__":
    main()
