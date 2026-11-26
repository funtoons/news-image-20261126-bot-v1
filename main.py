#!/usr/bin/env python3
"""News-image-20261126: one-page newspaper of Thursday 26 November 2026.

Draws a 1024x1024 PNG with a stdlib-only PNG encoder (struct + zlib) and a
hand-built 5x7 bitmap font. No network, no randomness, no timestamps in the
output: the same input always produces the same bytes.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (248, 244, 233)
INK = (22, 21, 19)
RED = (164, 31, 36)
BLUE = (29, 78, 121)
GOLD = (150, 110, 20)
GREY = (110, 104, 92)
WHITE = (255, 255, 255)


# ---------------------------------------------------------------- font -----
# 5x7 bitmap font. Each glyph: seven rows of five bits, written as 0/1.
_FONT_RAW = """
A 01110 10001 10001 11111 10001 10001 10001
B 11110 10001 10001 11110 10001 10001 11110
C 01110 10001 10000 10000 10000 10001 01110
D 11110 10001 10001 10001 10001 10001 11110
E 11111 10000 10000 11110 10000 10000 11111
F 11111 10000 10000 11110 10000 10000 10000
G 01110 10001 10000 10111 10001 10001 01111
H 10001 10001 10001 11111 10001 10001 10001
I 01110 00100 00100 00100 00100 00100 01110
J 00111 00010 00010 00010 00010 10010 01100
K 10001 10010 10100 11000 10100 10010 10001
L 10000 10000 10000 10000 10000 10000 11111
M 10001 11011 10101 10101 10001 10001 10001
N 10001 11001 10101 10011 10001 10001 10001
O 01110 10001 10001 10001 10001 10001 01110
P 11110 10001 10001 11110 10000 10000 10000
Q 01110 10001 10001 10001 10101 10010 01101
R 11110 10001 10001 11110 10100 10010 10001
S 01111 10000 10000 01110 00001 00001 11110
T 11111 00100 00100 00100 00100 00100 00100
U 10001 10001 10001 10001 10001 10001 01110
V 10001 10001 10001 10001 10001 01010 00100
W 10001 10001 10001 10101 10101 10101 01010
X 10001 10001 01010 00100 01010 10001 10001
Y 10001 10001 01010 00100 00100 00100 00100
Z 11111 00001 00010 00100 01000 10000 11111
a 00000 00000 01110 00001 01111 10001 01111
b 10000 10000 10110 11001 10001 10001 11110
c 00000 00000 01110 10000 10000 10001 01110
d 00001 00001 01101 10011 10001 10001 01111
e 00000 00000 01110 10001 11111 10000 01110
f 00110 01001 01000 11110 01000 01000 01000
g 00000 00000 01111 10001 10001 01111 00001 01110
h 10000 10000 10110 11001 10001 10001 10001
i 00100 00000 01100 00100 00100 00100 01110
j 00010 00000 00110 00010 00010 10010 01100
k 10000 10000 10010 10100 11000 10100 10010
l 01100 00100 00100 00100 00100 00100 01110
m 00000 00000 11010 10101 10101 10101 10101
n 00000 00000 10110 11001 10001 10001 10001
o 00000 00000 01110 10001 10001 10001 01110
p 00000 00000 10110 11001 10001 11110 10000
q 00000 00000 01101 10011 10001 01111 00001
r 00000 00000 10110 11001 10000 10000 10000
s 00000 00000 01111 10000 01110 00001 11110
t 01000 01000 11110 01000 01000 01001 00110
u 00000 00000 10001 10001 10001 10011 01101
v 00000 00000 10001 10001 10001 01010 00100
w 00000 00000 10001 10101 10101 10101 01010
x 00000 00000 10001 01010 00100 01010 10001
y 00000 00000 10001 10001 01111 00001 01110
z 00000 00000 11111 00010 00100 01000 11111
0 01110 10001 10011 10101 11001 10001 01110
1 00100 01100 00100 00100 00100 00100 01110
2 01110 10001 00001 00110 01000 10000 11111
3 11111 00010 00100 00010 00001 10001 01110
4 00010 00110 01010 10010 11111 00010 00010
5 11111 10000 11110 00001 00001 10001 01110
6 00110 01000 10000 11110 10001 10001 01110
7 11111 00001 00010 00100 01000 01000 01000
8 01110 10001 10001 01110 10001 10001 01110
9 01110 10001 10001 01111 00001 00010 01100
. 00000 00000 00000 00000 00000 01100 01100
, 00000 00000 00000 00000 01100 00100 01000
: 00000 01100 01100 00000 01100 01100 00000
; 00000 01100 01100 00000 01100 00100 01000
! 00100 00100 00100 00100 00100 00000 00100
? 01110 10001 00001 00110 00100 00000 00100
' 00100 00100 01000 00000 00000 00000 00000
" 01010 01010 01010 00000 00000 00000 00000
- 00000 00000 00000 11111 00000 00000 00000
( 00010 00100 01000 01000 01000 00100 00010
) 01000 00100 00010 00010 00010 00100 01000
/ 00001 00010 00010 00100 01000 01000 10000
% 11001 11010 00010 00100 01000 01011 10011
$ 00100 01111 10100 01110 00101 11110 00100
+ 00000 00100 00100 11111 00100 00100 00000
= 00000 00000 11111 00000 11111 00000 00000
* 00000 10101 01110 11111 01110 10101 00000
# 01010 01010 11111 01010 11111 01010 01010
@ 01110 10001 10111 10101 10110 10000 01110
"""


def _load_font():
    font = {" ": ["00000"] * 7}
    for line in _FONT_RAW.strip().splitlines():
        parts = line.split()
        ch = parts[0]
        rows = parts[1:]
        if len(rows) == 8:  # descender glyphs: merge last two rows
            rows = rows[:6] + [rows[6]]
            # keep 7 rows: first five, then combined descender pair
            rows = parts[1:6] + [parts[6], parts[7][:5]]
            rows = rows[:7]
        font[ch] = rows[:7]
    return font


FONT = _load_font()


# ------------------------------------------------------------- canvas ------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def text_width(self, s, scale, spacing=0):
        if not s:
            return 0
        return len(s) * (6 * scale + spacing) - spacing

    def text(self, x, y, s, scale, color, spacing=0):
        cx = x
        for ch in s:
            rows = FONT.get(ch, FONT[" "])
            for ry, row in enumerate(rows):
                for rx, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(cx + rx * scale, y + ry * scale,
                                       scale, scale, color)
            cx += 6 * scale + spacing
        return cx

    def text_centered(self, y, s, scale, color, spacing=0, cx=512):
        w = self.text_width(s, scale, spacing)
        return self.text(cx - w // 2, y, s, scale, color, spacing)


def wrap(text, max_chars):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- png --------
def write_png(path, w, h, rgb):
    raw = b"".join(b"\x00" + rgb[y * w * 3:(y + 1) * w * 3]
                   for y in range(h))

    def chunk(tag, data):
        body = tag + data
        return (struct.pack(">I", len(data)) + body +
                struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# -------------------------------------------------------------- map --------
# Dotted world map: per row, inclusive (start, end) column spans of land.
# 72 columns (5 deg each, lon -180..180), 30 rows (5 deg each, lat 90..-60).
MAP_ROWS = [
    [(10, 13), (26, 28)],
    [(8, 16), (25, 29), (40, 41)],
    [(6, 20), (25, 30), (48, 68)],
    [(2, 8), (9, 21), (26, 29), (44, 69)],
    [(2, 9), (10, 22), (33, 33), (40, 43), (44, 70)],
    [(3, 9), (11, 23), (36, 36), (40, 44), (45, 70)],
    [(12, 24), (37, 45), (46, 69)],
    [(13, 25), (37, 44), (45, 68)],
    [(14, 26), (37, 43), (45, 66), (67, 68)],
    [(15, 27), (38, 43), (46, 64), (67, 67)],
    [(16, 27), (38, 43), (52, 63), (67, 67)],
    [(17, 27), (38, 46), (47, 50), (53, 56), (57, 62)],
    [(17, 21), (38, 47), (48, 51), (53, 56), (58, 62)],
    [(18, 22), (39, 47), (53, 55), (58, 63)],
    [(20, 23), (39, 47), (59, 63)],
    [(21, 23), (24, 27), (39, 47), (60, 64)],
    [(23, 27), (40, 47), (59, 65)],
    [(23, 28), (40, 47), (60, 66)],
    [(23, 28), (40, 47), (61, 68)],
    [(24, 28), (41, 46), (64, 68)],
    [(24, 28), (41, 46), (60, 66)],
    [(24, 27), (41, 45), (48, 48), (59, 67)],
    [(24, 27), (41, 45), (48, 48), (60, 67)],
    [(25, 27), (41, 45), (61, 66)],
    [(25, 26), (42, 44), (62, 65), (69, 70)],
    [(25, 26), (69, 70)],
    [(25, 25)],
    [(25, 25)],
    [(25, 25)],
    [],
    [],
]

# (lon, lat) of the stories, for red map markers.
MARKERS = [
    (47, 24), (-77, 39), (-74, 41), (31, 30), (116, 40), (100, 40),
    (90, 24), (126, 39), (37, 56), (34, 31), (121, 31), (6, 46),
    (-75, 10), (6, 10), (77, 29), (0, 51), (4, 51), (43, 55),
    (30, 50), (21, 52), (7, 6),
]


# ----------------------------------------------------------- content -------
LEAD = [
    ("1", "HOUTHIS HIT SAUDI REFINERY",
     "Houthis claim a strike on Ras Tanura refinery. Brent tops $94."),
    ("2", "US TARIFFS HIT 14 NATIONS",
     "Washington proposes tariffs of up to 40% on China and 35% on Vietnam."),
]

STORIES = [
    ("3", "1M SATELLITES FOR SPACEX",
     "FCC clears SpaceX to launch 1m orbital data-centre satellites."),
    ("4", "MACY'S PARADE POSTPONED",
     "The 100th parade moves to Saturday, a first, as a storm hits New York."),
    ("5", "BIRTHRIGHT ORDER BLOCKED",
     "A second judge blocks Trump's birthright citizenship order."),
    ("6", "CAIRO FIRE KILLS 30",
     "A fuel tanker overturns on the ring road; at least 30 dead, 15 hurt."),
    ("7", "FIRST PAKISTANI IN SPACE",
     "Shenzhou-24 docks at Tiangong; Ali is the first Pakistani in orbit."),
    ("8", "BANGLADESH WAGE UP 36%",
     "Garment workers' minimum pay rises to Tk17,000 after weeks of protests."),
    ("9", "N. KOREA EXPELS ENVOY",
     "Pyongyang shuts the Swiss office; its envoy has 48 hours to leave."),
    ("10", "RUSSIA'S WAR DEAD: 490K",
     "Leaked state data analysed by the BBC put Russian deaths near 500,000."),
    ("11", "GAZA: HAMAS CHIEFS KILLED",
     "Israel kills two Hamas security chiefs in 24 hours; the ceasefire strains."),
    ("12", "CHINA PURGE HITS SHANGHAI",
     "Xi's graft probe hits Shanghai chief Chen Jining, a 4th Politburo fall."),
]

ALSO_LEFT = [
    "Ukraine hits air base; 5 warplanes hit",
    "Russia hits Ukraine power; 5 regions cut",
    "Kyiv hit by Russian ballistic missiles",
    "Nigeria: militants kill at least 30",
    "Nigeria: $227m meth lab smashed",
    "Colombia: 20 hostages freed in siege",
    "Poland plans no-fly zone on border",
    "Cards pass cash in eurozone shops",
    "India marks Constitution Day; 26/11",
    "India pledges Rs15,000 crore to Nepal",
    "EU summit opens in Brussels",
    "Chess: Gukesh-Sindarov, game 3",
]

ALSO_RIGHT = [
    "Sooryavanshi, 15, hits 204 off 53",
    "IPL 2027 auction draws 1,220 players",
    "Hera images show crater on asteroid",
    "Thanksgiving travel hit by storm",
    "No US probe of Huang before return",
    "IITs add 6,000 seats in AI, space",
    "India condemns Riyadh tower attack",
    "Taiwan faces 15% US tariff",
    "US proposes 10% duty on Embraer jets",
    "US Army blows up 5 tons of explosives",
    "Melania Trump reunites 7th child group",
]

TIMELINE = [
    "24 NOV 20:00  Wage +36% Bangladesh",
    "25 NOV 00:18  Shenzhou-24 launches",
    "25 NOV 03:56  Shenzhou-24 docks",
    "25 NOV 09:10  N. Korea expels envoy",
    "25 NOV 17:55  FCC clears SpaceX 1m",
    "25 NOV 23:08  Macy's parade delayed",
    "26 NOV 00:48  Houthi claim reported",
]


# ------------------------------------------------------------ drawing ------
def draw_flame(c, x, y, s):
    # Stylised flame: red outer triangle, gold inner.
    c.fill_rect(x, y + 2 * s, 6 * s, 2 * s, RED)
    c.fill_rect(x + s, y + s, 4 * s, 2 * s, RED)
    c.fill_rect(x + 2 * s, y, 2 * s, 2 * s, RED)
    c.fill_rect(x + 2 * s, y + 2 * s, 2 * s, 2 * s, GOLD)


def draw_globe(c, x, y, r):
    c.circle(x, y, r, BLUE)
    c.circle(x, y, r - 2, PAPER)
    c.circle(x, y, r - 2, BLUE)
    c.fill_rect(x - r + 2, y - 1, 2 * r - 4, 2, BLUE)
    c.fill_rect(x - 1, y - r + 2, 2, 2 * r - 4, BLUE)


def draw_page():
    c = Canvas(WIDTH, HEIGHT, PAPER)
    c.rect(8, 8, 1008, 1008, INK, 2)
    c.rect(14, 14, 996, 996, INK, 1)

    # ---- masthead ----
    c.text_centered(28, "THE WORLD IN ONE PAGE", 2, GREY, spacing=6)
    c.text_centered(52, "26 NOVEMBER 2026", 7, INK)
    c.fill_rect(20, 110, 984, 3, RED)
    c.text_centered(120,
                    "THURSDAY - ONE DAY OF WORLD NEWS - 35 STORIES, EACH CHECKED TWICE",
                    2, INK)

    # ---- lead stories ----
    lead_y = 148
    lead_h = 100
    for i, (num, head, summ) in enumerate(LEAD):
        bx = 20 + i * 500
        c.rect(bx, lead_y, 484, lead_h, INK, 2)
        c.fill_rect(bx + 2, lead_y + 2, 8, lead_h - 4, RED)
        c.text(bx + 22, lead_y + 12, head, 3, INK)
        for j, line in enumerate(wrap(summ, 38)):
            c.text(bx + 22, lead_y + 42 + j * 16, line, 2, INK)
        if i == 0:
            draw_flame(c, bx + 448, lead_y + lead_h - 16, 2)
        else:
            draw_globe(c, bx + 456, lead_y + lead_h - 14, 10)

    c.hline(20, 258, 984, INK, 2)

    # ---- numbered stories 3-12 ----
    top = 268
    row_h = 72
    for idx, (num, head, summ) in enumerate(STORIES):
        col = idx % 2
        row = idx // 2
        x = 20 + col * 500
        y = top + row * row_h
        c.fill_rect(x, y, 26, 26, RED)
        num_w = c.text_width(num, 2)
        c.text(x + (26 - num_w) // 2, y + 6, num, 2, WHITE)
        c.text(x + 34, y + 2, head, 3, INK)
        for j, line in enumerate(wrap(summ, 37)):
            c.text(x + 34, y + 28 + j * 15, line, 2, INK)

    c.hline(20, 638, 984, INK, 2)

    # ---- ALSO ON ----
    c.text(20, 648, "ALSO ON - 26 NOVEMBER", 3, RED)
    c.hline(20, 672, 984, INK, 1)
    item_y = 680
    for i, item in enumerate(ALSO_LEFT):
        y = item_y + i * 14
        c.fill_rect(20, y + 4, 6, 6, RED)
        c.text(34, y, item, 2, INK)
    for i, item in enumerate(ALSO_RIGHT):
        y = item_y + i * 14
        c.fill_rect(520, y + 4, 6, 6, RED)
        c.text(534, y, item, 2, INK)

    c.hline(20, 852, 984, INK, 2)

    # ---- map ----
    c.text(20, 862, "THE DAY ON THE MAP - RED DOTS MARK THE STORIES", 2, INK)
    map_x, map_y, map_w, map_h = 20, 884, 560, 108
    cw = map_w / 72.0
    ch = map_h / 30.0
    for r, spans in enumerate(MAP_ROWS):
        for (a, b) in spans:
            for col in range(a, b + 1):
                px = int(map_x + col * cw + cw / 2)
                py = int(map_y + r * ch + ch / 2)
                c.fill_rect(px, py, 2, 2, INK)
    for (lon, lat) in MARKERS:
        col = (lon + 180.0) / 5.0
        row = (90.0 - lat) / 5.0
        px = int(map_x + col * cw)
        py = int(map_y + row * ch)
        c.circle(px, py, 5, WHITE)
        c.circle(px, py, 4, RED)

    # ---- timeline ----
    c.text(600, 862, "WHEN IT BROKE (UTC)", 2, INK)
    for i, entry in enumerate(TIMELINE):
        y = 884 + i * 15
        c.text(600, y, entry, 2, INK)

    # ---- audit line ----
    c.text_centered(
        996,
        "DATE-CHECK: 35 stories verified against 2+ sources; 8 older stories rejected.",
        2, GREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    canvas = draw_page()
    write_png(path, WIDTH, HEIGHT, canvas.px)


if __name__ == "__main__":
    main()
