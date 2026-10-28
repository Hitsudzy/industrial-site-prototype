#!/usr/bin/env python3
"""Worst-case WCAG contrast of the first-screen text over the code-drawn background.

The hero is layered (bottom to top):
  1. --hero-bg          gradient + radial glow           (assets/css/tokens.css)
  2. --hero-art         hero-a.svg / hero-b.svg           (assets/img, tools/gen_art.py)
  3. scan line          concept A only                    (.hero__scan, base.css)
  4. scrim              .hero__art::after                 (base.css)
  5. text

The model is deliberately pessimistic: under the text it assumes the brightest
point of the glow AND the brightest stroke of the artwork at once, then lays the
scrim at its weakest strength under text. If the text passes AA (4.5:1) there,
it passes everywhere. Keep the numbers below in sync with tokens.css / gen_art.py.

Usage:  python3 tools/check_hero_contrast.py      exit 0 = all pairs >= 4.5
"""
import sys


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def over(top, alpha, under):
    return tuple(alpha * t + (1 - alpha) * u for t, u in zip(top, under))


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


CONCEPTS = {
    "A": {
        # brightest point of --hero-bg: cyan glow 0.16 over the lighter gradient end
        "bg": over(rgb("2fd3e0"), 0.16, rgb("0b1220")),
        # brightest art pixel: amber indicator lamp in the line-up group (group
        # opacity 0.55), with the scan line on top (accent 0.6 inside opacity 0.5)
        "art": [(rgb("ffd166"), 0.55), (rgb("2fd3e0"), 0.30)],
        "scrim": rgb("070d18"),
        "text": {"text": "e6edf5", "muted": "9fb0c4", "accent (eyebrow)": "2fd3e0"},
    },
    "B": {
        "bg": over(rgb("8fb3ff"), 0.22, rgb("13246a")),
        # glow ellipse 0.25, cabinet fill 0.14, lamp dot 0.3 stacked on one pixel
        "art": [(rgb("5b8cff"), 0.25), (rgb("8fb3ff"), 0.14), (rgb("b9cfff"), 0.30)],
        "scrim": rgb("0b1640"),
        "text": {"text": "ffffff", "muted": "b8c2dd", "accent (eyebrow)": "8fb3ff"},
    },
}

# weakest scrim strength anywhere under text (.hero__art::after in assets/css/base.css)
SCRIMS = {"narrow < 900px": 0.62, "wide >= 900px, text column": 0.72}


def main():
    worst_all = 99
    for name, c in CONCEPTS.items():
        under = c["bg"]
        for colour, alpha in c["art"]:
            under = over(colour, alpha, under)
        for sname, s in SCRIMS.items():
            backdrop = over(c["scrim"], s, under)
            for tname, t in c["text"].items():
                r = ratio(rgb(t), backdrop)
                worst_all = min(worst_all, r)
                flag = "ok " if r >= 4.5 else "LOW"
                print(f"{flag} {name} {sname:28} {tname:17} {r:5.2f}:1")
        bare = min(ratio(rgb(t), under) for t in c["text"].values())
        print(f"    {name} without scrim (art area, no text)        worst {bare:5.2f}:1")
    return 0 if worst_all >= 4.5 else 1


if __name__ == "__main__":
    sys.exit(main())
