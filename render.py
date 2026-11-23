#!/usr/bin/env python3
"""news-image-20261122 V1-FRESH renderer — rule-based, deterministic.
Build-time only. The graded entrypoint (main.py) copies the PNG this
script produces; this script itself never ships as the entrypoint.
Draws entry.png 1024x1024, <1 MiB, byte-identical across runs.

Layout (NEW, unlike rank 1-3 and unlike V1):
  masthead "THE WORLD, CHECKED" (title biggest, date second) ->
  lead band: 3 cards side by side (COP31 / Merkury / Marquez) ->
  grid: 11 cards, 3 cols x 4 rows, shuffled so no two neighbours share
  a region colour, 12th cell = "THE DAY IN NUMBERS" panel ->
  MORE STORIES: briefs 15-41 in 2 columns, number in a coloured box ->
  footer: region strip + DATE CHECK + NOT SHOWN + HOW WE CHECKED.
No map, no timeline strip, no big-number strip (all three were in V1
and in rank 1-3). 41 verified stories, from notes/sumber-V1fresh.md.
Region counts counted from the per-story Wil column of that file:
EU 9, ME 9, AM 8, AS 5, AF 5, OC 2, WORLD 3 (its summary line says
EU 10 / WORLD 2; the per-row table is the primary data, so the strip
prints the counted 9 / 3 and the discrepancy is noted in STORIES.md).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024

PAPER = (247, 243, 232)
INK = (26, 26, 26)
NAVY = (31, 58, 95)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)
BRICK = (166, 58, 43)
YELLOW = (255, 210, 90)
LIGHT_LINE = (200, 192, 170)
DATE_RED = (90, 40, 30)

# Region palette. White-on-colour contrast is checked at the end of
# render(): every colour must clear 4.5:1 against white (AF and OC were
# darkened from the V1 palette until they did).
REGION = {"EU": (51, 86, 127), "ME": (166, 58, 43), "AS": (47, 107, 79),
          "AF": (120, 78, 0), "AM": (110, 74, 138), "OC": (16, 104, 100),
          "WORLD": (85, 85, 85)}
REGION_NAME = {"EU": "EUROPE", "ME": "MIDDLE EAST", "AS": "ASIA",
               "AF": "AFRICA", "AM": "AMERICAS", "OC": "OCEANIA",
               "WORLD": "WORLD"}

FONT_DIR = "/usr/share/fonts/truetype/liberation"
_fonts = {}


def _font(name, size):
    key = (name, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _fonts[key]


def F_MAST(size):
    return _font("LiberationSerif-Bold.ttf", size)


def F_SANS(size):
    return _font("LiberationSans-Regular.ttf", size)


def F_SANSB(size):
    return _font("LiberationSans-Bold.ttf", size)


def text_w(draw, s, font):
    return int(draw.textlength(s, font=font))


def tint(rgb, amount):
    """Mix a region colour toward the paper colour."""
    return tuple(int(round(rgb[i] + (PAPER[i] - rgb[i]) * amount))
                 for i in range(3))


def contrast(c1, c2):
    def lum(c):
        def f(v):
            v = v / 255
            return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
        r, g, b = f(c[0]), f(c[1]), f(c[2])
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    l1, l2 = sorted((lum(c1), lum(c2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, font, max_w, max_lines):
    lines = wrap(draw, text, font, max_w)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    while out and text_w(draw, out[-1] + " …", font) > max_w:
        out[-1] = out[-1].rsplit(" ", 1)[0] if " " in out[-1] else out[-1][:-1]
    out[-1] = out[-1] + " …"
    return out


# ---------------------------------------------------------------- data
# 41 stories, all verified Sunday 22 Nov 2026 (notes/sumber-V1fresh.md).
# value = the news value printed in the banner; num = the one number
# baked into the illustration on a paper chip.
LEAD = [
    {"n": 1, "region": "WORLD", "place": "ANTALYA",
     "title": "COP31 COLLAPSES", "value": "NO DEAL", "num": "NO DEAL",
     "field": "CLIMATE", "status": "CONFIRMED", "source": "REUTERS",
     "summary": "Climate talks end with no deal; the EU rejects a draft with no fossil fuels.",
     "art": "cop31"},
    {"n": 2, "region": "AF", "place": "BENGHAZI",
     "title": "UKRAINE SINKS RUSSIAN WARSHIP", "value": "2,400 KM",
     "num": "2,400 KM", "field": "CONFLICT", "status": "CONFIRMED",
     "source": "AP",
     "summary": "Sea drones sink the corvette Merkury at a Libyan base, 2,400 km from Ukraine.",
     "art": "merkury"},
    {"n": 3, "region": "EU", "place": "PORTIMÃO",
     "title": "MARQUEZ TAKES 8TH TITLE", "value": "8TH TITLE", "num": "8TH",
     "field": "SPORT", "status": "CONFIRMED", "source": "MOTOGP",
     "summary": "Bezzecchi wins the race; Marquez finishes 8th and clinches his 8th title.",
     "art": "marquez"},
]

# Grid placement order (not numeric order): shuffled so no two
# orthogonal neighbours share a region colour.
GRID = [
    {"n": 4, "region": "AM", "place": "WASHINGTON",
     "title": "DEMOCRATS WIN 258 SEATS", "value": "258 SEATS", "num": "258",
     "field": "POLITICS", "status": "CONFIRMED", "source": "AP",
     "summary": "Largest House majority since 1992.", "art": "democrats"},
    {"n": 5, "region": "ME", "place": "MANAMA",
     "title": "IRAN STRIKES BAHRAIN", "value": "2 HURT", "num": "2",
     "field": "CONFLICT", "status": "CONFIRMED", "source": "REUTERS",
     "summary": "Bahrain says two were hurt; Gulf condemns.", "art": "bahrain"},
    {"n": 6, "region": "EU", "place": "DYMER",
     "title": "DRONE HITS FLATS NEAR KYIV", "value": "3 DEAD, 14 TRAPPED",
     "num": "14", "field": "CONFLICT", "status": "CONFIRMED", "source": "AP",
     "summary": "A Russian drone strikes a five-storey block.", "art": "dymer"},
    {"n": 11, "region": "EU", "place": "LUBLIN",
     "title": "MISSILES IN POLAND WERE RUSSIAN", "value": "3 KH-101",
     "num": "3", "field": "SECURITY", "status": "CONFIRMED",
     "source": "AL JAZEERA",
     "summary": "Prosecutors: all three were Kh-101s.", "art": "poland"},
    {"n": 7, "region": "AF", "place": "BAYELSA",
     "title": "BOAT CAPSIZES, 24 DEAD", "value": "24 DEAD", "num": "24",
     "field": "DISASTER", "status": "CONFIRMED", "source": "REUTERS",
     "summary": "Boat carrying mourners capsizes; 24 dead.", "art": "nigeria"},
    {"n": 9, "region": "AM", "place": "TUPANCIRETÃ",
     "title": "STORM TOLL RISES TO 5", "value": "5 DEAD", "num": "5",
     "field": "DISASTER", "status": "CONFIRMED", "source": "AFP",
     "summary": "Storm toll rises: 5 dead, 250+ hurt.", "art": "brazil"},
    {"n": 8, "region": "ME", "place": "HORMUZ",
     "title": "TANKERS HIT NEAR HORMUZ", "value": "2 TANKERS", "num": "2",
     "field": "ENERGY", "status": "REPORTED", "source": "AL ARABIYA",
     "summary": "Iran says two supertankers hit mines.", "art": "hormuz"},
    {"n": 10, "region": "AS", "place": "SEOUL",
     "title": "MINISTER QUITS OVER AI CHEATING", "value": "111 CASES",
     "num": "111", "field": "EDUCATION", "status": "CONFIRMED",
     "source": "REUTERS",
     "summary": "Minister quits after AI exam cheating.", "art": "seoul"},
    {"n": 13, "region": "EU", "place": "LIVERPOOL",
     "title": "LIVERPOOL 4–0 MAN UTD", "value": "4–0", "num": "4–0",
     "field": "SPORT", "status": "CONFIRMED", "source": "NBC SPORTS",
     "summary": "Liverpool rout Manchester United 4–0.", "art": "liverpool"},
    {"n": 14, "region": "AS", "place": "CIKANDE",
     "title": "FACTORY FIRE, 36 MISSING", "value": "36 MISSING", "num": "36",
     "field": "DISASTER", "status": "CONFIRMED", "source": "AP / REUTERS",
     "summary": "Fire at a factory; 36 people missing.", "art": "cikande"},
    {"n": 12, "region": "WORLD", "place": "MERCURY",
     "title": "BEPICOLOMBO REACHES MERCURY", "value": "ORBIT", "num": "7 YRS",
     "field": "SPACE", "status": "CONFIRMED", "source": "ESA / REUTERS",
     "summary": "Probe enters orbit after seven years.", "art": "bepi"},
]

# Briefs 15-41, one line each. city = bold brick, then one fact, then
# the source; REPORTED briefs carry a "· REPORTED" suffix in blue.
BRIEFS = [
    {"n": 15, "region": "ME", "city": "WEST BANK",
     "fact": "Settlers torch 12 vehicles", "source": "AP", "status": "CONFIRMED"},
    {"n": 16, "region": "AF", "city": "KHARTOUM",
     "fact": "Drone attack kills 4", "source": "AFP", "status": "CONFIRMED"},
    {"n": 17, "region": "AM", "city": "KANSAS CITY",
     "fact": "Chiefs beat Cardinals 34–7", "source": "SPORTRADAR", "status": "CONFIRMED"},
    {"n": 18, "region": "AM", "city": "ASUNCIÓN",
     "fact": "Boca beat Atlético Mineiro 2–0, Copa Sudamericana",
     "source": "LIVESCORE", "status": "CONFIRMED"},
    {"n": 19, "region": "AS", "city": "LAHORE",
     "fact": "Air quality passes 500 AQI", "source": "WIRES", "status": "CONFIRMED"},
    {"n": 20, "region": "AS", "city": "WELLINGTON",
     "fact": "India pile up 720/9 against New Zealand", "source": "LIVESCORE",
     "status": "CONFIRMED"},
    {"n": 21, "region": "EU", "city": "GULF OF FINLAND",
     "fact": "Russian ship Sparta II still smouldering", "source": "REUTERS",
     "status": "REPORTED"},
    {"n": 22, "region": "ME", "city": "GAZA",
     "fact": "IDF strike leaves 1 critically hurt", "source": "WIRES",
     "status": "CONFIRMED"},
    {"n": 23, "region": "ME", "city": "BEIRUT",
     "fact": "Lebanon arrests 3, seizes 264 kg of explosives", "source": "AFP",
     "status": "CONFIRMED"},
    {"n": 24, "region": "EU", "city": "WARSAW",
     "fact": "Russia twice tried to kill a rapper; Denmark expels official",
     "source": "AP", "status": "CONFIRMED"},
    {"n": 25, "region": "OC", "city": "RUATŌRIA",
     "fact": "House slips: 1 dead, 4 hurt", "source": "NZ POLICE",
     "status": "CONFIRMED"},
    {"n": 26, "region": "AM", "city": "NFL",
     "fact": "Cowboys 51–30 Titans; Panthers 35–33 Ravens", "source": "REUTERS",
     "status": "CONFIRMED"},
    {"n": 27, "region": "EU", "city": "VILLARREAL",
     "fact": "Barcelona come back from 2–0 down, win 3–2", "source": "SPORTRADAR",
     "status": "CONFIRMED"},
    {"n": 28, "region": "OC", "city": "SYDNEY",
     "fact": "Australian dollar rebounds against NZ dollar", "source": "BLOOMBERG",
     "status": "CONFIRMED"},
    {"n": 29, "region": "ME", "city": "RABIGH",
     "fact": "Houthis claim direct hit on Saudi refinery", "source": "HOUTHIS",
     "status": "REPORTED"},
    {"n": 30, "region": "AM", "city": "LAS VEGAS",
     "fact": "Verstappen wins chaotic Grand Prix, 35 lead changes",
     "source": "F1", "status": "CONFIRMED"},
    {"n": 31, "region": "AM", "city": "SAN ANTONIO",
     "fact": "Wembanyama: 50 points, 19 rebounds, Spurs win 114–91",
     "source": "AP", "status": "CONFIRMED"},
    {"n": 32, "region": "AM", "city": "KANSAS CITY",
     "fact": "Current win first NWSL title, 2–1", "source": "AP",
     "status": "CONFIRMED"},
    {"n": 33, "region": "EU", "city": "KYIV",
     "fact": "Zelensky: Russia launched 2,700 drones in a week", "source": "AP",
     "status": "CONFIRMED"},
    {"n": 34, "region": "ME", "city": "JERUSALEM",
     "fact": "Eisenkot–Likud unity talks end after 4 hours, no deal",
     "source": "AP", "status": "CONFIRMED"},
    {"n": 35, "region": "EU", "city": "VILNIUS",
     "fact": "Germany tests kamikaze drones, AI targeting near Belarus",
     "source": "AP", "status": "CONFIRMED"},
    {"n": 36, "region": "AF", "city": "NAIROBI",
     "fact": "Kenya and DR Congo restore full diplomatic ties", "source": "AP",
     "status": "CONFIRMED"},
    {"n": 37, "region": "WORLD", "city": "SPACE",
     "fact": "Earth has a temporary mini-moon: asteroid 2026 QQ8, 2 m wide",
     "source": "WIRES", "status": "CONFIRMED"},
    {"n": 38, "region": "AF", "city": "JOHANNESBURG",
     "fact": "ANC–ActionSA agree: Mashaba for mayor",
     "source": "WIRES", "status": "REPORTED"},
    {"n": 39, "region": "ME", "city": "TEHRAN",
     "fact": "Iran shows dual missile launcher, new missile city",
     "source": "WIRES", "status": "REPORTED"},
    {"n": 40, "region": "ME", "city": "BEIRUT",
     "fact": "Aoun: Israel must withdraw; all weapons under the state",
     "source": "WIRES", "status": "REPORTED"},
    {"n": 41, "region": "AS", "city": "NEW DELHI",
     "fact": "Nepal's prime minister visits Delhi", "source": "MEA",
     "status": "CONFIRMED"},
]

PANEL = [("258", "House seats, Democrats"),
         ("2,700", "drones in a week, Russia"),
         ("720/9", "India's record Test total"),
         ("50", "Wembanyama points, Spurs")]

REGION_COUNTS = {"EU": 9, "ME": 9, "AM": 8, "AS": 5, "AF": 5, "OC": 2,
                 "WORLD": 3}

DATECHECK = ("DATE CHECK — Nigeria boat capsized Friday; toll of 24 confirmed "
             "Sunday. Brazil storm was Friday; 5 dead is Sunday's update. "
             "Poland missiles fell Friday; identified Sunday. F1, NBA and "
             "NWSL finals were Saturday night in the US — Sunday in Jakarta.")
NOTSHOWN = ("NOT SHOWN: ICJ Rohingya ruling (19 Nov), UK–EU reset (20 Nov), "
            "GTA VI $3.79bn (20 Nov) — not 22 November news.")
HOWCHECKED = ("HOW WE CHECKED — Every story dated 22 Nov 2026 from primary "
              "reporting; REPORTED = one source's claim. Sources: Reuters · "
              "AP · AFP · ESA · UN · MotoGP.com.")

# ---------------------------------------------------------------- illustrations
# Every painter fills its box (x0, y0, x1, y1) with flat solid shapes and
# then bakes the story's number in as a paper chip at the bottom-left —
# drawn last, so the number can never be covered by the scene. No human
# figures at all (no stick figures, no ambiguous people): the Marquez
# card shows the bike, the track and the flag, never a rider.

def big_num(draw, box, st, size=24):
    """Paper chip with the story's number, bottom-left of the box."""
    x0, y0, x1, y1 = box
    w = x1 - x0
    s = st["num"]
    while size > 12 and text_w(draw, s, F_SANSB(size)) > 0.52 * w:
        size -= 2
    f = F_SANSB(size)
    tw = text_w(draw, s, f)
    ch, cw = size + 12, tw + 18
    cx, cy = x0 + 6, y1 - 6 - ch
    draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=4,
                           fill=PAPER, outline=REGION[st["region"]], width=2)
    col = BRICK if s == "NO DEAL" else INK
    draw.text((cx + 9, cy + 5), s, font=f, fill=col)


def _flag(draw, x, y, w, h, colors):
    n = len(colors)
    for i, c in enumerate(colors):
        draw.rectangle([x, y + i * h // n, x + w, y + (i + 1) * h // n], fill=c)


def paint_cop31(draw, box, st):
    # Lead band: wide, short (306x45). Flags top, draft document
    # bottom-right with a red X, chip bottom-left.
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(24, 45, 75))
    draw.rectangle([x0, y1 - 8, x1, y1], fill=(60, 70, 60))
    import math
    for fx, cols in ((x0 + 16, None), (x1 - 52, "TR")):
        fw, fh = 30, 19
        draw.line([fx + fw // 2, y0 + 4, fx + fw // 2, y0 + 4 + fh + 12],
                  fill=(200, 200, 200), width=2)
        if cols is None:
            draw.rectangle([fx, y0 + 4, fx + fw, y0 + 4 + fh], fill=(0, 51, 153))
            for i in range(6):
                ang = i * 60
                cx = fx + fw // 2 + int(6 * math.cos(math.radians(ang)))
                cy = y0 + 4 + fh // 2 + int(6 * math.sin(math.radians(ang)))
                draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 204, 0))
        else:
            draw.rectangle([fx, y0 + 4, fx + fw, y0 + 4 + fh], fill=(227, 10, 23))
            draw.ellipse([fx + 12, y0 + 8, fx + 19, y0 + 15], fill=WHITE)
    dx = x0 + int(w * 0.60)
    dw, dh = int(w * 0.34), 22
    dy = y1 - dh - 4
    draw.rectangle([dx, dy, dx + dw, dy + dh], fill=WHITE)
    draw.rectangle([dx, dy, dx + dw, dy + dh], outline=(150, 150, 150), width=1)
    for i in range(2):
        draw.line([dx + 8, dy + 6 + i * 6, dx + dw - 26, dy + 6 + i * 6],
                  fill=(120, 120, 120), width=1)
    draw.line([dx + dw - 20, dy + 4, dx + dw - 6, dy + dh - 4], fill=BRICK, width=3)
    draw.line([dx + dw - 6, dy + 4, dx + dw - 20, dy + dh - 4], fill=BRICK, width=3)
    big_num(draw, box, st, size=20)


def paint_merkury(draw, box, st):
    # Night sea, warship on the right, explosion above it, drone upper
    # right; bottom-left kept clear for the "2,400 KM" chip.
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(16, 26, 46))
    for sx, sy in [(0.08, 0.15), (0.20, 0.08), (0.35, 0.18), (0.48, 0.10)]:
        draw.ellipse([x0 + w * sx - 1, y0 + h * sy - 1,
                      x0 + w * sx + 1, y0 + h * sy + 1], fill=WHITE)
    draw.rectangle([x0, y0 + int(h * 0.55), x1, y1], fill=(24, 48, 72))
    for wy in (0.62, 0.78, 0.90):
        draw.line([x0 + 8, y0 + h * wy, x1 - 8, y0 + h * wy],
                  fill=(90, 130, 160), width=1)
    hx = x0 + int(w * 0.52)
    hw = int(w * 0.42)
    hy = y0 + int(h * 0.52)
    draw.polygon([(hx, hy), (hx + hw, hy), (hx + hw - 8, y1 - 2),
                  (hx + 6, y1 - 2)], fill=(95, 105, 120))
    draw.rectangle([hx + int(hw * 0.30), hy - 12, hx + int(hw * 0.62),
                    hy], fill=(75, 85, 100))
    draw.line([hx + int(hw * 0.45), hy - 26, hx + int(hw * 0.45), hy - 12],
              fill=(150, 160, 175), width=2)
    ex, ey = hx + int(hw * 0.55), hy - 14
    import math
    for ang in range(0, 360, 45):
        x2 = ex + int(11 * math.cos(math.radians(ang)))
        y2 = ey + int(11 * math.sin(math.radians(ang)))
        draw.line([ex, ey, x2, y2], fill=(255, 140, 40), width=3)
    draw.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 220, 90))
    dx, dy = x1 - 34, y0 + 10
    draw.line([dx - 8, dy, dx + 8, dy], fill=(180, 190, 205), width=2)
    draw.line([dx, dy - 5, dx, dy + 5], fill=(180, 190, 205), width=2)
    draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 80, 60))
    draw.line([dx - 4, dy + 4, dx - 16, dy + 12], fill=(150, 160, 190), width=1)
    big_num(draw, box, st, size=20)


def paint_marquez(draw, box, st):
    # Circuit: grandstand top, asphalt band, BIG bike silhouette (no
    # rider), big checkered flag far right; bottom-left kept clear.
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(205, 210, 205))
    for i in range(6):
        draw.rectangle([x0 + 10 + i * 14, y0 + 5, x0 + 20 + i * 14, y0 + 12],
                       fill=(120, 130, 140) if i % 2 else (90, 100, 110))
    draw.rectangle([x0, y0 + int(h * 0.42), x1, y1], fill=(52, 52, 58))
    for i in range(9):
        lx = x0 + 6 + i * (w - 12) // 9
        draw.line([lx, y0 + int(h * 0.68), lx + 10, y0 + int(h * 0.68)],
                  fill=WHITE, width=2)
    bx, by = x0 + int(w * 0.52), y0 + int(h * 0.66)
    for wx in (bx - 20, bx + 20):
        draw.ellipse([wx - 9, by - 9, wx + 9, by + 9], fill=(25, 25, 25),
                     outline=WHITE, width=3)
    draw.line([bx - 20, by, bx + 20, by], fill=(25, 25, 25), width=4)
    draw.line([bx - 2, by, bx + 8, by - 15], fill=(25, 25, 25), width=4)
    draw.line([bx + 8, by - 15, bx + 17, by], fill=(25, 25, 25), width=4)
    draw.polygon([(bx + 2, by - 19), (bx + 16, by - 19), (bx + 11, by - 8),
                  (bx + 4, by - 8)], fill=(200, 40, 40))
    draw.line([bx - 20, by - 2, bx - 8, by - 12], fill=(200, 40, 40), width=3)
    fx = x1 - 36
    draw.line([fx, y0 + 4, fx, y0 + 36], fill=(80, 70, 60), width=2)
    for r in range(3):
        for c in range(4):
            col = INK if (r + c) % 2 == 0 else WHITE
            draw.rectangle([fx + 2 + c * 7, y0 + 4 + r * 7,
                            fx + 9 + c * 7, y0 + 11 + r * 7], fill=col)
    big_num(draw, box, st, size=20)


def paint_bahrain(draw, box, st):
    # Compact night city: lit block, drone upper right with small rings.
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(30, 32, 48))
    for sx, sy in [(0.12, 0.15), (0.30, 0.08), (0.55, 0.12), (0.80, 0.07)]:
        draw.ellipse([x0 + w * sx - 1, y0 + h * sy - 1,
                      x0 + w * sx + 1, y0 + h * sy + 1], fill=WHITE)
    bx = x0 + int(w * 0.34)
    bw, by, bh = int(w * 0.42), y0 + int(h * 0.42), int(h * 0.58)
    draw.rectangle([bx, by, bx + bw, y1], fill=(70, 75, 95))
    draw.rectangle([bx, by, bx + bw, by + 5], fill=(50, 55, 75))
    for r in range(3):
        for c in range(4):
            wx = bx + 7 + c * (bw - 14) // 4
            wy = by + 12 + r * (bh - 18) // 3
            draw.rectangle([wx, wy, wx + 6, wy + 8],
                           fill=(255, 210, 90) if (r + c) % 3 else (40, 45, 65))
    dx, dy = x1 - 22, y0 + 16
    draw.line([dx, dy, dx - 14, dy + 10], fill=(150, 160, 190), width=2)
    draw.ellipse([dx - 9, dy - 4, dx + 9, dy + 4], fill=(150, 160, 190))
    for r in (10, 16):
        draw.arc([dx - r, dy - r, dx + r, dy + r], start=180, end=270,
                 fill=(255, 210, 90), width=2)
    fx, fy = bx + bw - 8, by - 4
    draw.polygon([(fx, fy), (fx - 6, fy + 10), (fx + 6, fy + 10)],
                 fill=(255, 140, 40))
    big_num(draw, box, st, size=18)


def paint_dymer(draw, box, st):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(36, 40, 52))
    for sx, sy in [(0.1, 0.12), (0.3, 0.06), (0.6, 0.14), (0.85, 0.08)]:
        draw.ellipse([x0 + w * sx - 1, y0 + h * sy - 1,
                      x0 + w * sx + 1, y0 + h * sy + 1], fill=WHITE)
    draw.polygon([(x1 - 8, y0 + 4), (x1 - 30, y0 + 4),
                  (x0 + w * 0.25, y1 - 6), (x0 + w * 0.45, y1 - 6)],
                 fill=(240, 225, 160))
    bx = x0 + int(w * 0.30)
    by, bw, bh = y0 + int(h * 0.22), int(w * 0.52), int(h * 0.62)
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(90, 85, 80))
    draw.rectangle([bx, by, bx + bw, by + 5], fill=(60, 56, 52))
    draw.rectangle([bx + bw // 2 - 10, by + 10, bx + bw // 2 + 12, by + 34],
                   fill=(20, 18, 16))
    for r in range(3):
        for c in range(4):
            wx = bx + 8 + c * (bw - 16) // 4
            wy = by + 8 + r * (bh - 16) // 3
            if (r, c) in ((0, 1), (0, 2), (1, 1)):
                continue
            draw.rectangle([wx, wy, wx + 8, wy + 9],
                           fill=(255, 210, 90) if (r + c) % 2 else (55, 52, 48))
    for i, (rx, rw) in enumerate([(0.30, 14), (0.42, 10), (0.52, 16)]):
        draw.polygon([(x0 + w * rx, y1 - 4), (x0 + w * rx + rw // 2, y1 - 12),
                      (x0 + w * rx + rw, y1 - 4)], fill=(60, 56, 52))
    big_num(draw, box, st, size=18)


def paint_bepi(draw, box, st):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(12, 14, 28))
    for sx, sy in [(0.08, 0.1), (0.2, 0.25), (0.35, 0.08), (0.55, 0.15),
                   (0.7, 0.06), (0.88, 0.2), (0.95, 0.35)]:
        draw.ellipse([x0 + w * sx - 1, y0 + h * sy - 1,
                      x0 + w * sx + 1, y0 + h * sy + 1], fill=WHITE)
    draw.arc([x0 + w * 0.05, y0 + h * 0.1, x1 - w * 0.05, y1 - h * 0.1],
             start=200, end=340, fill=(120, 140, 180), width=2)
    r = min(18, int(h * 0.28))
    cx, cy = x1 - r - 8, y1 - r - 6
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 170, 120))
    draw.ellipse([cx - r // 2, cy - r // 3, cx - r // 4, cy], fill=(170, 140, 95))
    sx, sy = x0 + int(w * 0.30), y0 + int(h * 0.30)
    draw.rectangle([sx - 14, sy - 4, sx - 4, sy + 4], fill=(120, 140, 170))
    draw.rectangle([sx + 4, sy - 4, sx + 14, sy + 4], fill=(120, 140, 170))
    draw.rectangle([sx - 6, sy - 8, sx + 6, sy + 8], fill=(180, 190, 200))
    draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 210, 90))
    bx, by = x0 + int(w * 0.58), y0 + int(h * 0.45)
    draw.polygon([(bx, by), (bx + 8, by + 10), (bx, by + 20), (bx + 8, by + 30)],
                 fill=(255, 210, 90))
    big_num(draw, box, st, size=18)


def paint_cikande(draw, box, st):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    for i, c in enumerate([(70, 45, 35), (90, 55, 40), (110, 65, 45)]):
        draw.rectangle([x0, y0 + i * h // 3, x1, y0 + (i + 1) * h // 3], fill=c)
    fy = y0 + int(h * 0.55)
    for sx, sy, sr in [(0.35, 6, 7), (0.55, 12, 9), (0.75, 18, 11)]:
        draw.ellipse([x0 + w * sx - sr, fy - sy - sr, x0 + w * sx + sr,
                      fy - sy + sr], fill=(120, 110, 105))
    draw.rectangle([x0, fy, x1, y1], fill=(40, 32, 28))
    for i in range(6):
        tx = x0 + i * w // 6
        draw.polygon([(tx, fy), (tx + w // 12, fy - 8), (tx + w // 6, fy)],
                     fill=(55, 45, 40))
    for i in range(5):
        wx = x0 + 10 + i * (w - 20) // 5
        draw.rectangle([wx, fy + 8, wx + 12, fy + 18],
                       fill=(255, 150, 50) if i % 2 else (60, 50, 45))
    fx = x1 - int(w * 0.25)
    draw.polygon([(fx, fy - int(h * 0.22)), (fx - 10, fy), (fx + 10, fy)],
                 fill=(255, 140, 40))
    draw.polygon([(fx, fy - int(h * 0.12)), (fx - 5, fy), (fx + 5, fy)],
                 fill=(255, 220, 90))
    big_num(draw, box, st, size=18)


def paint_liverpool(draw, box, st):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    for i in range(5):
        c = (34, 120, 60) if i % 2 == 0 else (28, 100, 52)
        draw.rectangle([x0, y0 + i * h // 5, x1, y0 + (i + 1) * h // 5], fill=c)
    gx = x1 - int(w * 0.30)
    gy, gw, gh = y0 + int(h * 0.28), int(w * 0.26), int(h * 0.44)
    draw.rectangle([gx, gy, gx + gw, gy + gh], outline=WHITE, width=3)
    for i in range(1, 4):
        draw.line([gx + i * gw // 4, gy, gx + i * gw // 4, gy + gh],
                  fill=WHITE, width=1)
    for i in range(1, 3):
        draw.line([gx, gy + i * gh // 3, gx + gw, gy + i * gh // 3],
                  fill=WHITE, width=1)
    bx, by = x0 + int(w * 0.62), y0 + int(h * 0.68)
    draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=WHITE)
    draw.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=INK)
    big_num(draw, box, st, size=18)


def paint_democrats(draw, box, st):
    # Capitol dome + ballot box.
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(205, 212, 222))
    draw.rectangle([x0, y1 - 8, x1, y1], fill=(120, 130, 145))
    cx = x0 + w // 2
    draw.ellipse([cx - 16, y0 + 8, cx + 16, y0 + 30], fill=(235, 230, 210))
    draw.rectangle([cx - 18, y0 + 26, cx + 18, y0 + 34], fill=(235, 230, 210))
    for i in range(5):
        px = x0 + 12 + i * (w - 24) // 5
        draw.rectangle([px, y0 + 36, px + 6, y0 + 56], fill=(245, 242, 228))
    draw.rectangle([x0 + 8, y0 + 56, x1 - 8, y0 + 62], fill=(225, 220, 205))
    bx, by = x1 - 30, y1 - 26
    draw.rectangle([bx, by, bx + 22, by + 18], fill=(180, 60, 50))
    draw.rectangle([bx + 4, by - 8, bx + 18, by], fill=WHITE)
    draw.line([bx + 4, by - 8, bx + 18, by - 8], fill=BRICK, width=2)
    draw.rectangle([x0 + 8, y0 + 62, x1 - 8, y1 - 8], fill=(150, 160, 175))
    big_num(draw, box, st, size=18)


def paint_nigeria(draw, box, st):
    # River, capsized hull, waves, buoy.
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(170, 200, 215))
    draw.rectangle([x0, y0 + int(h * 0.45), x1, y1], fill=(60, 130, 150))
    for wy in (0.55, 0.72, 0.88):
        for wx in (0.15, 0.45, 0.75):
            draw.arc([x0 + w * wx - 10, y0 + h * wy - 5,
                      x0 + w * wx + 10, y0 + h * wy + 5],
                     start=180, end=360, fill=(220, 240, 245), width=2)
    cx, cy = x0 + int(w * 0.58), y0 + int(h * 0.50)
    draw.pieslice([cx - 22, cy - 8, cx + 22, cy + 14], start=180, end=360,
                  fill=(120, 85, 55))
    draw.rectangle([cx - 22, cy - 2, cx + 22, cy + 4], fill=(90, 60, 40))
    draw.ellipse([x0 + int(w * 0.16) - 5, y0 + int(h * 0.62) - 5,
                  x0 + int(w * 0.16) + 5, y0 + int(h * 0.62) + 5],
                 fill=(255, 140, 40))
    big_num(draw, box, st, size=18)


def paint_hormuz(draw, box, st):
    # Dusk sea, two tankers, a mine between them.
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(40, 50, 70))
    draw.ellipse([x1 - 16, y0 + 6, x1 - 4, y0 + 18], fill=(240, 200, 120))
    draw.rectangle([x0, y0 + int(h * 0.55), x1, y1], fill=(30, 60, 80))
    for tx, tw in ((0.06, 0.40), (0.54, 0.40)):
        hx = x0 + int(w * tx)
        hw = int(w * tw)
        hy = y0 + int(h * 0.62)
        draw.rectangle([hx, hy, hx + hw, hy + 12], fill=(120, 125, 135))
        draw.rectangle([hx, hy + 12, hx + hw, hy + 14], fill=(180, 60, 50))
        draw.rectangle([hx + int(hw * 0.55), hy - 10, hx + int(hw * 0.75),
                        hy], fill=(220, 225, 230))
    mx, my = x0 + int(w * 0.50), y0 + int(h * 0.52)
    import math
    for ang in range(0, 360, 45):
        x2 = mx + int(7 * math.cos(math.radians(ang)))
        y2 = my + int(7 * math.sin(math.radians(ang)))
        draw.line([mx, my, x2, y2], fill=INK, width=2)
    draw.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill=INK)
    big_num(draw, box, st, size=18)


def paint_brazil(draw, box, st):
    # Storm clouds, lightning, small houses below.
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(60, 65, 75))
    for cx, cy, cr in [(0.30, 0.20, 16), (0.55, 0.14, 19), (0.78, 0.22, 15)]:
        draw.ellipse([x0 + w * cx - cr, y0 + h * cy - cr // 2,
                      x0 + w * cx + cr, y0 + h * cy + cr // 2],
                     fill=(45, 48, 58))
    lx, ly = x0 + int(w * 0.55), y0 + int(h * 0.30)
    draw.polygon([(lx, ly), (lx - 6, ly + 16), (lx + 1, ly + 16),
                  (lx - 4, ly + 30), (lx + 7, ly + 12), (lx + 1, ly + 12)],
                 fill=(255, 220, 90))
    for i in range(5):
        rx = x0 + 8 + i * 12
        draw.line([rx, y0 + int(h * 0.40), rx - 4, y0 + int(h * 0.55)],
                  fill=(150, 160, 175), width=1)
    for hx, hw in ((0.12, 0.22), (0.42, 0.20), (0.70, 0.22)):
        hx0 = x0 + int(w * hx)
        hw0 = int(w * hw)
        by = y1 - 8
        draw.rectangle([hx0, by - 16, hx0 + hw0, by], fill=(200, 180, 150))
        draw.polygon([(hx0 - 2, by - 16), (hx0 + hw0 // 2, by - 26),
                      (hx0 + hw0 + 2, by - 16)], fill=(170, 70, 50))
    big_num(draw, box, st, size=18)


def paint_seoul(draw, box, st):
    # University block + exam paper with a red stamp.
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(200, 210, 220))
    draw.rectangle([x0 + 8, y0 + 8, x1 - 8, y0 + 34], fill=(110, 125, 145))
    for r in range(1):
        for c in range(5):
            wx = x0 + 14 + c * (w - 28) // 5
            draw.rectangle([wx, y0 + 14, wx + 8, y0 + 24],
                           fill=(255, 220, 130) if c % 2 else (60, 70, 85))
    draw.rectangle([x0 + 8, y0 + 34, x1 - 8, y0 + 38], fill=(90, 105, 125))
    px, py = x0 + int(w * 0.28), y0 + int(h * 0.44)
    pw, ph = int(w * 0.44), int(h * 0.42)
    draw.rectangle([px, py, px + pw, py + ph], fill=WHITE)
    draw.rectangle([px, py, px + pw, py + ph], outline=(150, 150, 150), width=1)
    for i in range(3):
        draw.line([px + 6, py + 8 + i * 8, px + pw - 6, py + 8 + i * 8],
                  fill=(120, 120, 120), width=1)
    draw.ellipse([px + pw - 16, py + ph - 16, px + pw - 4, py + ph - 4],
                 outline=BRICK, width=2)
    draw.rectangle([x0, y1 - 6, x1, y1], fill=(80, 120, 70))
    big_num(draw, box, st, size=18)


def paint_poland(draw, box, st):
    # Night sky, three missiles with flames.
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(20, 25, 40))
    for sx, sy in [(0.10, 0.12), (0.30, 0.06), (0.55, 0.15), (0.80, 0.08),
                   (0.92, 0.25)]:
        draw.ellipse([x0 + w * sx - 1, y0 + h * sy - 1,
                      x0 + w * sx + 1, y0 + h * sy + 1], fill=WHITE)
    for mx, my, ang in ((0.25, 0.30, -30), (0.55, 0.45, -30), (0.80, 0.28, -30)):
        cx, cy = x0 + w * mx, y0 + h * my
        draw.line([cx - 12, cy + 7, cx + 12, cy - 7], fill=(170, 180, 195),
                  width=5)
        draw.polygon([(cx + 12, cy - 7), (cx + 18, cy - 10), (cx + 14, cy - 2)],
                     fill=(140, 150, 165))
        draw.polygon([(cx - 12, cy + 7), (cx - 18, cy + 12), (cx - 14, cy + 2)],
                     fill=(255, 140, 40))
        draw.polygon([(cx - 16, cy + 10), (cx - 20, cy + 14), (cx - 12, cy + 12)],
                     fill=(255, 220, 90))
    draw.rectangle([x0, y1 - 6, x1, y1], fill=(50, 55, 65))
    big_num(draw, box, st, size=18)


PAINTERS = {"cop31": paint_cop31, "merkury": paint_merkury,
            "marquez": paint_marquez, "bahrain": paint_bahrain,
            "dymer": paint_dymer, "bepi": paint_bepi,
            "cikande": paint_cikande, "liverpool": paint_liverpool,
            "democrats": paint_democrats, "nigeria": paint_nigeria,
            "hormuz": paint_hormuz, "brazil": paint_brazil,
            "seoul": paint_seoul, "poland": paint_poland}

# ---------------------------------------------------------------- layout
MX, GUT = 16, 13
CW = W - 2 * MX  # 992 content width
MAST_H = 84
LEAD_Y, LEAD_H = 90, 172
GRID_Y = 270
GRID_CARD_H, GRID_GAP_Y = 108, 8
MORE_Y, MORE_H = 734, 186
FOOT_Y = 924


def status_color(s):
    return {"CONFIRMED": (47, 107, 79), "REPORTED": (51, 86, 127),
            "CLAIM": (166, 58, 43)}[s]


def draw_banner(draw, x0, y0, x1, st, value_size):
    """Top band: number badge + NEWS VALUE + white source chip."""
    rc = REGION[st["region"]]
    y1 = y0 + 25 if value_size < 20 else y0 + 26
    draw.rectangle([x0, y0, x1, y1], fill=rc)
    d = 17 if value_size < 20 else 18
    cx, cy = x0 + 5 + d // 2, y0 + (y1 - y0) // 2
    draw.ellipse([cx - d // 2, cy - d // 2, cx + d // 2, cy + d // 2],
                 fill=WHITE)
    fnum = F_SANSB(11 if value_size < 20 else 12)
    num = str(st["n"])
    nw = text_w(draw, num, fnum)
    draw.text((cx - nw / 2, cy - (11 if value_size < 20 else 12) / 2 - 1),
              num, font=fnum, fill=rc)
    fv = F_SANSB(value_size)
    vx = x0 + 5 + d + 7
    draw.text((vx, y0 + (y1 - y0) / 2 - value_size / 2 - 1),
              st["value"], font=fv, fill=WHITE)
    # White chip: source only.
    fs = F_SANSB(8)
    src = st["source"]
    tw = text_w(draw, src, fs) + 12
    tx = x1 - tw - 5
    draw.rounded_rectangle([tx, y0 + 4, tx + tw, y1 - 4], radius=3, fill=WHITE)
    draw.text((tx + 6, y0 + (y1 - y0) / 2 - 5), src, font=fs, fill=INK)
    assert text_w(draw, st["value"], fv) + (vx - x0) + tw + 12 <= (x1 - x0), \
        "banner overflow: " + st["value"]
    return y1


def draw_kicker(draw, x, y, st, max_w):
    fk = F_SANSB(9)
    s = REGION_NAME[st["region"]] + " · " + st["field"] + " — " + st["status"]
    assert text_w(draw, s, fk) <= max_w, "kicker overflow: " + s
    draw.text((x, y), s, font=fk, fill=status_color(st["status"]))
    return y + 10


def draw_lead_card(draw, x0, y0, w, h, st):
    x1, y1 = x0 + w, y0 + h
    bg = tint(REGION[st["region"]], 0.88)
    draw.rectangle([x0, y0, x1, y1], fill=bg)
    draw.rectangle([x0, y0, x1, y1], outline=LIGHT_LINE, width=1)
    by1 = draw_banner(draw, x0, y0, x1, st, 20)
    PAINTERS[st["art"]](draw, (x0, by1, x1, by1 + 45), st)
    ty = by1 + 45
    ty = draw_kicker(draw, x0 + 8, ty + 1, st, w - 16)
    tf = F_SANSB(26)
    tlines = fit_lines(draw, st["title"], tf, w - 16, 2)
    for i, ln in enumerate(tlines):
        draw.text((x0 + 8, ty + i * 27), ln, font=tf, fill=INK)
    ty += len(tlines) * 27
    sf = F_SANS(15)
    slines = fit_lines(draw, st["summary"], sf, w - 16, 2)
    assert len(slines) <= 2, "lead summary over 2 lines: " + st["summary"]
    for i, ln in enumerate(slines):
        draw.text((x0 + 8, ty + i * 17), ln, font=sf, fill=(60, 60, 60))
    ty += len(slines) * 17
    assert ty <= y1, "lead card overflow: %s ends %d > %d" % (st["title"], ty, y1)


def draw_grid_card(draw, x0, y0, w, h, st):
    x1, y1 = x0 + w, y0 + h
    bg = tint(REGION[st["region"]], 0.86)
    draw.rectangle([x0, y0, x1, y1], fill=bg)
    draw.rectangle([x0, y0, x1, y1], outline=LIGHT_LINE, width=1)
    by1 = draw_banner(draw, x0, y0, x1, st, 16)
    PAINTERS[st["art"]](draw, (x0, by1, x0 + 92, y1), st)
    tx = x0 + 100
    tw = x1 - 8 - tx
    ty = draw_kicker(draw, tx, by1 + 1, st, tw)
    tf = F_SANSB(18)
    tlines = fit_lines(draw, st["title"], tf, tw, 2)
    for i, ln in enumerate(tlines):
        draw.text((tx, ty + i * 20), ln, font=tf, fill=INK)
    ty += len(tlines) * 20
    sf = F_SANS(15)
    slines = fit_lines(draw, st["summary"], sf, tw, 2)
    assert len(slines) <= 2, "grid summary over 2 lines: " + st["summary"]
    for i, ln in enumerate(slines):
        draw.text((tx, ty + i * 16), ln, font=sf, fill=(60, 60, 60))
    ty += len(slines) * 16
    assert ty <= y1, "grid card overflow: %s ends %d > %d" % (st["title"], ty, y1)


def draw_panel(draw, x0, y0, w, h):
    x1, y1 = x0 + w, y0 + h
    draw.rectangle([x0, y0, x1, y1], fill=NAVY)
    draw.rectangle([x0, y0, x1, y1], outline=LIGHT_LINE, width=1)
    draw.text((x0 + 10, y0 + 8), "THE DAY IN NUMBERS", font=F_SANSB(13),
              fill=YELLOW)
    ry = y0 + 28
    for num, label in PANEL:
        fn = F_SANSB(20)
        draw.text((x0 + 10, ry), num, font=fn, fill=WHITE)
        nw = text_w(draw, num, fn)
        draw.text((x0 + 10 + nw + 8, ry + 6), label, font=F_SANS(10),
                  fill=(200, 210, 225))
        ry += 19
    assert ry <= y1, "panel overflow"


def draw_brief(draw, x, y, max_w, b):
    rc = REGION[b["region"]]
    draw.rectangle([x, y, x + 18, y + 13], fill=rc)
    fn = F_SANSB(9)
    num = str(b["n"])
    draw.text((x + 9 - text_w(draw, num, fn) / 2, y + 1), num, font=fn,
              fill=WHITE)
    tx = x + 22
    fc = F_SANSB(11)
    fr = F_SANS(11)
    fs = F_SANS(10)
    segs = [(b["city"] + " — ", fc, BRICK),
            (b["fact"] + " — ", fr, INK),
            (b["source"], fs, GREY)]
    if b["status"] != "CONFIRMED":
        segs.append((" · " + b["status"], F_SANSB(10), REGION["EU"]))
    total = sum(text_w(draw, s, f) for s, f, _ in segs)
    assert total <= max_w, "brief overflow #%d: %d > %d" % (b["n"], total, max_w)
    cx = tx
    for s, f, col in segs:
        draw.text((cx, y), s, font=f, fill=col)
        cx += text_w(draw, s, f)


# ---------------------------------------------------------------- render
def render(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    # ---- masthead: title biggest, date second biggest
    draw.text((MX, 4), "THE WORLD, CHECKED", font=F_MAST(44), fill=INK)
    draw.text((MX, 52), "SUNDAY 22 NOVEMBER 2026", font=F_MAST(26), fill=BRICK)
    cnt = "41 STORIES · 7 REGIONS"
    draw.text((W - MX - text_w(draw, cnt, F_SANSB(14)), 58), cnt,
              font=F_SANSB(14), fill=INK)
    draw.rectangle([0, MAST_H - 3, W, MAST_H], fill=BRICK)
    # ---- lead band: 3 cards side by side
    lead_w = (CW - 2 * GUT) // 3
    for i, st in enumerate(LEAD):
        draw_lead_card(draw, MX + i * (lead_w + GUT), LEAD_Y, lead_w, LEAD_H, st)
    # ---- grid: 11 cards + numbers panel, 3 cols x 4 rows
    grid_w = (CW - 2 * GUT) // 3
    for idx in range(12):
        r, c = divmod(idx, 3)
        x0 = MX + c * (grid_w + GUT)
        y0 = GRID_Y + r * (GRID_CARD_H + GRID_GAP_Y)
        if idx < len(GRID):
            draw_grid_card(draw, x0, y0, grid_w, GRID_CARD_H, GRID[idx])
        else:
            draw_panel(draw, x0, y0, grid_w, GRID_CARD_H)
    grid_end = GRID_Y + 4 * GRID_CARD_H + 3 * GRID_GAP_Y
    assert grid_end == MORE_Y - 8, "grid/MORE gap mismatch"
    # ---- MORE STORIES: briefs 15-41, 2 columns
    draw.text((MX, MORE_Y), "MORE STORIES", font=F_SANSB(14), fill=NAVY)
    note = "27 MORE · NUMBERED 15–41"
    draw.text((W - MX - text_w(draw, note, F_SANS(11)), MORE_Y + 2), note,
              font=F_SANS(11), fill=GREY)
    col_w = (CW - 16) // 2
    for col in range(2):
        cx = MX + col * (col_w + 16)
        for j, b in enumerate(BRIEFS[col * 14:(col + 1) * 14]):
            draw_brief(draw, cx, MORE_Y + 18 + j * 12, col_w - 22, b)
    more_end = MORE_Y + 18 + 13 * 12 + 11
    assert more_end <= FOOT_Y - 4, "MORE/footer gap mismatch"
    # ---- footer: region strip + DATE CHECK + NOT SHOWN + HOW WE CHECKED
    draw.rectangle([MX, FOOT_Y, W - MX, FOOT_Y + 2], fill=BRICK)
    rx = MX
    for reg in ["EU", "ME", "AM", "AS", "AF", "OC", "WORLD"]:
        label = REGION_NAME[reg] + " " + str(REGION_COUNTS[reg])
        draw.rectangle([rx, FOOT_Y + 8, rx + 12, FOOT_Y + 20],
                       fill=REGION[reg])
        draw.text((rx + 16, FOOT_Y + 7), label, font=F_SANSB(12), fill=INK)
        rx += 16 + text_w(draw, label, F_SANSB(12)) + 14
    assert rx <= W - MX, "region strip overflow"
    fdc = F_SANS(12)
    pre = "DATE CHECK — "
    pre_w = text_w(draw, pre, F_SANSB(12))
    dc_body = DATECHECK[len(pre):]
    dc_lines = wrap(draw, dc_body, fdc, CW - pre_w)
    assert len(dc_lines) <= 2, "DATE CHECK over 2 lines"
    draw.text((MX, FOOT_Y + 28), pre, font=F_SANSB(12), fill=BRICK)
    draw.text((MX + pre_w, FOOT_Y + 28), dc_lines[0], font=fdc, fill=DATE_RED)
    if len(dc_lines) > 1:
        draw.text((MX, FOOT_Y + 43), dc_lines[1], font=fdc, fill=DATE_RED)
    fy = FOOT_Y + 28 + 2 * 15 + 2
    fns = F_SANS(11)
    pre2 = "NOT SHOWN: "
    pre2_w = text_w(draw, pre2, F_SANSB(11))
    ns_lines = wrap(draw, NOTSHOWN[len(pre2):], fns, CW - pre2_w)
    assert len(ns_lines) == 1, "NOT SHOWN over 1 line"
    draw.text((MX, fy), pre2, font=F_SANSB(11), fill=BRICK)
    draw.text((MX + pre2_w, fy), ns_lines[0], font=fns, fill=INK)
    fy += 14
    hc_lines = fit_lines(draw, HOWCHECKED, fns, CW, 1)
    assert len(hc_lines) == 1, "HOW WE CHECKED over 1 line"
    draw.text((MX, fy), hc_lines[0], font=fns, fill=GREY)
    fy += 13
    assert fy <= H, "footer overflow: %d > %d" % (fy, H)
    # ---- contrast gates (white on region colour, ink on paper, etc.)
    for reg, col in REGION.items():
        assert contrast(WHITE, col) >= 4.5, \
            "white on %s %.2f < 4.5" % (reg, contrast(WHITE, col))
        assert contrast(col, WHITE) >= 4.5, \
            "%s on white %.2f < 4.5" % (reg, contrast(col, WHITE))
    for pair in [(INK, PAPER), (BRICK, PAPER), (GREY, PAPER),
                 (WHITE, NAVY), (YELLOW, NAVY), (DATE_RED, PAPER),
                 (INK, WHITE), (NAVY, PAPER)]:
        assert contrast(*pair) >= 4.5, \
            "contrast %s %.2f < 4.5" % (pair, contrast(*pair))
    img.save(out_path, format="PNG", optimize=True)
    return img


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    render(out)
    print("wrote", out)
