"""
Generate product datasheet PDFs for the WTD2-P range.
Run: python3 scripts/make_datasheets.py
"""
from datetime import date
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
OUT = ROOT / "datasheets"
OUT.mkdir(exist_ok=True)

REVISION = "1.0"
ISSUED = date.today().strftime("%B %Y")  # e.g. "April 2026"

STANDARDS = [
    ("EN 81",     "European elevator safety"),
    ("CE",        "Compliant configurations"),
    ("IEC 60034", "Rotating electrical machines"),
    ("Class F",   "Insulation rating"),
    ("IP41",      "Ingress protection"),
]

# Brand colors (matching the website)
INK = HexColor("#1a1d23")
INK2 = HexColor("#3d434c")
INK3 = HexColor("#6b7280")
LINE = HexColor("#e5e7eb")
LINE2 = HexColor("#f0f1f4")
SOFT = HexColor("#fafbfc")
BG_SOFT = HexColor("#f5f6f8")
ACCENT = HexColor("#1f4788")
ACCENT_SOFT = HexColor("#eaeff7")

PW, PH = A4  # 595.28 x 841.89 pt

MODELS = {
    "wtd2-p400-100d": {
        "name": "WTD2-P400-100D",
        "capacity": "400 / 408 kg",
        "speed": "1.0 m/s",
        "drawing": IMG / "drawing-wtd2-p400-100d.png",
        "electrical": [
            ("Rated power",       "2.7 kW"),
            ("Rated current",     "8 A"),
            ("Rated speed",       "119 rpm"),
            ("Frequency",         "19.9 Hz"),
            ("Rated torque",      "217 N·m"),
            ("Number of poles",   "20"),
            ("Rated voltage",     "AC 380 V · 50/60 Hz"),
            ("Brake voltage",     "DC 110 V · single coil"),
        ],
        "mechanical": [
            ("Net weight",        "140 kg"),
            ("Total length",      "454.7 mm"),
            ("Overall height",    "362 mm"),
            ("Mounting height",   "165 mm"),
            ("Mounting holes",    "4 × Ø18 @ 250 mm"),
            ("Sheave diameter",   "Ø 320 mm"),
            ("Static shaft load", "2,500 kg"),
            ("Travelling height", "≤ 90 m"),
        ],
    },
    "wtd2-p544-100d": {
        "name": "WTD2-P544-100D",
        "capacity": "544 kg",
        "speed": "1.0 m/s",
        "drawing": IMG / "drawing-wtd2-p544-100d.png",
        "electrical": [
            ("Rated power",       "3.6 kW"),
            ("Rated current",     "10 A"),
            ("Rated speed",       "119 rpm"),
            ("Frequency",         "19.9 Hz"),
            ("Rated torque",      "290 N·m"),
            ("Number of poles",   "20"),
            ("Rated voltage",     "AC 380 V · 50/60 Hz"),
            ("Brake voltage",     "DC 110 V · single coil"),
        ],
        "mechanical": [
            ("Net weight",        "200 kg"),
            ("Total length",      "534.7 mm"),
            ("Overall height",    "384.5 mm"),
            ("Mounting height",   "165 mm"),
            ("Mounting holes",    "4 × Ø18 @ 250 mm"),
            ("Sheave diameter",   "Ø 320 mm"),
            ("Static shaft load", "2,500 kg"),
            ("Travelling height", "≤ 90 m"),
        ],
    },
}

COMMON = [
    ("Motor type",        "PM synchronous"),
    ("Wrap",              "Single"),
    ("Roping",            "4 × Ø8 × 12 · ratio 2:1"),
    ("Groove profile",    "Undercut U"),
    ("Cut angle β",       "90°"),
    ("Groove angle γ",    "30°"),
    ("Duty cycle",        "S5 – 40%"),
    ("Insulation class",  "F"),
    ("Protection",        "IP41"),
]


def draw_image_contained(c, path, x, y, w, h):
    """Draw an image inside box (x,y,w,h) preserving aspect, centered."""
    img = ImageReader(str(path))
    iw, ih = img.getSize()
    s = min(w / iw, h / ih)
    dw, dh = iw * s, ih * s
    dx = x + (w - dw) / 2
    dy = y + (h - dh) / 2
    c.drawImage(img, dx, dy, dw, dh, mask='auto')


def draw_kv_table(c, x, y, w, rows, row_h=14 * mm / 14 * 14, label_w=None):
    """Draw a label/value table at (x,y) growing downward.
       y is the TOP of the table. Returns the bottom y."""
    label_w = label_w or w * 0.55
    line_h = 18
    cur_y = y
    for k, v in rows:
        cur_y -= line_h
        c.setFillColor(INK3)
        c.setFont("Helvetica", 9)
        c.drawString(x, cur_y + 5, k)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(x + w, cur_y + 5, v)
        c.setStrokeColor(LINE2)
        c.setLineWidth(0.5)
        c.line(x, cur_y, x + w, cur_y)
    return cur_y


def section_label(c, x, y, text, accent_w=14):
    """Section label with a small accent stripe underneath."""
    c.setFillColor(INK3)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, y, text.upper())
    c.setFillColor(ACCENT)
    c.rect(x, y - 4, accent_w, 1.5, fill=1, stroke=0)


def render_pdf(model_key, model):
    pdf_path = OUT / f"{model_key}.pdf"
    doc_no = f"DS-{model['name']}".upper()
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    c.setTitle(f"{model['name']} · ASTON Gearless Traction Machine")
    c.setAuthor("ASTON")
    c.setSubject("Technical datasheet")
    c.setKeywords("elevator, traction, gearless, permanent magnet, "
                  + model['name'])

    # Page margins
    margin = 18 * mm
    inner_w = PW - 2 * margin
    top = PH - margin

    # ============ HEADER BAR ============
    header_h = 14 * mm
    c.setFillColor(INK)
    c.rect(0, PH - header_h, PW, header_h, fill=1, stroke=0)
    # Brand mark
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margin, PH - header_h + 4.5 * mm, "ASTON")
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#9aa0aa"))
    c.drawString(margin + 16 * mm, PH - header_h + 4.5 * mm,
                 "Gearless Traction Systems")
    # Right-side: doc metadata stack
    c.setFont("Helvetica", 8)
    c.setFillColor(white)
    c.drawRightString(PW - margin, PH - header_h + 7 * mm,
                      "TECHNICAL DATASHEET")
    c.setFont("Helvetica", 7.5)
    c.setFillColor(HexColor("#9aa0aa"))
    c.drawRightString(PW - margin, PH - header_h + 3 * mm,
                      f"{doc_no}  ·  Rev {REVISION}  ·  {ISSUED}")

    # Accent stripe directly under header
    c.setFillColor(ACCENT)
    c.rect(0, PH - header_h - 2, PW, 2, fill=1, stroke=0)

    # ============ TITLE SECTION ============
    cur_y = PH - header_h - 12 * mm
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin, cur_y, "WTD2-P SERIES · PERMANENT MAGNET GEARLESS")
    cur_y -= 7 * mm
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(margin, cur_y, model["name"])
    # Capacity pill on the right
    pill_text = f"{model['capacity']}  ·  {model['speed']}"
    c.setFont("Helvetica-Bold", 9)
    pill_w = c.stringWidth(pill_text, "Helvetica-Bold", 9) + 14
    pill_h = 18
    pill_x = PW - margin - pill_w
    pill_y = cur_y - 2
    c.setFillColor(ACCENT_SOFT)
    c.roundRect(pill_x, pill_y, pill_w, pill_h, 2, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.drawString(pill_x + 7, pill_y + 5, pill_text)
    cur_y -= 5 * mm
    c.setFillColor(INK3)
    c.setFont("Helvetica", 10.5)
    c.drawString(
        margin, cur_y,
        "Compact permanent magnet synchronous machine for residential "
        "and small commercial elevators."
    )

    # ============ HERO: PHOTO + DRAWING ============
    cur_y -= 6 * mm
    hero_y_top = cur_y
    hero_h = 70 * mm
    half = (inner_w - 6 * mm) / 2

    # Photo card
    photo_x = margin
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.setFillColor(white)
    c.rect(photo_x, hero_y_top - hero_h, half, hero_h, fill=1, stroke=1)
    draw_image_contained(c, IMG / "wtd2-p.png",
                         photo_x + 6 * mm, hero_y_top - hero_h + 6 * mm,
                         half - 12 * mm, hero_h - 12 * mm)
    # Photo label tag
    c.setFillColor(SOFT)
    c.rect(photo_x + 5 * mm, hero_y_top - 9 * mm, 38 * mm, 5 * mm,
           fill=1, stroke=0)
    c.setFillColor(INK3)
    c.setFont("Helvetica", 7.5)
    c.drawString(photo_x + 7 * mm, hero_y_top - 7.5 * mm,
                 f"REFERENCE UNIT · {model['name'].split('-')[0]}-{model['name'].split('-')[1]}")

    # Drawing card
    drw_x = photo_x + half + 6 * mm
    c.setStrokeColor(LINE)
    c.setFillColor(white)
    c.rect(drw_x, hero_y_top - hero_h, half, hero_h, fill=1, stroke=1)
    draw_image_contained(c, model["drawing"],
                         drw_x + 5 * mm, hero_y_top - hero_h + 5 * mm,
                         half - 10 * mm, hero_h - 10 * mm)
    c.setFillColor(SOFT)
    c.rect(drw_x + 5 * mm, hero_y_top - 9 * mm, 38 * mm, 5 * mm,
           fill=1, stroke=0)
    c.setFillColor(INK3)
    c.setFont("Helvetica", 7.5)
    c.drawString(drw_x + 7 * mm, hero_y_top - 7.5 * mm,
                 "DIMENSION DRAWING · MM")

    cur_y = hero_y_top - hero_h - 8 * mm

    # ============ ELECTRICAL + MECHANICAL ============
    sec_top = cur_y
    label_y = sec_top
    section_label(c, margin, label_y, "Electrical Characteristics")
    section_label(c, margin + half + 6 * mm, label_y, "Mechanical Properties")
    table_y = sec_top - 4 * mm
    bot1 = draw_kv_table(c, margin, table_y, half, model["electrical"])
    bot2 = draw_kv_table(c, margin + half + 6 * mm, table_y, half, model["mechanical"])
    cur_y = min(bot1, bot2) - 8 * mm

    # ============ DESIGN & STANDARDS ============
    section_label(c, margin, cur_y, "Design & Standards")
    cur_y -= 4 * mm
    # 3-col layout, properly spaced rows
    col_gap = 6 * mm
    col_w = (inner_w - 2 * col_gap) / 3
    rows = [COMMON[i:i + 3] for i in range(0, len(COMMON), 3)]
    line_h = 30  # generous, so label + value have breathing room
    cell_pad_x = 4 * mm
    box_top = cur_y
    box_h = line_h * len(rows) + 4 * mm  # extra top/bottom padding
    box_y = box_top - box_h
    # Outer box
    c.setFillColor(SOFT)
    c.rect(margin, box_y, inner_w, box_h, fill=1, stroke=0)
    c.setStrokeColor(LINE)
    c.rect(margin, box_y, inner_w, box_h, fill=0, stroke=1)
    # Row dividers between rows
    c.setStrokeColor(LINE)
    c.setLineWidth(0.4)
    for ri in range(1, len(rows)):
        y_div = box_top - 2 * mm - ri * line_h
        c.line(margin, y_div, margin + inner_w, y_div)
    # Cells
    for ri, row in enumerate(rows):
        for ci, (k, v) in enumerate(row):
            cx = margin + ci * (col_w + col_gap) + cell_pad_x
            cell_top = box_top - 2 * mm - ri * line_h
            c.setFillColor(INK3)
            c.setFont("Helvetica", 8)
            c.drawString(cx, cell_top - 11, k)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(cx, cell_top - 23, v)
    cur_y = box_y - 8 * mm

    # ============ STANDARDS & CERTIFICATIONS ============
    section_label(c, margin, cur_y, "Standards & Certifications")
    cur_y -= 5 * mm
    badge_w = (inner_w - 4 * 4 * mm) / len(STANDARDS)
    badge_h = 14 * mm
    for i, (code, desc) in enumerate(STANDARDS):
        bx = margin + i * (badge_w + 4 * mm)
        by = cur_y - badge_h
        # Badge box
        c.setFillColor(white)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.rect(bx, by, badge_w, badge_h, fill=1, stroke=1)
        # Code
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(bx + 4 * mm, by + badge_h - 6 * mm, code)
        # Description
        c.setFillColor(INK3)
        c.setFont("Helvetica", 7)
        c.drawString(bx + 4 * mm, by + 3 * mm, desc)
    cur_y -= badge_h + 6 * mm

    # ============ NOTES ============
    section_label(c, margin, cur_y, "Notes")
    cur_y -= 4 * mm
    c.setFillColor(INK2)
    c.setFont("Helvetica", 8)
    notes = [
        "Specifications stated at rated voltage and rated load. Operating conditions outside the rated envelope may shift performance.",
        "Drawings dimensioned in millimetres. Tolerances ±0.5 mm on mounting hole spacing. Refer to engineering for full GA drawings.",
        "Configurations beyond the published baseline (alternative voltages, groove geometries, sheave diameters) available on request.",
    ]
    for n in notes:
        c.drawString(margin, cur_y, "•  " + n)
        cur_y -= 3.5 * mm

    # ============ FOOTER ============
    foot_h = 14 * mm
    c.setFillColor(BG_SOFT)
    c.rect(0, 0, PW, foot_h, fill=1, stroke=0)
    c.setStrokeColor(LINE)
    c.line(0, foot_h, PW, foot_h)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, foot_h - 5 * mm, "ASTON")
    c.setFillColor(INK3)
    c.setFont("Helvetica", 8)
    c.drawString(margin + 14 * mm, foot_h - 5 * mm,
                 "Gearless Traction Systems  ·  Operations: India & China")
    c.setFillColor(INK3)
    c.setFont("Helvetica", 8)
    c.drawRightString(PW - margin, foot_h - 5 * mm,
                      "info@astontraction.com  ·  astontraction.com")
    c.setFillColor(HexColor("#9aa0aa"))
    c.setFont("Helvetica", 7)
    c.drawString(margin, foot_h - 9 * mm,
                 f"© ASTON. {doc_no}  ·  Rev {REVISION}  ·  {ISSUED}.  "
                 "Specifications subject to change without notice. Issued for technical evaluation.")
    c.drawRightString(PW - margin, foot_h - 9 * mm, "Page 1 of 1")

    c.showPage()
    c.save()
    print(f"  → {pdf_path.relative_to(ROOT)}  ({pdf_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    print("Generating datasheets...")
    for key, m in MODELS.items():
        render_pdf(key, m)
    print("Done.")
