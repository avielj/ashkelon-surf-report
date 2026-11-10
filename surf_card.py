#!/usr/bin/env python3
"""
surf_card.py — render the Ashkelon wave forecast as a Telegram-ready image card.

A visual summary of the Ashkelon Wave Forecast page (hero verdict + week strip),
drawn with Pillow so it runs anywhere (incl. GitHub Actions) with no browser.
Hebrew text is shaped with python-bidi; fonts fall back from Noto Sans Hebrew
to DejaVu Sans (present on ubuntu-latest runners).

Usage:
    from surf_card import build_card
    build_card(days, hero_idx=1, out_path="card.png")
where each day is a dict:
    {"dow": "שני", "dnum": "9.11", "date": "2026-11-09", "weekend": False,
     "score": "GREEN", "surf_m": 1.2, "desc": "מותן", "period_s": 7.7,
     "wind_kmh": 20, "wind_class": "offshore", "seanow": 8.8}
score: GREEN / YELLOW / FLAT. wind_class: offshore / onshore / side.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGIN = 56

_FONT_PATHS = {
    # DejaVu first: it covers Hebrew + Latin + digits (and ships on
    # ubuntu-latest runners). Noto Sans Hebrew on this system lacks digits.
    "bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansHebrew-Bold.ttf",
    ],
    "regular": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf",
    ],
}

_font_cache = {}


def _font(size, bold=False):
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    kind = "bold" if bold else "regular"
    for path in _FONT_PATHS[kind]:
        if os.path.exists(path):
            f = ImageFont.truetype(path, size)
            _font_cache[key] = f
            return f
    f = ImageFont.load_default()
    _font_cache[key] = f
    return f


def hb(text):
    """Reorder a Hebrew (possibly mixed) string for display."""
    try:
        from bidi.algorithm import get_display
        return get_display(str(text))
    except Exception:
        return str(text)


WIND_HE = {"offshore": "מהיבשה", "onshore": "מהים", "side": "מהצד"}
WIND_EN = {"offshore": "אוף־שור", "onshore": "און־שור", "side": "מהצד"}

VERDICT = {
    "GREEN": ("לך", (23, 114, 69), (125, 255, 169)),
    "YELLOW": ("שווה בדיקה", (138, 97, 0), (255, 214, 100)),
    "FLAT": ("שטוח", (90, 109, 117), (200, 205, 210)),
}

PILL = {
    "GREEN": ("ירוק", (23, 114, 69)),
    "YELLOW": ("צהוב", (138, 97, 0)),
    "FLAT": ("שטוח", None),  # flat pill: light teal (pre-blended, see below)
}


# NOTE: ImageDraw on an RGBA image does NOT alpha-blend shapes — it writes the
# RGBA values raw, and convert("RGB") then drops the alpha, so translucent
# fills came out solid white/black. All fills below are SOLID colors,
# pre-blended against the local gradient colour.
FILL_STAT_BOX = (40, 125, 140)      # ~12% white over mid teal
FILL_WEEK_COL = (8, 74, 87)         # ~21% black over lower teal
FILL_CAM_BAR = (7, 64, 74)          # ~27% black over lower teal
FILL_TAG = (31, 76, 92)             # ~10% white over top teal
FILL_FLAT_PILL = (52, 108, 118)     # ~18% white over week column


def _gradient(size):
    """Vertical teal gradient background."""
    top = (6, 56, 74)
    mid = (11, 107, 124)
    bot = (10, 85, 99)
    img = Image.new("RGB", size)
    px = img.load()
    h = size[1]
    for y in range(h):
        t = y / h
        if t < 0.58:
            f = t / 0.58
            c = tuple(round(top[i] + (mid[i] - top[i]) * f) for i in range(3))
        else:
            f = (t - 0.58) / 0.42
            c = tuple(round(mid[i] + (bot[i] - mid[i]) * f) for i in range(3))
        for x in range(size[0]):
            px[x, y] = c
    return img


def _waves(img):
    """Subtle white sine-wave lines across the card."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for row in range(13):
        y0 = 40 + row * 104
        pts = []
        for x in range(0, W + 20, 20):
            pts.append((x, y0 + 9 * math.sin(x / 95.0 + row)))
        d.line(pts, fill=(255, 255, 255, 16), width=3)
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def _text_right(d, x_right, y, s, font, fill):
    d.text((x_right, y), hb(s), font=font, fill=fill, anchor="ra")


def _text_left(d, x_left, y, s, font, fill):
    d.text((x_left, y), hb(s), font=font, fill=fill, anchor="la")


def _text_center(d, x_center, y, s, font, fill):
    d.text((x_center, y), hb(s), font=font, fill=fill, anchor="ma")


def _summary_lines(day):
    """Two summary lines for the hero day, in Aviel's wording rules."""
    if day["score"] == "FLAT":
        return ("שטוח — אין גלים בחלון הבוקר.",
                "הסוול הבא עוד לא נראה — העין על התחזית הבאה.")
    wc = day.get("wind_class", "side")
    if day["score"] == "YELLOW":
        if wc == "onshore":
            return ("צהוב — גליש, אבל צ׳ופי ועם סייג.",
                    "כדאי להגיע ב־06:00 — החלון הטוב הוא עד ~07:00.")
        return ("צהוב — גליש, אבל עם סייג.",
                "כדאי להגיע ב־06:00 — שווה בדיקה.")
    if wc == "offshore":
        return ("אוף־שור — גלאס, הסטים מגיעים נקיים ומסודרים.",
                "כדאי להגיע ב־06:00 — שווה סשן.")
    if wc == "onshore":
        return ("און־שור — צ׳ופי, אבל הגל עובר את הכלל.",
                "כדאי להגיע ב־06:00 — החלון הטוב הוא עד ~07:00.")
    return ("רוח מהצד — הגל עובר את הכלל.",
            "כדאי להגיע ב־06:00 — שווה סשן.")


def build_card(days, hero_idx=0, out_path="card.png", example=False,
               footer_stamp=None):
    """Render the card. days: list of 7 day dicts; hero_idx: hero position."""
    hero = days[hero_idx]
    win = "06:00–10:00" if hero.get("weekend") else "06:00–08:00"
    verdict_text, verdict_color, dot_color = VERDICT[hero["score"]]

    img = _waves(_gradient((W, H)))
    d = ImageDraw.Draw(img, "RGBA")
    right = W - MARGIN
    left = MARGIN

    # ---- header ----
    _text_right(d, right, 52, "תחזית גלים · אשקלון", _font(34, bold=True), (255, 255, 255))
    if example:
        tag = "דוגמה"
        tw = d.textlength(hb(tag), font=_font(24, bold=True)) + 40
        d.rounded_rectangle([left, 56, left + tw, 56 + 44], radius=22,
                            outline=(255, 255, 255), width=2,
                            fill=FILL_TAG)
        _text_center(d, left + tw / 2, 64, tag, _font(24, bold=True), (255, 255, 255))

    # ---- verdict pill ----
    pill_text = f"{verdict_text} · {win}" if hero["score"] != "FLAT" else "שטוח · אין גלים בחלון הבוקר"
    pf = _font(40, bold=True)
    pw = d.textlength(hb(pill_text), font=pf) + 92
    px0 = right - pw
    py0 = 168
    d.rounded_rectangle([px0, py0, right, py0 + 76], radius=38, fill=verdict_color)
    # green dot at the RTL start (right side), text to its left
    d.ellipse([right - 48, py0 + 29, right - 30, py0 + 47], fill=dot_color)
    _text_right(d, right - 66, py0 + 14, pill_text, pf, (255, 255, 255))

    # ---- hero date ----
    _text_right(d, right, 268, f"{hero['dow']} · {hero['dnum']} · חלון הבוקר",
                _font(40, bold=True), (255, 255, 255))

    # ---- big surf number ----
    num = f"{hero['surf_m']:.1f}"
    num_font = _font(185, bold=True)
    num_w = d.textlength(num, font=num_font)
    unit = f"מ׳ ({hero.get('desc', '')})" if hero.get('desc') else "מ׳"
    d.text((right, 330), num, font=num_font, fill=(255, 255, 255), anchor="ra")
    _text_right(d, right - num_w - 22, 470, unit, _font(56, bold=True), (255, 217, 168))

    # ---- stats row ----
    stats = [
        ("משך סוול", f"{hero['period_s']:.1f}", "שניות"),
        ("רוח", f"{hero['wind_kmh']}", "קמ״ש " + WIND_HE.get(hero.get("wind_class", "side"), "")),
        ("SEANOW דלילה 06:00",
         f"{hero['seanow']:.1f}" if hero.get("seanow") is not None else "—",
         "ציון 06:00"),
    ]
    box_w = (W - 2 * MARGIN - 2 * 16) / 3
    box_h = 158
    y_stats = 600
    for i, (lab, val, sub) in enumerate(stats):
        x0 = right - (i + 1) * box_w - i * 16
        # x0 is the right edge of this box in RTL order: boxes go right->left
        bx0 = W - MARGIN - (i + 1) * box_w - i * 16
        bx1 = bx0 + box_w
        d.rounded_rectangle([bx0, y_stats, bx1, y_stats + box_h], radius=18,
                            outline=(255, 255, 255), width=2,
                            fill=FILL_STAT_BOX)
        cx = (bx0 + bx1) / 2
        _text_center(d, cx, y_stats + 16, lab, _font(23, bold=True), (188, 214, 220))
        _text_center(d, cx, y_stats + 52, val, _font(46, bold=True), (255, 255, 255))
        _text_center(d, cx, y_stats + 112, sub, _font(23), (207, 230, 235))

    # ---- summary lines ----
    l1, l2 = _summary_lines(hero)
    _text_right(d, right, 800, l1, _font(32, bold=True), (255, 255, 255))
    _text_right(d, right, 852, l2, _font(32, bold=True), (255, 255, 255))

    # ---- week strip ----
    _text_right(d, right, 930, "השבוע · חלון הבוקר בלבד", _font(26, bold=True), (188, 214, 220))
    col_w = (W - 2 * MARGIN - 6 * 10) / 7
    col_h = 190
    y_week = 972
    for i, day in enumerate(days):
        # RTL: first day at the right
        cx0 = W - MARGIN - (i + 1) * col_w - i * 10
        cx1 = cx0 + col_w
        d.rounded_rectangle([cx0, y_week, cx1, y_week + col_h], radius=14,
                            fill=FILL_WEEK_COL)
        if i == hero_idx:
            d.rounded_rectangle([cx0, y_week, cx1, y_week + col_h], radius=14,
                                outline=(255, 217, 168), width=3)
        ccx = (cx0 + cx1) / 2
        _text_center(d, ccx, y_week + 12, day["dow"], _font(24, bold=True), (255, 255, 255))
        _text_center(d, ccx, y_week + 44, day["dnum"], _font(22), (188, 214, 220))
        _text_center(d, ccx, y_week + 74, f"{day['surf_m']:.1f} מ׳", _font(32, bold=True), (255, 255, 255))
        pname, pcolor = PILL[day["score"]]
        pw2 = d.textlength(hb(pname), font=_font(20, bold=True)) + 24
        py2 = y_week + 126
        if pcolor is None:
            d.rounded_rectangle([ccx - pw2 / 2, py2, ccx + pw2 / 2, py2 + 34], radius=17,
                                fill=FILL_FLAT_PILL)
        else:
            d.rounded_rectangle([ccx - pw2 / 2, py2, ccx + pw2 / 2, py2 + 34], radius=17,
                                fill=pcolor)
        _text_center(d, ccx, py2 + 3, pname, _font(20, bold=True), (255, 255, 255))

    # ---- camera bar ----
    cam_y = 1200
    d.rounded_rectangle([left, cam_y, right, cam_y + 72], radius=16, fill=FILL_CAM_BAR)
    _text_right(d, right - 24, cam_y + 16, "מצלמה חיה — SwellStock", _font(30, bold=True), (255, 255, 255))
    d.text((left + 24, cam_y + 18), "swellstock.co.il/cams", font=_font(28, bold=True),
           fill=(255, 217, 168), anchor="la")

    # ---- footer ----
    _text_right(d, right, 1296, "מקור: 4surfers · הצלבה: SEANOW דלילה", _font(22), (159, 195, 204))
    if footer_stamp:
        d.text((left, 1296), footer_stamp, font=_font(22), fill=(159, 195, 204), anchor="la")

    img.convert("RGB").save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    # Demo render with the last GREEN day (Mon 9.11) + the flat week after it.
    demo = [
        {"dow": "שני", "dnum": "9.11", "date": "2026-11-09", "weekend": False,
         "score": "GREEN", "surf_m": 1.2, "desc": "מותן", "period_s": 7.7,
         "wind_kmh": 20, "wind_class": "offshore", "seanow": 8.8},
        {"dow": "שלישי", "dnum": "10.11", "date": "2026-11-10", "weekend": False,
         "score": "FLAT", "surf_m": 0.5, "desc": "ברך", "period_s": 5.6,
         "wind_kmh": 9, "wind_class": "side", "seanow": 3.9},
        {"dow": "רביעי", "dnum": "11.11", "date": "2026-11-11", "weekend": False,
         "score": "FLAT", "surf_m": 0.3, "desc": "קרסול", "period_s": 4.2,
         "wind_kmh": 6, "wind_class": "offshore", "seanow": None},
        {"dow": "חמישי", "dnum": "12.11", "date": "2026-11-12", "weekend": False,
         "score": "FLAT", "surf_m": 0.3, "desc": "קרסול", "period_s": 4.4,
         "wind_kmh": 6, "wind_class": "offshore", "seanow": None},
        {"dow": "שישי", "dnum": "13.11", "date": "2026-11-13", "weekend": False,
         "score": "FLAT", "surf_m": 0.2, "desc": "קרסול", "period_s": 3.5,
         "wind_kmh": 7, "wind_class": "offshore", "seanow": None},
        {"dow": "שבת", "dnum": "14.11", "date": "2026-11-14", "weekend": True,
         "score": "FLAT", "surf_m": 0.4, "desc": "קרסול עד ברך", "period_s": 4.6,
         "wind_kmh": 6, "wind_class": "side", "seanow": None},
        {"dow": "ראשון", "dnum": "15.11", "date": "2026-11-15", "weekend": False,
         "score": "FLAT", "surf_m": 0.3, "desc": "קרסול", "period_s": 4.2,
         "wind_kmh": 9, "wind_class": "side", "seanow": None},
    ]
    build_card(demo, hero_idx=0, out_path="card.png", example=True,
               footer_stamp="דוגמה — לא תחזית להיום")
    print("wrote card.png")
