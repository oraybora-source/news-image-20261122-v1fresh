#!/usr/bin/env python3
"""Render the front-page news image for 22 November 2026.

Draws "THE WORLD, CHECKED" — 41 verified stories from Sunday
22 November 2026 — as a single 1024x1024 PNG. Deterministic:
no network, no clock, no randomness. Every pixel comes from the
data tables below and the geometry constants next to them.

Usage:  python3 render.py [output-path]
Default output is entry.png next to this file.
"""

import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)      # page background
INK = (26, 26, 26)           # titles, body ink
BRICK = (166, 58, 43)        # masthead date, cities, footer labels
GREEN = (47, 107, 79)        # kicker line colour
SUMMARY = (60, 60, 60)       # card summaries
GREY90 = (90, 90, 90)        # small grey footer lines
DATE_RED = (112, 68, 58)     # DATE CHECK body
NAVY = (31, 58, 95)          # numbers panel, MORE header
YELLOW = (255, 210, 90)      # numbers panel title
LABEL_BLUE = (179, 192, 209)  # numbers panel labels
WHITE = (255, 255, 255)
NIGHT = (16, 26, 46)         # night-sky illustration base
ORANGE = (255, 140, 40)      # explosions, flames
RED_FLAG = (227, 10, 23)     # COP31 flag / X mark
BLUE_TAB = (0, 51, 153)      # small tab above the COP31 box
LEAF = (60, 70, 60)          # green strip at the foot of the COP31 scene

REGION = {
    "EU": (51, 86, 127),
    "ME": (166, 58, 43),
    "AM": (110, 74, 138),
    "AS": (47, 107, 79),
    "AF": (120, 78, 0),
    "OC": (16, 104, 100),
    "WORLD": (85, 85, 85),
}
REGION_NAME = {
    "EU": "EUROPE",
    "ME": "MIDDLE EAST",
    "AM": "AMERICAS",
    "AS": "ASIA",
    "AF": "AFRICA",
    "OC": "OCEANIA",
    "WORLD": "WORLD",
}
REGION_COUNTS = [("EU", 9), ("ME", 9), ("AM", 9), ("AS", 5),
                 ("AF", 5), ("OC", 2), ("WORLD", 2)]


def tint(region, alpha):
    """Region colour washed over the paper; lead cards use 0.12,
    grid cards 0.14 (measured from the reference render)."""
    r, g, b = REGION[region]
    return (round(PAPER[0] * (1 - alpha) + r * alpha),
            round(PAPER[1] * (1 - alpha) + g * alpha),
            round(PAPER[2] * (1 - alpha) + b * alpha))


# ---------------------------------------------------------------- fonts
FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
SERIF_B = str(FONT_DIR / "LiberationSerif-Bold.ttf")
SANS_B = str(FONT_DIR / "LiberationSans-Bold.ttf")
SANS = str(FONT_DIR / "LiberationSans-Regular.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


F_MASTHEAD = font(SERIF_B, 44)
F_DATE = font(SERIF_B, 26)
F_COUNT = font(SANS_B, 14)
F_VALUE = font(SANS_B, 16)
F_CHIP = font(SANS_B, 8)
F_CIRCLE = font(SANS_B, 15)
F_BOX = font(SANS_B, 20)
F_KICKER = font(SANS_B, 9)
F_LEAD_TITLE = font(SERIF_B, 26)
F_GRID_TITLE = font(SERIF_B, 18)
F_SUMMARY = font(SANS, 15)
F_MORE_HEAD = font(SERIF_B, 14)
F_MORE_SUB = font(SANS, 11)
F_BRIEF_CITY = font(SANS_B, 11)
F_BRIEF = font(SANS, 11)
F_SQNUM = font(SANS_B, 9)
F_STRIP = font(SANS_B, 12)
F_FOOT = font(SANS, 12)
F_FOOT_B = font(SANS_B, 12)
F_FOOT11 = font(SANS, 11)
F_FOOT_B11 = font(SANS_B, 11)
F_HOW = font(SANS, 11)
F_PANEL_TITLE = font(SANS_B, 13)
F_PANEL_NUM = font(SANS_B, 20)
F_PANEL_LABEL = font(SANS, 11)


# ---------------------------------------------------------------- data
# Lead band, left to right. "box" is the number baked into the picture.
LEAD = [
    dict(num=1, region="WORLD", field="CLIMATE", status="CONFIRMED",
         value="NO DEAL", source="REUTERS", box="NO DEAL", box_ink=BRICK,
         title="COP31 COLLAPSES",
         summary="Climate talks end with no deal; the EU rejects "
                 "a draft with no fossil fuels."),
    dict(num=2, region="AF", field="CONFLICT", status="CONFIRMED",
         value="2,400 KM", source="AP", box="2,400 KM", box_ink=INK,
         title="UKRAINE SINKS RUSSIAN WARSHIP",
         summary="Sea drones sink the corvette Merkury at a Libyan "
                 "base, 2,400 km from Ukraine."),
    dict(num=3, region="EU", field="SPORT", status="CONFIRMED",
         value="8TH TITLE", source="MOTOGP", box="8TH", box_ink=INK,
         title="MARQUEZ TAKES 8TH TITLE",
         summary="Bezzecchi wins the race; Marquez finishes 8th and "
                 "clinches his 8th title."),
]

# Grid, in spatial (reading) order: row by row, left to right.
GRID = [
    dict(num=4, region="AM", field="POLITICS", status="CONFIRMED",
         value="258 SEATS", source="AP", box="258",
         title="DEMOCRATS WIN 258 SEATS",
         summary="Largest House majority since 1992."),
    dict(num=5, region="ME", field="CONFLICT", status="CONFIRMED",
         value="2 HURT", source="REUTERS", box="2",
         title="IRAN STRIKES BAHRAIN",
         summary="Bahrain says two were hurt; Gulf condemns."),
    dict(num=6, region="EU", field="CONFLICT", status="CONFIRMED",
         value="3 DEAD, 14 TRAPPED", source="AP", box="14",
         title="DRONE HITS FLATS NEAR KYIV",
         summary="One of 186 drones; strikes a five-storey block."),
    dict(num=11, region="EU", field="SECURITY", status="CONFIRMED",
         value="3 KH-101", source="AL JAZEERA", box="3",
         title="MISSILES IN POLAND WERE RUSSIAN",
         summary="Prosecutors: all three were Kh-101s."),
    dict(num=7, region="AF", field="DISASTER", status="CONFIRMED",
         value="24 DEAD", source="REUTERS", box="24",
         title="BOAT CAPSIZES, 24 DEAD",
         summary="Boat carrying mourners capsizes; 24 dead."),
    dict(num=9, region="AM", field="DISASTER", status="CONFIRMED",
         value="5 DEAD", source="AFP", box="5",
         title="STORM TOLL RISES TO 5",
         summary="Storm toll rises: 5 dead, 250+ hurt."),
    dict(num=8, region="ME", field="ENERGY", status="REPORTED",
         value="2 TANKERS", source="AL ARABIYA", box="2",
         title="TANKERS HIT NEAR HORMUZ",
         summary="Iran says two supertankers hit mines."),
    dict(num=10, region="AS", field="EDUCATION", status="CONFIRMED",
         value="111 CASES", source="REUTERS", box="111",
         title="MINISTER QUITS OVER AI CHEATING",
         summary="Minister quits after AI exam cheating."),
    dict(num=13, region="EU", field="SPORT", status="CONFIRMED",
         value="4–0", source="NBC SPORTS", box="4–0",
         title="LIVERPOOL 4–0 MAN UTD",
         summary="Liverpool rout Manchester United 4–0."),
    dict(num=14, region="AS", field="DISASTER", status="CONFIRMED",
         value="36 MISSING", source="AP / REUTERS", box="36",
         title="FACTORY FIRE, 36 MISSING",
         summary="Fire at a factory; 3 dead, 36 missing."),
    dict(num=12, region="WORLD", field="SPACE", status="CONFIRMED",
         value="ORBIT", source="ESA / REUTERS", box="7 YRS",
         title="BEPICOLOMBO REACHES MERCURY",
         summary="Probe enters orbit after seven years."),
]

# Briefs 15-41: (number, region, city, fact, source, reported?).
BRIEFS = [
    (15, "ME", "WEST BANK", "Settlers torch 12 vehicles", "AP", False),
    (16, "AF", "KHARTOUM", "Drone attack kills 4", "AFP", False),
    (17, "AM", "KANSAS CITY", "Chiefs beat Cardinals 34–7", "SPORTRADAR", False),
    (18, "AM", "BARRANQUILLA",
     "Boca beat Atlético Mineiro 2–0, Copa Sudamericana", "LIVESCORE", False),
    (19, "AS", "LAHORE", "Air quality passes 500 AQI", "WIRES", False),
    (20, "AS", "WELLINGTON", "India pile up 720/9 against New Zealand",
     "LIVESCORE", False),
    (21, "EU", "GULF OF FINLAND", "Russian ship Sparta II still smouldering",
     "REUTERS", True),
    (22, "ME", "GAZA", "IDF strike leaves 1 critically hurt", "WIRES", False),
    (23, "ME", "QAA", "Lebanon arrests 3, seizes 264 kg of explosives",
     "AFP", False),
    (24, "EU", "WARSAW",
     "Russia twice tried to kill a rapper; Denmark expels official", "AP", False),
    (25, "OC", "RUATŌRIA", "House slips: 1 dead, 4 hurt", "NZ POLICE", False),
    (26, "AM", "NFL", "Cowboys 51–30 Titans; Panthers 35–33 Ravens",
     "REUTERS", False),
    (27, "EU", "VILLARREAL", "Barcelona come back from 2–0 down, win 3–2",
     "SPORTRADAR", False),
    (28, "OC", "MELBOURNE",
     "Olympians reunite at MCG, 70 years after 1956 Games opened", "ABC", False),
    (29, "ME", "RABIGH", "Houthis claim direct hit on Saudi refinery",
     "HOUTHIS", True),
    (30, "AM", "LAS VEGAS", "Verstappen wins chaotic Grand Prix, 35 lead changes",
     "F1", False),
    (31, "AM", "SAN ANTONIO",
     "Wembanyama: 50 points, 19 rebounds, Spurs win 114–91", "AP", False),
    (32, "AM", "WASHINGTON", "Current win first NWSL title, 2–1", "AP", False),
    (33, "EU", "KYIV", "Zelensky: Russia launched 2,700 drones in a week",
     "AP", False),
    (34, "ME", "HERZLIYA", "Eisenkot–Likud unity talks end after 4 hours, no deal",
     "AP", False),
    (35, "EU", "RŪDNINKAI",
     "Germany tests kamikaze drones, AI targeting near Belarus", "AP", False),
    (36, "AF", "OYO", "Kenya and DR Congo restore full diplomatic ties",
     "AP", False),
    (37, "AS", "HONG KONG", "856 candidates for 723 seats; turnout 98.79%",
     "INFO.GOV.HK", False),
    (38, "AF", "JOHANNESBURG", "ANC–ActionSA agree: Mashaba for mayor",
     "WIRES", True),
    (39, "ME", "TEHRAN", "Iran begins electricity rationing; cuts up to 2 hours a day",
     "RFE/RL", False),
    (40, "ME", "BEIRUT", "Aoun: Israel must withdraw; all weapons under the state",
     "WIRES", True),
    (41, "AM", "BRASÍLIA", "Bolsonaro in intensive care with bowel obstruction",
     "THE TIMES", False),
]

PANEL = [
    ("258", "House seats, Democrats"),
    ("2,700", "drones in a week, Russia"),
    ("720/9", "India's record Test total"),
    ("50", "Wembanyama points, Spurs"),
]

DATE_CHECK_BODY = (
    "Nigeria boat capsized Friday; toll of 24 confirmed Sunday. "
    "Brazil storm was Friday; 5 dead is Sunday's update. "
    "Poland missiles fell Friday; identified Sunday. "
    "F1, NBA, NWSL finals: Sat. night in US. "
    "Bahrain strike was Saturday; 2 hurt announced Sunday.")
NOT_SHOWN_BODY = (
    "ICJ Rohingya ruling (19 Nov), UK–EU reset (20 Nov), "
    "GTA VI $3.79bn (20 Nov) — not 22 November news.")
HOW_BODY = (
    "Every story dated 22 Nov 2026 from primary reporting; "
    "REPORTED = one source's claim. "
    "Sources: Reuters · AP · AFP · ESA · UN · MotoGP.com.")

# Expected wraps (checked by the asserts in main): the design's line
# breaks, so a font or width drift fails loudly instead of silently
# re-flowing the page.
EXPECTED_TITLES = {
    1: ["COP31 COLLAPSES"],
    2: ["UKRAINE SINKS", "RUSSIAN WARSHIP"],
    3: ["MARQUEZ TAKES 8TH", "TITLE"],
    4: ["DEMOCRATS WIN 258", "SEATS"],
    5: ["IRAN STRIKES", "BAHRAIN"],
    6: ["DRONE HITS FLATS", "NEAR KYIV"],
    11: ["MISSILES IN POLAND", "WERE RUSSIAN"],
    7: ["BOAT CAPSIZES, 24", "DEAD"],
    9: ["STORM TOLL RISES TO", "5"],
    8: ["TANKERS HIT NEAR", "HORMUZ"],
    10: ["MINISTER QUITS OVER", "AI CHEATING"],
    13: ["LIVERPOOL 4–0 MAN", "UTD"],
    14: ["FACTORY FIRE, 36", "MISSING"],
    12: ["BEPICOLOMBO", "REACHES MERCURY"],
}
EXPECTED_SUMMARIES = {
    1: ["Climate talks end with no deal; the EU rejects",
        "a draft with no fossil fuels."],
    2: ["Sea drones sink the corvette Merkury at a",
        "Libyan base, 2,400 km from Ukraine."],
    3: ["Bezzecchi wins the race; Marquez finishes",
        "8th and clinches his 8th title."],
    4: ["Largest House majority since", "1992."],
    5: ["Bahrain says two were hurt;", "Gulf condemns."],
    6: ["One of 186 drones; strikes a", "five-storey block."],
    11: ["Prosecutors: all three were", "Kh-101s."],
    7: ["Boat carrying mourners", "capsizes; 24 dead."],
    9: ["Storm toll rises: 5 dead, 250+", "hurt."],
    8: ["Iran says two supertankers hit", "mines."],
    10: ["Minister quits after AI exam", "cheating."],
    13: ["Liverpool rout Manchester", "United 4–0."],
    14: ["Fire at a factory; 3 dead, 36", "missing."],
    12: ["Probe enters orbit after seven", "years."],
}


# ---------------------------------------------------------------- helpers
def wrap(text, fnt, width):
    """Greedy word wrap; returns a list of lines, each <= width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if fnt.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def rel_lum(rgb):
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(fg, bg):
    """WCAG contrast ratio; the page floor is 4.5:1."""
    a, b = sorted((rel_lum(fg), rel_lum(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def draw_top(d, x, ink_top, text, fnt, fill):
    """Draw text so its ink (not its em box) starts at ink_top."""
    top = fnt.getbbox(text)[1]
    d.text((x, ink_top - top), text, font=fnt, fill=fill)


def draw_centred(d, cx, cy, text, fnt, fill):
    """Draw text centred on (cx, cy) by its ink box."""
    d.text((cx, cy), text, font=fnt, fill=fill, anchor="mm")


def rounded_rect(d, box, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill,
                        outline=outline, width=width)


# ---------------------------------------------------------------- banner
def draw_banner(d, x, y, w, card):
    """Coloured banner: number disc, value text, source chip."""
    col = REGION[card["region"]]
    d.rectangle([x, y, x + w - 1, y + 25], fill=col)
    cx, cy = x + 17, y + 13
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=WHITE)
    draw_centred(d, cx, cy + 1, str(card["num"]), F_CIRCLE, col)
    draw_top(d, x + 30, y + 7, card["value"], F_VALUE, WHITE)
    chip_w = int(F_CHIP.getlength(card["source"])) + 12
    chip_x = x + w - 5 - chip_w
    rounded_rect(d, [chip_x, y + 4, chip_x + chip_w - 1, y + 21],
                 radius=4, fill=WHITE)
    draw_centred(d, chip_x + chip_w // 2, y + 13,
                 card["source"], F_CHIP, INK)


def draw_value_box(d, x, y, w, h, text, region, ink):
    """Paper box with a region-coloured border, baked-in number."""
    col = REGION[region]
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=PAPER,
                outline=col, width=2)
    draw_centred(d, x + w // 2, y + h // 2, text, F_BOX, ink)


def draw_kicker_title_summary(d, tx, y0, card, title_font, title_pitch,
                              summary_pitch, wrap_w, kicker_top,
                              title_top, gap_after_title):
    region = card["region"]
    kicker = (REGION_NAME[region] + " · " + card["field"] + " — "
              + card["status"])
    draw_top(d, tx, y0 + kicker_top, kicker, F_KICKER, GREEN)
    title_lines = wrap(card["title"], title_font, wrap_w)
    assert title_lines == EXPECTED_TITLES[card["num"]], (
        card["num"], title_lines)
    for i, line in enumerate(title_lines):
        draw_top(d, tx, y0 + title_top + i * title_pitch,
                 line, title_font, INK)
    # The summary follows the last title line, so a one-line title
    # pulls it up a full line.
    summary_top = (title_top + title_pitch * (len(title_lines) - 1)
                   + gap_after_title)
    sum_lines = wrap(card["summary"], F_SUMMARY, wrap_w)
    assert sum_lines == EXPECTED_SUMMARIES[card["num"]], (
        card["num"], sum_lines)
    for i, line in enumerate(sum_lines):
        draw_top(d, tx, y0 + summary_top + i * summary_pitch,
                 line, F_SUMMARY, SUMMARY)


# ---------------------------------------------------------------- pictures
# Each picture is a small flat scene inside its tile. The tile origin
# (x, y) is the picture's top-left corner; w/h are its size.

def star(d, cx, cy, r, fill):
    """Eight-point sparkle: a plus over an X."""
    d.line([cx - r, cy, cx + r, cy], fill=fill, width=2)
    d.line([cx, cy - r, cx, cy + r], fill=fill, width=2)
    d.line([cx - r, cy - r, cx + r, cy + r], fill=fill, width=1)
    d.line([cx - r, cy + r, cx + r, cy - r], fill=fill, width=1)


def pic_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(24, 45, 75))
    d.rectangle([x, y + h - 6, x + w - 1, y + h - 1], fill=LEAF)
    d.rectangle([x + 16, y + 4, x + 46, y + 6], fill=BLUE_TAB)
    # paper with the draft, crossed out
    px, py, pw, ph = x + 194, y + 8, 108, 33
    d.rectangle([px, py, px + pw - 1, py + ph - 1], fill=WHITE)
    d.line([px + 8, py + 12, px + 62, py + 12], fill=(150, 150, 150), width=2)
    d.line([px + 8, py + 20, px + 52, py + 20], fill=(150, 150, 150), width=2)
    d.line([px + pw - 24, py + 6, px + pw - 6, py + 26], fill=RED_FLAG, width=4)
    d.line([px + pw - 24, py + 26, px + pw - 6, py + 6], fill=RED_FLAG, width=4)
    # red flag above the paper
    fx, fy = x + 270, y + 4
    d.rectangle([fx, fy, fx + 30, fy + 14], fill=RED_FLAG)
    d.ellipse([fx + 11, fy + 4, fx + 19, fy + 12], fill=WHITE)


def pic_merkury(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=NIGHT)
    for sx, sy in [(24, 4), (64, 12), (114, 6), (154, 14), (204, 5),
                   (254, 11), (294, 4), (44, 22), (134, 20), (234, 22)]:
        star(d, x + sx, y + sy, 2, WHITE)
    # warship: hull, deck, mast
    d.polygon([(x + 150, y + 22), (x + 290, y + 22), (x + 272, y + 40),
               (x + 168, y + 40)], fill=(75, 85, 100))
    d.rectangle([x + 190, y + 12, x + 240, y + 22], fill=(95, 105, 120))
    d.line([x + 215, y + 12, x + 215, y + 4], fill=(150, 155, 165), width=2)
    # explosion over the deck
    star(d, x + 235, y + 10, 9, ORANGE)
    d.ellipse([x + 231, y + 6, x + 239, y + 14], fill=(255, 210, 90))
    # sea lanes + dark water line
    for wy in (28, 33, 38):
        d.line([x + 6, y + wy, x + w - 6, y + wy], fill=(90, 130, 160), width=1)
    d.rectangle([x, y + h - 2, x + w - 1, y + h - 1], fill=(24, 48, 72))
    # sea drone, top right
    dx, dy = x + 292, y + 12
    d.line([dx - 12, dy + 8, dx, dy], fill=(200, 200, 200), width=1)
    d.line([dx - 4, dy - 3, dx + 4, dy + 3], fill=WHITE, width=2)
    d.line([dx - 4, dy + 3, dx + 4, dy - 3], fill=WHITE, width=2)
    d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=RED_FLAG)


def pic_marquez(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(205, 210, 205))
    for i in range(5):
        d.rectangle([x + 14 + i * 16, y + 4, x + 26 + i * 16, y + 12],
                    fill=(60, 60, 66))
    d.rectangle([x, y + 15, x + w - 1, y + h - 1], fill=(52, 52, 58))
    for dx in (20, 70, 150, 200, 250):
        d.rectangle([x + dx, y + 32, x + dx + 22, y + 35], fill=WHITE)
    # motorcycle: two white-rimmed wheels, red tank, black frame
    for wx in (120, 172):
        d.ellipse([x + wx - 12, y + 20, x + wx + 12, y + 44], fill=WHITE)
        d.ellipse([x + wx - 8, y + 24, x + wx + 8, y + 40], fill=(52, 52, 58))
    d.line([x + 120, y + 32, x + 146, y + 22], fill=(20, 20, 20), width=4)
    d.line([x + 146, y + 22, x + 172, y + 32], fill=(20, 20, 20), width=4)
    d.line([x + 146, y + 22, x + 158, y + 14], fill=(20, 20, 20), width=3)
    d.polygon([(x + 138, y + 12), (x + 162, y + 12), (x + 158, y + 24),
               (x + 142, y + 24)], fill=RED_FLAG)
    d.line([x + 128, y + 18, x + 140, y + 12], fill=RED_FLAG, width=4)
    # chequered flag, right
    fx = x + w - 36
    d.line([fx + 30, y + 4, fx + 30, y + 30], fill=(30, 30, 30), width=2)
    for r in range(3):
        for c in range(4):
            if (r + c) % 2 == 0:
                d.rectangle([fx + c * 8, y + 4 + r * 8,
                             fx + c * 8 + 7, y + 11 + r * 8], fill=(20, 20, 20))
            else:
                d.rectangle([fx + c * 8, y + 4 + r * 8,
                             fx + c * 8 + 7, y + 11 + r * 8], fill=WHITE)


def pic_capitol(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(205, 212, 222))
    # dome
    d.pieslice([x + 22, y + 4, x + 70, y + 36], 180, 360, fill=(235, 230, 210))
    d.rectangle([x + 18, y + 30, x + 74, y + 44], fill=(235, 230, 210))
    for cx in (28, 40, 52, 64):
        d.rectangle([x + cx, y + 44, x + cx + 5, y + 64], fill=WHITE)
    d.rectangle([x + 14, y + 64, x + 78, y + 70], fill=(180, 60, 50))
    d.rectangle([x, y + h - 8, x + w - 1, y + h - 1], fill=(150, 160, 175))


def pic_bahrain(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(30, 32, 48))
    for sx, sy in [(10, 8), (30, 16), (70, 6), (84, 20)]:
        star(d, x + sx, y + sy, 2, WHITE)
    # tower block with lit windows
    d.rectangle([x + 18, y + 30, x + 62, y + h - 1], fill=(40, 45, 60))
    for wy in (36, 48, 60):
        for wx in (26, 38, 50):
            d.rectangle([x + wx, y + wy, x + wx + 7, y + wy + 7],
                        fill=(255, 210, 90))
    d.polygon([(x + 18, y + 30), (x + 40, y + 16), (x + 62, y + 30)],
              fill=ORANGE)
    # missile trails + burst
    d.arc([x + 4, y + 2, x + 60, y + 40], 200, 330, fill=(255, 210, 90), width=2)
    d.arc([x + 20, y - 6, x + 76, y + 32], 200, 330, fill=(255, 210, 90), width=2)
    star(d, x + 66, y + 12, 7, ORANGE)


def pic_dymer(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(20, 25, 40))
    for sx, sy in [(8, 10), (26, 5), (52, 12), (80, 7)]:
        star(d, x + sx, y + sy, 2, WHITE)
    d.rectangle([x + 14, y + 26, x + 66, y + h - 1], fill=(50, 50, 60))
    for wy in (32, 44, 56):
        for wx in (22, 34, 46):
            d.rectangle([x + wx, y + wy, x + wx + 7, y + wy + 7],
                        fill=(255, 210, 90))
    # drone: yellow diamond with a light
    dx, dy = x + 74, y + 14
    d.polygon([(dx, dy - 7), (dx + 8, dy), (dx, dy + 7), (dx - 8, dy)],
              fill=(240, 225, 160))
    d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=WHITE)


def pic_poland(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(20, 25, 40))
    for sx, sy in [(10, 8), (34, 16), (60, 6), (84, 18), (20, 26)]:
        star(d, x + sx, y + sy, 2, WHITE)
    for (mx, my) in [(30, 34), (58, 48)]:
        d.polygon([(x + mx - 20, y + my + 6), (x + mx + 16, y + my - 8),
                   (x + mx + 22, y + my - 2), (x + mx - 14, y + my + 12)],
                  fill=(150, 155, 165))
        d.polygon([(x + mx - 20, y + my + 6), (x + mx - 30, y + my + 12),
                   (x + mx - 26, y + my + 2)], fill=ORANGE)
        d.polygon([(x + mx + 16, y + my - 8), (x + mx + 24, y + my - 12),
                   (x + mx + 24, y + my - 2)], fill=(150, 155, 165))


def pic_boat(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(170, 200, 215))
    d.rectangle([x, y + 34, x + w - 1, y + h - 1], fill=(60, 130, 150))
    for wy in (48, 60, 72):
        for wx in (8, 34, 60):
            d.arc([x + wx, y + wy, x + wx + 18, y + wy + 10], 180, 360,
                  fill=WHITE, width=2)
    # capsized hull, keel up
    d.polygon([(x + 22, y + 30), (x + 70, y + 30), (x + 62, y + 42),
               (x + 30, y + 42)], fill=(120, 80, 50))
    d.rectangle([x + 40, y + 26, x + 52, y + 30], fill=(90, 60, 40))


def pic_storm(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(215, 215, 205))
    d.ellipse([x + 6, y + 6, x + 44, y + 26], fill=(60, 60, 65))
    d.ellipse([x + 34, y + 2, x + 72, y + 22], fill=(60, 60, 65))
    d.ellipse([x + 58, y + 8, x + 88, y + 26], fill=(60, 60, 65))
    d.polygon([(x + 40, y + 24), (x + 48, y + 24), (x + 38, y + 44),
               (x + 46, y + 44), (x + 34, y + 62), (x + 52, y + 38)],
              fill=(255, 210, 90))
    for rx in (12, 30, 52, 74):
        d.line([x + rx, y + 34, x + rx - 3, y + 46], fill=(120, 130, 145), width=1)
    for hx in (10, 52):
        d.rectangle([x + hx, y + 58, x + hx + 30, y + h - 1], fill=(230, 215, 190))
        d.polygon([(x + hx - 3, y + 58), (x + hx + 15, y + 44),
                   (x + hx + 33, y + 58)], fill=(180, 60, 50))


def pic_tankers(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(40, 50, 70))
    d.ellipse([x + 66, y + 6, x + 82, y + 22], fill=(255, 210, 90))
    d.rectangle([x, y + 44, x + w - 1, y + h - 1], fill=(30, 60, 80))
    for wx in (8, 34, 60):
        d.line([x + wx, y + 56, x + wx + 16, y + 56], fill=(90, 130, 160), width=1)
    # two tankers, near and far
    d.rectangle([x + 8, y + 34, x + 52, y + 48], fill=(120, 130, 145))
    d.rectangle([x + 8, y + 44, x + 52, y + 48], fill=(180, 60, 50))
    d.rectangle([x + 20, y + 26, x + 34, y + 34], fill=(120, 130, 145))
    d.rectangle([x + 48, y + 38, x + 86, y + 50], fill=(110, 120, 135))
    d.rectangle([x + 48, y + 46, x + 86, y + 50], fill=(180, 60, 50))
    d.rectangle([x + 62, y + 30, x + 72, y + 38], fill=(110, 120, 135))
    # black derrick silhouette, left
    d.polygon([(x + 2, y + 44), (x + 10, y + 14), (x + 18, y + 44)],
              fill=(15, 18, 25))


def pic_exam(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(110, 125, 145))
    d.rectangle([x + 10, y + 8, x + w - 10, y + 40], fill=(70, 80, 95))
    for i, col in enumerate([(255, 210, 90), WHITE, (120, 130, 145)]):
        d.rectangle([x + 18 + i * 22, y + 16, x + 32 + i * 22, y + 30], fill=col)
    # answer paper with a red cross mark
    d.rectangle([x + 22, y + 44, x + 70, y + h - 6], fill=WHITE)
    d.line([x + 28, y + 50, x + 64, y + 50], fill=(150, 150, 150), width=2)
    d.line([x + 28, y + 58, x + 58, y + 58], fill=(150, 150, 150), width=2)
    d.ellipse([x + 46, y + 60, x + 66, y + 76], outline=RED_FLAG, width=3)
    d.line([x + 48, y + 62, x + 64, y + 74], fill=RED_FLAG, width=3)


def pic_pitch(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(34, 120, 60))
    d.rectangle([x + 46, y, x + w - 1, y + h - 1], fill=(45, 140, 75))
    d.line([x, y + h - 6, x + w - 1, y + h - 6], fill=WHITE, width=2)
    # goal, right side
    d.rectangle([x + 58, y + 12, x + 62, y + 52], fill=WHITE)
    d.rectangle([x + 58, y + 12, x + 90, y + 16], fill=WHITE)
    d.rectangle([x + 86, y + 12, x + 90, y + 52], fill=WHITE)
    for gy in range(20, 52, 8):
        d.line([x + 62, y + gy, x + 90, y + gy], fill=(220, 220, 220), width=1)
    for gx in range(66, 90, 8):
        d.line([x + gx, y + 16, x + gx, y + 52], fill=(220, 220, 220), width=1)
    # ball
    d.ellipse([x + 22, y + 58, x + 34, y + 70], fill=WHITE)
    d.ellipse([x + 26, y + 62, x + 30, y + 66], fill=(30, 30, 30))


def pic_fire(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(70, 45, 35))
    for (sx, sy, sr) in [(22, 10, 12), (48, 6, 14), (72, 12, 11)]:
        d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr],
                  fill=(110, 105, 100))
    # factory block + flame
    d.rectangle([x + 8, y + 40, x + w - 8, y + h - 1], fill=(40, 32, 28))
    d.polygon([(x + 30, y + 40), (x + 42, y + 18), (x + 54, y + 40)],
              fill=ORANGE)
    d.polygon([(x + 38, y + 40), (x + 44, y + 28), (x + 50, y + 40)],
              fill=(255, 210, 90))
    d.rectangle([x + 62, y + 52, x + 74, y + 64], fill=ORANGE)
    d.rectangle([x, y + h - 6, x + w - 1, y + h - 1], fill=(25, 20, 18))


def pic_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=(12, 14, 28))
    for sx, sy in [(10, 8), (30, 20), (52, 6), (78, 14), (16, 30)]:
        star(d, x + sx, y + sy, 2, WHITE)
    # orbit arc + planet
    d.arc([x - 30, y - 6, x + 70, y + 70], 200, 80, fill=(140, 170, 200), width=2)
    d.ellipse([x + 44, y + 38, x + 96, y + 90], fill=(200, 175, 130))
    d.ellipse([x + 56, y + 48, x + 68, y + 60], fill=(180, 155, 115))
    # probe on the arc
    d.rectangle([x + 16, y + 12, x + 28, y + 24], fill=(150, 155, 165))
    d.rectangle([x + 28, y + 15, x + 38, y + 21], fill=(255, 210, 90))
    d.line([x + 22, y + 12, x + 22, y + 4], fill=(200, 200, 200), width=2)
    d.ellipse([x + 20, y + 2, x + 24, y + 6], fill=(255, 210, 90))


ILLUSTRATIONS = {
    1: pic_cop31, 2: pic_merkury, 3: pic_marquez,
    4: pic_capitol, 5: pic_bahrain, 6: pic_dymer,
    11: pic_poland, 7: pic_boat, 9: pic_storm,
    8: pic_tankers, 10: pic_exam, 13: pic_pitch,
    14: pic_fire, 12: pic_mercury,
}


# ---------------------------------------------------------------- sections
CARD_X = [16, 351, 686]
CARD_W = 323
LEAD_Y = 90
LEAD_H = 173          # 90..262
GRID_Y = [270, 386, 502, 618]
GRID_H = 109          # rows end 378 / 494 / 610 / 726


def draw_masthead(d):
    draw_top(d, 16, 15, "THE WORLD, CHECKED", F_MASTHEAD, INK)
    draw_top(d, 16, 59, "SUNDAY 22 NOVEMBER 2026", F_DATE, BRICK)
    count = "41 STORIES · 7 REGIONS"
    draw_top(d, W - 16 - int(F_COUNT.getlength(count)), 61,
             count, F_COUNT, INK)
    d.rectangle([16, 81, 1007, 84], fill=BRICK)


EDGE = (200, 192, 170)      # 1 px line along each card's bottom edge


def draw_lead_card(d, i, card):
    x = CARD_X[i]
    y = LEAD_Y
    d.rectangle([x, y, x + CARD_W - 1, y + LEAD_H - 1],
                fill=tint(card["region"], 0.12))
    d.line([x, y + LEAD_H - 1, x + CARD_W - 1, y + LEAD_H - 1], fill=EDGE)
    draw_banner(d, x, y, CARD_W, card)
    ILLUSTRATIONS[card["num"]](d, x, y + 26, CARD_W, 46)
    box_w = int(F_BOX.getlength(card["box"])) + 20
    draw_value_box(d, x + 6, y + 33, box_w, 33, card["box"],
                   card["region"], card.get("box_ink", INK))
    draw_kicker_title_summary(
        d, x + 8, y, card, F_LEAD_TITLE, 27, 17, 305,
        kicker_top=74, title_top=88, gap_after_title=24)


def draw_grid_card(d, slot, card):
    row, col = divmod(slot, 3)
    x = CARD_X[col]
    y = GRID_Y[row]
    d.rectangle([x, y, x + CARD_W - 1, y + GRID_H - 1],
                fill=tint(card["region"], 0.14))
    d.line([x, y + GRID_H - 1, x + CARD_W - 1, y + GRID_H - 1], fill=EDGE)
    draw_banner(d, x, y, CARD_W, card)
    ILLUSTRATIONS[card["num"]](d, x, y + 26, 93, GRID_H - 26)
    box_w = int(F_BOX.getlength(card["box"])) + 12
    draw_value_box(d, x + 6, y + GRID_H - 37, box_w, 31, card["box"],
                   card["region"], INK)
    draw_kicker_title_summary(
        d, x + 100, y, card, F_GRID_TITLE, 20, 16, 212,
        kicker_top=28, title_top=41, gap_after_title=18)


def draw_panel(d):
    x, y = CARD_X[2], GRID_Y[3]
    d.rectangle([x, y, x + CARD_W - 1, y + GRID_H - 1], fill=NAVY)
    d.line([x, y + GRID_H - 1, x + CARD_W - 1, y + GRID_H - 1], fill=EDGE)
    draw_top(d, x + 11, y + 10, "THE DAY IN NUMBERS", F_PANEL_TITLE, YELLOW)
    for k, (num, label) in enumerate(PANEL):
        ny = y + 28 + 19 * k
        draw_top(d, x + 10, ny + 5, num, F_PANEL_NUM, WHITE)
        lx = x + 10 + F_PANEL_NUM.getbbox(num)[2] - 2
        draw_top(d, lx, ny + 10, label, F_PANEL_LABEL, LABEL_BLUE)


def draw_more(d):
    draw_top(d, 16, 737, "MORE STORIES", F_MORE_HEAD, NAVY)
    sub = "27 MORE · NUMBERED 15–41"
    draw_top(d, W - 16 - int(F_MORE_SUB.getlength(sub)), 738,
             sub, F_MORE_SUB, GREY90)
    for k, (num, region, city, fact, source, reported) in enumerate(BRIEFS):
        col_x = 16 if k < 14 else 520
        ry = 752 + 12 * (k % 14)
        d.rectangle([col_x, ry, col_x + 18, ry + 11], fill=REGION[region])
        draw_centred(d, col_x + 9, ry + 6, str(num), F_SQNUM, WHITE)
        tx = col_x + 24
        draw_top(d, tx, ry + 2, city, F_BRIEF_CITY, BRICK)
        tx += int(F_BRIEF_CITY.getlength(city))
        rest = " — " + fact + " — " + source
        draw_top(d, tx, ry + 2, rest, F_BRIEF, INK)
        tx += int(F_BRIEF.getlength(rest))
        if reported:
            draw_top(d, tx, ry + 2, " · REPORTED", F_BRIEF, REGION["EU"])
            tx += int(F_BRIEF.getlength(" · REPORTED"))
        limit = 505 if k < 14 else 1008
        assert tx <= limit, (num, tx, limit)


def draw_footer(d):
    d.rectangle([16, 924, 1007, 926], fill=BRICK)
    sx = 16
    for region, count in REGION_COUNTS:
        d.rectangle([sx, 932, sx + 12, 944], fill=REGION[region])
        text = REGION_NAME[region] + " " + str(count)
        draw_top(d, sx + 16, 933, text, F_STRIP, INK)
        sx += 17 + int(F_STRIP.getlength(text)) + 13
    assert sx <= 1008, sx
    # DATE CHECK (label + wrapped body, max two lines)
    label = "DATE CHECK — "
    label_w = int(F_FOOT_B.getlength(label))
    first_w = 992 - label_w
    lines = wrap(DATE_CHECK_BODY, F_FOOT, first_w)
    rest = DATE_CHECK_BODY[len(lines[0]):].lstrip()
    lines = [lines[0]] + wrap(rest, F_FOOT, 992) if rest else lines
    assert len(lines) == 2, lines
    draw_top(d, 16, 954, label, F_FOOT_B, BRICK)
    draw_top(d, 16 + label_w, 954, lines[0], F_FOOT, DATE_RED)
    draw_top(d, 16, 969, lines[1], F_FOOT, DATE_RED)
    # NOT SHOWN (11 px, like the HOW line below)
    label2 = "NOT SHOWN: "
    draw_top(d, 16, 986, label2, F_FOOT_B11, BRICK)
    draw_top(d, 16 + int(F_FOOT_B11.getlength(label2)), 986,
             NOT_SHOWN_BODY, F_FOOT11, INK)
    assert int(F_FOOT11.getlength(NOT_SHOWN_BODY)) <= 992 - int(
        F_FOOT_B11.getlength(label2))
    # HOW WE CHECKED
    label3 = "HOW WE CHECKED — "
    draw_top(d, 16, 1000, label3, F_HOW, GREY90)
    draw_top(d, 16 + int(F_HOW.getlength(label3)), 1000,
             HOW_BODY, F_HOW, GREY90)
    assert int(F_HOW.getlength(HOW_BODY)) <= 992 - int(
        F_HOW.getlength(label3))


# ---------------------------------------------------------------- gates
def check_contrast():
    """Every text/background pair on the page clears 4.5:1."""
    pairs = []
    for region, col in REGION.items():
        pairs.append((f"white on {region}", WHITE, col))
        pairs.append((f"ink on {region}-tint", INK, tint(region, 0.14)))
        pairs.append((f"summary on {region}-tint", SUMMARY, tint(region, 0.14)))
        pairs.append((f"kicker on {region}-tint", GREEN, tint(region, 0.14)))
    pairs += [
        ("ink on paper", INK, PAPER),
        ("brick on paper", BRICK, PAPER),
        ("date-red on paper", DATE_RED, PAPER),
        ("grey90 on paper", GREY90, PAPER),
        ("yellow on navy", YELLOW, NAVY),
        ("white on navy", WHITE, NAVY),
        ("label-blue on navy", LABEL_BLUE, NAVY),
        ("navy on paper", NAVY, PAPER),
    ]
    worst = min(pairs, key=lambda p: contrast(p[1], p[2]))
    for name, fg, bg in pairs:
        c = contrast(fg, bg)
        assert c >= 4.5, (name, round(c, 2))
    return worst


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    for i, card in enumerate(LEAD):
        draw_lead_card(d, i, card)
    for slot, card in enumerate(GRID):
        draw_grid_card(d, slot, card)
    draw_panel(d)
    draw_more(d)
    draw_footer(d)
    return img


def main(argv):
    out = Path(argv[1]) if len(argv) > 1 else Path(__file__).with_name("entry.png")
    worst = check_contrast()
    img = build()
    assert img.size == (1024, 1024)
    img.save(out, format="PNG")
    data = out.read_bytes()
    assert len(data) <= 1024 * 1024, len(data)
    print("wrote", out, len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())
    print("worst contrast", worst[0], round(contrast(worst[1], worst[2]), 2))


if __name__ == "__main__":
    main(sys.argv)
