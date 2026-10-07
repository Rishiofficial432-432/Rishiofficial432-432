#!/usr/bin/env python3
"""
Generate a neofetch-style info card SVG -> info-card.svg.

Looks like `neofetch` output in a terminal: ASCII "SMIT" logo on the left,
key/value rows on the right - each text row fades + slides in on a short
stagger (CSS animation), plays once, then freezes.

GitHub renders SVGs inside <img> and runs CSS/SMIL animations there;
JS does not run, so all motion lives in SVG attributes.

    python scripts/make_info_card.py [output.svg]
    STATIC=1 python scripts/make_info_card.py   # frozen snapshot for preview
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

# canvas (840x880 - same as portrait so both panels sit at equal heights)
W, H = 840, 880
PAD  = 28
TITLEBAR_H = 30
CONTENT_TOP = TITLEBAR_H + PAD + 8

# palette
BG      = "#0d1117"
BG2     = "#0b1320"
FRAME   = "#30363d"
MUTED   = "#7d8590"
GREEN   = "#39d353"
CYAN    = "#22d3ee"
YELLOW  = "#f2cc60"
MAGENTA = "#c678dd"
BLUE    = "#4e9bff"
RED     = "#e06c75"
WHITE   = "#e6edf3"
DIM     = "#8b949e"
ORANGE  = "#f79000"

# profile data
USERNAME = "smit"
HOSTNAME  = "github"

INFO_ROWS = [
    (CYAN,    "name",       WHITE,   "Smit"),
    (CYAN,    "role",       WHITE,   "Founder · AI Strategist · Creator"),
    (None,    None,         None,    None),
    (CYAN,    "now",        GREEN,   "Aveon AI India - Startup since Nov 2024"),
    (CYAN,    "focus",      YELLOW,  "UI/UX · Prompt Engineering · AI Tools"),
    (CYAN,    "expertise",  MAGENTA, "3500+ AI tools · Google Looker Studio"),
    (None,    None,         None,    None),
    (CYAN,    "languages",  WHITE,   "English · Hindi · Gujarati"),
    (CYAN,    "stack",      WHITE,   "Python · JavaScript · React · Node.js"),
    (CYAN,    "learning",   CYAN,    "Quantum Computing · Cloud · LLMs"),
    (None,    None,         None,    None),
    (CYAN,    "hobbies",    ORANGE,  "Writing · Guitar · Painting · Cooking"),
    (CYAN,    "github",     BLUE,    "github.com/Rishiofficial432-432"),
]

# ASCII "SMIT" logo (6 rows, box-drawing block art)
LOGO_LINES = [
    (" .d8888b.  888b     d888 8888888 88888888888 ", GREEN),
    ("d88P  Y88b 8888b   d8888   888       888     ", GREEN),
    ("Y88b.      88888b.d88888   888       888     ", CYAN),
    (" Y888b.    888Y88888P888   888       888     ", CYAN),
    ("    Y88b.  888 Y888P 888   888       888     ", BLUE),
    ("Y88b  888  888  Y8P  888   888       888     ", BLUE),
    (" Y8888P    888   Y   888 8888888     888     ", MAGENTA),
]

SWATCH_ROWS = [
    ["#1c1c1c","#e06c75","#98c379","#e5c07b","#61afef","#c678dd","#56b6c2","#abb2bf"],
    ["#3e4451","#e06c75","#98c379","#e5c07b","#61afef","#c678dd","#56b6c2","#ffffff"],
]

LOGO_FONT   = 12
LOGO_LINE_H = 20
LOGO_X      = PAD
LOGO_Y0     = CONTENT_TOP + 4

INFO_FONT   = 20
INFO_LINE_H = 27
_logo_cols  = max(len(line) for line, _ in LOGO_LINES)
INFO_X      = PAD + int(_logo_cols * LOGO_FONT * 0.605) + 24
INFO_Y0     = CONTENT_TOP

ANIM_DUR     = 0.30
ANIM_STAGGER = 0.09


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


parts = []
delay_counter = [0.0]


def next_cls():
    if STATIC:
        return ""
    d = delay_counter[0]
    delay_counter[0] += ANIM_STAGGER
    return f' class="r" style="animation-delay:{d:.2f}s"'


parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" '
    f"font-family=\"ui-monospace,SFMono-Regular,Menlo,Consolas,'Courier New',monospace\">"
)

if not STATIC:
    parts.append(
        "<style>"
        f".r{{opacity:0;animation:si {ANIM_DUR:.2f}s ease-out both}}"
        "@keyframes si{0%{opacity:0;transform:translateX(-10px)}100%{opacity:1;transform:translateX(0)}}"
        "@media(prefers-reduced-motion:reduce){.r{opacity:1!important;transform:none!important;animation:none!important}}"
        "</style>"
    )

parts.append(
    "<defs>"
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/>'
    f'<stop offset="1" stop-color="{BG}"/>'
    "</linearGradient></defs>"
)
parts.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>')
parts.append(
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" '
    f'fill="none" stroke="{FRAME}" stroke-width="1"/>'
)

parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
parts.append(
    f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
    f'text-anchor="middle">smit@github: ~ $ neofetch</text>'
)

# ASCII logo rows
for li, (text, color) in enumerate(LOGO_LINES):
    y = LOGO_Y0 + li * LOGO_LINE_H + LOGO_FONT
    cls = next_cls()
    parts.append(
        f'<text x="{LOGO_X}" y="{y}"{cls} '
        f'fill="{color}" font-size="{LOGO_FONT}" xml:space="preserve">{esc(text)}</text>'
    )

# info header
header_y = INFO_Y0 + INFO_FONT + 4
cls = next_cls()
parts.append(
    f'<text x="{INFO_X}" y="{header_y}"{cls} font-size="{INFO_FONT}">'
    f'<tspan fill="{GREEN}">{esc(USERNAME)}</tspan>'
    f'<tspan fill="{MUTED}">@</tspan>'
    f'<tspan fill="{CYAN}">{esc(HOSTNAME)}</tspan>'
    "</text>"
)

# separator
sep_y = header_y + INFO_LINE_H
cls = next_cls()
sep = chr(0x2500) * (len(USERNAME) + 1 + len(HOSTNAME))
parts.append(
    f'<text x="{INFO_X}" y="{sep_y}"{cls} fill="{DIM}" font-size="{INFO_FONT}">{esc(sep)}</text>'
)

# info rows
info_y = sep_y + INFO_LINE_H + 4
for lc, label, vc, value in INFO_ROWS:
    if label is None:
        info_y += int(INFO_LINE_H * 0.45)
        continue
    cls = next_cls()
    parts.append(
        f'<text x="{INFO_X}" y="{info_y}"{cls} font-size="{INFO_FONT}">'
        f'<tspan fill="{lc}">{esc(label)}</tspan>'
        f'<tspan fill="{MUTED}">: </tspan>'
        f'<tspan fill="{vc}">{esc(value)}</tspan>'
        "</text>"
    )
    info_y += INFO_LINE_H

# vertical divider
div_x = INFO_X - 14
parts.append(
    f'<line x1="{div_x}" y1="{CONTENT_TOP}" x2="{div_x}" y2="{H - PAD - 50}" '
    f'stroke="{FRAME}" stroke-opacity="0.5" stroke-dasharray="3 4"/>'
)

# color swatches
SW, SH, SGAP = 20, 16, 3
swatch_y = H - PAD - SH * 2 - SGAP - 32
for ri, row_colors in enumerate(SWATCH_ROWS):
    sy = swatch_y + ri * (SH + SGAP)
    for ci, color in enumerate(row_colors):
        sx = LOGO_X + ci * (SW + SGAP)
        cls = next_cls()
        parts.append(
            f'<rect x="{sx}" y="{sy}" width="{SW}" height="{SH}" rx="2" fill="{color}"{cls}/>'
        )

# status bar
status_line_y = H - PAD - 26
parts.append(f'<line x1="0" y1="{status_line_y}" x2="{W}" y2="{status_line_y}" stroke="{FRAME}"/>')
status_y = status_line_y + 17
parts.append(
    f'<text x="{PAD}" y="{status_y}" fill="{MUTED}" font-size="13">'
    f'smit@github:~$ neofetch <tspan fill="{GREEN}">done</tspan></text>'
)
cursor_x = PAD + int(29 * 7.8) + 4
parts.append(
    f'<rect x="{cursor_x}" y="{status_y - 12}" width="8" height="14" fill="{WHITE}">'
    '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
    'dur="1s" repeatCount="indefinite"/></rect>'
)

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {OUT}  ({W}x{H}, {len(svg)//1024} KB)")
