"""Markdown -> ReportLab Platypus renderer for D&D adventure PDFs.

Session-agnostic. Copy unchanged into each new session folder. Driven by:
- Three markdown files (`<slug>-1-adventure.md`, `<slug>-2-combat-tracker.md`,
  `<slug>-3-player-handouts.md`).
- An `images.json` manifest of `{description, url, aspect_ratio}` so images can
  be sized without re-querying Gemini.

Entry point: `build_pdf(md_files, images_json, out_path, title)`.
"""
from __future__ import annotations
import json
import re
import urllib.request
from io import BytesIO
from pathlib import Path

import mistune
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image, KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)
from reportlab.platypus.flowables import HRFlowable

# --- colors / styles -------------------------------------------------------

INK = HexColor("#1a1a1a")
ACCENT = HexColor("#5a1a1a")
MUTED = HexColor("#555555")
PARCH = HexColor("#f4ecd8")
PARCH_DK = HexColor("#e8dec1")
ROW_ALT = HexColor("#f7f1e1")

_ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=_ss["Heading1"], fontName="Times-Bold",
    fontSize=18, leading=22, textColor=ACCENT, spaceBefore=14, spaceAfter=8,
    keepWithNext=1)
H2 = ParagraphStyle("H2", parent=_ss["Heading2"], fontName="Times-Bold",
    fontSize=14, leading=18, textColor=INK, spaceBefore=10, spaceAfter=4,
    keepWithNext=1)
H3 = ParagraphStyle("H3", parent=_ss["Heading3"], fontName="Times-BoldItalic",
    fontSize=12, leading=15, textColor=ACCENT, spaceBefore=6, spaceAfter=3,
    keepWithNext=1)
H4 = ParagraphStyle("H4", parent=_ss["Heading4"], fontName="Times-Bold",
    fontSize=11, leading=14, textColor=INK, spaceBefore=4, spaceAfter=2,
    keepWithNext=1)
BODY = ParagraphStyle("Body", parent=_ss["BodyText"], fontName="Times-Roman",
    fontSize=10.5, leading=14, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6,
    allowWidows=0, allowOrphans=0)
BODY_LEFT = ParagraphStyle("BodyL", parent=BODY, alignment=TA_LEFT)
BULLET = ParagraphStyle("Bul", parent=BODY, leftIndent=30, bulletIndent=20,
    bulletFontName="Times-Roman", bulletFontSize=10, alignment=TA_LEFT, spaceAfter=2)
CAPTION = ParagraphStyle("Cap", parent=BODY, fontName="Times-Italic",
    fontSize=9, leading=11, textColor=MUTED, alignment=TA_CENTER,
    spaceBefore=2, spaceAfter=12)
READ = ParagraphStyle("Read", parent=BODY, fontName="Times-Italic",
    leftIndent=18, rightIndent=18, borderPadding=8, borderColor=ACCENT,
    borderWidth=0.6, backColor=PARCH, spaceBefore=8, spaceAfter=10)
APP_LABEL = ParagraphStyle("AppL", parent=H1, alignment=TA_CENTER, spaceBefore=18)
CARD_BODY = ParagraphStyle("CardBody", parent=BODY, fontSize=9.5, leading=12,
    alignment=TA_LEFT, spaceAfter=3)
CARD_TITLE = ParagraphStyle("CardTitle", parent=H3, fontSize=13, leading=15,
    spaceBefore=0, spaceAfter=2)
CARD_SUB = ParagraphStyle("CardSub", parent=BODY, fontName="Times-Italic",
    fontSize=9.5, leading=11, textColor=MUTED, spaceAfter=4)

# --- image cache -----------------------------------------------------------

_bytes_cache: dict[str, bytes] = {}

def _fetch(url: str) -> BytesIO:
    if url not in _bytes_cache:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            _bytes_cache[url] = r.read()
    return BytesIO(_bytes_cache[url])

def _aspect(ratio: str) -> tuple[int, int]:
    a, b = ratio.split(":")
    return int(a), int(b)

def load_images(path: str | Path) -> dict[str, dict]:
    """Return {url: {description, aspect_ratio}} from images.json."""
    data = json.loads(Path(path).read_text())
    return {item["url"]: item for item in data}

def sized_image(url: str, manifest: dict, max_w_in: float = 5.5,
                max_h_in: float | None = None) -> Image:
    info = manifest.get(url)
    if info:
        aw, ah = _aspect(info["aspect_ratio"])
    else:
        aw, ah = 4, 3  # safe default
    w = max_w_in * inch
    h = w * ah / aw
    if max_h_in and h > max_h_in * inch:
        h = max_h_in * inch
        w = h * aw / ah
    return Image(_fetch(url), width=w, height=h)

# --- inline rendering ------------------------------------------------------

# Substitute ☐ glyph (Times-Roman lacks it) with a tiny inline checkbox built
# from a Unicode-safe font. We use Helvetica + a small white box character
# rendered via Paragraph markup. For paragraphs the simplest fix is to wrap
# the glyph in a font tag pointing at a fallback, but ReportLab's default
# fonts also lack ☐. So instead we replace ☐ with a small bordered table cell
# at table-rendering time. For inline paragraphs we substitute "[ ]".
CHECKBOX_GLYPH = "\u2610"

def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def _inline_to_html(children: list) -> str:
    out = []
    for tok in children or []:
        t = tok.get("type")
        if t == "text":
            out.append(_esc(tok.get("raw", "")))
        elif t == "strong":
            out.append(f"<b>{_inline_to_html(tok.get('children', []))}</b>")
        elif t == "emphasis":
            out.append(f"<i>{_inline_to_html(tok.get('children', []))}</i>")
        elif t == "codespan":
            out.append(f"<font face='Courier'>{_esc(tok.get('raw', ''))}</font>")
        elif t == "linebreak" or t == "softbreak":
            out.append("<br/>")
        elif t == "link":
            out.append(_inline_to_html(tok.get("children", [])))
        elif t == "image":
            out.append("")  # images handled at block level; ignore inline
        else:
            out.append(_inline_to_html(tok.get("children", [])) or _esc(tok.get("raw", "")))
    s = "".join(out)
    # Replace ☐ with a visible bracketed box for inline paragraphs (rare).
    return s.replace(CHECKBOX_GLYPH, "<font face='Courier'>[ ]</font>")


# --- low-level flowable helpers --------------------------------------------

def _box_cell(label: str = "", size: float = 9) -> Table:
    """A single bordered checkbox cell of ~size points square."""
    t = Table([[label]], colWidths=[size], rowHeights=[size])
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, INK),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t

def _checkbox_row(n: int, size: float = 9, gap: float = 1) -> Table:
    """A horizontal row of n empty bordered cells."""
    cells = [[""] * n]
    widths = [size] * n
    t = Table(cells, colWidths=widths, rowHeights=[size])
    style = [
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), gap),
        ("RIGHTPADDING", (0, 0), (-1, -1), gap),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]
    for i in range(n):
        style.append(("BOX", (i, 0), (i, 0), 0.5, INK))
    t.setStyle(TableStyle(style))
    return t

def _hp_cell(text: str) -> list:
    """Render an HP cell text like '75: ☐☐☐☐☐ ☐☐☐☐☐ ☐☐☐☐☐' as label + boxes.

    Falls back to plain Paragraph if no ☐ glyph present.
    """
    if CHECKBOX_GLYPH not in text:
        return [Paragraph(_esc(text), CARD_BODY)]
    n = text.count(CHECKBOX_GLYPH)
    label = text.split(":", 1)[0].strip() if ":" in text else ""
    parts: list = []
    if label:
        parts.append(Paragraph(f"<b>{_esc(label)}</b>", CARD_BODY))
    parts.append(_checkbox_row(n, size=8, gap=0.5))
    return parts

# --- table rendering -------------------------------------------------------

def _cell_text(children: list) -> str:
    """Plain text of a table cell (used for header/pattern matching)."""
    out = []
    for tok in children or []:
        t = tok.get("type")
        if t == "text":
            out.append(tok.get("raw", ""))
        elif t in ("strong", "emphasis", "link"):
            out.append(_cell_text(tok.get("children", [])))
        elif t == "codespan":
            out.append(tok.get("raw", ""))
    return "".join(out)

def _cell_flow(children: list, style: ParagraphStyle = CARD_BODY):
    """Render a table cell's children. Returns a flowable or list of flowables."""
    raw = _cell_text(children)
    if CHECKBOX_GLYPH in raw:
        flow = _hp_cell(raw)
        return flow if len(flow) > 1 else flow[0]
    html = _inline_to_html(children)
    return Paragraph(html or "&nbsp;", style)

def _is_init_table(headers: list[str]) -> bool:
    norm = [h.strip().lower() for h in headers]
    return norm[:5] == ["init", "combatant", "ac", "hp", "notes"]

def _render_table(node: dict) -> Table:
    header_cells: list = []
    body_rows: list = []
    for child in node.get("children", []):
        if child["type"] == "table_head":
            header_cells = child.get("children", [])
        elif child["type"] == "table_body":
            body_rows = child.get("children", [])
    header_text = [_cell_text(c.get("children", [])) for c in header_cells]
    is_init = _is_init_table(header_text)
    rows = [[_cell_flow(c.get("children", []), CARD_BODY) for c in header_cells]]
    for row in body_rows:
        rows.append([_cell_flow(c.get("children", []), CARD_BODY)
                     for c in row.get("children", [])])
    ncols = len(header_text)
    if is_init:
        col_widths = [0.5*inch, 2.4*inch, 0.5*inch, 1.7*inch, 1.9*inch][:ncols]
    else:
        col_widths = None
    t = Table(rows, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.5, MUTED),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, MUTED),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), PARCH_DK),
    ]
    if is_init:
        for i in range(1, len(rows)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(style))
    return t



# --- frontmatter & special-paragraph helpers -------------------------------

_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
_CHECKBOX_TOKEN_RE = re.compile(r"\u2610\s*([^\u2610·]+?)(?=\s*[\u2610·]|$)")
_RULED_LINE_RE = re.compile(r"^[\s_]+$")

def strip_frontmatter(text: str) -> tuple[str, dict]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return text, {}
    fm_text = m.group(0)
    rest = text[m.end():]
    meta: dict = {}
    for line in fm_text.splitlines()[1:-1]:
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"')
    return rest, meta

def _para_plain_text(node: dict) -> str:
    return _cell_text(node.get("children", []))

def _is_checkbox_strip(text: str) -> bool:
    return text.lstrip().startswith((
        "Round:", "Ritual Countdown", "Portal Anchor object",
    )) and CHECKBOX_GLYPH in text

def _li_plain_text(li: dict) -> str:
    """Plain text of a list item's first inline children (block_text/paragraph)."""
    out = []
    for child in li.get("children", []):
        if child.get("type") in ("block_text", "paragraph"):
            out.append(_cell_text(child.get("children", [])))
    return "".join(out)

def _is_ruled_line_item(li: dict) -> bool:
    children = li.get("children", [])
    # Mistune parses `- ___...` as a list item whose only child is a thematic_break
    # (3+ underscores is a CommonMark horizontal rule).
    if children and all(c.get("type") == "thematic_break" for c in children):
        return True
    text = _li_plain_text(li)
    return bool(text) and bool(_RULED_LINE_RE.match(text))

def _is_bold_only_paragraph(node: dict) -> bool:
    """Paragraph whose meaningful content is a single <strong> (e.g. **Actions**)."""
    children = [c for c in node.get("children", [])
                if c.get("type") not in ("softbreak", "linebreak")]
    return len(children) == 1 and children[0].get("type") == "strong"

def _render_checkbox_strip(text: str) -> Table:
    """Render '**Label:** ☐ 1 · ☐ 2 · ...' as label + bordered boxes with numbers."""
    label, _, rest = text.partition(":")
    pairs = _CHECKBOX_TOKEN_RE.findall(rest)
    pairs = [p.strip(" ·") for p in pairs if p.strip(" ·")]
    cells = [Paragraph(f"<b>{_esc(label.strip())}:</b>", CARD_BODY)]
    widths = [1.4 * inch]
    for label_txt in pairs:
        cells.append(_box_cell(size=9))
        cells.append(Paragraph(_esc(label_txt), CARD_BODY))
        widths.extend([9, 0.30 * inch])
    t = Table([cells], colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t

# --- block renderer --------------------------------------------------------

class BlockRenderer:
    """Walk a mistune v3 AST and emit Platypus flowables for one .md file."""

    def __init__(self, manifest: dict, section: str, first_h1_pagebreak: bool = False,
                 font_scale: float = 1.0):
        self.manifest = manifest
        self.section = section  # 'adventure' | 'combat-tracker' | 'player-handouts'
        self.first_h1_pagebreak = first_h1_pagebreak
        self.font_scale = font_scale
        self.in_stat_cards = False
        self._h1_seen = False
        self._h2_seen_in_section = False
        self._after_stat_label = False
        self._last_was_map = False  # True after a tactical map image; cleared on next ---
        self.out: list = []
        if font_scale == 1.0:
            self.body = BODY
            self.body_left = BODY_LEFT
            self.bullet = BULLET
            self.read = READ
        else:
            s = font_scale
            self.body = ParagraphStyle("BodyScaled", parent=BODY,
                fontSize=BODY.fontSize * s, leading=BODY.leading * s)
            self.body_left = ParagraphStyle("BodyLScaled", parent=BODY_LEFT,
                fontSize=BODY_LEFT.fontSize * s, leading=BODY_LEFT.leading * s)
            self.bullet = ParagraphStyle("BulScaled", parent=BULLET,
                fontSize=BULLET.fontSize * s, leading=BULLET.leading * s,
                leftIndent=BULLET.leftIndent * s, bulletIndent=BULLET.bulletIndent * s)
            self.read = ParagraphStyle("ReadScaled", parent=READ,
                fontSize=READ.fontSize * s, leading=READ.leading * s)

    def render(self, tokens: list) -> list:
        for tok in tokens:
            self._handle(tok)
        return self.out

    # -- dispatch -----------------------------------------------------------

    def _handle(self, node: dict) -> None:
        t = node.get("type")
        method = getattr(self, f"_h_{t}", None)
        if method:
            method(node)
        elif "children" in node:
            for child in node["children"]:
                self._handle(child)

    # -- handlers -----------------------------------------------------------

    def _h_blank_line(self, node: dict) -> None:
        pass

    def _h_heading(self, node: dict) -> None:
        self._after_stat_label = False
        level = node["attrs"]["level"]
        text = _inline_to_html(node.get("children", []))
        plain = _para_plain_text(node)
        if level == 1:
            if self.first_h1_pagebreak or self._h1_seen:
                self._append_pagebreak()
            self._h1_seen = True
            self._h2_seen_in_section = False
            if plain.strip().lower().startswith("stat cards"):
                self.in_stat_cards = True
            self.out.append(Paragraph(text, H1))
        elif level == 2:
            # Combat-tracker encounters carry a full tracker sheet under each
            # H2 — force each onto its own page boundary. Adventure and
            # player-handouts let H2 sections flow naturally so short
            # entries (e.g., a landscape-image handout followed by another
            # landscape-image handout) can share a page rather than leaving
            # half-empty bottoms.
            if self.section == "combat-tracker" and self._h2_seen_in_section:
                self._append_pagebreak()
            self._h2_seen_in_section = True
            self.out.append(Paragraph(text, H2))
        elif level == 3:
            self.out.append(Paragraph(text, H3))
        else:
            self.out.append(Paragraph(text, H4))

    def _h_thematic_break(self, node: dict) -> None:
        if self._last_was_map:
            # The --- immediately after a tactical map is the hard page break
            # separating the map's dedicated page from the tracker sheet.
            self._append_pagebreak()
            self._last_was_map = False
        else:
            self.out.append(Spacer(1, 6))

    def _h_paragraph(self, node: dict) -> None:
        children = node.get("children", [])
        # Solo image paragraph -> block image with caption.
        if len(children) == 1 and children[0].get("type") == "image":
            self._emit_image(children[0])
            self._after_stat_label = False
            return
        self._last_was_map = False
        text = _para_plain_text(node)
        if _is_checkbox_strip(text):
            self.out.append(_render_checkbox_strip(text))
            self.out.append(Spacer(1, 4))
            self._after_stat_label = False
            return
        html = _inline_to_html(children)
        if html.strip():
            self.out.append(Paragraph(html, self.body))
        # Track stat-block labels (e.g. **Actions**, **Traits**, **Spellcasting (...)**)
        # so a list immediately after them renders without bullets.
        self._after_stat_label = _is_bold_only_paragraph(node)

    def _h_block_text(self, node: dict) -> None:
        # Used inside list items.
        html = _inline_to_html(node.get("children", []))
        if html.strip():
            self.out.append(Paragraph(html, self.body_left))

    def _h_block_quote(self, node: dict) -> None:
        self._after_stat_label = False
        # Collect inner text; detect Obsidian callout `[!quote] Read Aloud`.
        inner_html_parts: list[str] = []
        for child in node.get("children", []):
            if child.get("type") == "paragraph":
                inner_html_parts.append(_inline_to_html(child.get("children", [])))
        inner = "<br/>".join(p for p in inner_html_parts if p.strip())
        # Strip Obsidian callout prefix from first line.
        inner = re.sub(r"^\[!\w+\][^<]*<br/>", "", inner)
        inner = re.sub(r"^\[!\w+\][^<]*", "", inner)
        if inner.strip():
            self.out.append(Paragraph(inner, self.read))

    def _h_list(self, node: dict) -> None:
        children = node.get("children", [])
        after_label = self._after_stat_label
        self._after_stat_label = False
        # Write-in slots: every item is just underscores -> plain ruled lines, no bullets.
        if children and all(_is_ruled_line_item(li) for li in children):
            box: list = []
            for _ in children:
                box.append(Spacer(1, 4))
                box.append(HRFlowable(width="100%", thickness=0.4,
                                      color=INK, spaceBefore=0, spaceAfter=0))
            box.append(Spacer(1, 4))
            # If the immediately preceding flowable is a heading, bind it with
            # the write-in box so the box can't drift away from its heading.
            # The box is short and predictable, so this is always safe.
            end = len(self.out) - 1
            while end >= 0 and isinstance(self.out[end], (Spacer, HRFlowable)):
                end -= 1
            if end >= 0 and self._is_heading_flow(self.out[end]):
                bound = list(self.out[end:]) + box
                del self.out[end:]
                self.out.append(KeepTogether(bound))
            else:
                self.out.extend(box)
            return
        # Stat-block content under a bold label (Traits / Actions / Reactions /
        # Spellcasting): conventional 5e formatting is labeled paragraphs, no bullets.
        if after_label:
            for li in children:
                inner_html = []
                for child in li.get("children", []):
                    if child.get("type") in ("block_text", "paragraph"):
                        inner_html.append(_inline_to_html(child.get("children", [])))
                html = "<br/>".join(h for h in inner_html if h.strip())
                if html.strip():
                    self.out.append(Paragraph(html, self.body_left))
            return
        # Default: real bulleted list. Render each item as a Paragraph with bulletText
        # so we can independently control bullet position (bulletIndent) and text
        # position (leftIndent) — bullet sits just left of its text, both indented
        # past the heading column.
        for li in children:
            inner_html = []
            for child in li.get("children", []):
                if child.get("type") == "block_text":
                    inner_html.append(_inline_to_html(child.get("children", [])))
                elif child.get("type") == "paragraph":
                    inner_html.append(_inline_to_html(child.get("children", [])))
            html = "<br/>".join(h for h in inner_html if h.strip())
            p = Paragraph(html or "&nbsp;", self.bullet, bulletText="\u2022")
            self.out.append(p)
        self.out.append(Spacer(1, 4))

    def _h_table(self, node: dict) -> None:
        self._after_stat_label = False
        self.out.append(_render_table(node))
        self.out.append(Spacer(1, 6))

    def _h_block_code(self, node: dict) -> None:
        self._after_stat_label = False
        raw = node.get("raw", "")
        self.out.append(Paragraph(f"<font face='Courier'>{_esc(raw)}</font>", self.body_left))

    # -- image emission -----------------------------------------------------

    def _append_pagebreak(self) -> None:
        """Append a PageBreak unless one is already effective at this point.

        Skips when the last flowable is a PageBreak *or* when only decorative
        flowables (Spacer / HRFlowable) sit between us and the previous
        PageBreak — those don't add page content, so another break would
        produce a blank page. Also skips on an empty `out` to avoid a leading
        blank page."""
        if not self.out:
            return
        for f in reversed(self.out):
            if isinstance(f, PageBreak):
                return
            if isinstance(f, (Spacer, HRFlowable)):
                continue
            break
        self.out.append(PageBreak())

    @staticmethod
    def _is_heading_flow(flow) -> bool:
        return (isinstance(flow, Paragraph)
                and getattr(flow.style, "name", "")
                in {"H1", "H2", "H3", "H4"})

    @staticmethod
    def _is_short_intro_flow(flow) -> bool:
        """A short body paragraph that likely belongs to the preceding heading
        (e.g. the italic scene-reference line under a combat-tracker H2)."""
        if not isinstance(flow, Paragraph):
            return False
        if getattr(flow.style, "name", "") in {"H1", "H2", "H3", "H4"}:
            return False
        try:
            text = flow.getPlainText()
        except Exception:
            return False
        return len(text) <= 300

    def _emit_image(self, img_node: dict) -> None:
        url = img_node.get("attrs", {}).get("url") or img_node.get("url", "")
        if not url:
            return

        alt = (img_node.get("attrs", {}).get("alt", "")
               or _cell_text(img_node.get("children", [])))
        is_tactical_map = (self.section == "combat-tracker"
                           and alt.startswith("Tactical Map"))

        # Look back, skipping trailing decorative flowables, for a heading
        # (optionally with one short intro paragraph between heading and
        # image). If found, bind the heading and image into a `KeepTogether`
        # so ReportLab keeps them on the same page — preventing orphaned
        # headings on otherwise-empty pages. Tactical maps follow this same
        # path; their encounter heading + italic line are bound with the map
        # image (max 7.2"×8.5"), and the `---` that follows the image
        # (handled by _h_thematic_break) adds the PageBreak that separates
        # the map+header page from the tracker sheet.
        end = len(self.out) - 1
        while end >= 0 and isinstance(self.out[end], (Spacer, HRFlowable)):
            end -= 1

        heading_idx = None
        if end >= 0 and self._is_heading_flow(self.out[end]):
            heading_idx = end
        elif end >= 0 and self._is_short_intro_flow(self.out[end]):
            prev = end - 1
            while prev >= 0 and isinstance(self.out[prev], (Spacer, HRFlowable)):
                prev -= 1
            if prev >= 0 and self._is_heading_flow(self.out[prev]):
                heading_idx = prev

        if heading_idx is not None:
            bound = list(self.out[heading_idx:])
            del self.out[heading_idx:]
            img = sized_image(url, self.manifest, max_w_in=7.2, max_h_in=8.5)
            img.hAlign = "CENTER"
            bound.extend([Spacer(1, 4), img])
            self.out.append(KeepTogether(bound))
            self._last_was_map = is_tactical_map
            return

        # No pairing — image flows naturally. ReportLab page-breaks before
        # it if the image doesn't fit in the remaining space (a portrait
        # image won't squeeze into a couple of inches at the bottom of a
        # text page), but a landscape image that does fit will render below
        # preceding text instead of forcing a near-empty page.
        img = sized_image(url, self.manifest, max_w_in=7.2, max_h_in=9.8)
        img.hAlign = "CENTER"
        self.out.append(img)
        self._last_was_map = is_tactical_map


# --- public API ------------------------------------------------------------

_SECTION_FROM_FILENAME = {
    "1-adventure": "adventure",
    "2-combat-tracker": "combat-tracker",
    "3-player-handouts": "player-handouts",
    "4-dm-quick-ref": "dm-quick-ref",
}

def _infer_section(path: Path, meta: dict) -> str:
    if meta.get("section"):
        s = meta["section"].strip()
        if s == "main-body":
            return "adventure"
        return s
    stem = path.stem
    for key, val in _SECTION_FROM_FILENAME.items():
        if stem.endswith(key):
            return val
    return "adventure"

def _make_parser():
    return mistune.create_markdown(renderer=None, plugins=["table"])

def build_pdf(md_files: list[str | Path], images_json: str | Path,
              out_path: str | Path, title: str | None = None) -> Path:
    """Parse the given .md files in order and emit a single PDF at out_path."""
    manifest = load_images(images_json)
    parser = _make_parser()
    story: list = []
    for i, md_path in enumerate(md_files):
        path = Path(md_path)
        text = path.read_text()
        text, meta = strip_frontmatter(text)
        section = _infer_section(path, meta)
        font_scale = float(meta.get("font_scale", 1.0))
        ast = parser(text)
        renderer = BlockRenderer(manifest, section,
                                 first_h1_pagebreak=False,
                                 font_scale=font_scale)
        if i > 0 and story:
            story.append(PageBreak())
        story.extend(renderer.render(ast))
    out = Path(out_path)
    doc = SimpleDocTemplate(
        str(out), pagesize=LETTER,
        leftMargin=0.65*inch, rightMargin=0.65*inch,
        topMargin=0.6*inch, bottomMargin=0.6*inch,
        title=title or out.stem,
    )
    doc.build(story)
    return out
