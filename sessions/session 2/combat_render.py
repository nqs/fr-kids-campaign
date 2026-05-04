"""Render combat tracker pages from ENCOUNTERS + STAT_BLOCKS data.

Exposes build_combat_tracker(g) — returns a list of flowables to splice
into the adventure PDF between the main body and the player handouts.
"""
import math
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether, Image,
)
from combat_tracker import ENCOUNTERS, CONDITIONS_REF
from combat_stat_blocks import STAT_BLOCKS

MUTED = HexColor("#555555")
INK = HexColor("#1a1a1a")
ACCENT = HexColor("#5a1a1a")
PARCH = HexColor("#f4ecd8")
CARDBG = HexColor("#fbf6e8")

HP_PER_BOX = 5

def tick_boxes(n, box_pt=8):
    """A horizontal row of n empty checkboxes (~box_pt square)."""
    if n <= 0:
        return Paragraph("—", _small())
    cells = [[""] * n]
    t = Table(cells, colWidths=[box_pt] * n, rowHeights=[box_pt], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.4, MUTED),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, MUTED),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t

_small_cache = {}
def _small(name="small", size=9, leading=11, italic=False):
    key = (name, size, leading, italic)
    if key not in _small_cache:
        from reportlab.lib.styles import ParagraphStyle
        _small_cache[key] = ParagraphStyle(
            name, fontName="Times-Italic" if italic else "Times-Roman",
            fontSize=size, leading=leading, textColor=INK)
    return _small_cache[key]

def _hp_cell(hp):
    """Returns a stacked cell: 'HP 78' label above tick-box row."""
    n = math.ceil(hp / HP_PER_BOX)
    label = Paragraph(f"<b>HP {hp}</b> <font size=7 color='#555555'>"
                      f"({HP_PER_BOX}/box)</font>", _small())
    boxes = tick_boxes(n, box_pt=9)
    inner = Table([[label], [boxes]], colWidths=[2.6 * inch])
    inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return inner

def _init_table(combatants, g):
    """Initiative table: 5 blank PC rows then NPC rows."""
    H = ["Init", "Combatant", "AC", "HP & Damage", "Notes"]
    rows = [H]
    for i in range(5):
        rows.append(["___",
                     Paragraph(f"<i>PC #{i+1} — _________________</i>", _small()),
                     "__",
                     Paragraph("HP ____ &nbsp; Cond: _____________________", _small()),
                     ""])
    for c in combatants:
        rows.append([
            Paragraph(f"<b>{c['init']}</b>", _small()),
            Paragraph(f"<b>{c['name']}</b>", _small()),
            Paragraph(f"<b>{c['ac']}</b>", _small()),
            _hp_cell(c['hp']),
            Paragraph(c.get('note', ''), _small()),
        ])
    t = Table(rows, colWidths=[0.45 * inch, 1.95 * inch, 0.4 * inch,
                               2.7 * inch, 1.5 * inch], repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#e8dec1")),
        ("BACKGROUND", (0, 1), (-1, 5), HexColor("#fbf9f0")),
        ("BOX", (0, 0), (-1, -1), 0.5, MUTED),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, MUTED),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t

def _header_strip(enc, g):
    boxed_table = g["boxed_table"]
    rows = [
        ["Encounter", enc["name"]],
        ["Scene", enc["scene_ref"]],
        ["Location", enc["location"]],
        ["Difficulty", enc["difficulty"]],
        ["Light", enc["light"]],
        ["Terrain", enc["terrain"]],
    ]
    return boxed_table(rows, header=False, col_widths=[0.95 * inch, 5.95 * inch])

def _round_strip(g):
    """Round tracker: 'Round:' label, then 10 inline boxes, then number guide."""
    label = Paragraph("<b>Round (tick as completed):</b>", _small())
    boxes = tick_boxes(10, box_pt=14)
    guide_html = ("<font size=8 color='#555555'>"
                  "&nbsp;1 &nbsp;&nbsp;2 &nbsp;&nbsp;3 &nbsp;&nbsp;4 &nbsp;&nbsp;5 "
                  "&nbsp;&nbsp;6 &nbsp;&nbsp;7 &nbsp;&nbsp;8 &nbsp;&nbsp;9 &nbsp;10"
                  "</font>")
    guide = Paragraph(guide_html, _small(size=8))
    inner = Table([[boxes], [guide]], colWidths=[1.7 * inch])
    inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
    ]))
    t = Table([[label, inner]], colWidths=[2.2 * inch, 4.7 * inch])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, MUTED),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t

def _writein_block(label, lines=3, line_w=6.9):
    rows = [[Paragraph(f"<b>{label}</b>", _small())]]
    for _ in range(lines):
        rows.append([Paragraph("&nbsp;", _small(size=10, leading=18))])
    t = Table(rows, colWidths=[line_w * inch])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, MUTED),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, MUTED),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t

def _tracker_sheet(enc, g):
    H1, H2, H3, BODY = g["H1"], g["H2"], g["H3"], g["BODY"]
    p, b = g["p"], g["b"]
    out = [
        Paragraph(f"Combat: {enc['name']}", H1),
        _header_strip(enc, g),
        Spacer(1, 0.08 * inch),
        _round_strip(g),
        Spacer(1, 0.08 * inch),
        Paragraph("Initiative &amp; Damage", H3),
        _init_table(enc["combatants"], g),
        Spacer(1, 0.05 * inch),
        Paragraph(f"<i>Conditions: {CONDITIONS_REF}</i>", _small(italic=True)),
        Spacer(1, 0.08 * inch),
        Paragraph("Triggers, Countdowns &amp; Reinforcements", H3),
    ]
    out += b(enc["triggers"])
    out += [
        Spacer(1, 0.04 * inch),
        _writein_block("Concentration / Ongoing Effects", lines=3),
        Spacer(1, 0.06 * inch),
        Paragraph(f"<b>Tactics summary:</b>", _small(size=10)),
    ]
    for c in enc["combatants"]:
        out.append(Paragraph(
            f"&nbsp;&nbsp;<b>{c['name']}:</b> {c.get('tactics','—')}", _small()))
    out += [
        Spacer(1, 0.06 * inch),
        Paragraph(f"<b>Loot / Aftermath:</b> {enc['loot']}", _small()),
        _writein_block("Notes (resources spent, conditions persisting, XP awarded)", lines=3),
        PageBreak(),
    ]
    return out

def _spell_line(level, names, slots):
    if slots == 0:
        return Paragraph(f"<b>{level}:</b> {names}", _small(size=8, leading=10))
    label = Paragraph(f"<b>{level}</b>", _small(size=8, leading=10))
    boxes = tick_boxes(slots, box_pt=8)
    text = Paragraph(f": {names}", _small(size=8, leading=10))
    row = Table([[label, boxes, text]],
                colWidths=[0.45 * inch, slots * 0.13 * inch, 5.5 * inch])
    row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return row

def _stat_card(sb, g):
    """Render a single half-page stat block card."""
    img = g["img"]
    IMAGES = g["IMAGES"]
    rows = []
    # --- header row: portrait (if any) + title block
    title_html = (f"<font size=12><b>{sb['title']}</b></font><br/>"
                  f"<font size=8 color='#555555'><i>{sb['type_line']}</i> &nbsp;·&nbsp; "
                  f"<b>CR {sb['cr']}</b> ({sb['xp']} XP)</font>")
    title_para = Paragraph(title_html, _small(size=10, leading=12))
    if sb.get("portrait") and sb["portrait"] in IMAGES:
        thumb = img(sb["portrait"], max_w_in=0.9)
        head = Table([[thumb, title_para]], colWidths=[0.95 * inch, 6.0 * inch])
        head.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ]))
        rows.append([head])
    else:
        rows.append([title_para])
    # --- defenses
    rows.append([Paragraph(
        f"<b>AC</b> {sb['ac']} &nbsp;·&nbsp; <b>HP</b> {sb['hp']} &nbsp;·&nbsp; "
        f"<b>Speed</b> {sb['speed']}", _small())])
    rows.append([Paragraph(sb["abilities"], _small())])
    rows.append([Paragraph(sb["saves_skills"], _small(size=8, leading=10))])
    # --- traits
    if sb.get("traits"):
        rows.append([Paragraph("<b>Traits</b>", _small(size=9))])
        for t in sb["traits"]:
            rows.append([Paragraph("• " + t, _small(size=8, leading=10))])
    # --- spells
    if sb.get("spells"):
        sp = sb["spells"]
        rows.append([Paragraph(f"<b>{sp['header']}</b>", _small(size=9))])
        for level, names, slots in sp["lines"]:
            rows.append([_spell_line(level, names, slots)])
    # --- actions
    rows.append([Paragraph("<b>Actions</b>", _small(size=9))])
    for a in sb["actions"]:
        rows.append([Paragraph("• " + a, _small(size=8, leading=10))])
    if sb.get("reactions"):
        rows.append([Paragraph("<b>Reactions</b>", _small(size=9))])
        for r in sb["reactions"]:
            rows.append([Paragraph("• " + r, _small(size=8, leading=10))])
    # --- tactics + loot
    rows.append([Paragraph(f"<b>Tactics:</b> {sb['tactics']}",
                           _small(size=8, leading=10, italic=True))])
    rows.append([Paragraph(f"<b>On defeat:</b> {sb['loot']}",
                           _small(size=8, leading=10))])

    card = Table(rows, colWidths=[7.0 * inch])
    card.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, ACCENT),
        ("BACKGROUND", (0, 0), (-1, -1), CARDBG),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return KeepTogether([card, Spacer(1, 0.12 * inch)])

def build_combat_tracker(g):
    """Entry point — returns flowables for the combat tracker section."""
    H1, BODY, p = g["H1"], g["BODY"], g["p"]
    out = [
        Paragraph("DM Combat Tracker", g["TITLE"]),
        Paragraph("Printable per-encounter sheets &amp; stat-block cards",
                  g["SUBTITLE"]),
        p("Each combat in this session has a one-page tracker (header, "
          "initiative table with HP tick boxes, triggers, concentration "
          "scratch space, tactics summary, and aftermath notes) followed by "
          "stat-block cards for every non-PC combatant. Print these pages, "
          "or keep them open on a second screen at the table. Tick HP boxes "
          "as damage is dealt (5 HP per box); tick spell-slot boxes as "
          "Khelziir burns through them."),
        PageBreak(),
    ]
    seen_cards = set()
    for enc in ENCOUNTERS:
        out += _tracker_sheet(enc, g)
        for card_key in enc["stat_cards"]:
            if card_key in STAT_BLOCKS:
                out.append(_stat_card(STAT_BLOCKS[card_key], g))
        out.append(PageBreak())
    return out

