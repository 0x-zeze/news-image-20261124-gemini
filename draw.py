"""Pure Python 3 stdlib newspaper renderer for The Global Edition (Tuesday 24 November 2026)."""

import base64
import math
import os
import struct
import zlib

from assets import FONT_B64, LAND_B64

W, H = 1024, 1024

# Editorial broadsheet palette
BG = (247, 243, 234)
INK = (22, 22, 24)
MUTED = (92, 88, 80)
RULE = (188, 180, 165)
RULE_LIGHT = (226, 220, 206)
TINT_BAR = (237, 231, 217)
TINT_CHECK = (240, 233, 220)
OCEAN = (218, 232, 241)
GRAT = (196, 214, 226)
LAND = (214, 209, 189)
COAST = (140, 135, 118)
WHITE = (255, 255, 255)
CHECK_ACCENT = (145, 52, 38)

REGION_COLORS = {
    "Europe": (29, 78, 137),
    "Middle East": (166, 38, 38),
    "Asia-Pacific": (15, 107, 91),
    "Americas": (176, 86, 14),
    "Africa": (107, 45, 122),
}

REGION_CODES = {
    "Europe": "EU",
    "Middle East": "ME",
    "Asia-Pacific": "AP",
    "Americas": "AM",
    "Africa": "AF",
}

# (id, region, headline, source, status, utc, lat, lon)
STORIES = [
    # EUROPE (10)
    (1, "Europe", "Russian strike on Zaporizhzhia kills 2, wounds 22", "Reuters", "C", "04:18", 47.84, 35.14),
    (2, "Europe", "Hacked Rosstat data puts Russian war dead near 500,000", "Guardian", "R", "01:02", 55.75, 37.62),
    (3, "Europe", "Russia claims drone strikes on Starlink sites in Sumy", "TOI / TASS", "R", "03:56", 50.91, 34.80),
    (4, "Europe", "Zelensky urges four-way peace talks with US, EU, Russia", "France 24", "C", "00:30", 50.45, 30.52),
    (5, "Europe", "Denmark Supreme Court upholds 'ghetto law' evictions", "Al Jazeera", "C", "04:52", 55.68, 12.57),
    (6, "Europe", "HRW reports violent Croatia migrant pushbacks to Bosnia", "HRW", "R", "05:00", 45.81, 15.98),
    (7, "Europe", "European gas prices surge as Arctic cold snap arrives", "Guardian", "C", "02:30", 52.37, 4.90),
    (8, "Europe", "EU risks leaving €85bn on table in UN global tax talks", "TJN", "R", "00:07", 50.85, 4.35),
    (9, "Europe", "Unilever shift from TV to influencers hits UK Channel 4", "Guardian", "R", "05:00", 51.51, -0.13),
    (10, "Europe", "Bank of France moves to boost scarce €5 banknote supply", "Le Monde", "C", "00:38", 48.86, 2.35),
    # MIDDLE EAST (10)
    (11, "Middle East", "IRGC says 3 oil tankers ablaze after hitting Hormuz mines", "Al Jazeera", "R", "00:00", 26.57, 56.25),
    (12, "Middle East", "Israeli strike kills at least 3 Palestinians in Khan Younis", "MEE / ST", "R", "00:22", 31.34, 34.30),
    (13, "Middle East", "Bus-truck collision kills 11 in UAE's Ras Al Khaimah", "The National", "C", "05:20", 25.79, 55.94),
    (14, "Middle East", "UAE & ADEX launch cross-border AI push at Abu Dhabi forum", "The National", "C", "04:00", 24.45, 54.38),
    (15, "Middle East", "Qatar PM seeks to revive US–Iran talks after Rubio meeting", "Al Jazeera", "C", "01:32", 25.29, 51.53),
    (16, "Middle East", "Iraqi forces enter Iran-backed militia stronghold", "Iran Intl", "R", "03:00", 33.31, 44.37),
    (17, "Middle East", "Israeli army raids southern Syrian village amid tensions", "MEE", "R", "02:16", 33.12, 35.82),
    (18, "Middle East", "Iran speaker warns US seeks stalemate, urges deterrence", "A News", "C", "03:53", 35.69, 51.39),
    (19, "Middle East", "US senators urge Rubio to expand Gaza flood relief aid", "US Senate", "C", "04:14", 31.50, 34.47),
    (20, "Middle East", "Brent falls 3.5% as Gulf supply offsets Hormuz threat", "CNA / OGME", "C", "02:56", 24.71, 46.67),
    # ASIA-PACIFIC (12)
    (21, "Asia-Pacific", "South Korea scrambles jets, alerts island over Russian planes", "Guardian", "C", "03:35", 37.50, 130.86),
    (22, "Asia-Pacific", "China to launch Shenzhou-24 with first foreign astronaut", "SCMP / CNA", "C", "01:21", 40.96, 100.29),
    (23, "Asia-Pacific", "China graft watchdog probes science official Liu Min", "SCMP", "C", "04:57", 39.90, 116.41),
    (24, "Asia-Pacific", "Malaysia advises data centres to cut blacklisted US firms", "CNA", "C", "05:52", 3.14, 101.69),
    (25, "Asia-Pacific", "Australia backs 5% global revenue fines for Big Tech harms", "Guardian", "C", "02:26", -35.28, 149.13),
    (26, "Asia-Pacific", "Ousted Bangladesh PM Hasina asks to return on Dec 16", "CNA / TOI", "C", "03:06", 23.81, 90.41),
    (27, "Asia-Pacific", "HRW report warns of deepening authoritarianism in India", "DW", "R", "04:33", 28.61, 77.21),
    (28, "Asia-Pacific", "Singapore PM vows AI chip crackdown; Q3 exports +45.8%", "CNA / SCMP", "C", "02:47", 1.35, 103.82),
    (29, "Asia-Pacific", "NASA: Submarine eruption extends Japan's Iwo Jima beach", "NASA", "C", "05:01", 24.78, 141.32),
    (30, "Asia-Pacific", "North Korea threatens to close Swiss diplomatic office", "Japan Times", "R", "03:29", 39.04, 125.76),
    (31, "Asia-Pacific", "Japan & South Korea stocks surge on Huang Nvidia return", "SCMP / JT", "C", "02:55", 35.68, 139.65),
    (32, "Asia-Pacific", "India tests all bottled water brands after Bisleri alert", "Al Jazeera", "C", "04:44", 19.08, 72.88),
    # AMERICAS (10)
    (33, "Americas", "SpaceX and Tesla tap five directors for merger talks", "FT / CNA", "R", "05:23", 30.27, -97.74),
    (34, "Americas", "Appeals court clears US Army toxic explosives blast in Iowa", "BBC / Guard.", "C", "02:25", 40.83, -91.26),
    (35, "Americas", "Commanders edge Bengals 22–20 after stadium lights fail", "Guardian", "C", "04:43", 38.91, -76.86),
    (36, "Americas", "Car bomb hits Meta governor's office in Villavicencio", "Al Jazeera", "C", "04:49", 4.14, -73.63),
    (37, "Americas", "Dominica jails 2 Americans for life in tech founder murder", "Straits Times", "C", "02:07", 15.30, -61.39),
    (38, "Americas", "Lula fiscal plan approved to calm Brazilian real selloff", "Bloomberg", "C", "03:50", -15.79, -47.88),
    (39, "Americas", "Peru's Lima stock exchange slides 21% from record high", "Latin Times", "C", "04:46", -12.05, -77.04),
    (40, "Americas", "Bukele details deaths of Salvadoran troops deployed in Haiti", "Al Jazeera", "C", "01:06", 18.54, -72.34),
    (41, "Americas", "Wolbachia mosquito trials cut arboviral disease in Brazil", "Med. Xpress", "R", "02:40", -22.91, -43.17),
    (42, "Americas", "Lawmakers rip Trump after claim he 'convinced' Nvidia", "BBC / Guard.", "C", "04:36", 38.91, -77.04),
    # AFRICA (8)
    (43, "Africa", "UN ECA urges Africa to turn health pledges into action", "UN ECA", "C", "04:23", 9.03, 38.74),
    (44, "Africa", "Libya UN-backed govt condemns Kyiv Benghazi ship strike", "Guardian", "C", "01:08", 32.89, 13.19),
    (45, "Africa", "Libya's Sharara oil pipeline restarts, easing supply fears", "OGME", "C", "05:00", 26.59, 12.17),
    (46, "Africa", "Nigeria's Borno school enrolment nearly doubles post-war", "Al Jazeera", "C", "00:02", 11.83, 13.15),
    (47, "Africa", "South Africa rallies on GBV after Facebook murder case", "BBC Africa", "R", "00:02", -26.20, 28.05),
    (48, "Africa", "ArcelorMittal reaches preliminary R10bn South Africa exit", "Yahoo Fin.", "R", "03:20", -26.71, 27.84),
    (49, "Africa", "Nigeria INEC picks 17,676 polling units for mock BVAS", "Punch NG", "C", "01:50", 9.08, 7.40),
    (50, "Africa", "Egypt's Al Ahly dismiss coach Ammouta after Pyramids loss", "CNA", "C", "02:00", 30.04, 31.24),
]

TIMELINE = [
    ("00:22", "Middle East", "Israeli strike kills at least 3 in Gaza's Khan Younis", "MEE / ST"),
    ("01:21", "Asia-Pacific", "China names Pakistani astronaut for Shenzhou-24", "SCMP / CNA"),
    ("02:00", "Africa", "Egypt's Al Ahly dismiss coach Ammouta after loss", "CNA"),
    ("03:35", "Asia-Pacific", "S. Korea scrambles jets as Russian planes near ADIZ", "Guardian"),
    ("04:18", "Europe", "Russian strike kills 2, wounds 22 in Zaporizhzhia", "Reuters"),
    ("05:20", "Middle East", "Bus-truck crash kills 11 in UAE's Ras Al Khaimah", "The National"),
    ("05:23", "Americas", "SpaceX and Tesla name 5 directors for merger talks", "FT / CNA"),
    ("05:52", "Asia-Pacific", "Malaysia tells data centres to cut blacklisted firms", "CNA"),
]

DATE_CHECK = [
    ("23 Nov", "Nvidia reinstates Jensen Huang as CEO (CBS / Wikipedia)"),
    ("23 Nov 23:16", "US blacklists Singapore AI firm Megaspeed (BBC World)"),
    ("23 Nov 22:33", "NATO space-defence vow; UN chief AI call (F24 / UN News)"),
    ("23 Nov", "Israel Flydubai OK; West Bank & COGAT talks (AJ / JPost)"),
    ("23 Nov", "Trump hush-money ruling; Mexico 'Chapo Isidro' remarks (AJ)"),
    ("23 Nov", "Estonia–Russia row; ship-cyber probe; COP31 fails (JT / ST)"),
]


def _load_fonts():
    raw = zlib.decompress(base64.b64decode(FONT_B64))
    pos = 0
    (nfonts,) = struct.unpack_from(">H", raw, pos)
    pos += 2
    fonts = {}
    for _ in range(nfonts):
        (nlen,) = struct.unpack_from(">B", raw, pos)
        pos += 1
        name = raw[pos : pos + nlen].decode("ascii")
        pos += nlen
        ascent, descent, nglyphs = struct.unpack_from(">HHH", raw, pos)
        pos += 6
        glyphs = {}
        for _ in range(nglyphs):
            cp, adv, x0, y0, gw, gh = struct.unpack_from(">IbbbbB", raw, pos)
            pos += 9
            nbytes = gw * gh
            bmp = raw[pos : pos + nbytes] if nbytes else b""
            pos += nbytes
            glyphs[chr(cp)] = (adv, x0, y0, gw, gh, bmp)
        fonts[name] = (ascent, descent, glyphs)
    return fonts


def _load_land():
    raw = zlib.decompress(base64.b64decode(LAND_B64))
    pos = 0
    (nrings,) = struct.unpack_from(">H", raw, pos)
    pos += 2
    rings = []
    for _ in range(nrings):
        (npts,) = struct.unpack_from(">H", raw, pos)
        pos += 2
        pts = []
        for _ in range(npts):
            x10, y10 = struct.unpack_from(">hh", raw, pos)
            pos += 4
            pts.append((x10 * 0.1, y10 * 0.1))
        rings.append(pts)
    return rings


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))
        self.fonts = _load_fonts()

    def set_px(self, x, y, col, a=255):
        if x < 0 or y < 0 or x >= self.w or y >= self.h or a <= 0:
            return
        idx = (y * self.w + x) * 3
        if a >= 255:
            self.buf[idx] = col[0]
            self.buf[idx + 1] = col[1]
            self.buf[idx + 2] = col[2]
        else:
            inv = 255 - a
            self.buf[idx] = (col[0] * a + self.buf[idx] * inv + 127) // 255
            self.buf[idx + 1] = (col[1] * a + self.buf[idx + 1] * inv + 127) // 255
            self.buf[idx + 2] = (col[2] * a + self.buf[idx + 2] * inv + 127) // 255

    def fill_rect(self, x0, y0, x1, y1, col):
        x0 = max(0, int(x0))
        y0 = max(0, int(y0))
        x1 = min(self.w, int(x1))
        y1 = min(self.h, int(y1))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(col) * (x1 - x0)
        stride = self.w * 3
        for y in range(y0, y1):
            i = y * stride + x0 * 3
            self.buf[i : i + len(row)] = row

    def stroke_rect(self, x0, y0, x1, y1, col, t=1):
        self.fill_rect(x0, y0, x1, y0 + t, col)
        self.fill_rect(x0, y1 - t, x1, y1, col)
        self.fill_rect(x0, y0, x0 + t, y1, col)
        self.fill_rect(x1 - t, y0, x1, y1, col)

    def hline(self, x0, x1, y, col, t=1):
        self.fill_rect(x0, y, x1, y + t, col)

    def vline(self, x, y0, y1, col, t=1):
        self.fill_rect(x, y0, x + t, y1, col)

    def fill_rounded_rect(self, x0, y0, x1, y1, r, col):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        self.fill_rect(x0 + r, y0, x1 - r, y1, col)
        self.fill_rect(x0, y0 + r, x1, y1 - r, col)
        corners = [
            (x0 + r, y0 + r, x0, y0, x0 + r, y0 + r),
            (x1 - r - 1, y0 + r, x1 - r, y0, x1, y0 + r),
            (x0 + r, y1 - r - 1, x0, y1 - r, x0 + r, y1),
            (x1 - r - 1, y1 - r - 1, x1 - r, y1 - r, x1, y1),
        ]
        for cx, cy, bx0, by0, bx1, by1 in corners:
            for py in range(by0, by1):
                for px in range(bx0, bx1):
                    d = math.hypot(px - cx, py - cy)
                    if d <= r - 0.5:
                        self.set_px(px, py, col, 255)
                    elif d < r + 0.5:
                        self.set_px(px, py, col, int(round((r + 0.5 - d) * 255)))

    def fill_circle_aa(self, cx, cy, r, col, ring_col=None, ring_w=1.0):
        outer = r + (ring_w if ring_col else 0.0)
        x0 = max(0, int(math.floor(cx - outer - 1)))
        x1 = min(self.w - 1, int(math.ceil(cx + outer + 1)))
        y0 = max(0, int(math.floor(cy - outer - 1)))
        y1 = min(self.h - 1, int(math.ceil(cy + outer + 1)))
        for py in range(y0, y1 + 1):
            dy = py - cy
            for px in range(x0, x1 + 1):
                d = math.hypot(px - cx, dy)
                if ring_col:
                    if d <= r - 0.5:
                        self.set_px(px, py, col, 255)
                    elif d < r + 0.5:
                        t = r + 0.5 - d
                        mix = (
                            int(col[0] * t + ring_col[0] * (1 - t)),
                            int(col[1] * t + ring_col[1] * (1 - t)),
                            int(col[2] * t + ring_col[2] * (1 - t)),
                        )
                        self.set_px(px, py, mix, 255)
                    elif d <= outer - 0.5:
                        self.set_px(px, py, ring_col, 255)
                    elif d < outer + 0.5:
                        self.set_px(px, py, ring_col, int(round((outer + 0.5 - d) * 255)))
                else:
                    if d <= r - 0.5:
                        self.set_px(px, py, col, 255)
                    elif d < r + 0.5:
                        self.set_px(px, py, col, int(round((r + 0.5 - d) * 255)))

    def draw_line_aa(self, x0, y0, x1, y1, col, alpha=255):
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0, x1, y1 = y0, x0, y1, x1
        if x0 > x1:
            x0, x1, y0, y1 = x1, x0, y1, y0
        dx = x1 - x0
        dy = y1 - y0
        grad = dy / dx if dx != 0 else 0.0

        def plot(px, py, br):
            a = int(round(br * alpha))
            if steep:
                self.set_px(py, px, col, a)
            else:
                self.set_px(px, py, col, a)

        xend = round(x0)
        yend = y0 + grad * (xend - x0)
        xgap = 1 - ((x0 + 0.5) - math.floor(x0 + 0.5))
        xpxl1 = int(xend)
        ypxl1 = int(math.floor(yend))
        plot(xpxl1, ypxl1, (1 - (yend - math.floor(yend))) * xgap)
        plot(xpxl1, ypxl1 + 1, (yend - math.floor(yend)) * xgap)
        intery = yend + grad

        xend = round(x1)
        yend = y1 + grad * (xend - x1)
        xgap = (x1 + 0.5) - math.floor(x1 + 0.5)
        xpxl2 = int(xend)
        ypxl2 = int(math.floor(yend))
        plot(xpxl2, ypxl2, (1 - (yend - math.floor(yend))) * xgap)
        plot(xpxl2, ypxl2 + 1, (yend - math.floor(yend)) * xgap)

        for x in range(xpxl1 + 1, xpxl2):
            iy = int(math.floor(intery))
            f = intery - iy
            plot(x, iy, 1 - f)
            plot(x, iy + 1, f)
            intery += grad

    def fill_polygon(self, pts, fill_col, stroke_col=None, clip=None):
        if len(pts) < 3:
            return
        min_y = int(math.floor(min(p[1] for p in pts)))
        max_y = int(math.ceil(max(p[1] for p in pts)))
        cx0, cy0, cx1, cy1 = clip if clip else (0, 0, self.w, self.h)
        y_start = max(cy0, min_y)
        y_end = min(cy1 - 1, max_y)
        n = len(pts)
        stride = self.w * 3
        for y in range(y_start, y_end + 1):
            yf = y + 0.5
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= yf < y2) or (y2 <= yf < y1):
                    xs.append(x1 + (yf - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xa = max(cx0, int(math.ceil(xs[i])))
                xb = min(cx1, int(math.floor(xs[i + 1])) + 1)
                if xb > xa:
                    row = bytes(fill_col) * (xb - xa)
                    idx = y * stride + xa * 3
                    self.buf[idx : idx + len(row)] = row
        if stroke_col:
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                # Skip antimeridian wrap lines if any
                if abs(x2 - x1) < 120:
                    self.draw_line_aa(x1, y1, x2, y2, stroke_col, 190)

    def measure_text(self, text, font_name):
        _, _, glyphs = self.fonts[font_name]
        w = 0
        for ch in text:
            g = glyphs.get(ch) or glyphs.get("?")
            w += g[0]
        return w

    def draw_text(self, x, y, text, font_name, col, align="left"):
        _, _, glyphs = self.fonts[font_name]
        tw = self.measure_text(text, font_name)
        if align == "center":
            cx = int(round(x - tw / 2))
        elif align == "right":
            cx = int(round(x - tw))
        else:
            cx = int(round(x))
        iy = int(round(y))
        start_x = cx
        for ch in text:
            g = glyphs.get(ch) or glyphs.get("?")
            adv, x0, y0, gw, gh, bmp = g
            if gw and gh:
                gx = cx + x0
                gy = iy + y0
                for py in range(gh):
                    yy = gy + py
                    if yy < 0 or yy >= self.h:
                        continue
                    row_off = py * gw
                    for px in range(gw):
                        a = bmp[row_off + px]
                        if a:
                            self.set_px(gx + px, yy, col, a)
            cx += adv
        return start_x, cx


def write_png(path, w, h, rgb_buf):
    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    # PNG Sub filter (type 1) per scanline for compact deterministic compression
    stride = w * 3
    filtered = bytearray()
    for y in range(h):
        filtered.append(1)
        row = rgb_buf[y * stride : (y + 1) * stride]
        filtered.extend(row[:3])
        for i in range(3, stride):
            filtered.append((row[i] - row[i - 3]) & 0xFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(filtered), 9)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def _relax_pins(pins, x0, y0, map_w, map_h, min_dist=11.5):
    """Deterministic repulsion so numbered map pins never overlap while staying near true anchors."""
    pos = [[p["tx"], p["ty"]] for p in pins]
    pad = 7.0
    for _ in range(85):
        for i in range(len(pos)):
            # Gentle spring toward true equirectangular anchor
            pos[i][0] += (pins[i]["tx"] - pos[i][0]) * 0.06
            pos[i][1] += (pins[i]["ty"] - pos[i][1]) * 0.06
            for j in range(i + 1, len(pos)):
                dx = pos[j][0] - pos[i][0]
                dy = pos[j][1] - pos[i][1]
                d = math.hypot(dx, dy)
                if d < min_dist:
                    if d < 0.01:
                        ang = (i * 2.399963 + j * 0.7) % (2 * math.pi)
                        dx, dy, d = math.cos(ang), math.sin(ang), 1.0
                    push = (min_dist - d) * 0.52
                    ux, uy = dx / d, dy / d
                    pos[i][0] -= ux * push
                    pos[i][1] -= uy * push
                    pos[j][0] += ux * push
                    pos[j][1] += uy * push
        for p in pos:
            p[0] = max(x0 + pad, min(x0 + map_w - pad, p[0]))
            p[1] = max(y0 + pad, min(y0 + map_h - pad, p[1]))
    return pos


def render(out_path):
    c = Canvas(W, H, BG)
    L, R = 18, 1006

    # --- 1. MASTHEAD (y = 12..84) ---
    c.hline(L, R, 12, INK, 2)
    c.hline(L, R, 16, INK, 1)

    # Left ear box
    c.stroke_rect(L, 22, 198, 60, RULE, 1)
    c.draw_text(108, 25, "ONE-DAY WORLD BRIEF", "tiny_b", INK, "center")
    c.draw_text(108, 37, f"{len(STORIES)} VERIFIED STORIES", "tiny", MUTED, "center")
    c.draw_text(108, 48, "WINDOW: 00:00–05:55 UTC", "tiny", MUTED, "center")

    # Center masthead
    c.draw_text(512, 18, "The Global Edition", "masthead", INK, "center")

    # Right ear box
    c.stroke_rect(826, 22, R, 60, RULE, 1)
    c.draw_text(916, 25, "TUESDAY 24 NOV 2026", "tiny_b", INK, "center")
    c.draw_text(916, 37, "5 REGIONS · 18+ SOURCES", "tiny", MUTED, "center")
    c.draw_text(916, 48, "STDLIB PURE-PYTHON", "tiny", MUTED, "center")

    # Dateline bar
    c.fill_rect(L, 64, R, 83, TINT_BAR)
    c.hline(L, R, 64, INK, 1)
    c.hline(L, R, 83, INK, 1)
    c.draw_text(L + 6, 68, "TUESDAY 24 NOVEMBER 2026", "small_b", INK, "left")
    c.draw_text(512, 68, "ALL STORIES HAPPENED OR FIRST REPORTED 24 NOV 2026", "small", MUTED, "center")
    c.draw_text(R - 6, 68, "[C] CONFIRMED · [R] REPORTED", "small_b", INK, "right")

    # --- 2. TOP VISUAL BAND: WORLD MAP (LEFT) + TIMELINE & DATE CHECK (RIGHT) ---
    # World map: exact 2:1 equirectangular (480 x 240)
    map_x0, map_y0, map_w, map_h = L, 104, 480, 240
    c.fill_rect(L, 89, L + map_w, 104, INK)
    c.draw_text(L + 6, 91, "WORLD MAP · 50 NUMBERED PINS", "tiny_b", WHITE, "left")
    # Compact legend inside map header bar
    lx = L + 240
    for reg in ("Europe", "Middle East", "Asia-Pacific", "Americas", "Africa"):
        c.fill_circle_aa(lx + 4, 96.5, 3.3, REGION_COLORS[reg], WHITE, 0.7)
        _, lx = c.draw_text(lx + 10, 91, REGION_CODES[reg], "tiny_b", WHITE, "left")
        lx += 11
    c.draw_text(L + map_w - 5, 91, "NE 1:110M", "tiny", (195, 195, 195), "right")

    # Ocean & graticule
    c.fill_rect(map_x0, map_y0, map_x0 + map_w, map_y0 + map_h, OCEAN)
    for lon in range(-150, 180, 30):
        gx = int(round(map_x0 + (lon + 180.0) / 360.0 * map_w))
        c.vline(gx, map_y0, map_y0 + map_h, GRAT, 1)
    for lat in range(-60, 90, 30):
        gy = int(round(map_y0 + (90.0 - lat) / 180.0 * map_h))
        c.hline(map_x0, map_x0 + map_w, gy, (175, 197, 212) if lat == 0 else GRAT, 1)

    # Natural Earth 1:110m land polygons (equirectangular projection)
    clip = (map_x0, map_y0, map_x0 + map_w, map_y0 + map_h)
    for ring in _load_land():
        pts = [
            (map_x0 + (lon + 180.0) / 360.0 * map_w, map_y0 + (90.0 - lat) / 180.0 * map_h)
            for lon, lat in ring
        ]
        c.fill_polygon(pts, LAND, COAST, clip=clip)

    # Numbered pins at equirectangular coords with collision-free markers + leader lines
    pins = []
    for sid, reg, _hl, _src, _st, _utc, lat, lon in STORIES:
        tx = map_x0 + (lon + 180.0) / 360.0 * map_w
        ty = map_y0 + (90.0 - lat) / 180.0 * map_h
        pins.append({"id": sid, "reg": reg, "tx": tx, "ty": ty})
    placed = _relax_pins(pins, map_x0, map_y0, map_w, map_h, min_dist=12.0)

    # Draw anchor dots + leader lines first so pins sit cleanly on top
    for p, (px, py) in zip(pins, placed):
        if math.hypot(px - p["tx"], py - p["ty"]) > 3.5:
            c.draw_line_aa(p["tx"], p["ty"], px, py, (70, 70, 70), 170)
            c.fill_circle_aa(p["tx"], p["ty"], 1.5, INK)

    for p, (px, py) in zip(pins, placed):
        col = REGION_COLORS[p["reg"]]
        c.fill_circle_aa(px, py, 5.1, col, WHITE, 0.85)
        lbl = str(p["id"])
        c.draw_text(px, py - 4.5, lbl, "pin", WHITE, "center")

    c.stroke_rect(map_x0, map_y0, map_x0 + map_w, map_y0 + map_h, INK, 1)

    # --- RIGHT OF MAP: UTC TIMELINE (y = 89..226) + DATE CHECK (y = 232..344) ---
    rx0, rx1 = 508, R
    # UTC Timeline Strip
    c.fill_rect(rx0, 89, rx1, 104, INK)
    c.draw_text(rx0 + 6, 91, "UTC TIMELINE · 8 VERIFIED TIMESTAMPS (24 NOV 2026)", "tiny_b", WHITE, "left")
    c.stroke_rect(rx0, 104, rx1, 226, RULE, 1)
    rail_x = rx0 + 49
    c.vline(rail_x, 110, 220, RULE, 1)
    for i, (t_utc, reg, desc, src) in enumerate(TIMELINE):
        ty = 107 + i * 14.5
        if i % 2 == 1:
            c.fill_rect(rx0 + 1, int(ty) - 1, rx1 - 1, int(ty) + 13, (242, 238, 228))
        c.draw_text(rx0 + 6, ty, t_utc, "small_b", INK, "left")
        c.fill_circle_aa(rail_x + 0.5, ty + 5.5, 3.2, REGION_COLORS[reg], WHITE, 0.6)
        _, hx1 = c.draw_text(rx0 + 58, ty, desc, "small", INK, "left")
        sx0, _ = c.draw_text(rx1 - 5, ty + 0.5, src, "tiny", MUTED, "right")
        assert hx1 + 4 <= sx0, f"Timeline overflow on {t_utc}: {hx1} vs {sx0}"

    # DATE CHECK Box
    dc_y0, dc_y1 = 232, 344
    c.fill_rect(rx0, dc_y0, rx1, dc_y1, TINT_CHECK)
    c.fill_rect(rx0, dc_y0, rx1, dc_y0 + 15, CHECK_ACCENT)
    c.draw_text(rx0 + 6, dc_y0 + 2, "DATE CHECK · EXCLUDED (23 NOV 2026 OR EARLIER)", "tiny_b", WHITE, "left")
    c.fill_rect(rx0, dc_y0 + 15, rx0 + 3, dc_y1, CHECK_ACCENT)
    c.stroke_rect(rx0, dc_y0, rx1, dc_y1, CHECK_ACCENT, 1)
    for i, (dt_lbl, text) in enumerate(DATE_CHECK):
        dy = dc_y0 + 19 + i * 15
        _, dx1 = c.draw_text(rx0 + 8, dy, dt_lbl, "tiny_b", CHECK_ACCENT, "left")
        _, tx1 = c.draw_text(rx0 + 78, dy, text, "small", INK, "left")
        assert tx1 <= rx1 - 4, f"DATE CHECK overflow on row {i}: {tx1} > {rx1 - 4}"

    # --- 3. MAIN STORY LIST GROUPED BY REGION (y = 351..986) ---
    c.vline(512, 352, 985, RULE, 1)

    by_region = {}
    for st in STORIES:
        by_region.setdefault(st[1], []).append(st)

    def draw_region_block(reg, x0, x1, y_top, row_h=20):
        col = REGION_COLORS[reg]
        items = by_region[reg]
        # Section header
        c.fill_rect(x0, y_top, x1, y_top + 18, col)
        c.draw_text(x0 + 6, y_top + 2.5, f"{reg.upper()} ({len(items)})", "sec", WHITE, "left")
        c.draw_text(x1 - 6, y_top + 3.5, f"PINS #{items[0][0]}–#{items[-1][0]}", "tiny_b", (232, 232, 232), "right")
        y = y_top + 19
        for idx, (sid, _r, headline, src, status, utc, _lat, _lon) in enumerate(items):
            if idx % 2 == 1:
                c.fill_rect(x0, y, x1, y + row_h, (242, 238, 229))
            # Pin number badge
            c.fill_rounded_rect(x0 + 2, y + 3, x0 + 20, y + 16, 3, col)
            c.draw_text(x0 + 11, y + 4.5, f"{sid:02d}", "tiny_b", WHITE, "center")
            # Headline
            _, hx1 = c.draw_text(x0 + 25, y + 3.5, headline, "body", INK, "left")
            # Right-aligned source + attribution tag
            tag = f"{src} [{status}]"
            sx0, _ = c.draw_text(x1 - 3, y + 4.5, tag, "tiny", MUTED, "right")
            assert hx1 + 5 <= sx0, f"Story #{sid} overlap: headline ends {hx1}, tag starts {sx0}"
            c.hline(x0, x1, y + row_h - 1, RULE_LIGHT, 1)
            y += row_h
        return y

    # Left column: Europe (10), Middle East (10), Africa (8)
    yl = draw_region_block("Europe", L, 506, 352, row_h=20)
    yl = draw_region_block("Middle East", L, 506, yl + 7, row_h=20)
    yl = draw_region_block("Africa", L, 506, yl + 7, row_h=20)

    # Right column: Asia-Pacific (12), Americas (10)
    yr = draw_region_block("Asia-Pacific", 518, R, 352, row_h=20)
    yr = draw_region_block("Americas", 518, R, yr + 7, row_h=20)

    # Bottom-right balance box: EDITION AT A GLANCE (y = yr+7 .. yl)
    gx0, gx1 = 518, R
    gy0, gy1 = yr + 7, yl
    c.fill_rect(gx0, gy0, gx1, gy1, TINT_BAR)
    c.fill_rect(gx0, gy0, gx1, gy0 + 18, INK)
    c.draw_text(gx0 + 6, gy0 + 3, "24 NOVEMBER 2026 · EDITION AT A GLANCE", "sec", WHITE, "left")
    c.stroke_rect(gx0, gy0, gx1, gy1, RULE, 1)

    # Left half of glance box: regional bar chart
    c.draw_text(gx0 + 8, gy0 + 23, "REGIONAL COVERAGE (50 STORIES)", "tiny_b", INK, "left")
    bar_x = gx0 + 84
    bar_max_w = 128
    for i, reg in enumerate(("Europe", "Middle East", "Asia-Pacific", "Americas", "Africa")):
        cnt = len(by_region[reg])
        by = gy0 + 38 + i * 16
        c.draw_text(gx0 + 8, by, reg, "small", INK, "left")
        bw = int(round(cnt / 12.0 * bar_max_w))
        c.fill_rect(bar_x, by + 1, bar_x + bar_max_w, by + 11, (226, 220, 206))
        c.fill_rect(bar_x, by + 1, bar_x + bw, by + 11, REGION_COLORS[reg])
        c.draw_text(bar_x + bar_max_w + 6, by, str(cnt), "small_b", INK, "left")

    # Attribution summary below bars
    n_conf = sum(1 for s in STORIES if s[4] == "C")
    n_rep = sum(1 for s in STORIES if s[4] == "R")
    c.draw_text(gx0 + 8, gy1 - 16, f"Attribution: {n_conf} Confirmed [C] · {n_rep} Reported [R]", "tiny_b", MUTED, "left")

    # Right half of glance box: Key numbers of 24 Nov
    mx0 = gx0 + 244
    c.vline(mx0 - 8, gy0 + 22, gy1 - 8, RULE, 1)
    c.draw_text(mx0, gy0 + 23, "KEY FIGURES OF 24 NOV 2026", "tiny_b", INK, "left")
    metrics = [
        ("~500k", "Russian war dead in leaked Rosstat data"),
        ("45.8%", "Singapore Q3 non-oil exports growth"),
        ("5%", "Max global revenue fine in AU tech bill"),
        ("11", "Killed in UAE Ras Al Khaimah crash"),
        ("-21%", "Peru Lima stock exchange drop from high"),
        ("€85bn", "EU tax revenue at stake in UN talks"),
    ]
    for i, (num, desc) in enumerate(metrics):
        my = gy0 + 38 + i * 16
        c.draw_text(mx0, my, num, "small_b", CHECK_ACCENT, "left")
        _, ex1 = c.draw_text(mx0 + 44, my, desc, "small", INK, "left")
        assert ex1 <= gx1 - 6, f"Metric overflow on {num}: {ex1} > {gx1 - 6}"

    # --- 4. FOOTER (y = 990..1016) ---
    assert yl <= 988, f"Left column overflow: {yl}"
    c.hline(L, R, 991, INK, 1)
    counts = " · ".join(f"{REGION_CODES[r]} {len(by_region[r])}" for r in REGION_CODES)
    assert sum(len(v) for v in by_region.values()) == len(STORIES)
    c.draw_text(L, 996, "The Global Edition · Tuesday 24 November 2026", "small_b", INK, "left")
    c.draw_text(512, 996, f"TOTAL: {len(STORIES)} STORIES ({counts})", "small_b", INK, "center")
    c.draw_text(R, 996, "Natural Earth 1:110m (PD) · Python Stdlib", "small", MUTED, "right")

    size = write_png(out_path, W, H, c.buf)
    assert size <= 1024 * 1024, f"PNG exceeds 1 MiB: {size}"
    return size


if __name__ == "__main__":
    nbytes = render("entry.png")
    print(f"Rendered entry.png ({W}x{H}, {nbytes:,} bytes)")
