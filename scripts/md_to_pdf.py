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

# --- colors / styles -------------------------------------------------------

INK = HexColor("#1a1a1a")
ACCENT = HexColor("#5a1a1a")
MUTED = HexColor("#555555")
PARCH = HexColor("#f4ecd8")
PARCH_DK = HexColor("#e8dec1")
ROW_ALT = HexColor("#f7f1e1")

_ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=_ss["Heading1"], fontName="Times-Bold",
    fontSize=18, leading=22, textColor=ACCENT, spaceBefore=14, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=_ss["Heading2"], fontName="Times-Bold",
    fontSize=14, leading=18, textColor=INK, spaceBefore=10, spaceAfter=4)
H3 = ParagraphStyle("H3", parent=_ss["Heading3"], fontName="Times-BoldItalic",
    fontSize=12, leading=15, textColor=ACCENT, spaceBefore=6, spaceAfter=3)
H4 = ParagraphStyle("H4", parent=_ss["Heading4"], fontName="Times-Bold",
    fontSize=11, leading=14, textColor=INK, spaceBefore=4, spaceAfter=2)
BODY = ParagraphStyle("Body", parent=_ss["BodyText"], fontName="Times-Roman",
    fontSize=10.5, leading=14, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6)
BODY_LEFT = ParagraphStyle("BodyL", parent=BODY, alignment=TA_LEFT)
BULLET = ParagraphStyle("Bul", parent=BODY, leftIndent=14, bulletIndent=2, spaceAfter=2)
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

    def __init__(self, manifest: dict, section: str, first_h1_pagebreak: bool = False):
        self.manifest = manifest
        self.section = section  # 'adventure' | 'combat-tracker' | 'player-handouts'
        self.first_h1_pagebreak = first_h1_pagebreak
        self.in_stat_cards = False
        self._h1_seen = False
        self._h2_seen_in_section = False
        self.out: list = []

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
        level = node["attrs"]["level"]
        text = _inline_to_html(node.get("children", []))
        plain = _para_plain_text(node)
        if level == 1:
            if self.first_h1_pagebreak or self._h1_seen:
                self.out.append(PageBreak())
            self._h1_seen = True
            self._h2_seen_in_section = False
            if plain.strip().lower().startswith("stat cards"):
                self.in_stat_cards = True
            self.out.append(Paragraph(text, H1))
        elif level == 2:
            wants_break = self.section in ("combat-tracker", "player-handouts")
            if wants_break and self._h2_seen_in_section:
                self.out.append(PageBreak())
            self._h2_seen_in_section = True
            self.out.append(Paragraph(text, H2))
        elif level == 3:
            self.out.append(Paragraph(text, H3))
        else:
            self.out.append(Paragraph(text, H4))

    def _h_thematic_break(self, node: dict) -> None:
        # Used as a separator. Tracker between encounters/cards already gets
        # PageBreak from H2 handling, so a thin spacer is enough here.
        self.out.append(Spacer(1, 6))

    def _h_paragraph(self, node: dict) -> None:
        children = node.get("children", [])
        # Solo image paragraph -> block image with caption.
        if len(children) == 1 and children[0].get("type") == "image":
            self._emit_image(children[0])
            return
        text = _para_plain_text(node)
        if _is_checkbox_strip(text):
            self.out.append(_render_checkbox_strip(text))
            self.out.append(Spacer(1, 4))
            return
        html = _inline_to_html(children)
        if html.strip():
            self.out.append(Paragraph(html, BODY))

    def _h_block_text(self, node: dict) -> None:
        # Used inside list items.
        html = _inline_to_html(node.get("children", []))
        if html.strip():
            self.out.append(Paragraph(html, BODY_LEFT))

    def _h_block_quote(self, node: dict) -> None:
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
            self.out.append(Paragraph(inner, READ))

    def _h_list(self, node: dict) -> None:
        items = []
        for li in node.get("children", []):
            inner_html = []
            for child in li.get("children", []):
                if child.get("type") == "block_text":
                    inner_html.append(_inline_to_html(child.get("children", [])))
                elif child.get("type") == "paragraph":
                    inner_html.append(_inline_to_html(child.get("children", [])))
            html = "<br/>".join(h for h in inner_html if h.strip())
            items.append(ListItem(Paragraph(html or "&nbsp;", BULLET),
                                  leftIndent=10))
        self.out.append(ListFlowable(items, bulletType="bullet", start="•",
                                     leftIndent=14, bulletFontSize=8,
                                     bulletOffsetY=-1, spaceBefore=2, spaceAfter=6))

    def _h_table(self, node: dict) -> None:
        self.out.append(_render_table(node))
        self.out.append(Spacer(1, 6))

    def _h_block_code(self, node: dict) -> None:
        raw = node.get("raw", "")
        self.out.append(Paragraph(f"<font face='Courier'>{_esc(raw)}</font>", BODY_LEFT))

    # -- image emission -----------------------------------------------------

    def _emit_image(self, img_node: dict) -> None:
        url = img_node.get("attrs", {}).get("url") or img_node.get("url", "")
        alt = _cell_text(img_node.get("children", []))
        if not url:
            return
        if self.section == "player-handouts":
            img = sized_image(url, self.manifest, max_w_in=6.5, max_h_in=7.5)
        else:
            img = sized_image(url, self.manifest, max_w_in=5.5, max_h_in=4.0)
        img.hAlign = "CENTER"
        self.out.append(KeepTogether([img, Paragraph(_esc(alt), CAPTION)]))


# --- public API ------------------------------------------------------------

_SECTION_FROM_FILENAME = {
    "1-adventure": "adventure",
    "2-combat-tracker": "combat-tracker",
    "3-player-handouts": "player-handouts",
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
        ast = parser(text)
        renderer = BlockRenderer(manifest, section,
                                 first_h1_pagebreak=(i > 0))
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
