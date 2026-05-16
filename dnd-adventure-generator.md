# D&D 5e Adventure Generator

This file defines the procedure the agent follows to produce print-ready D&D 5e adventures, encounters, NPCs, and stat blocks. The primary deliverable is a set of Obsidian markdown files with AI-generated portraits and maps embedded by URL; printable PDFs are compiled from those markdown files as a separate, opt-in step.

This is a **preparation tool**, not an interactive DM. Do not simulate gameplay, roll dice, or track party state across sessions. Produce content the DM can read at the table.

## Workflow

Follow these steps in order. Do not skip ahead.

### 1. Scope

If the user hasn't specified what they want, ask whether they're looking for:
- A full adventure
- A single encounter
- An NPC or monster

### 2. Party Info

For adventures or encounters, confirm the party size and level before generating content. Use this to size CR and encounter difficulty correctly.

### 3. Outline & Iterate

Draft the overall idea and plot, and ask for changes. Once that's locked, provide an outline with short descriptions of each encounter or area. Ask for revisions — or whether the user is ready to generate images.

When the outline needs Forgotten Realms canon (a city, faction, deity, recurring NPC), pull it from the markdown extracts in `references/campaign-guide/_raw/` and `references/players-guide/_raw/` (use `full.md` or `pages/page-NNNN.md`; figures are in `images/`). These extracts are the only canon source — the original FR PDFs are no longer in the vault. Source-hierarchy and citation rules live in `agents.md`.

Stay in this loop until the user explicitly says to move to images. Don't jump to image generation on your own.

### 4. Image Generation

Once the user approves moving to images, plan what's needed:
- A portrait for each major NPC or monster
- A top-down map for **every combat encounter** (required — do not skip any)
- A scene/landscape illustration for each major location

Rules for this step:

- Use `generate_image_gemini` (Gemini MCP) for **every** image.
- Never use any other image source. No Pillow, no matplotlib, no SVG drawing, no placeholders, no colored rectangles. Substituting anything else for Gemini is unacceptable.
- If Gemini fails after a single retry, skip that image and tell the user. Never fall back to a placeholder.
- Extract the hosted URL from each tool result. Do **not** extract or decode base64 data — Gemini's URLs are valid for 30 days and are the source of truth.
- Before generating the first image, create an `images/` subfolder inside `sessions/session <N>/`.
- Keep a running list of `{description, url, aspect_ratio}` for every image generated. Persist it as `sessions/session <N>/images/images.json` so the markdown files and the PDF renderer can both reference image sizes without re-querying Gemini. This list is the handoff to Step 5.
- Save each generated image as a jpg file in `sessions/session <N>/images/` using a slugified form of the description as the filename (e.g., `khelziir-portrait.jpg`). If the tool writes a local file, move it there; otherwise download the image from the URL. Saving images locally ensures they are tracked in the git repo and survive Gemini URL expiry.
- Present images to the user by referencing the URLs. Ask for regenerations, changes, or approval to author the markdown files.

### 5. Markdown Authoring

Once images are approved, write four markdown files into `sessions/session <N>/` (the next session number after the highest-numbered existing folder). These are the **primary deliverable** — what the user reviews, edits, and reads at the table. PDF compilation is a separate, opt-in step.

Naming pattern, slugified from the adventure title (e.g., *The Second Cleft* → `the-second-cleft`):

1. `<slug>-1-adventure.md` — main body
2. `<slug>-2-combat-tracker.md` — DM combat tracker
3. `<slug>-3-player-handouts.md` — player handout appendix
4. `<slug>-4-dm-quick-ref.md` — DM quick reference cheat sheet

Each file starts with YAML frontmatter:

```yaml
---
tags: [campaign/session-<N>, <section-tag>, dnd-5e]
session: "<NNN>"
adventure: <Adventure Title>
section: <main-body|combat-tracker|player-handouts|dm-quick-ref>
---
```

The adventure file may add `tier`, `party_level`, and `duration` keys. Inline images use standard markdown `![Caption](https://…)` referencing the Gemini URLs from Step 4 — never download or rehost. Use vanilla Obsidian markdown (tables, headers, lists, fenced code). Do not use Fantasy Statblocks or Admonition syntax unless the user has explicitly asked for them; the print/export pipelines assume plain markdown.

**File 1 — `<slug>-1-adventure.md`:** lead with a summary table (**Title, Tier, Duration, Setting, Hook From**), then the adventure narrative — summary, scenes, encounters, NPCs, treasure, loose ends. **File 1 contains no images.** Do not embed any inline images anywhere in this file — no portraits, no monster art, no scene illustrations, no maps. All imagery lives in File 2 (maps) or File 3 (everything else).

**File 2 — `<slug>-2-combat-tracker.md`:** for every combat encounter: a **dedicated full-page tactical map** followed by a hard page break, then the tracker sheet and stat-block cards described in the Combat Tracker section below. A tactical map is **required** for every combat encounter — do not author a combat encounter entry without one. Tracker sheets and stat-block cards are expressed as markdown tables. HP boxes, round counters, and spell slots use the `☐` glyph (Obsidian renders it; the PDF font does not — see PDF rules).

**File 3 — `<slug>-3-player-handouts.md`:** opens with a **"Where We Left Off" recap page** (see the **Session Recap Page** section below), then **every non-tactical image generated in Step 4** — NPC portraits, monster art, location scenes — each under its own `##` heading naming the subject. One image per section. This file is the **sole home** for adventure imagery: because File 1 carries no images, every portrait, monster, and location illustration the players ever see is here. **Tactical / encounter maps never appear in this file** — they live in File 2 (combat tracker) so the DM keeps them table-side without revealing the encounter layout to the players.

**File 4 — `<slug>-4-dm-quick-ref.md`:** print-and-keep-at-the-table cheat sheet. Tables and short bulleted lists only — no narrative. See the **DM Quick Reference** section below for the contents and structure.

Present the four file paths to the user. Stop here and wait for review. Once the user approves the markdown as canon, **proceed to Step 6 (Update the Campaign Bible) automatically — do not wait for a separate ask.** Do **not** proceed to Step 7 (PDF compilation) unless the user explicitly asks for it.

### 6. Update the Campaign Bible

Once the four markdown files are approved as canon, the campaign bible must be updated to reflect the new content. **Treat this as a required step in the generation workflow, not an optional follow-up.** Different files update at different points in the session lifecycle — call out the timing distinction explicitly to the user when proposing changes.

**Update immediately, before the session is played:**

- **`campaign/roster.md`** — full entries for any new recurring NPCs (role, affiliation, location, status, one-line summary, appearance, personality, motivations, party relationship, statline reference pointing to `<slug>-2-combat-tracker.md` by wikilink). Add new edges to the NPC Relationship Web. Promote any noteworthy mechanical details that the DM will want at-a-glance during play (a recurring NPC's bargain matrix, a vendetta flag, a faction-link callout) so they live in the roster, not buried in the session file.
- **`campaign/factions.md`** — new faction intelligence, organizational details, retaliation clocks, doctrinal signatures, iconography, and references to any homebrew stat blocks introduced in the combat tracker (link by wikilink). When the new content extends an existing faction section, expand that section in place rather than appending a parallel one.
- **`campaign/geography.md`** — new permanent locations, dungeon sites, regional landmarks, or travel routes. Place under the **DM Additions** section, tag `(DM ADDITION)`, and add a source-notes callout when the surrounding region is canonical FR so the DM/CG/PG provenance is clear.

**Hold until after the session is actually played:**

- **`campaign/session-log.md`** — Session Index row, Campaign Arc refresh, Recent Session pointer, Loose Ends Tracker resolutions, Foreshadowing Log entries. **Do not write session-log entries based on planned content — only on what actually happened at the table.** State this hold explicitly to the user when proposing the pre-play bible updates so they know `campaign/session-log.md` is intentionally untouched. The user runs the session, then asks for a post-play log update as a separate request. **Never copy read-aloud / spoke text from the session plan into any session log** — summarize what happened in plain prose instead. Read-aloud text is a DM preparation artifact; it is not a record of what occurred.

**Edit mode depends on agent capability.** When running with file-write access (Augment, Cursor, similar), edit the bible files directly using file-editing tools and summarize the diff back to the user. When running as a stock chat model without write access, produce copy-pasteable markdown blocks instead. In either mode, surface every change to the user, never silently modify content, and never claim a file was edited if it wasn't.

**Scratch files** — if the session prep produced a working scratch file (e.g., `session-<N>-plan.md`), delete it as part of this step once the three deliverables are authored and the bible is updated. The deliverables and the bible are the persistent record; the scratch plan is not.

After the bible is updated, present a summary of the diff and stop. Step 7 is opt-in.

### 7. PDF Compilation (on request)

Only run this step when the user explicitly asks for PDFs. The four markdown files from Step 5 are the source of truth; the PDF is rendered **from** them. Never write narrative content into the PDF build that doesn't exist in the markdown — if something needs to change, change the markdown and rebuild.

Two acceptable approaches — ask which the user prefers if it isn't already established:

- **Obsidian-native** — the user exports each markdown file via the **Better Export PDF** plugin (configured in `Obsidian Setup.md`, with the `dnd-print.css` snippet enabled). The agent's job is to make sure the markdown renders cleanly. No script work required.
- **ReportLab build (markdown → PDF renderer)** — for adventures that need rendered checkbox cells, parchment stat-card backgrounds, or a single combined PDF, run the reusable build script at `scripts/build_pdf.py`. It parses the four markdown files in order (`<slug>-1-adventure.md` → `<slug>-2-combat-tracker.md` → `<slug>-3-player-handouts.md` → `<slug>-4-dm-quick-ref.md`) and emits a single PDF. The script contains no duplicated narrative — narrative lives only in the markdown.

The reusable scripts:

- **`scripts/build_pdf.py`** — CLI entry point. Auto-discovers the session folder, slug, the markdown files (the three required plus the optional file 4 when present), `images.json`, and PDF title (from the adventure file's `adventure:` frontmatter key). Do not copy this into the session folder; invoke it from the repo root.
- **`scripts/md_to_pdf.py`** — the markdown→Platypus renderer (page styles, AST walker, checkbox replacement, stat-card and init-table special cases). Imported by `build_pdf.py`. Session-agnostic; do not copy or fork per session.

ReportLab build rules (these describe what `scripts/md_to_pdf.py` already implements; touch the script if any of these need to change, never reimplement per session):

- Parse each markdown file with a library that exposes an AST. The current implementation uses `mistune` v3 in AST mode (with the `table` plugin). Walk the AST and map nodes to Platypus flowables.
- Required node mappings:
  - `heading` level 1 → page break + `H1` Paragraph
  - `heading` level 2/3 → `H2` / `H3` Paragraph
  - `paragraph` → body Paragraph (preserve inline `em` / `strong` / `code`)
  - `list` → `ListFlowable` of bullet or numbered items
  - `table` → ReportLab `Table` with the standard grid style; tables matching tracker patterns get the special styling described in the Combat Tracker section
  - `image` (`![alt](url)`) → stream the URL into a `BytesIO` with `urllib` or `requests` and emit an `Image()` sized to fill an 8.5"×11" page (max 7.2"×9.8") while preserving the captured aspect ratio (see `images.json` below). No PIL/Pillow. **Every image renders at full-page size** — portraits, monster art, location scenes, and tactical maps alike. There is no inline / thumbnail variant. When the immediately preceding flowable is a section heading (optionally with one short intro paragraph), the renderer binds them with the image in a `KeepTogether` and shrinks the image to max 7.2"×8.5" so the heading + image pair fits one page. Otherwise the image flows naturally — ReportLab page-breaks before it if it doesn't fit in the remaining space, but a short landscape image will render below trailing text on the same page rather than forcing a near-empty page.
  - `block_code` (fenced) → preformatted Paragraph in a monospace style
  - `block_quote` → indented body Paragraph
- **Checkbox glyphs.** Whenever a paragraph or table cell contains `☐`, the renderer replaces each glyph with a small empty bordered cell. Times-Roman does not carry `☐` and falls back to a filled square. Do not register a substitute font; replace at render time so the boxes are crisp and consistently sized.
- **Image sizing.** Every image renders **full-page on an 8.5"×11" sheet** — sized to fill the printable area while preserving aspect ratio. Max 7.2"×9.8" for an unbound image; max 7.2"×8.5" when bound to a heading via `KeepTogether` (so the heading + image fit one page). Step 4 captures `{description, url, aspect_ratio}` for each image; persist that list as `images/images.json` in the session folder so the renderer can letterbox correctly without re-querying Gemini. Lookup is by URL; if a URL isn't found, fall back to a 4:3 default and warn. Generate every image at high enough resolution to print at full size.
- **Page-break placement.** The renderer aims to keep the page filled. Concretely: each section heading immediately followed by an image is bound to that image (`KeepTogether`) so the heading isn't orphaned on an otherwise-empty page; an image not bound to a heading flows naturally — ReportLab page-breaks before it if it doesn't fit in the remaining space, but a short landscape image will render below trailing text rather than force a near-empty page. Adjacent page breaks are coalesced (no blank pages), and body paragraphs use `allowWidows=0` / `allowOrphans=0` so a paragraph can't leave one stray line at the top of an otherwise-empty page. In the combat-tracker file, each encounter (`## Encounter N`) still gets its own page boundary so the tracker sheet stays organized; in the adventure and player-handout files, H2 sections flow naturally so two short entries (e.g., two landscape-image handouts) can share a page.
- **Output:** single PDF at `sessions/session <N>/<adventure-slug>.pdf` (the slug is derived from `<slug>-1-adventure.md`).
- **Run:** from the repo root, `.venv/bin/python scripts/build_pdf.py [<session-number-or-folder>]`. With no argument it builds the latest session; pass `3` or `"sessions/session 3"` to target a specific one. Optional `--title` and `--out` flags override the auto-detected title and output path. Tell the user the PDF path on completion; the user opens it themselves in Obsidian or Finder.
- **Dependencies:** `mistune` and `reportlab`, installed into a project venv at `.venv/`. If the venv is missing, create it once with `python3 -m venv .venv && .venv/bin/python -m pip install mistune reportlab`. Do not install into the system Python (Homebrew Python is PEP 668 externally-managed).

## Text Standards

**Adventures** include: hook, overview, locations, encounters, NPCs, and treasure.

**Encounters** include: setup, environment, tactics, read-aloud/boxed text, and scaling notes (Easy–Deadly).

**NPCs & PCs** include: personality (traits, ideals, bonds, flaws) and a full 5e stat block (AC, HP, Speed, Ability Scores with modifiers, Saves, Skills, Senses, Languages, CR, Actions, Reactions, Legendary Actions where appropriate).

**Rules**: Use official 5e rules. Mark any homebrew with ⚗️.

## Image Generation Specs

All images come from `generate_image_gemini`. Write rich, specific prompts (>15 words) that name the subject, mood, color palette, and style. Always work with the returned URL, never the base64 payload.

- **Tactical / encounter maps**: Top-down, print-optimized (minimal background clutter, high contrast). Include a scale indicator, N-arrow, and room/area labels. Use `aspect_ratio="4:3"` for landscape or `aspect_ratio="3:4"` for portrait. **Always generate at full-page resolution** — every map prints at full 8.5"×11" size, one map per page, with no surrounding content crowding it. A map is **required for every combat encounter** — generate it in Step 4 before authoring File 2. Tactical maps belong to **File 2 only** (the combat tracker). Never embed them in File 1 (adventure narrative) or File 3 (player handouts) — players should not see the encounter layout.
- **Portraits**: `aspect_ratio="3:4"`, painterly fantasy style, neutral background. Must match the text description exactly — armor, species, distinguishing features, attitude. Generated at full-page resolution — every portrait renders at full-page size in the handout appendix.
- **Location art**: `aspect_ratio="16:9"` for scene/landscape illustrations. Generated at full-page resolution — every location scene renders at full-page width; following content flows into the space below.

Never use any built-in vector drawing tool or any Python-drawn graphics for adventure art. Maps, portraits, and scene art come from Gemini only.

## PDF Formatting

- Lead with a summary block: **Title, Tier, Duration, Setting**.
- Use clear headers and styled body text via ReportLab Platypus paragraph styles.
- Images flow through from the markdown only — the renderer does not insert images that aren't already in the source files. File 1 carries no images. Every portrait, monster art, and scene illustration renders inside the handout appendix (File 3), each under its own subheading. Tactical maps render full-page from File 2 only, each on its own dedicated page followed by a hard page break before the tracker sheet.
- **Every image renders full-page (8.5"×11").** The renderer page-breaks before and after each `![alt](url)` and sizes the image to fill the printable area while preserving its aspect ratio. There is no inline / shrunken variant — portraits, monster art, location scenes, and tactical maps all print at full-page size.
- Images stream from their Gemini URLs into memory at PDF build time — no local caching required.
- Final PDF output goes to `sessions/session <N>/<adventure-slug>.pdf`. The user opens it in Obsidian or Finder; do not attempt to invoke a presentation tool.

### Session folder layout

Each session lives in `sessions/session <N>/` with this file layout:

**Markdown deliverables (always produced — Step 5):**

- `<adventure-slug>-1-adventure.md` — main adventure body.
- `<adventure-slug>-2-combat-tracker.md` — per-encounter trackers and stat-block cards.
- `<adventure-slug>-3-player-handouts.md` — labeled images, one per section.
- `<adventure-slug>-4-dm-quick-ref.md` — DM quick-reference cheat sheet.

**Image assets (always written when Step 4 runs):**

- `images/images.json` — list of `{description, url, aspect_ratio}` captured during image generation. The renderer uses `aspect_ratio` to size each `Image()`. Always present so the PDF can be built later without re-querying Gemini.
- `images/<description-slug>.jpg` — one jpg per generated image, named from the description slug. Tracked in git so images survive Gemini URL expiry.

**ReportLab PDF artifact (only when the user asks for a scripted PDF — Step 7):**

- `<adventure-slug>.pdf` — the build output. Produced by `scripts/build_pdf.py` from the markdown files plus `images/images.json`.

The build scripts themselves live at the repo root, not per-session: `scripts/build_pdf.py` (CLI entry point) and `scripts/md_to_pdf.py` (markdown→Platypus renderer). Do not copy them into the session folder. The old per-session `build_pdf_content.py`, `combat_tracker.py`, `combat_stat_blocks.py`, and `combat_render.py` modules are no longer used either. All adventure, encounter, stat-block, and quick-reference content lives in the four markdown files; the renderer parses them.

## Combat Tracker

Every adventure must include a **DM combat tracker** — as the dedicated `<slug>-2-combat-tracker.md` file (always) and, when a ReportLab PDF is built, as a section between the main body and the player handout appendix. The tracker is a printable, fillable reference the DM uses at the table — it is not a replacement for the encounter prose in the main body.

### Per-encounter contents

For each combat encounter in the adventure, generate:

**1. Tactical map** — **required for every combat encounter.** Do not write a combat encounter entry without one. The map occupies its own dedicated page immediately after the encounter heading: the image fills the printable area of one full 8.5"×11" page, followed by a hard page break before the tracker sheet begins. This keeps the map and the tracker on separate pages so the DM can tear them apart or lay them side-by-side at the table. Tactical maps are **DM-only**: they live in File 2 alone, never in File 1 (narrative) or File 3 (player handouts). Use `aspect_ratio="4:3"` for landscape encounters or `aspect_ratio="3:4"` for portrait; the renderer sizes the map to fill the printable area while preserving aspect ratio.

**2. Tracker sheet (one page per encounter)** containing:
- Header strip: encounter name, scene reference, location, difficulty (XP total + threshold), light, terrain.
- Round counter: 10 tick boxes labeled 1–10.
- **Initiative & damage table** — NPC rows with **pre-rolled initiative** (averaged from DEX), AC, HP shown as **tick boxes at 5 HP per box** (DM crosses out as damage is dealt), and a notes column. **Blank rows are interleaved with the monsters so the DM can write each PC into the table at the right initiative count after dice are rolled.** See the *Initiative table layout* rules below.
- Conditions reference strip (5e abbreviations: Bln · Chr · Deaf · Frt · Grp · Inc · Inv · Prl · Pet · Pzn · Prn · Rst · Stn · Uns · Conc).
- Triggers, countdowns, reinforcement conditions (bulleted) — anything time-sensitive that affects when/how the fight escalates.
- Concentration / Ongoing Effects write-in box (3 blank lines).
- Tactics summary line per non-PC combatant.
- Loot/aftermath note.
- Notes write-in box (resources spent, persisting conditions, XP awarded).

**3. Stat-block cards** for every unique non-PC combatant in that encounter:
- Title + type/alignment line + CR (XP). (No portrait on the card itself — portraits live in the handout appendix; stat-block cards stay compact for table use.)
- AC / HP / Speed; ability scores; saves, skills, senses, languages.
- Traits — write innate spellcasting as `1× spell · 1× spell · 1× spell` so the DM strikes uses inline rather than relying on a checkbox glyph.
- Spellcasting block with **slot tick boxes per spell level** (1st/2nd/3rd…), DC, attack modifier.
- Actions, Reactions, Legendary Actions where applicable.
- Tactics paragraph (round-by-round if the creature has a defined opener).
- On-defeat loot.

If a creature type appears in multiple encounters, **reprint** its card under each encounter rather than referencing back. The DM should not need to flip pages mid-fight.

### Markdown form

In `<slug>-2-combat-tracker.md`, render each encounter as:

- A level-2 heading (`## Encounter N — <name>`) plus an italic line with scene reference and difficulty.
- A **tactical map** image on its own line immediately under the heading: `![Tactical Map — <encounter name>](<url>)`. The alt text starts with `Tactical Map` so the encounter section is self-labeling. The map occupies its own dedicated page (the renderer inserts a page break before and after the image). A `---` thematic break (rendered as a page break) follows the image to separate the map page from the tracker sheet.
- A small key/value table for **Location**, **Light**, **Terrain**.
- A round strip line: `**Round:** ☐ 1 · ☐ 2 · ☐ 3 · …` through 10.
- An **Initiative & Damage** markdown table with pre-filled NPC rows interleaved with blank PC rows (`__` / `_________________`) per the *Initiative table layout* rules below. Render HP as `<total>: ☐☐☐☐☐ ☐☐☐☐☐ …` (5 HP per box, ceiling-rounded).
- `### Triggers & Countdowns`, `### Concentration / Ongoing Effects`, `### Tactics Summary`, `### Loot / Aftermath`, and `### Notes` sections.

Stat-block cards follow as level-3 sections under each encounter, reprinted in full when a creature appears in multiple encounters.

#### Initiative table layout

Blank rows are placed around the monster rows so the DM can slot each PC into the right initiative count after live dice are rolled. The rules:

1. **Each monster (or same-init monster group) gets at least 2 blank rows above and at least 2 blank rows below it.**
2. **Monsters with the same pre-rolled initiative are listed adjacent** — no blank rows between them. The 2-above / 2-below buffer applies to the group, not each member.
3. **Monsters with different initiatives are separated by 2 blank rows.** The 2-below of the higher-init monster and the 2-above of the lower-init monster overlap into a single 2-row gap.
4. **Every initiative table has at least 6 blank rows total.** If rules 1–3 produce fewer than 6 (e.g., a single-monster encounter), pad evenly — add a third blank row above and a third below.

Worked examples (assuming a party that needs ~5 PC slots):

- *1 monster* → 3 blank · monster · 3 blank (6 blanks total — padded for the minimum)
- *2 monsters at the same init* → 3 blank · M · M · 3 blank (6 blanks total — padded)
- *3 monsters at different inits (A > B > C)* → 2 blank · A · 2 blank · B · 2 blank · C · 2 blank (8 blanks total — already over the minimum)
- *3 monsters, two share an init (A > B = C)* → 2 blank · A · 2 blank · B · C · 2 blank (6 blanks total)

Blank-row format matches the column widths exactly:
`| __ | _________________ | __ | _________________ | _________________ |`

Do **not** include `_PC 1_` / `_PC 2_` placeholder labels in the blank rows — the DM writes the PC name directly into the cell when assigning initiative. Do **not** hard-code a fixed PC count; the layout is monster-relative and works for any party size.

### PDF rendering pattern (only when compiling a ReportLab PDF)

The combat tracker section of the PDF is rendered by `md_to_pdf.py` directly from `<slug>-2-combat-tracker.md`. There are no parallel python data modules — the markdown is the source. The renderer recognizes the patterns from the **Markdown form** above and applies these special cases when emitting Platypus flowables:

- A markdown table whose header row is `Init | Combatant | AC | HP | Notes` becomes the **initiative table**: alternating row shading, fixed column widths. Each HP cell text matching `<n>: <runs of ☐>` is split — the integer is left-aligned as a label (`HP 78`), and the `☐` runs are replaced with bordered tick boxes (5 HP per box).
- A paragraph beginning `**Round:**` followed by `☐ N · ☐ N …` becomes the **round strip**: a row of bordered numbered tick boxes, one per round 1–10.
- A level-3 heading naming a creature, followed by a key/value block (`AC`, `HP`, `Speed`, ability scores, traits, actions), becomes a **stat-block card** with parchment background and a thin accent border. Stat-block cards never embed images — portraits live in the handout appendix.
- **Every `![alt](url)` image renders full-page**, including tactical maps: a page break is inserted before, the image is sized to fill the printable area while preserving aspect ratio, and a page break follows. A `---` thematic break immediately after a tactical map image is rendered as an additional explicit page break, ensuring the map and the tracker sheet always land on separate pages. No caption is rendered (the surrounding heading already names it).
- A line of `☐` glyphs inside a Spellcasting block (e.g., `1st: ☐ ☐ ☐`) becomes a row of spell-slot tick boxes, one per slot.
- A `### Notes` or `### Concentration / Ongoing Effects` section whose body is a sequence of underscore lines (`______`) renders as a bordered write-in box with the right number of blank lines.

These rules are **single-pass and pattern-based** — the renderer recognizes shapes in the parsed markdown rather than consulting a separate data structure. If the markdown matches the patterns documented under **Markdown form**, the PDF inherits the right styling automatically.

### PDF rendering rules

- **Replace every `☐` glyph with a rendered bordered cell.** Times-Roman does not carry the ballot-box glyph and falls back to a filled square. The renderer's checkbox helper substitutes empty-bordered cells of a fixed point size. (The markdown file keeps `☐` because Obsidian renders it correctly — this rule is PDF-only.)
- **Pre-roll NPC initiative** so it is printed in the markdown, and the PDF inherits it. PCs roll live and write into the blank rows. Use the average of `1d20 + DEX_mod` rounded to the nearest integer.
- **HP tick boxes** use 5 HP per box, ceiling-rounded. Print the total HP next to the boxes (e.g., `HP 78`) so the DM can confirm.
- **Spell-slot tick boxes** match the level's slot count exactly. Cantrips have no boxes.
- Stat-block cards use a parchment background and a thin accent border to distinguish them visually from narrative content.
- Initiative tables alternate row shading lightly to keep rows scannable.
- Single-encounter trackers should fit on one page when feasible. Boss-tier encounters with 5+ combatants and multiple triggers may flow to a second page; do not compress to fit.
- **Every image renders at full-page size on an 8.5"×11" sheet** — max 7.2"×9.8" unbound, max 7.2"×8.5" when paired with a heading via `KeepTogether`. Portrait images (3:4) fill the page; landscape images (16:9, 4:3) preserve aspect ratio and let surrounding content flow into the remaining vertical space. Heading + image pairs are bound together so headings aren't orphaned. Adjacent page breaks are coalesced, and body paragraphs use `allowWidows=0` / `allowOrphans=0` so a paragraph can't leave one stray line alone at the top of an otherwise-empty page.

### Reuse across sessions

The renderer (`scripts/md_to_pdf.py`) and the CLI (`scripts/build_pdf.py`) are session-agnostic and live at the repo root. Reference them in place — do not copy or fork them into session folders. Only the four markdown files and `images.json` are written fresh per session; the PDF is rebuilt from them on demand.

## Session Recap Page

Every player-handout file (`<slug>-3-player-handouts.md`) **opens with a one-page recap of the previous session** so the players can re-orient before play begins. It is the first page of the handout appendix — before any NPC/location/monster handouts.

Source the recap from `campaign/session-log.md` (the most recent played-session entry). If the prior session has not yet been logged — e.g., the recap is being authored before the post-play update — pull from the prior session's adventure file (`sessions/session <N-1>/<slug>-1-adventure.md`) and flag the gap to the user. Session 1 has no recap; skip the page and note it in the file's preamble.

### Form

- A level-1 heading: `# Where We Left Off`.
- **One image** at the top: a scene illustration of the location the PCs are starting this session at. This is usually the same location they ended the previous session at (a cold camp, the doorway of a dungeon they didn't enter, the road outside a town). Generate it in Step 4 like any other location image, with `aspect_ratio="16:9"`, and add it to `images/images.json`. It also gets its own `## <Location Name>` section later in the handout file like any other location image — the recap reuses the URL, it does not duplicate the entry in `images.json`.
- **Brief recap prose** — 4–8 short sentences or bullet points covering: where the party is now, what they accomplished last session, what they learned, and the immediate decision in front of them. Bold the key facts. No spoilers for the new adventure.
- Optional **"What Now?"** bulleted list of 1–3 immediate hooks or choices, framed as the party's options at the table.
- Frontmatter stays the standard player-handouts block (`section: player-handouts`); no separate section tag.
- Followed by a `---` thematic break, then the rest of the handout entries.

The recap is a player-facing artifact — write it in the second person ("You burned a wounded drider…"), keep the tone tight, and avoid DM-only information (faction maneuvering the party hasn't seen, hidden NPC motivations, future encounter setups).

## DM Quick Reference

Every adventure must include a **DM quick reference cheat sheet** as `<slug>-4-dm-quick-ref.md`. It is a print-and-keep-at-the-table summary of the at-a-glance information the DM needs mid-session, condensed from File 1. Tables and short bulleted lists only — full prose stays in File 1. If the DM has to re-read the adventure body to find a number, the cheat sheet has failed.

### Required sections

Adapt the section list to the adventure's actual content — don't include sections that don't apply, but don't skip ones that do. The standard set is:

- **Scene Order** — single table: `# | Scene | Key mechanic | DM flag`. One row per scene (cold open through debrief).
- **Boss / Countdown mechanics** — for any encounter with a ticking timer, ritual, escalation trigger, or named-NPC ability stack: a small table summarizing how to stop it, caveats, and what happens at zero.
- **NPC behavior priority** — for boss-tier or returning antagonists: a round-by-round action/bonus-action table or a short tactics summary.
- **Faction priorities & timing** — for multi-faction fights or pressure-valve encounters (e.g., a third faction crashing the boss fight): a bulleted list of trigger conditions, faction priorities, and the resulting major loose ends.
- **Bargain / negotiation matrix** — for any scene where a fey, devil, hag, or merchant offers boons in exchange for costs: a table of `Boon | Effect | Cost tier`. Include stiffed/threatened/probed-on-secret responses as bullets below.
- **Endings** — for adventures with branching outcomes: a table of `Ending | How | Reputation | Loose end` with one row per ending plus a `Withdraw without ending` row when relevant.
- **Debrief payments** — table of `Item | Condition | Payer | Amount`, including the milestone or XP advance.
- **Who-talks-to-whom branches** — for sessions that fork on which NPC the party reports to first: a short bullet list with the consequence of each choice.
- **Tone / staging beats** — short bulleted tells the DM should cue at the table (a recurring NPC's posture changes, a one-line read-aloud, a callback to a prior session).
- **Loose Ends to Flag in Session Log After Play** — a checklist of `- [ ]` items the DM ticks off after the session, which the agent will fold into `campaign/session-log.md` when asked for a post-play update.

### Form

- Frontmatter: `section: dm-quick-ref`, plus the standard `tags`, `session`, `adventure` keys.
- Title: `# DM Quick Reference — <Adventure Title>` followed by an italic line: `*Session NNN · Print and keep at the table · Full detail in file 1*`.
- Each section is a level-2 heading separated by `---` thematic breaks.
- No inline images. No long prose blocks. If a sentence runs more than two lines, it belongs in File 1.
- Cross-references to File 1 are by scene number / scene name, not by page.
- Numbers must match File 1 and File 2 exactly. If something changes in the adventure, update the cheat sheet in the same edit.