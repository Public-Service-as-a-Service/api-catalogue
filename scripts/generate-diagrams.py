#!/usr/bin/env python3
"""Generate per-API architecture SVG diagrams for the API catalogue.

Data comes from scripts/apis-data.json, with facts derived from each
api-service source repository (dependency versions from the integration
client specifications, behaviour from the service layer code).
Run from anywhere: output is written to assets/diagrams/ in the repo root.
"""

import json
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "diagrams")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apis-data.json")

# Palette aligned with the site's stylesheet
INK = "#1c2b33"
INK_SOFT = "#46595f"
PRIMARY = "#005a70"
PRIMARY_DARK = "#00434f"
BLUE_FILL = "#dbeafe"
BLUE_EDGE = "#2563eb"
GREEN_FILL = "#e8f5ee"
GREEN_EDGE = "#15803d"
YELLOW_FILL = "#fdf3d7"
YELLOW_EDGE = "#b45309"
GREY_FILL = "#eef1f4"
GREY_EDGE = "#64748b"
ARROW = "#7d99a1"

W = 1400


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, title, sub, fill, edge, dashed=False, title_size=15, sub_size=11.5):
    dash = ' stroke-dasharray="7,5"' if dashed else ""
    s = f'<rect x="{x}" y="{y}" rx="10" width="{w}" height="{h}" fill="{fill}" stroke="{edge}" stroke-width="2"{dash}/>'
    cx = x + w / 2
    if sub:
        s += f'<text x="{cx}" y="{y + h/2 - 4}" text-anchor="middle" font-size="{title_size}" font-weight="bold" fill="{INK}">{esc(title)}</text>'
        s += f'<text x="{cx}" y="{y + h/2 + 15}" text-anchor="middle" font-size="{sub_size}" fill="{INK_SOFT}">{esc(sub)}</text>'
    else:
        s += f'<text x="{cx}" y="{y + h/2 + 5}" text-anchor="middle" font-size="{title_size}" font-weight="bold" fill="{INK}">{esc(title)}</text>'
    return s


def arrow(x1, y1, x2, y2, color=ARROW, dashed=False, curve=True):
    dash = ' stroke-dasharray="6,5"' if dashed else ""
    if curve:
        my = (y1 + y2) / 2
        d = f"M {x1} {y1} C {x1} {my}, {x2} {my}, {x2} {y2}"
    else:
        d = f"M {x1} {y1} L {x2} {y2}"
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6"{dash} marker-end="url(#arr)"/>'


def group_rect(x, y, w, h, label, fill, edge):
    return (f'<rect x="{x}" y="{y}" rx="12" width="{w}" height="{h}" fill="{fill}" stroke="{edge}" stroke-width="1.5" opacity="0.55"/>'
            f'<text x="{x+16}" y="{y+24}" font-size="13" font-weight="bold" letter-spacing="1" fill="{INK}">{esc(label)}</text>')


def rows_layout(items, x0, x1, y, bw, bh, gap_y=16, min_gap=14):
    """Lay out items in centered rows within [x0, x1]. Returns (positions, bottom_y)."""
    per_row = max(1, int((x1 - x0 + min_gap) // (bw + min_gap)))
    pos = []
    i = 0
    while i < len(items):
        row = items[i:i + per_row]
        total = len(row) * bw + (len(row) - 1) * min_gap
        start = x0 + ((x1 - x0) - total) / 2
        for j in range(len(row)):
            pos.append((start + j * (bw + min_gap), y))
        y += bh + gap_y
        i += per_row
    return pos, y - gap_y


def clip(s, n):
    """Trim text so it fits inside a diagram box."""
    s = (s or "").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def diagram(filename, title, service_sub, dependencies, database, externals, notes):
    """dependencies: list of (name, version, usage); database/externals: strings."""
    parts = []
    y = 16
    parts.append(f'<text x="{W/2}" y="{y+18}" text-anchor="middle" font-size="22" font-weight="bold" fill="{PRIMARY_DARK}">Lösningsarkitektur — {esc(title)}</text>')
    y += 44
    parts.append(f'<text x="{W/2}" y="{y}" text-anchor="middle" font-size="13" fill="{INK_SOFT}">Pilar visar anrop. Konsumenter når API:et via kommunens API-plattform (WSO2); tjänsten anropar i sin tur andra mikrotjänster.</text>')
    y += 24

    # Consumers box
    cw, ch = 420, 64
    cx = (W - cw) / 2
    parts.append(box(cx, y, cw, ch, "Konsumerande applikationer", "webbappar, e-tjänster och verksamhetssystem", GREY_FILL, GREY_EDGE, dashed=True, title_size=15))
    consumer_bottom = (W / 2, y + ch)
    y += ch + 46

    # Gateway bar
    gw, gh = 640, 58
    gx = (W - gw) / 2
    parts.append(arrow(consumer_bottom[0], consumer_bottom[1], W / 2, y, color=GREY_EDGE, curve=False))
    parts.append(f'<text x="{W/2 + 12}" y="{consumer_bottom[1] + 28}" font-size="11" fill="{INK_SOFT}">OAuth2 (CLIENT_KEY/CLIENT_SECRET)</text>')
    parts.append(box(gx, y, gw, gh, "API-plattform (WSO2)", "api.sundsvall.se — gemensam ingång till alla verksamhets-API:er", GREY_FILL, PRIMARY, title_size=16))
    gate_bottom = (W / 2, y + gh)
    y += gh + 46

    # The service itself (+ database to the right)
    sw, sh = 440, 74
    sx = (W - sw) / 2
    parts.append(arrow(gate_bottom[0], gate_bottom[1], W / 2, y, color=BLUE_EDGE, curve=False))
    parts.append(box(sx, y, sw, sh, title, service_sub, BLUE_FILL, BLUE_EDGE, title_size=17))
    if database:
        db_w, db_h = 260, 60
        db_x = W - db_w - 30
        parts.append(box(db_x, y + 7, db_w, db_h, "Databas", database, YELLOW_FILL, YELLOW_EDGE))
        parts.append(arrow(sx + sw, y + sh / 2, db_x, y + 7 + db_h / 2, color=YELLOW_EDGE, curve=False))
        parts.append(f'<text x="{(sx+sw+db_x)/2}" y="{y + sh/2 - 10}" text-anchor="middle" font-size="11" fill="{YELLOW_EDGE}">lagring</text>')
    service_bottom = (sx + sw / 2, y + sh)
    y += sh + 52

    bw, bh = 205, 64
    margin = 40
    inner_pad = 20

    # Dependency group
    if dependencies:
        pos, rows_bottom = rows_layout(dependencies, margin + inner_pad, W - margin - inner_pad, y + 40, bw, bh)
        parts.append(group_rect(margin, y, W - 2 * margin, rows_bottom - y + inner_pad, "BEROENDE MIKROTJÄNSTER — anropas av tjänsten", "#f4faf6", GREEN_EDGE))
        for (name, ver, sub), (bx, by) in zip(dependencies, pos):
            label = f"{name} {ver}".strip()
            parts.append(box(bx, by, bw, bh, label, sub, GREEN_FILL, GREEN_EDGE, title_size=14))
            parts.append(arrow(service_bottom[0], service_bottom[1], bx + bw / 2, by))
        y = rows_bottom + inner_pad + 34

    # External systems / integrations group
    if externals:
        ext = [(name, "", "integration") for name in externals]
        pos, rows_bottom = rows_layout(ext, margin + inner_pad, W - margin - inner_pad, y + 40, bw, bh)
        parts.append(group_rect(margin, y, W - 2 * margin, rows_bottom - y + inner_pad, "EXTERNA SYSTEM OCH INTEGRATIONER", "#f4f5f7", GREY_EDGE))
        for (name, _ver, sub), (bx, by) in zip(ext, pos):
            parts.append(box(bx, by, bw, bh, name, sub, GREY_FILL, GREY_EDGE, dashed=True, title_size=14))
            parts.append(arrow(service_bottom[0], service_bottom[1], bx + bw / 2, by, dashed=True))
        y = rows_bottom + inner_pad + 28

    # Notes + legend
    for note in notes:
        parts.append(f'<text x="{margin}" y="{y}" font-size="12" fill="{INK_SOFT}">• {esc(note)}</text>')
        y += 20
    y += 8
    lx = margin
    legend = [
        (BLUE_FILL, BLUE_EDGE, False, "Detta API"),
        (GREEN_FILL, GREEN_EDGE, False, "Beroende mikrotjänst"),
        (YELLOW_FILL, YELLOW_EDGE, False, "Databas"),
        (GREY_FILL, GREY_EDGE, True, "Extern/gemensam tjänst"),
    ]
    for fill, edge, dashed, label in legend:
        dash = ' stroke-dasharray="5,4"' if dashed else ""
        parts.append(f'<rect x="{lx}" y="{y}" width="26" height="16" rx="4" fill="{fill}" stroke="{edge}" stroke-width="1.5"{dash}/>')
        parts.append(f'<text x="{lx+33}" y="{y+13}" font-size="12.5" fill="{INK}">{esc(label)}</text>')
        lx += 33 + len(label) * 6.7 + 34
    y += 40

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {int(y)}" '
           f'font-family="Segoe UI, Helvetica Neue, Arial, sans-serif" role="img" '
           f'aria-label="Arkitekturdiagram för {esc(title)}">'
           f'<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           f'<path d="M 0 1 L 9 5 L 0 9 z" fill="{ARROW}"/></marker></defs>'
           f'<rect width="{W}" height="{int(y)}" fill="#ffffff"/>'
           + "".join(parts) + "</svg>")
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(path, f"({int(y)}px)")


with open(DATA, encoding="utf-8") as f:
    apis = json.load(f)

for api in apis:
    deps = [(clip(d["name"], 22), d.get("version") or "", clip(d.get("usage"), 33))
            for d in (api.get("beroenden") or [])]
    teknik = api.get("teknik") or {}
    stack_bits = [p for p in [teknik.get("sprak"), teknik.get("ramverk")] if p]
    service_sub = (" + ".join(stack_bits) + " — " + api["repo"]) if stack_bits else api["repo"]
    if len(service_sub) > 60:
        service_sub = api["repo"]
    database = None
    if api.get("databas"):
        database = clip(api["databas"].split(";")[0].split(" med ")[0], 30)
    diagram(
        f"{api['slug']}.svg",
        f"{api['namn']} {api.get('apiVersion', '')}".strip(),
        service_sub,
        deps,
        database,
        (api.get("integrationer") or [])[:10],
        (api.get("anteckningar") or [])[:3],
    )
