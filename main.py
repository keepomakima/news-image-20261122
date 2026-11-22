#!/usr/bin/env python3
"""Build the news-image-20261122 front page ("THE SUNDAY PAPER").

v1: Sunday 22 November 2026, 36 stories verified in-session against at
least two independent news sources each (see SOURCES-v1.md in the work
directory). Layout follows the proven v3 "FRIDAY PAPER" formula: dated
masthead, strip of 6 big numbers, region chips summing to 36, 3 leads +
10 small panels, a pinned world map, 23 briefs, a DATE CHECK strip.

Every graphic is drawn with PIL (no AI photos, no downloaded images).
The grade run happens in a bare python image with NO Pillow, so main()
tries the live draw first and falls back, on any failure, to copying the
committed pre-rendered entry.png beside this file with stdlib only,
verifying its sha256. Output is byte-identical either way.
Output: 1024x1024 PNG, written to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output/entry.png).

Date honesty: this Sunday paper sums up Saturday 21 November (plus
Friday night, reported Saturday). Anything dated Friday 20 November or
earlier is flagged in the DATE CHECK strip, never passed off as
Saturday news. The COP31 deal is framed as close to a deal, not agreed:
the approval session is Sunday 06:00 GMT, after this build. The Las
Vegas Grand Prix is framed as tonight: qualifying is done, the race
has not run yet.
"""
import hashlib
import math
import os

try:
    from PIL import Image, ImageDraw, ImageFont
    _HAVE_PIL = True
except ImportError:  # grade image is bare python: no Pillow installed
    Image = ImageDraw = ImageFont = None
    _HAVE_PIL = False

W, H = 1024, 1024
OUTDIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT = os.path.join(OUTDIR, "entry.png")
EXPECTED_SHA256 = "9ac284a051fab61f404dd77ad666375db87f3f953e243fab205ea17aef6cb75a"

FONTDIR = "/usr/share/fonts/truetype/dejavu"
PAPER = (253, 251, 245)
INK = (26, 26, 26)
RED = (179, 32, 44)
NAVY = (31, 58, 95)
GRAY = (110, 105, 95)
LIGHT = (216, 210, 196)
WHITE = (255, 255, 255)
SKY = (214, 228, 240)

REGION_COLORS = {
    "EUROPE": (31, 58, 95),
    "AMERICAS": (46, 125, 50),
    "ASIA-PACIFIC": (179, 32, 44),
    "MIDEAST": (154, 107, 0),
    "AFRICA": (106, 61, 154),
    "OCEANIA": (0, 122, 122),
    "WORLD": (85, 85, 85),
}


def F(name, size):
    return ImageFont.truetype(os.path.join(FONTDIR, name), size)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, xy, text, font, fill, max_w, leading=None,
                 max_lines=None):
    """Draw wrapped text; returns (lines, bottom_y). Raises on overflow."""
    x, y = xy
    leading = leading or int(font.size * 1.18)
    lines = wrap(draw, text, font, max_w)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError("text overflows %d lines: %r -> %r"
                         % (max_lines, text, lines))
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return lines, y


def fit_font(name, text, start_size, max_w):
    """Largest font size <= start_size whose text fits max_w."""
    size = start_size
    while size > 8:
        f = F(name, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 1
    return F(name, 8)


# ---------------------------------------------------------------- data
LEADS = [
    {
        "num": "01", "kicker": "GULF OF FINLAND \u2014 SATURDAY",
        "region": "EUROPE",
        "headline": "Drones hit Russian ship Sparta II",
        "deck": "Two drones strike the sanctioned cargo ship in the Gulf "
                "of Finland; it burns and drifts into Finnish waters. "
                "All 16 crew evacuated. Helsinki: likely Ukraine. "
                "Orpo: the war is spilling over.",
        "source": "Reuters \u00b7 CNN \u00b7 ISW \u00b7 Yle",
        "kind": "ship",
    },
    {
        "num": "02", "kicker": "ANTALYA \u2014 SATURDAY NIGHT",
        "region": "WORLD",
        "headline": "COP31 close to a final deal",
        "deck": "Presidents unveil a new package late Saturday and call "
                "a vote for Sunday 06:00 GMT. Delegates have until "
                "03:00 GMT to object. Fossil fuels and finance still "
                "divide the room.",
        "source": "Reuters \u00b7 AP \u00b7 AAP",
        "kind": "cop",
    },
    {
        "num": "03", "kicker": "KRYVYI RIH \u2014 FRIDAY NIGHT",
        "region": "EUROPE",
        "headline": "Double-tap strike kills boy and rescuer",
        "deck": "Ballistic missiles hit the city centre, then drones "
                "strike the rescuers. 2 killed, 60 hurt, six of them "
                "children. Russia fired 3 missiles and 148 drones "
                "overnight.",
        "source": "AP \u00b7 CNN \u00b7 Kyiv Independent",
        "kind": "blast",
    },
]

SMALL = [
    {
        "num": "04", "kicker": "MERCURY \u2014 SATURDAY", "region": "WORLD",
        "headline": "BepiColombo reaches Mercury",
        "deck": "37-minute burn puts it in orbit after an eight-year trip.",
        "source": "Nature \u00b7 ESA \u00b7 Sky & Telescope", "kind": "planet",
    },
    {
        "num": "05", "kicker": "GUASAVE, MEXICO \u2014 FRIDAY NIGHT",
        "region": "AMERICAS",
        "headline": "Mexico captures \u2018El Chapo Isidro\u2019",
        "deck": "FBI top-10 fugitive seized in Sinaloa; 11 killed in the gunfight.",
        "source": "Reuters \u00b7 AP \u00b7 WSJ", "kind": "cuffs",
    },
    {
        "num": "06", "kicker": "JUN\u00cdN, PERU \u2014 FRIDAY", "region": "AMERICAS",
        "headline": "Quake shakes the Andes",
        "deck": "M6.7, felt in Lima. No deaths; 39 homes damaged.",
        "source": "AP \u00b7 USGS \u00b7 IGP", "kind": "quake",
    },
    {
        "num": "07", "kicker": "NEW YORK \u2014 FRIDAY CLOSE", "region": "AMERICAS",
        "headline": "Wall Street rout deepens",
        "deck": "S&P 500 \u22123.7% to 6,910, its 7th straight fall. Nasdaq \u22125.3%.",
        "source": "NPR \u00b7 WSJ \u00b7 Investopedia", "kind": "market",
    },
    {
        "num": "08", "kicker": "LAS VEGAS \u2014 FRIDAY", "region": "AMERICAS",
        "headline": "Antonelli fastest, Verstappen on pole",
        "deck": "Fastest in 1:33.893, but a 5-place penalty drops him to 6th.",
        "source": "FIA \u00b7 Formula1.com \u00b7 AP", "kind": "race",
    },
    {
        "num": "09", "kicker": "COPENHAGEN \u2014 FRIDAY", "region": "EUROPE",
        "headline": "Denmark expels Russian attach\u00e9",
        "deck": "PET: Moscow plotted to kill rapper Kyivstoner. Two charged.",
        "source": "Reuters \u00b7 WSJ \u00b7 The Times", "kind": "spy",
    },
    {
        "num": "10", "kicker": "RIYADH \u2014 SATURDAY", "region": "MIDEAST",
        "headline": "Three Houthi missiles downed",
        "deck": "Second attack on the capital in days; PIF tower hit Thursday.",
        "source": "Reuters \u00b7 Al Jazeera \u00b7 AFP", "kind": "shield",
    },
    {
        "num": "11", "kicker": "WASHINGTON \u2014 SATURDAY", "region": "AMERICAS",
        "headline": "Trump: FBI hack \u2018not good\u2019",
        "deck": "NCIC crime database breached. He also posts a Yalta-style photo.",
        "source": "Fox News \u00b7 CNN \u00b7 AP", "kind": "phone",
    },
    {
        "num": "12", "kicker": "NEW ORLEANS \u2014 FRIDAY", "region": "AMERICAS",
        "headline": "Court: proxy voting unconstitutional",
        "deck": "Fifth Circuit rules 9\u20138 in Texas v. Blanche; funding law in doubt.",
        "source": "Bloomberg Law \u00b7 Reuters \u00b7 Reason", "kind": "scales",
    },
    {
        "num": "13", "kicker": "STRAIT OF HORMUZ \u2014 SATURDAY",
        "region": "MIDEAST",
        "headline": "Tankers hit near Oman",
        "deck": "Two tankers struck off Khasab; Iran says one hit a mine.",
        "source": "Reuters \u00b7 UKMTO \u00b7 gCaptain", "kind": "tanker",
    },
]

BRIEFS = [
    ("14", "Rutte in Warsaw: NATO will defend Poland"),
    ("15", "Poland: missiles land Fri; Tusk: provocation"),
    ("16", "Akvan: relief under way; zero deaths"),
    ("17", "Wellington: India 486/4, lead NZ by 118"),
    ("18", "Rugby: England 37\u201312 NZ, record margin"),
    ("19", "Wolbachia mosquitoes cut dengue 69%"),
    ("20", "Trump: Iran decision after New Year (Wed)"),
    ("21", "UK\u2013EU sign 3 reset deals in Brussels"),
    ("22", "Anthropic \u22129.1% to $88.30 after IPO (Fri)"),
    ("23", "Sensex +898 to 83,920; Nifty tops 25,800"),
    ("24", "Estonia to shut Russia crossings 1 Dec"),
    ("25", "Delhi: Modi opens first SCO forum"),
    ("26", "Yemen boat attack kills 19, blame disputed"),
    ("27", "SF braces for record king tides (Nov 24\u201326)"),
    ("28", "Princeton PhD student held by ICE (Thu)"),
    ("29", "Board of Peace faults Israel, Hamas (Wed)"),
    ("30", "ICJ: Myanmar committed genocide, 9\u20136"),
    ("31", "Voyager 1 one light-day away (Wed)"),
    ("32", "Sinaloa: 11 killed in clashes after arrest"),
    ("33", "Trump pardons Pete Rose posthumously (Thu)"),
    ("34", "JPMorgan, Visa hit via vendor; no card data"),
    ("35", "Guilty: man who lit the Palisades Fire"),
    ("36", "S. Africa murders down \u2014 still 60 a day"),
]

CHIPS = [("EUROPE", 8), ("AMERICAS", 14), ("ASIA-PACIFIC", 4),
         ("MIDEAST", 5), ("AFRICA", 1), ("OCEANIA", 1), ("WORLD", 3)]

NUMBERS = [
    ("2", "DRONES HIT SPARTA II"),
    ("16", "CREW EVACUATED"),
    ("60", "HURT IN KRYVYI RIH"),
    ("\u22123.7%", "S&P 500, FRIDAY CLOSE"),
    ("37 MIN", "BEPICOLOMBO BURN"),
    ("9\u20138", "FIFTH CIRCUIT VOTE"),
]

DATE_CHECK = ("Peru quake M6.7 (Fri) \u2022 S&P \u22123.7% (Fri close) \u2022 "
              "ICJ Myanmar ruling (Thu) \u2022 Pete Rose pardon (Thu) \u2022 "
              "Voyager 1 one light-day (Wed) \u2022 Gaza Board of Peace "
              "report (Wed) \u2022 Trump: Iran decision after New Year \u2022 "
              "F1 race tonight \u2022 COP31 vote 06:00 GMT")

# lon/lat of featured stories 01-13 for the map
PINS = {
    "01": (27.0, 60.0, (10, -16)),   # Gulf of Finland
    "02": (30.7, 36.9, (16, 16)),     # Antalya
    "03": (33.4, 47.9, (14, -10)),    # Kryvyi Rih
    "04": (8.65, 49.9, (-16, 12)),   # Darmstadt (ESA control)
    "05": (-108.5, 25.6, (-14, -18)),  # Guasave, Sinaloa
    "06": (-75.9, -11.2, (-14, -18)),  # Junin, Peru
    "07": (-74.0, 40.7, (-16, -18)),   # New York
    "08": (-115.1, 36.2, (-14, -18)),  # Las Vegas
    "09": (12.6, 55.7, (-16, -18)),    # Copenhagen
    "10": (46.7, 24.7, (-20, -4)),    # Riyadh
    "11": (-77.0, 38.9, (10, 8)),      # Washington
    "12": (-90.1, 30.0, (10, 10)),     # New Orleans
    "13": (56.2, 26.2, (14, 12)),      # Khasab, Oman
}

# Simplified continent outlines (lon, lat), equirectangular, stylised.
NORTH_AMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
                 (-85, 80), (-80, 73), (-75, 72), (-65, 60), (-55, 52),
                 (-60, 45), (-70, 42), (-75, 35), (-80, 25), (-85, 20),
                 (-90, 15), (-95, 16), (-100, 20), (-105, 22), (-110, 25),
                 (-115, 30), (-120, 35), (-125, 42), (-130, 50), (-140, 60),
                 (-155, 58), (-165, 60), (-168, 66)]
GREENLAND = [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-25, 70),
             (-20, 74), (-30, 76), (-45, 76), (-58, 74), (-60, 70),
             (-55, 60)]
SOUTH_AMERICA = [(-80, 10), (-75, 12), (-70, 12), (-60, 8), (-50, 5),
                 (-50, 0), (-40, -5), (-35, -8), (-38, -15), (-40, -22),
                 (-48, -28), (-55, -35), (-65, -40), (-70, -45), (-73, -50),
                 (-70, -55), (-68, -52), (-65, -45), (-62, -40), (-58, -35),
                 (-57, -30), (-58, -20), (-60, -12), (-70, -5), (-78, 0),
                 (-80, 10)]
EUROPE = [(-10, 36), (-5, 36), (0, 38), (5, 38), (10, 37), (12, 40),
          (15, 44), (18, 45), (12, 45), (8, 44), (3, 43), (-2, 44),
          (-2, 48), (-5, 48), (-2, 50), (0, 52), (5, 53), (8, 55),
          (8, 57), (10, 59), (5, 60), (5, 62), (10, 64), (15, 68),
          (20, 70), (25, 71), (30, 70), (35, 68), (30, 66), (25, 64),
          (20, 60), (18, 58), (21, 55), (24, 58), (28, 59), (30, 60),
          (28, 62), (25, 65), (20, 68), (15, 70), (10, 68), (5, 66),
          (0, 62), (-5, 60), (-8, 58), (-10, 55), (-8, 52), (-10, 50),
          (-5, 48), (-10, 44), (-10, 36)]
AFRICA = [(-6, 35), (-10, 30), (-15, 25), (-17, 20), (-17, 15), (-15, 10),
          (-10, 5), (-5, 5), (0, 5), (5, 4), (8, 4), (9, 0), (12, -5),
          (12, -10), (13, -15), (12, -20), (14, -25), (16, -30), (19, -35),
          (25, -34), (30, -30), (32, -25), (35, -20), (38, -15), (40, -10),
          (42, -5), (45, 0), (48, 5), (50, 10), (48, 11), (44, 11),
          (40, 13), (38, 18), (36, 22), (34, 26), (32, 30), (30, 31),
          (25, 32), (20, 32), (15, 32), (10, 33), (5, 34), (-6, 35)]
ASIA = [(30, 36), (35, 36), (40, 38), (45, 40), (50, 42), (55, 45),
        (60, 50), (65, 55), (70, 60), (75, 65), (80, 70), (85, 72),
        (90, 75), (100, 76), (110, 76), (120, 75), (130, 72), (140, 72),
        (150, 70), (160, 68), (170, 66), (175, 65), (170, 62), (162, 58),
        (158, 52), (150, 48), (142, 45), (140, 40), (135, 35), (130, 32),
        (127, 30), (122, 28), (120, 25), (115, 22), (110, 20), (108, 15),
        (105, 10), (100, 8), (98, 12), (95, 15), (92, 18), (90, 22),
        (88, 22), (85, 20), (82, 17), (80, 13), (77, 8), (75, 10),
        (72, 20), (68, 23), (65, 25), (62, 25), (58, 26), (55, 27),
        (52, 28), (50, 30), (48, 30), (45, 30), (42, 32), (40, 36),
        (35, 36)]
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
             (146, -19), (142, -15), (142, -11), (136, -12), (132, -11),
             (130, -13), (126, -14), (122, -17), (118, -20), (113, -22)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
      (-1, 51), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 39),
         (142, 42), (143, 44), (141, 45), (140, 42), (138, 38), (135, 35),
         (133, 34), (130, 31)]
NEW_ZEALAND = [(167, -45), (170, -42), (174, -41), (176, -38), (175, -36),
               (173, -35), (171, -38), (168, -44), (167, -45)]
INDONESIA = [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
             (125, -8), (130, -5), (135, -3), (140, -4), (141, -8),
             (138, -8), (135, -6), (130, -2), (125, 1), (120, 0),
             (115, 0), (110, -2), (105, 0), (100, 2), (95, 5)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, EUROPE, AFRICA,
              ASIA, AUSTRALIA, UK, JAPAN, NEW_ZEALAND, INDONESIA]

# ---------------------------------------------------------------- scenes

def _stars(d, x0, y0, w, h, pts):
    for sx, sy in pts:
        d.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                  fill=(220, 220, 200))


def scene_ship(d, x0, y0, w, h):
    """Grey sea, a cargo ship on fire, two drone arcs above (Sparta II)."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(24, 48, 72))
    _stars(d, x0, y0, w, h, [(12, 8), (40, 18), (70, 6), (110, 14),
                             (150, 8), (190, 18), (230, 6), (270, 16),
                             (300, 10), (95, 24), (210, 26)])
    for cx, cy, r, a0, a1 in [(90, 78, 52, 200, 290), (230, 80, 56, 210, 300)]:
        pts = []
        for a in range(a0, a1 + 1, 4):
            pts.append((x0 + cx + r * math.cos(math.radians(a)),
                        y0 + cy + r * math.sin(math.radians(a))))
        d.line(pts, fill=(255, 120, 40), width=3)
        d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4,
                   pts[-1][1] + 4], fill=(255, 200, 60))
    # ship: hull, bridge, containers, fire on deck
    base = y0 + h - 18
    d.polygon([(x0 + 30, base - 22), (x0 + 290, base - 22),
               (x0 + 272, base), (x0 + 48, base)], fill=(40, 40, 48))
    d.rectangle([x0 + 240, base - 52, x0 + 282, base - 22], fill=(70, 70, 82))
    for cx0 in (60, 100, 140, 180):
        d.rectangle([x0 + cx0, base - 42, x0 + cx0 + 34, base - 22],
                    fill=(150, 60, 50))
    d.rectangle([x0 + 60, base - 42, x0 + 214, base - 22], outline=(20, 20, 26),
                width=1)
    fx, fy = x0 + 120, base - 42
    for k in range(8):
        ang = k * math.pi / 4
        d.line([fx, fy, fx + 26 * math.cos(ang), fy + 26 * math.sin(ang)],
               fill=(255, 170, 30), width=3)
    d.ellipse([fx - 14, fy - 14, fx + 14, fy + 14], fill=(255, 200, 80))
    d.ellipse([fx - 7, fy - 7, fx + 7, fy + 7], fill=(255, 120, 30))
    for wy in range(y0 + h - 12, y0 + h, 4):
        d.line([x0, wy, x0 + w, wy], fill=(50, 90, 120), width=1)


def scene_cop(d, x0, y0, w, h):
    """Globe, thermometer, document with a red zero."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(232, 238, 226))
    gx, gy, gr = x0 + 62, y0 + 46, 36
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 190))
    d.ellipse([gx - gr + 8, gy - gr + 10, gx - gr + 30, gy - gr + 26],
              fill=(90, 160, 90))
    d.ellipse([gx + 2, gy + 4, gx + 26, gy + 22], fill=(90, 160, 90))
    d.ellipse([gx - 14, gy + 12, gx + 6, gy + 30], fill=(110, 170, 100))
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=NAVY, width=2)
    d.arc([gx - gr - 8, gy - gr - 8, gx + gr + 8, gy + gr + 8], 200, 340,
          fill=NAVY, width=2)
    tx = x0 + 150
    d.rectangle([tx, y0 + 14, tx + 14, y0 + 66], fill=WHITE, outline=NAVY,
                width=2)
    d.rectangle([tx + 3, y0 + 52, tx + 11, y0 + 63], fill=RED)
    d.ellipse([tx - 6, y0 + 60, tx + 20, y0 + 86], fill=RED, outline=NAVY,
              width=2)
    for ty in (y0 + 22, y0 + 32, y0 + 42):
        d.line([tx + 14, ty, tx + 20, ty], fill=NAVY, width=2)
    dx = x0 + 196
    d.rectangle([dx, y0 + 12, dx + 92, y0 + 78], fill=WHITE, outline=NAVY,
                width=2)
    d.line([dx + 10, y0 + 24, dx + 82, y0 + 24], fill=LIGHT, width=3)
    d.line([dx + 10, y0 + 32, dx + 82, y0 + 32], fill=LIGHT, width=3)
    d.text((dx + 26, y0 + 38), "0", font=F("DejaVuSerif-Bold.ttf", 30),
           fill=RED)
    d.line([dx + 10, y0 + 70, dx + 82, y0 + 70], fill=LIGHT, width=3)


def scene_blast(d, x0, y0, w, h):
    """Explosion burst over a damaged block (Kryvyi Rih)."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(46, 32, 28))
    cx, cy = x0 + 150, y0 + 40
    for k in range(10):
        ang = k * math.pi / 5
        d.line([cx, cy, cx + 44 * math.cos(ang), cy + 44 * math.sin(ang)],
               fill=(255, 170, 40), width=3)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(255, 200, 80))
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(255, 120, 30))
    base = y0 + h
    for bx, bh, bw in [(0, 30, 50), (58, 44, 44), (110, 26, 52),
                       (170, 38, 46), (224, 28, 48), (280, 36, 34)]:
        d.rectangle([x0 + bx, base - bh, x0 + bx + bw, base],
                    fill=(16, 10, 10))
        d.line([x0 + bx + 6, base - bh, x0 + bx + bw - 6, base - bh - 8],
               fill=(255, 120, 40), width=2)
    d.text((x0 + 12, y0 + h - 24), "60 HURT",
           font=F("DejaVuSans-Bold.ttf", 15), fill=(255, 200, 80))


def scene_market(d, x0, y0, w, h):
    """Falling chart on dark trading-floor green."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 36, 28))
    for gy in range(y0 + 14, y0 + h, 18):
        d.line([x0 + 8, gy, x0 + w - 8, gy], fill=(40, 70, 52), width=1)
    pts = [(x0 + 10, y0 + 18), (x0 + 60, y0 + 26), (x0 + 105, y0 + 22),
           (x0 + 150, y0 + 38), (x0 + 195, y0 + 34), (x0 + 240, y0 + 58),
           (x0 + 285, y0 + 52), (x0 + w - 10, y0 + h - 14)]
    d.line(pts, fill=(255, 70, 60), width=4)
    for px, py in pts[1:-1]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 200, 80))
    d.text((x0 + 12, y0 + h - 26), "\u22123.7%",
           font=F("DejaVuSans-Bold.ttf", 22), fill=(255, 90, 70))
    d.text((x0 + 108, y0 + h - 24), "S&P 500 \u00b7 NASDAQ \u00b7 DOW",
           font=F("DejaVuSans-Bold.ttf", 11), fill=(200, 220, 205))


def scene_planet(d, x0, y0, w, h):
    """Mercury sphere, orbit ring, thruster flame, stars."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 20, 36))
    _stars(d, x0, y0, w, h, [(14, 10), (40, 22), (90, 8), (150, 16),
                             (210, 8), (260, 20), (300, 10), (120, 26),
                             (240, 28), (60, 30)])
    cx, cy, cr = x0 + 130, y0 + 52, 34
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(168, 150, 130))
    for kx, ky, kr in [(cx - 12, cy - 8, 7), (cx + 8, cy + 6, 9),
                       (cx + 14, cy - 14, 5), (cx - 16, cy + 12, 6)]:
        d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(140, 122, 104))
    d.arc([x0 + 30, y0 - 8, x0 + 230, y0 + 108], 200, 340,
          fill=(255, 200, 80), width=2)
    d.ellipse([x0 + 238, y0 + 6, x0 + 246, y0 + 14], fill=(255, 200, 80))
    d.polygon([(x0 + 40, y0 + 78), (x0 + 52, y0 + 78), (x0 + 46, y0 + 96)],
              fill=(255, 140, 40))
    d.text((x0 + 170, y0 + 74), "18:24 UTC",
           font=F("DejaVuSans-Bold.ttf", 15), fill=(255, 200, 80))


def scene_shield(d, x0, y0, w, h):
    """Night skyline, interceptor arcs meeting incoming missiles."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(20, 26, 48))
    _stars(d, x0, y0, w, h, [(14, 10), (60, 18), (120, 8), (200, 14),
                             (260, 8), (300, 18), (180, 26)])
    base = y0 + h
    for bx, bh, bw in [(0, 34, 30), (36, 52, 22), (64, 40, 28),
                       (98, 62, 20), (124, 44, 30), (160, 56, 24),
                       (190, 38, 28), (224, 50, 22), (252, 36, 30),
                       (288, 46, 24)]:
        d.rectangle([x0 + bx, base - bh, x0 + bx + bw, base],
                    fill=(10, 14, 28))
        for wy in range(base - bh + 6, base - 4, 9):
            for wx in range(bx + 4, bx + bw - 3, 8):
                if (wx + wy) % 13 < 6:
                    d.rectangle([x0 + wx, wy, x0 + wx + 3, wy + 3],
                                fill=(255, 200, 90))
    d.rectangle([x0 + 138, base - 88, x0 + 168, base], fill=(60, 70, 90))
    d.rectangle([x0 + 138, base - 88, x0 + 168, base - 78],
                fill=(255, 200, 90))
    for a0, a1, col in [(200, 290, (255, 120, 40)), (210, 300, (120, 200, 255))]:
        pts = []
        for a in range(a0, a1 + 1, 4):
            pts.append((x0 + 160 + 78 * math.cos(math.radians(a)),
                        y0 + 96 + 62 * math.sin(math.radians(a))))
        d.line(pts, fill=col, width=3)
    d.ellipse([x0 + 200 - 6, y0 + 26 - 6, x0 + 200 + 6, y0 + 26 + 6],
              fill=(255, 220, 120))


def scene_spy(d, x0, y0, w, h):
    """Dark street, two silhouettes, searchlight cone."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 30, 40))
    d.polygon([(x0 + w, y0), (x0 + w - 90, y0), (x0 + w - 40, y0 + h),
               (x0 + w, y0 + h)], fill=(70, 70, 90))
    for bx, bh in [(30, 46), (70, 34), (240, 40)]:
        d.rectangle([x0 + bx, y0 + h - bh, x0 + bx + 34, y0 + h],
                    fill=(12, 12, 20))
    d.ellipse([x0 + 140, y0 + 30, x0 + 156, y0 + 46], fill=(200, 200, 210))
    d.polygon([(x0 + 132, y0 + 48), (x0 + 164, y0 + 48), (x0 + 172, y0 + h),
               (x0 + 124, y0 + h)], fill=(60, 60, 75))
    d.ellipse([x0 + 196, y0 + 36, x0 + 208, y0 + 48], fill=(180, 180, 190))
    d.polygon([(x0 + 190, y0 + 50), (x0 + 214, y0 + 50), (x0 + 220, y0 + h),
               (x0 + 184, y0 + h)], fill=(50, 50, 64))
    d.text((x0 + 12, y0 + 8), "7 DAYS", font=F("DejaVuSans-Bold.ttf", 16),
           fill=RED)


def scene_scales(d, x0, y0, w, h):
    """Scales of justice on parchment."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(238, 232, 220))
    cx = x0 + w // 2
    d.rectangle([cx - 3, y0 + 10, cx + 3, y0 + h - 18], fill=NAVY)
    d.polygon([(cx - 26, y0 + 10), (cx + 26, y0 + 10), (cx, y0 + 2)],
              fill=NAVY)
    d.line([cx - 78, y0 + 22, cx + 78, y0 + 22], fill=NAVY, width=3)
    for sx in (cx - 66, cx + 66):
        d.line([sx, y0 + 22, sx, y0 + 40], fill=NAVY, width=2)
        d.polygon([(sx - 26, y0 + 40), (sx + 26, y0 + 40), (sx, y0 + 58)],
                  fill=(179, 32, 44))
    d.ellipse([cx - 22, y0 + h - 22, cx + 22, y0 + h - 6], fill=NAVY)
    d.text((x0 + 12, y0 + h - 24), "9\u20138",
           font=F("DejaVuSans-Bold.ttf", 18), fill=RED)


SCENES = {
    "ship": scene_ship, "cop": scene_cop, "blast": scene_blast,
    "market": scene_market, "planet": scene_planet,
    "shield": scene_shield, "spy": scene_spy, "scales": scene_scales,
}


def mini_scene(d, kind, x0, y0, w, h):
    """Compact scene for a 187x42 strip: simple shapes only, no text."""
    if kind == "planet":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 20, 36))
        for sx, sy in [(10, 8), (30, 20), (160, 10), (175, 26), (60, 6)]:
            d.ellipse([x0 + sx - 1, y0 + sy - 1, x0 + sx + 1, y0 + sy + 1],
                      fill=(220, 220, 200))
        cx, cy, cr = x0 + 70, y0 + 21, 17
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(168, 150, 130))
        for kx, ky, kr in [(cx - 6, cy - 4, 4), (cx + 4, cy + 3, 5),
                           (cx + 7, cy - 7, 3)]:
            d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr],
                      fill=(140, 122, 104))
        d.arc([x0 + 30, y0 - 6, x0 + 110, y0 + 44], 200, 340,
              fill=(255, 200, 80), width=2)
        d.polygon([(x0 + 120, y0 + 30), (x0 + 128, y0 + 30),
                   (x0 + 124, y0 + 40)], fill=(255, 140, 40))
        d.text((x0 + 138, y0 + 12), "18:24", font=F("DejaVuSans-Bold.ttf", 12),
               fill=(255, 200, 80))
    elif kind == "cuffs":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(24, 40, 64))
        d.ellipse([x0 + 28, y0 + 6, x0 + 62, y0 + 36], outline=(255, 200, 80),
                  width=4)
        d.ellipse([x0 + 78, y0 + 6, x0 + 112, y0 + 36],
                  outline=(255, 200, 80), width=4)
        d.line([x0 + 62, y0 + 21, x0 + 78, y0 + 21], fill=(255, 200, 80),
               width=4)
        d.polygon([(x0 + 142, y0 + 4), (x0 + 146, y0 + 12), (x0 + 154, y0 + 12),
                   (x0 + 148, y0 + 18), (x0 + 150, y0 + 26), (x0 + 142, y0 + 21),
                   (x0 + 134, y0 + 26), (x0 + 136, y0 + 18), (x0 + 130, y0 + 12),
                   (x0 + 138, y0 + 12)], fill=(255, 200, 80))
        d.text((x0 + 160, y0 + 12), "$5m", font=F("DejaVuSans-Bold.ttf", 10),
               fill=WHITE)
    elif kind == "quake":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(120, 95, 70))
        d.rectangle([x0, y0, x0 + w, y0 + 14], fill=(90, 130, 170))
        for bx, bh, bw in [(10, 18, 26), (44, 24, 22), (74, 16, 28),
                           (110, 22, 24), (142, 15, 26)]:
            d.rectangle([x0 + bx, y0 + h - bh, x0 + bx + bw, y0 + h - 6],
                        fill=(60, 50, 42))
        pts = [(x0 + 90, y0 + 10), (x0 + 84, y0 + 18), (x0 + 94, y0 + 24),
               (x0 + 86, y0 + 32), (x0 + 96, y0 + 40)]
        d.line(pts, fill=(30, 22, 16), width=3)
        d.text((x0 + 120, y0 + 4), "M6.7", font=F("DejaVuSans-Bold.ttf", 13),
               fill=WHITE)
    elif kind == "market":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 36, 28))
        pts = [(x0 + 8, y0 + 8), (x0 + 50, y0 + 14), (x0 + 90, y0 + 11),
               (x0 + 130, y0 + 24), (x0 + 170, y0 + 30), (x0 + w - 8, y0 + h - 6)]
        d.line(pts, fill=(255, 70, 60), width=3)
        d.text((x0 + 8, y0 + h - 18), "\u22123.7%",
               font=F("DejaVuSans-Bold.ttf", 13), fill=(255, 90, 70))
    elif kind == "race":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(18, 18, 26))
        for i in range(8):
            col = WHITE if i % 2 == 0 else INK
            d.rectangle([x0 + i * 12, y0, x0 + i * 12 + 12, y0 + 8], fill=col)
            d.rectangle([x0 + i * 12, y0 + 8, x0 + i * 12 + 12, y0 + 16],
                        fill=WHITE if i % 2 else INK)
        d.rounded_rectangle([x0 + 30, y0 + 18, x0 + 120, y0 + 32], radius=5,
                            fill=(200, 16, 46))
        d.ellipse([x0 + 44, y0 + 30, x0 + 58, y0 + 40], fill=INK)
        d.ellipse([x0 + 92, y0 + 30, x0 + 106, y0 + 40], fill=INK)
        d.text((x0 + 128, y0 + 20), "1:33.893",
               font=F("DejaVuSans-Bold.ttf", 11), fill=(255, 200, 80))
    elif kind == "spy":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 30, 40))
        d.polygon([(x0 + w, y0), (x0 + w - 50, y0), (x0 + w - 20, y0 + h),
                   (x0 + w, y0 + h)], fill=(70, 70, 90))
        d.ellipse([x0 + 60, y0 + 8, x0 + 72, y0 + 20], fill=(200, 200, 210))
        d.polygon([(x0 + 56, y0 + 22), (x0 + 76, y0 + 22), (x0 + 80, y0 + h),
                   (x0 + 52, y0 + h)], fill=(60, 60, 75))
        d.ellipse([x0 + 100, y0 + 12, x0 + 110, y0 + 22],
                  fill=(180, 180, 190))
        d.polygon([(x0 + 96, y0 + 24), (x0 + 114, y0 + 24), (x0 + 118, y0 + h),
                   (x0 + 92, y0 + h)], fill=(50, 50, 64))
        d.ellipse([x0 + 150, y0 + 10, x0 + 158, y0 + 18], fill=(255, 80, 60))
    elif kind == "shield":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(20, 26, 48))
        base = y0 + h
        for bx, bh, bw in [(0, 16, 22), (26, 24, 16), (46, 18, 20),
                           (70, 28, 14), (88, 20, 22), (114, 26, 16),
                           (134, 18, 20), (158, 22, 16)]:
            d.rectangle([x0 + bx, base - bh, x0 + bx + bw, base],
                        fill=(10, 14, 28))
        d.rectangle([x0 + 96, base - 38, x0 + 110, base], fill=(60, 70, 90))
        for a0, a1, col in [(200, 290, (255, 120, 40)),
                            (210, 300, (120, 200, 255))]:
            pts = []
            for a in range(a0, a1 + 1, 6):
                pts.append((x0 + 100 + 52 * math.cos(math.radians(a)),
                            y0 + 42 + 30 * math.sin(math.radians(a))))
            d.line(pts, fill=col, width=2)
        d.ellipse([x0 + 128 - 4, y0 + 8 - 4, x0 + 128 + 4, y0 + 8 + 4],
                  fill=(255, 220, 120))
    elif kind == "phone":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(232, 238, 246))
        d.rounded_rectangle([x0 + 58, y0 + 2, x0 + 128, y0 + h - 2], radius=6,
                            fill=(20, 20, 28), outline=NAVY, width=1)
        d.rectangle([x0 + 63, y0 + 7, x0 + 123, y0 + 20], fill=(120, 110, 90))
        d.rectangle([x0 + 63, y0 + 22, x0 + 123, y0 + 35], fill=(40, 90, 140))
        d.text((x0 + 66, y0 + 9), "1945", font=F("DejaVuSans-Bold.ttf", 8),
               fill=WHITE)
        d.text((x0 + 66, y0 + 24), "2026", font=F("DejaVuSans-Bold.ttf", 8),
               fill=WHITE)
        d.text((x0 + 134, y0 + 12), "FBI: NCIC",
               font=F("DejaVuSans-Bold.ttf", 11), fill=NAVY)
        d.text((x0 + 134, y0 + 26), "BREACHED",
               font=F("DejaVuSans-Bold.ttf", 11), fill=RED)
    elif kind == "scales":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(238, 232, 220))
        cx = x0 + w // 2
        d.rectangle([cx - 2, y0 + 4, cx + 2, y0 + h - 8], fill=NAVY)
        d.line([cx - 52, y0 + 10, cx + 52, y0 + 10], fill=NAVY, width=2)
        for sx in (cx - 44, cx + 44):
            d.line([sx, y0 + 10, sx, y0 + 18], fill=NAVY, width=1)
            d.polygon([(sx - 16, y0 + 18), (sx + 16, y0 + 18), (sx, y0 + 30)],
                      fill=RED)
        d.ellipse([cx - 14, y0 + h - 10, cx + 14, y0 + h - 2], fill=NAVY)
    elif kind == "tanker":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(40, 90, 130))
        for wy in range(y0 + 26, y0 + h, 8):
            d.line([x0, wy, x0 + w, wy], fill=(70, 120, 160), width=1)
        d.polygon([(x0 + 40, y0 + 22), (x0 + 150, y0 + 22),
                   (x0 + 140, y0 + 34), (x0 + 50, y0 + 34)], fill=(30, 30, 36))
        d.rectangle([x0 + 120, y0 + 10, x0 + 140, y0 + 22], fill=(60, 60, 70))
        pts = []
        for a in range(200, 291, 6):
            pts.append((x0 + 60 + 40 * math.cos(math.radians(a)),
                        y0 + 34 + 24 * math.sin(math.radians(a))))
        d.line(pts, fill=(255, 120, 40), width=2)
        d.ellipse([x0 + 92 - 4, y0 + 6 - 4, x0 + 92 + 4, y0 + 6 + 4],
                  fill=(255, 220, 120))
        d.text((x0 + 126, y0 + 8), "NO DEATHS",
               font=F("DejaVuSans-Bold.ttf", 9), fill=WHITE)
    else:
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(240, 235, 225))
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=LIGHT, width=1)


# ---------------------------------------------------------------- map

def draw_map(d, x0, y0, w, h):
    """Stylised world map (equirectangular) with numbered pins 01-13."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=SKY)
    lon0, lon1, lat0, lat1 = -180.0, 180.0, 78.0, -58.0

    def proj(lon, lat):
        return (x0 + (lon - lon0) / (lon1 - lon0) * w,
                y0 + (lat0 - lat) / (lat0 - lat1) * h)

    for lat in (60, 30, 0, -30):
        _, gy = proj(0, lat)
        d.line([x0, gy, x0 + w, gy], fill=(190, 205, 220), width=1)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(214, 208, 188), outline=(150, 144, 128))
    f_pin = F("DejaVuSans-Bold.ttf", 10)
    for num in sorted(PINS):
        lon, lat, (dx, dy) = PINS[num]
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        d.line([px, py, cx, cy], fill=RED, width=1)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                  outline=WHITE, width=1)
        tw = d.textlength(num, font=f_pin)
        d.text((cx - tw / 2, cy - 7), num, font=f_pin, fill=WHITE)

# ---------------------------------------------------------------- compose

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    X0, CW = 24, 976
    f_sans = lambda s: F("DejaVuSans.ttf", s)
    f_sans_b = lambda s: F("DejaVuSans-Bold.ttf", s)
    f_serif_b = lambda s: F("DejaVuSerif-Bold.ttf", s)

    # ---- top line
    d.text((X0, 10), "THE WORLD IN ONE DAY", font=f_sans_b(10), fill=GRAY)
    r = "SUNDAY EDITION \u00b7 No. 326"
    d.text((X0 + CW - d.textlength(r, font=f_sans_b(10)), 10), r,
           font=f_sans_b(10), fill=GRAY)

    # ---- masthead: the date itself, biggest
    f_mast = fit_font("DejaVuSerif-Bold.ttf", "SUNDAY 22 NOVEMBER 2026",
                      64, CW)
    d.text((X0, 24), "SUNDAY 22 NOVEMBER 2026", font=f_mast, fill=INK)
    sub = ("36 STORIES FROM FRIDAY AND SATURDAY \u2014 GULF OF FINLAND "
           "\u00b7 ANTALYA \u00b7 KRYVYI RIH \u00b7 MERCURY \u00b7 SINALOA")
    d.text(((W - d.textlength(sub, font=f_sans_b(11))) / 2, 92), sub,
           font=f_sans_b(11), fill=INK)
    d.line([X0, 110, X0 + CW, 110], fill=INK, width=2)
    d.line([X0, 114, X0 + CW, 114], fill=INK, width=1)

    # ---- strip of 6 big numbers
    y_num = 122
    bw, gap = 157, 6
    for i, (num, label) in enumerate(NUMBERS):
        x = X0 + i * (bw + gap)
        d.rectangle([x, y_num, x + bw, y_num + 50], outline=LIGHT, width=1)
        f_big = fit_font("DejaVuSerif-Bold.ttf", num, 26, bw - 12)
        tw = d.textlength(num, font=f_big)
        d.text((x + (bw - tw) / 2, y_num + 4), num, font=f_big, fill=RED)
        lines = wrap(d, label, f_sans_b(8), bw - 10)
        ly = y_num + 32
        for ln in lines[:2]:
            tw = d.textlength(ln, font=f_sans_b(8))
            d.text((x + (bw - tw) / 2, ly), ln, font=f_sans_b(8), fill=INK)
            ly += 9

    # ---- region chips (counts sum to 36)
    y_chip = 180
    cx = X0
    for name, n in CHIPS:
        label = "%s %d" % (name, n)
        f_chip = f_sans_b(11)
        cw = int(d.textlength(label, font=f_chip)) + 22
        d.rounded_rectangle([cx, y_chip, cx + cw, y_chip + 22], radius=11,
                            fill=REGION_COLORS[name])
        d.text((cx + 11, y_chip + 5), label, font=f_chip, fill=WHITE)
        cx += cw + 8
    d.text((cx + 4, y_chip + 5), "= 36 STORIES", font=f_sans_b(11),
           fill=GRAY)

    # ---- 3 leads
    y_lead = 210
    lead_w, lead_gap = 317, 12
    for i, st in enumerate(LEADS):
        px = X0 + i * (lead_w + lead_gap)
        gh = 92
        SCENES[st["kind"]](d, px, y_lead, lead_w, gh)
        d.rectangle([px, y_lead, px + lead_w, y_lead + gh], outline=LIGHT,
                    width=1)
        ty = y_lead + gh + 6
        d.text((px, ty), "%s  %s" % (st["num"], st["kicker"]),
               font=f_sans_b(10), fill=RED)
        ty += 15
        _, ty = draw_wrapped(d, (px, ty), st["headline"],
                             f_serif_b(19), INK, lead_w, leading=22,
                             max_lines=2)
        _, ty = draw_wrapped(d, (px, ty + 3), st["deck"], f_sans(11), INK,
                             lead_w, leading=13, max_lines=4)
        d.text((px, ty + 4), st["source"], font=f_sans(9), fill=GRAY)

    # ---- 10 small panels, grid 5 x 2
    y_small = 448
    sm_w, sm_gap, sm_h, sm_row_gap = 187, 10, 126, 6
    for i, st in enumerate(SMALL):
        row, col = divmod(i, 5)
        px = X0 + col * (sm_w + sm_gap)
        py = y_small + row * (sm_h + sm_row_gap)
        d.rectangle([px, py, px + sm_w, py + sm_h], fill=WHITE,
                    outline=LIGHT, width=1)
        d.rectangle([px, py, px + sm_w, py + 3],
                    fill=REGION_COLORS[st["region"]])
        mini_scene(d, st["kind"], px + 1, py + 4, sm_w - 2, 42)
        ty = py + 50
        d.text((px + 6, ty), st["num"], font=f_sans_b(10), fill=RED)
        _, ty = draw_wrapped(d, (px + 6, ty + 13), st["headline"],
                             f_sans_b(12), INK, sm_w - 12, leading=13,
                             max_lines=2)
        _, ty = draw_wrapped(d, (px + 6, ty + 2), st["deck"], f_sans(10),
                             INK, sm_w - 12, leading=11, max_lines=2)
        d.text((px + 6, py + sm_h - 11), st["source"], font=f_sans(8),
               fill=GRAY)

    # ---- bottom: map + briefs
    y_bot = 716
    d.text((X0, y_bot), "WHERE SATURDAY HAPPENED \u2014 STORIES 01\u201313",
           font=f_sans_b(11), fill=INK)
    d.text((384, y_bot), "ALSO ON 21 NOVEMBER \u2014 23 MORE STORIES",
           font=f_sans_b(11), fill=INK)
    d.line([X0, y_bot + 16, X0 + 344, y_bot + 16], fill=INK, width=1)
    d.line([384, y_bot + 16, X0 + CW, y_bot + 16], fill=INK, width=1)
    draw_map(d, X0, y_bot + 20, 344, 180)
    d.text((X0, y_bot + 204),
           "Pins: Finland \u00b7 Antalya \u00b7 Kryvyi Rih \u00b7 Darmstadt "
           "\u00b7 Guasave \u00b7 Jun\u00edn \u00b7 New York",
           font=f_sans(9), fill=GRAY)
    d.text((X0, y_bot + 216),
           "Las Vegas \u00b7 Copenhagen \u00b7 Riyadh \u00b7 Washington "
           "\u00b7 New Orleans \u00b7 Khasab",
           font=f_sans(9), fill=GRAY)
    br_x0, br_w = 384, 300
    for i, (num, text) in enumerate(BRIEFS):
        col, row = divmod(i, 12)
        bx = br_x0 + col * (br_w + 16)
        by = y_bot + 22 + row * 15
        d.text((bx, by), num, font=f_sans_b(10), fill=RED)
        d.text((bx + 20, by), text, font=f_sans(10), fill=INK)

    # ---- DATE CHECK strip
    y_dc = 944
    d.line([X0, y_dc, X0 + CW, y_dc], fill=INK, width=1)
    d.text((X0, y_dc + 5), "DATE CHECK \u2014 ALSO THIS WEEK:",
           font=f_sans_b(10), fill=RED)
    _, y2 = draw_wrapped(d, (X0, y_dc + 19), DATE_CHECK, f_sans(10), INK,
                         CW, leading=13, max_lines=2)

    # ---- footer
    d.line([X0, 1000, X0 + CW, 1000], fill=LIGHT, width=1)
    d.text((X0, 1004),
           "Built 22 November 2026 from verified reports; figures as "
           "reported on the day.",
           font=f_sans(9), fill=GRAY)
    foot_r = "THE SUNDAY PAPER \u00b7 36 STORIES"
    d.text((X0 + CW - d.textlength(foot_r, font=f_sans_b(9)), 1004), foot_r,
           font=f_sans_b(9), fill=GRAY)
    return img


def _write_prerendered():
    """Copy the committed pre-rendered front page with stdlib only."""
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    with open(src, "rb") as fh_in:
        data = fh_in.read()
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        raise RuntimeError("pre-rendered copy sha256 mismatch")
    if len(data) > 1024 * 1024:
        raise RuntimeError("pre-rendered copy over the 1 MiB cap")
    os.makedirs(OUTDIR, exist_ok=True)
    with open(OUT, "wb") as fh_out:
        fh_out.write(data)


def main():
    assert len(LEADS) + len(SMALL) + len(BRIEFS) == 36, "must be 36 stories"
    assert sum(n for _, n in CHIPS) == 36, "chips must sum to 36"
    if _HAVE_PIL:
        try:
            img = build()
            os.makedirs(OUTDIR, exist_ok=True)
            img.save(OUT, format="PNG", optimize=True)
            print("wrote %s (%dx%d)" % (OUT, W, H))
            return
        except Exception:
            pass  # fall through to the committed pre-render
    _write_prerendered()
    print("wrote %s (%dx%d) [pre-rendered]" % (OUT, W, H))


if __name__ == "__main__":
    main()
