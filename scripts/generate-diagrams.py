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
SERVICE_W = 440


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# Character widths (Helvetica/Arial, 1/1000 em) used to measure text before it is
# drawn. The diagrams render in Segoe UI/Helvetica/Arial; Helvetica is marginally
# wider than Segoe UI, so the measurement errs towards truncating a little early.
_W_REGULAR = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667, "'": 191,
    "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333, ".": 278, "/": 278,
    ":": 278, ";": 278, "<": 584, "=": 584, ">": 584, "?": 556, "@": 1015,
    "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722,
    "I": 278, "J": 500, "K": 667, "L": 556, "M": 833, "N": 722, "O": 778, "P": 667,
    "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944, "X": 667,
    "Y": 667, "Z": 611, "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556, "`": 333,
    "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556, "h": 556,
    "i": 222, "j": 222, "k": 500, "l": 222, "m": 833, "n": 556, "o": 556, "p": 556,
    "q": 556, "r": 333, "s": 500, "t": 278, "u": 556, "v": 500, "w": 722, "x": 500,
    "y": 500, "z": 500, "{": 334, "|": 260, "}": 334, "~": 584,
    "–": 556, "—": 1000, "‘": 222, "’": 222, "“": 333, "”": 333, "…": 1000,
    "·": 278, "\u00a0": 278,
}
_W_BOLD = {
    " ": 278, "!": 333, '"': 474, "#": 556, "$": 556, "%": 889, "&": 722, "'": 238,
    "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333, ".": 278, "/": 278,
    ":": 333, ";": 333, "<": 584, "=": 584, ">": 584, "?": 611, "@": 975,
    "A": 722, "B": 722, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722,
    "I": 278, "J": 556, "K": 722, "L": 611, "M": 833, "N": 722, "O": 778, "P": 667,
    "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944, "X": 667,
    "Y": 667, "Z": 611, "[": 333, "\\": 278, "]": 333, "^": 584, "_": 556, "`": 333,
    "a": 556, "b": 611, "c": 556, "d": 611, "e": 556, "f": 333, "g": 611, "h": 611,
    "i": 278, "j": 278, "k": 556, "l": 278, "m": 889, "n": 611, "o": 611, "p": 611,
    "q": 611, "r": 389, "s": 556, "t": 333, "u": 611, "v": 556, "w": 778, "x": 556,
    "y": 556, "z": 500, "{": 389, "|": 280, "}": 389, "~": 584,
    "–": 556, "—": 1000, "‘": 278, "’": 278, "“": 500, "”": 500, "…": 1000,
    "·": 278, "\u00a0": 278,
}
# Accented characters are as wide as their base letter.
for _table in (_W_REGULAR, _W_BOLD):
    for _accented, _base in (("å", "a"), ("ä", "a"), ("ö", "o"), ("é", "e"), ("è", "e"),
                             ("ü", "u"), ("Å", "A"), ("Ä", "A"), ("Ö", "O"), ("É", "E")):
        _table[_accented] = _table[_base]

DEFAULT_W = 556


def text_width(s, size, bold=False):
    """Approximate rendered width of s in pixels at the given font size."""
    table = _W_BOLD if bold else _W_REGULAR
    return sum(table.get(ch, DEFAULT_W) for ch in s) * size / 1000.0


def fit(s, max_w, size, bold=False):
    """Truncate s with an ellipsis so that it renders within max_w pixels."""
    s = (s or "").strip()
    if not s or text_width(s, size, bold) <= max_w:
        return s
    table = _W_BOLD if bold else _W_REGULAR
    ell = table["…"] * size / 1000.0
    out = ""
    w = 0.0
    for ch in s:
        cw = table.get(ch, DEFAULT_W) * size / 1000.0
        if w + cw + ell > max_w:
            break
        out += ch
        w += cw
    return out.rstrip(" -–—,;:(") + "…"


def wrap(s, max_w, size, bold=False):
    """Greedily wrap s on word boundaries into lines that fit within max_w pixels."""
    lines = []
    cur = ""
    for word in (s or "").split():
        cand = f"{cur} {word}" if cur else word
        if cur and text_width(cand, size, bold) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines or [""]


def tooltip(full, shown):
    """A <title> child, so hovering a truncated label reveals the full text."""
    full = (full or "").strip()
    return f"<title>{esc(full)}</title>" if full and full != shown else ""


BOX_PAD = 12


def box(x, y, w, h, title, sub, fill, edge, dashed=False, title_size=15, sub_size=11.5):
    """Draw a labelled box. Text that is wider than the box is truncated with an
    ellipsis, so labels never spill outside the box or collide with a neighbour;
    the untruncated text is kept as a <title> tooltip."""
    dash = ' stroke-dasharray="7,5"' if dashed else ""
    s = f'<rect x="{x}" y="{y}" rx="10" width="{w}" height="{h}" fill="{fill}" stroke="{edge}" stroke-width="2"{dash}/>'
    cx = x + w / 2
    inner = w - 2 * BOX_PAD
    title_text = fit(title, inner, title_size, bold=True)
    sub_text = fit(sub, inner, sub_size) if sub else ""
    if sub:
        s += f'<text x="{cx}" y="{y + h/2 - 4}" text-anchor="middle" font-size="{title_size}" font-weight="bold" fill="{INK}">{esc(title_text)}{tooltip(title, title_text)}</text>'
        s += f'<text x="{cx}" y="{y + h/2 + 15}" text-anchor="middle" font-size="{sub_size}" fill="{INK_SOFT}">{esc(sub_text)}{tooltip(sub, sub_text)}</text>'
    else:
        s += f'<text x="{cx}" y="{y + h/2 + 5}" text-anchor="middle" font-size="{title_size}" font-weight="bold" fill="{INK}">{esc(title_text)}{tooltip(title, title_text)}</text>'
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
    # letter-spacing adds one pixel per character on top of the measured width.
    text = fit(label, w - 32 - len(label), 13, bold=True)
    return (f'<rect x="{x}" y="{y}" rx="12" width="{w}" height="{h}" fill="{fill}" stroke="{edge}" stroke-width="1.5" opacity="0.55"/>'
            f'<text x="{x+16}" y="{y+24}" font-size="13" font-weight="bold" letter-spacing="1" fill="{INK}">{esc(text)}{tooltip(label, text)}</text>')


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


def diagram(filename, title, service_sub, dependencies, database, externals, notes):
    """dependencies: list of (name, version, usage); database/externals: strings."""
    parts = []
    y = 16
    margin = 40
    heading = f"Lösningsarkitektur — {title}"
    heading_text = fit(heading, W - 2 * margin, 22, bold=True)
    parts.append(f'<text x="{W/2}" y="{y+18}" text-anchor="middle" font-size="22" font-weight="bold" fill="{PRIMARY_DARK}">{esc(heading_text)}{tooltip(heading, heading_text)}</text>')
    y += 44
    intro = "Pilar visar anrop. Konsumenter når API:et via kommunens API-plattform (WSO2); tjänsten anropar i sin tur andra mikrotjänster."
    parts.append(f'<text x="{W/2}" y="{y}" text-anchor="middle" font-size="13" fill="{INK_SOFT}">{esc(fit(intro, W - 2 * margin, 13))}</text>')
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
    sw, sh = SERVICE_W, 74
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
    bullet_indent = text_width("• ", 12)
    for note in notes:
        for i, line in enumerate(wrap(note, W - 2 * margin - bullet_indent, 12)):
            prefix = "• " if i == 0 else ""
            lx_note = margin if i == 0 else margin + bullet_indent
            parts.append(f'<text x="{lx_note}" y="{y}" font-size="12" fill="{INK_SOFT}">{prefix}{esc(line)}</text>')
            y += 18
        y += 2
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
        lx += 33 + text_width(label, 12.5) + 34
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
    deps = [(d["name"], d.get("version") or "", d.get("usage") or "")
            for d in (api.get("beroenden") or [])]
    teknik = api.get("teknik") or {}
    stack_bits = [p for p in [teknik.get("sprak"), teknik.get("ramverk")] if p]
    service_sub = (" + ".join(stack_bits) + " — " + api["repo"]) if stack_bits else api["repo"]
    if text_width(service_sub, 11.5) > SERVICE_W - 2 * BOX_PAD:
        service_sub = api["repo"]
    database = None
    if api.get("databas"):
        database = api["databas"].split(";")[0].split(" med ")[0]
    diagram(
        f"{api['slug']}.svg",
        f"{api['namn']} {api.get('apiVersion', '')}".strip(),
        service_sub,
        deps,
        database,
        (api.get("integrationer") or [])[:10],
        (api.get("anteckningar") or [])[:3],
    )
