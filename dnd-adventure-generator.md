# D&D 5e Adventure Generator

This file defines the procedure the agent follows to produce print-ready D&D 5e adventures, encounters, NPCs, and stat blocks. The primary deliverable is a set of GitHub-flavoured Markdown files with AI-generated portraits and maps embedded by URL; printable PDFs are compiled from those markdown files as a separate, opt-in step.

This is a **preparation tool**, not an interactive DM. Do not simulate gameplay, roll dice, or track party state across sessions. Produce content the DM can read at the table.

## Invariants

These cross-cutting rules hold throughout the workflow and the PDF pipeline. The sections below restate the section-specific details, but these are the canonical statements — when in doubt, follow these.

- **Four deliverables.** Every adventure produces four markdown files in `sessions/session <N>/`: `-1-adventure`, `-2-combat-tracker`, `-3-player-handouts`, `-4-dm-quick-ref`. They are the source of truth; the PDF renders **from** them and never adds narrative that isn't in the markdown.
- **Image placement.** File 1 carries exactly one image (the title page illustration). Tactical/encounter maps live in **File 2 only**, as part 6 of each encounter's section. Every other illustration (portraits, monster art, location scenes) lives in **File 3 only**. Stat-block cards are **text-only** — never embed an image in or beside one.
- **Image rendering.** Every image renders **full-page on an 8.5"×11" sheet**, preserving aspect ratio — no inline/thumbnail variant. Max **7.2"×9.8"** unbound; max **7.2"×8.5"** when bound to a heading via `KeepTogether`. Aspect ratios come from `images.json`; there is no PIL/Pillow.
- **Image source & durability.** All art comes from the `generate_image` (Gemini) MCP tool. Save each as a git-tracked jpg and record its filename in `images.json` under `file`. The ReportLab renderer reads that local jpg, so a scripted PDF still builds after the Gemini URL expires (~30 days).
- **Never schedule level-ups mid-session.** Do not plan a level-up as an at-the-table beat — rebuilding sheets during play takes too much time and stalls the session. If an adventure crosses a milestone (or enough XP to advance), record the advancement as something to apply **between sessions** (downtime / before the next session), not a live beat. In the DM quick reference and any debrief, flag the milestone as *earned, to be applied later* — never "the party levels up now."

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

When the outline needs Forgotten Realms canon (a city, faction, deity, recurring NPC), pull it from the markdown extracts in `references/campaign-guide/_raw/` and `references/players-guide/_raw/` (use `full.md` or `pages/page-NNNN.md`; figures are in `images/`). These extracts are the only canon source — the original FR PDFs are no longer in the repo. Source-hierarchy and citation rules live in `AGENTS.md`.

Stay in this loop until the user explicitly says to move to images. Don't jump to image generation on your own.

### 4. Image Generation

Once the user approves moving to images, plan what's needed:
- A **title page illustration** of the adventure's primary setting (required — one per adventure)
- A portrait for each major NPC or monster
- A top-down map for **every combat encounter** (required — do not skip any)
- A scene/landscape illustration for each major location

Rules for this step:

- Use `generate_image` (Gemini MCP) for **every** image.
- Never use any other image source. No Pillow, no matplotlib, no SVG drawing, no placeholders, no colored rectangles. Substituting anything else for Gemini is unacceptable.
- If Gemini fails after a single retry, skip that image and tell the user. Never fall back to a placeholder.
- Extract the hosted URL from each tool result. Do **not** extract or decode base64 data — Gemini's URLs are valid for 30 days and are the source of truth.
- Before generating the first image, create an `images/` subfolder inside `sessions/session <N>/`.
- Save each generated image as a jpg file in `sessions/session <N>/images/` using a slugified form of the description as the filename (e.g., `khelziir-portrait.jpg`). If the tool writes a local file, move it there; otherwise download the image from the URL. The local jpg is committed to git and is the **durable** copy: the PDF renderer reads it directly, so the adventure still builds after the Gemini URL expires (~30 days).
- Keep a running list of `{description, url, aspect_ratio, file}` for every image generated, where `file` is that saved jpg's filename. Persist it as `sessions/session <N>/images/images.json` so the markdown files and the PDF renderer can both reference image sizes without re-querying Gemini, and so the renderer can locate the local jpg. This list is the handoff to Step 5.
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

The session number appears in two intentionally different forms: the folder is `sessions/session <N>` with the bare number (e.g. `session 3`), while the `session:` frontmatter key and the quick-ref `Session NNN` line use a zero-padded three-digit form (e.g. `003`). Both refer to the same session; the padding keeps frontmatter values sorting correctly.

The adventure file may add `tier`, `party_level`, and `duration` keys. Inline images use standard markdown `![Caption](https://…)` referencing the Gemini URLs from Step 4 — never download or rehost. (The ReportLab renderer prefers the git-tracked local jpg via the `images.json` `file` key, so a scripted PDF still builds after a URL expires; on-screen GitHub rendering uses the embedded URL and so depends on it still being live.) Use plain GitHub-flavoured Markdown (tables, headers, lists, fenced code, and the five GitHub alert types). Do not use Fantasy Statblocks or Obsidian Admonition syntax; the print/export pipelines assume plain markdown.

**File 1 — `<slug>-1-adventure.md`:** opens with a **full-page title page**, then the adventure narrative — summary, scenes, encounters, NPCs, treasure, loose ends.

The title page is the **only image in File 1**. Structure it as:
1. A level-1 heading with the adventure title (`# <Title>`).
2. A compact summary table with two columns (label / value) covering **Tier**, **Party Level**, **Duration**, **Setting**, and **Hook From**.
3. The title page illustration on its own line: `![Title Page — <Adventure Title>](<url>)`. Use the `3:4` portrait-orientation setting illustration generated in Step 4 — it fills an 8.5"×11" portrait page cleanly. The renderer places the heading + summary table on the page, then the image fills the next full page, producing a two-page title spread.
4. A `---` thematic break after the image to signal the end of the title page before the narrative begins.

No other images appear anywhere else in File 1 — no portraits, no monster art, no scene illustrations, no additional maps. The title page illustration URL is reused in File 3 under its location section; the `images.json` entry is not duplicated. All other imagery lives in File 2 (maps) or File 3 (everything else).

**File 2 — `<slug>-2-combat-tracker.md`:** for every combat encounter, content is rendered in this **strict order**: (1) combat title heading, (2) italic subtitle line, (3) encounter summary table, (4) initiative table + tracker sheet sections, (5) stat-block cards for every non-PC combatant with round-by-round actions, (6) a **hard page break followed by a full-page tactical map on its own page**. See the Combat Tracker section below for the full specification. A tactical map is **required** for every combat encounter — do not author a combat encounter entry without one. Tactical maps live in File 2 **only** — never in File 1 or File 3. NPC portraits live in File 3 **only** — never in File 2. Tracker sheets and stat-block cards are expressed as markdown tables. HP boxes, round counters, and spell slots use the `☐` glyph (GitHub renders it; the PDF font does not — see PDF rules).

**File 3 — `<slug>-3-player-handouts.md`:** opens with a **"Where We Left Off" recap page** (see the **Session Recap Page** section below), then **every non-tactical image generated in Step 4** — NPC portraits, monster art, location scenes — each under its own `##` heading naming the subject. One image per section. This file is the **sole home** for player-facing adventure imagery: the title page illustration URL is reused here under its location section (File 1 holds the only other copy), and every portrait, monster, and location illustration the players ever see is here. **Tactical / encounter maps never appear in this file** — they live in File 2 (combat tracker) so the DM keeps them table-side without revealing the encounter layout to the players.

**File 4 — `<slug>-4-dm-quick-ref.md`:** print-and-keep-at-the-table cheat sheet. Tables and short bulleted lists only — no narrative. See the **DM Quick Reference** section below for the contents and structure.

Present the four file paths to the user. Stop here and wait for review. Once the user approves the markdown as canon, **proceed to Step 6 (Update the Campaign Guide) automatically — do not wait for a separate ask.** Do **not** proceed to Step 7 (PDF compilation) unless the user explicitly asks for it.

### 6. Update the Campaign Guide

Once the four markdown files are approved as canon, the campaign guide must be updated to reflect the new content. **Treat this as a required step in the generation workflow, not an optional follow-up.** Different files update at different points in the session lifecycle — call out the timing distinction explicitly to the user when proposing changes.

**Update immediately, before the session is played:**

- **`campaign/roster.md`** — full entries for any new recurring NPCs (role, affiliation, location, status, one-line summary, appearance, personality, motivations, party relationship, statline reference pointing to `<slug>-2-combat-tracker.md` by wikilink). Add new edges to the NPC Relationship Web. Promote any noteworthy mechanical details that the DM will want at-a-glance during play (a recurring NPC's bargain matrix, a vendetta flag, a faction-link callout) so they live in the roster, not buried in the session file.
- **`campaign/factions.md`** — new faction intelligence, organizational details, retaliation clocks, doctrinal signatures, iconography, and references to any homebrew stat blocks introduced in the combat tracker (link by wikilink). When the new content extends an existing faction section, expand that section in place rather than appending a parallel one.
- **`campaign/geography.md`** — new permanent locations, dungeon sites, regional landmarks, or travel routes. Place under the **DM Additions** section, tag `(DM ADDITION)`, and add a source-notes callout when the surrounding region is canonical FR so the DM/CG/PG provenance is clear.

**Hold until after the session is actually played:**

- **`campaign/session-log.md`** — Session Index row, Campaign Arc refresh, Recent Session pointer, Loose Ends Tracker resolutions, Foreshadowing Log entries. **Do not write session-log entries based on planned content — only on what actually happened at the table.** State this hold explicitly to the user when proposing the pre-play guide updates so they know `campaign/session-log.md` is intentionally untouched. The user runs the session, then asks for a post-play log update as a separate request. **Never copy read-aloud / spoke text from the session plan into any session log** — summarize what happened in plain prose instead. Read-aloud text is a DM preparation artifact; it is not a record of what occurred.

**Edit mode depends on agent capability.** When running with file-write access (Augment, Cursor, similar), edit the guide files directly using file-editing tools and summarize the diff back to the user. When running as a stock chat model without write access, produce copy-pasteable markdown blocks instead. In either mode, surface every change to the user, never silently modify content, and never claim a file was edited if it wasn't.

**Scratch files** — if the session prep produced a working scratch file (e.g., `session-<N>-plan.md`), delete it as part of this step once the four deliverables are authored and the guide is updated. The deliverables and the guide are the persistent record; the scratch plan is not.

After the guide is updated, present a summary of the diff and stop. Step 7 is opt-in.

### 7. PDF Compilation (on request)

Only run this step when the user explicitly asks for PDFs. The four markdown files from Step 5 are the source of truth; the PDF is rendered **from** them. Never write narrative content into the PDF build that doesn't exist in the markdown — if something needs to change, change the markdown and rebuild.

For on-screen reading, the Markdown renders directly on GitHub (repo or wiki) and in any Markdown previewer — no plugin or build step required. For a print-ready PDF, use the scripted path:

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
  - `image` (`![alt](url)`) → load the bytes into a `BytesIO` (the local jpg named by the manifest `file` key when present, else the URL via `urllib`) and emit an `Image()` sized to fill an 8.5"×11" page (max 7.2"×9.8") while preserving the captured aspect ratio (see `images.json` below). No PIL/Pillow. **Every image renders at full-page size** — portraits, monster art, location scenes, and tactical maps alike. There is no inline / thumbnail variant. When the immediately preceding flowable is a section heading (optionally with one short intro paragraph), the renderer binds them with the image in a `KeepTogether` and shrinks the image to max 7.2"×8.5" so the heading + image pair fits one page. Otherwise the image flows naturally — ReportLab page-breaks before it if it doesn't fit in the remaining space, but a short landscape image will render below trailing text on the same page rather than forcing a near-empty page.
  - `block_code` (fenced) → preformatted Paragraph in a monospace style
  - `block_quote` → indented body Paragraph
- **Checkbox glyphs.** Whenever a paragraph or table cell contains `☐`, the renderer replaces each glyph with a small empty bordered cell. Times-Roman does not carry `☐` and falls back to a filled square. Do not register a substitute font; replace at render time so the boxes are crisp and consistently sized.
- **Image sizing.** Every image renders **full-page on an 8.5"×11" sheet** — sized to fill the printable area while preserving aspect ratio. Max 7.2"×9.8" for an unbound image; max 7.2"×8.5" when bound to a heading via `KeepTogether` (so the heading + image fit one page). Step 4 captures `{description, url, aspect_ratio, file}` for each image; persist that list as `images/images.json` in the session folder so the renderer can letterbox correctly without re-querying Gemini. Lookup is by URL; the renderer reads the local `file` when present (durable, expiry-proof) and only fetches the URL as a fallback. If a URL isn't found in the manifest, fall back to a 4:3 default and warn. Generate every image at high enough resolution to print at full size.
- **Page-break placement.** The renderer aims to keep the page filled. Concretely: each section heading immediately followed by an image is bound to that image (`KeepTogether`) so the heading isn't orphaned on an otherwise-empty page; an image not bound to a heading flows naturally — ReportLab page-breaks before it if it doesn't fit in the remaining space, but a short landscape image will render below trailing text rather than force a near-empty page. Adjacent page breaks are coalesced (no blank pages), and body paragraphs use `allowWidows=0` / `allowOrphans=0` so a paragraph can't leave one stray line at the top of an otherwise-empty page. In the combat-tracker file, each encounter (`## Encounter N`) still gets its own page boundary so the tracker sheet stays organized; in the adventure and player-handout files, H2 sections flow naturally so two short entries (e.g., two landscape-image handouts) can share a page.
- **Output:** single PDF at `sessions/session <N>/<adventure-slug>.pdf` (the slug is derived from `<slug>-1-adventure.md`).
- **Run:** from the repo root, `.venv/bin/python scripts/build_pdf.py [<session-number-or-folder>]`. With no argument it builds the latest session; pass `3` or `"sessions/session 3"` to target a specific one. Optional `--title` and `--out` flags override the auto-detected title and output path. Tell the user the PDF path on completion; the user opens it themselves in their browser or Finder.
- **Dependencies:** `mistune` and `reportlab`, installed into a project venv at `.venv/`. If the venv is missing, create it once with `python3 -m venv .venv && .venv/bin/python -m pip install mistune reportlab`. Do not install into the system Python (Homebrew Python is PEP 668 externally-managed).

## Text Standards

**Adventures** include: hook, overview, locations, encounters, NPCs, and treasure.

**Encounters** include: setup, environment, tactics, read-aloud/boxed text, and scaling notes (Easy–Deadly).

**NPCs & PCs** include: personality (traits, ideals, bonds, flaws) and a full 5e stat block (AC, HP, Speed, Ability Scores with modifiers, Saves, Skills, Senses, Languages, CR, Actions, Reactions, Legendary Actions where appropriate).

**Rules**: Use official 5e rules. Mark any homebrew with ⚗️.

## Image Generation Specs

All images come from `generate_image` (the Gemini image MCP tool). Write rich, specific prompts (>15 words) that name the subject, mood, color palette, and style. Always work with the returned URL, never the base64 payload.

- **Title page illustration**: `aspect_ratio="3:4"` — a portrait-orientation establishing shot of the adventure's primary setting (dungeon entrance, city skyline, wilderness expanse, etc.). Generated at full-page resolution so it fills one 8.5"×11" page cleanly. This is the **only image placed in File 1**; the same URL is reused in File 3 under the matching location section (not duplicated in `images.json`). Generate this first, before any other images.
- **Tactical / encounter maps**: Top-down, print-optimized (minimal background clutter, high contrast). Include a scale indicator, N-arrow, and room/area labels. Use `aspect_ratio="3:4"` (portrait) for all standard encounter maps — portrait orientation fills the printable area cleanly. **Always generate at full-page resolution** — the map always renders **full-page on its own page**, placed at the **end** of the encounter's combat-tracker section after the stat-block cards. A map is **required for every combat encounter** — generate it in Step 4 before authoring File 2. Tactical maps belong to **File 2 only** (the combat tracker). Never embed them in File 1 (adventure narrative) or File 3 (player handouts) — players should not see the encounter layout.
- **Portraits**: `aspect_ratio="3:4"`, painterly fantasy style, neutral background. Must match the text description exactly — armor, species, distinguishing features, attitude. Generated at full-page resolution — every portrait renders at full-page size in the handout appendix.
- **Location art**: `aspect_ratio="16:9"` for scene/landscape illustrations. Generated at full-page resolution — every location scene renders at full-page width; following content flows into the space below.

Never use any built-in vector drawing tool or any Python-drawn graphics for adventure art. Maps, portraits, and scene art come from Gemini only.

## PDF Formatting

- Lead with the title-page summary block: **Title, Tier, Party Level, Duration, Setting, Hook From** — the same fields as the File 1 title-page table.
- Use clear headers and styled body text via ReportLab Platypus paragraph styles.
- Images flow through from the markdown only — the renderer does not insert images that aren't already in the source files. File 1 carries exactly one image: the title page illustration, which renders full-page immediately after the title heading and summary table, followed by a `---` page break before the narrative begins. Every portrait, monster art, and remaining scene illustration renders inside the handout appendix (File 3), each under its own subheading. Tactical maps render from File 2 **only**, and always **last in their encounter section** — after the tracker sheet and all stat-block cards — on their **own full page**, preceded by a hard page break (`---`). NPC and monster portraits **never** appear in File 2; stat-block cards in the combat tracker are text-only.
- **Every image renders full-page** (see **Invariants** for the sizing rule). The renderer page-breaks before and after each `![alt](url)` and sizes the image to fill the printable area while preserving its aspect ratio.
- Images load at PDF build time from the git-tracked local jpg (via the `images.json` `file` key), falling back to the Gemini URL when no local copy is present.
- Final PDF output goes to `sessions/session <N>/<adventure-slug>.pdf`. The user opens it in their browser or Finder; do not attempt to invoke a presentation tool.

### Session folder layout

Each session lives in `sessions/session <N>/` with this file layout:

**Markdown deliverables (always produced — Step 5):**

- `<adventure-slug>-1-adventure.md` — main adventure body.
- `<adventure-slug>-2-combat-tracker.md` — per-encounter trackers and stat-block cards.
- `<adventure-slug>-3-player-handouts.md` — labeled images, one per section.
- `<adventure-slug>-4-dm-quick-ref.md` — DM quick-reference cheat sheet.

**Image assets (always written when Step 4 runs):**

- `images/images.json` — list of `{description, url, aspect_ratio, file}` captured during image generation. The renderer uses `aspect_ratio` to size each `Image()` and `file` to read the local copy. Always present so the PDF can be built later without re-querying Gemini.
- `images/<description-slug>.jpg` — one jpg per generated image, named from the description slug and recorded as the `file` key in `images.json`. Tracked in git and read directly by the renderer, so the PDF still builds after the Gemini URL expires.

**ReportLab PDF artifact (only when the user asks for a scripted PDF — Step 7):**

- `<adventure-slug>.pdf` — the build output. Produced by `scripts/build_pdf.py` from the markdown files plus `images/images.json`.

The build scripts themselves live at the repo root, not per-session: `scripts/build_pdf.py` (CLI entry point) and `scripts/md_to_pdf.py` (markdown→Platypus renderer). Do not copy them into the session folder. The old per-session `build_pdf_content.py`, `combat_tracker.py`, `combat_stat_blocks.py`, and `combat_render.py` modules are no longer used either. All adventure, encounter, stat-block, and quick-reference content lives in the four markdown files; the renderer parses them.

## Combat Tracker

Every adventure must include a **DM combat tracker** — as the dedicated `<slug>-2-combat-tracker.md` file (always) and, when a ReportLab PDF is built, as a section between the main body and the player handout appendix. The tracker is a printable, fillable reference the DM uses at the table — it is not a replacement for the encounter prose in the main body.

### Per-encounter contents

Each combat encounter is rendered in this **strict six-part order**. Do not vary the order, do not interleave sections, and do not duplicate parts in other files.

**1. Combat Title** — a level-2 heading: `## Encounter N — <name>`.

**2. Subtitle** — an italic line immediately under the heading naming the scene reference and difficulty (XP total + threshold), e.g., `*Scene 3 · Hard (1,200 XP / Hard threshold 1,100)*`.

**3. Encounter Summary table** — a small key/value markdown table covering **Location**, **Light**, **Terrain**, and any other at-a-glance flags the DM needs at fight start (cover, hazards, reinforcement triggers). Two columns: label / value.

**4. Initiative Table & tracker sheet** — the working surface for the fight. Contains:
- A round strip line: `**Round:** ☐ 1 · ☐ 2 · ☐ 3 · …` through 10.
- The **Initiative & Damage** markdown table with pre-filled NPC rows (pre-rolled initiative averaged from DEX, AC, HP shown as `<total>: ☐☐☐☐☐ ☐☐☐☐☐ …` at 5 HP per box, ceiling-rounded, plus a notes column) interleaved with blank rows so the DM can write each PC in at the right initiative count after dice are rolled. Blank-row format and counts follow the *Initiative table layout* rules below.
- A conditions reference strip (5e abbreviations: Bln · Chr · Deaf · Frt · Grp · Inc · Inv · Prl · Pet · Pzn · Prn · Rst · Stn · Uns · Conc).
- `### Triggers & Countdowns` — bulleted, time-sensitive escalation/reinforcement conditions.
- `### Tactics Summary` — one line per non-PC combatant.
- `### Loot / Aftermath` — short bulleted note.

**5. Stat-block cards** — one level-3 section per **unique non-PC combatant** in the encounter, with full round-by-round actions. Each card contains:
- Title + type/alignment line + CR (XP). **No portrait. Stat-block cards are text-only.** Portraits live in File 3 (player handouts) and never appear in File 2.
- AC / HP / Speed; ability scores; saves, skills, senses, languages.
- Traits — write innate spellcasting inline as `1× spell · 1× spell · 1× spell`.
- Spellcasting block with **slot tick boxes per spell level** (1st/2nd/3rd…), DC, attack modifier.
- Actions, Reactions, Legendary Actions where applicable.
- **Round-by-round tactics paragraph** — what the creature does on round 1, round 2, round 3+, plus bonus-action priorities and reaction triggers.
- On-defeat loot.

If a creature type appears in multiple encounters, **reprint** its card under each encounter rather than referencing back. The DM should not need to flip pages mid-fight.

**6. Tactical map — full-page, on its own page, at the end of the encounter section.** A `---` thematic break (rendered as a hard page break) precedes the map so it lands alone on a fresh page. The map is then a single line: `![Tactical Map — <encounter name>](<url>)`. The alt text starts with `Tactical Map` so the page is self-labeling. The image renders at full-page size on an 8.5"×11" sheet. Use `aspect_ratio="3:4"` (portrait) for all standard encounter maps. **Tactical maps live in File 2 only — never in File 1 or File 3 — and always as part 6 of an encounter's combat-tracker section, never anywhere else in File 2 either** (no map at the top of an encounter, no map between stat-block cards). Required for every combat encounter — do not author a combat encounter entry without one.

### Markdown form

In `<slug>-2-combat-tracker.md`, render each encounter in the strict order from **Per-encounter contents** above:

1. `## Encounter N — <name>`
2. Italic subtitle: `*Scene <ref> · <difficulty>*`
3. Encounter Summary key/value table (Location / Light / Terrain / …)
4. `**Round:** ☐ 1 · ☐ 2 · …` strip, then the **Initiative & Damage** table (blank-row layout per the rules below), then `### Triggers & Countdowns`, `### Tactics Summary`, and `### Loot / Aftermath` sections.
5. Stat-block cards as level-3 sections (`### <Creature Name>`), one per unique non-PC combatant, reprinted in full when a creature recurs across encounters. **No images inside or adjacent to a stat-block card.**
6. A `---` thematic break, then the tactical map on its own line: `![Tactical Map — <encounter name>](<url>)`. The map is the last content in the encounter section; the next encounter (if any) begins with its own `## Encounter N — <name>` heading on the page after the map.

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
- A level-3 heading naming a creature, followed by a key/value block (`AC`, `HP`, `Speed`, ability scores, traits, actions), becomes a **stat-block card** with parchment background and a thin accent border. **Stat-block cards never embed images — no portraits, no monster art, no icons. Portraits live exclusively in File 3 (the handout appendix).**
- **Every `![alt](url)` image renders full-page**, including tactical maps. A tactical map (alt text begins `Tactical Map`) is always the **last flowable in its encounter section**, preceded by a `---` thematic break that the renderer treats as a hard page break — so the map lands alone on a fresh page, after the tracker sheet and all stat-block cards. The map is not bound to its encounter heading and is not co-located with the tracker sheet. No caption is rendered (the alt text on the page is sufficient).
- A line of `☐` glyphs inside a Spellcasting block (e.g., `1st: ☐ ☐ ☐`) becomes a row of spell-slot tick boxes, one per slot.

These rules are **single-pass and pattern-based** — the renderer recognizes shapes in the parsed markdown rather than consulting a separate data structure. If the markdown matches the patterns documented under **Markdown form**, the PDF inherits the right styling automatically.

### PDF rendering rules

- **Replace every `☐` glyph with a rendered bordered cell.** Times-Roman does not carry the ballot-box glyph and falls back to a filled square. The renderer's checkbox helper substitutes empty-bordered cells of a fixed point size. (The markdown file keeps `☐` because GitHub renders it correctly — this rule is PDF-only.)
- **Pre-roll NPC initiative** so it is printed in the markdown, and the PDF inherits it. PCs roll live and write into the blank rows. Use the average of `1d20 + DEX_mod` rounded to the nearest integer.
- **HP tick boxes** use 5 HP per box, ceiling-rounded. Print the total HP next to the boxes (e.g., `HP 78`) so the DM can confirm.
- **Spell-slot tick boxes** match the level's slot count exactly. Cantrips have no boxes.
- Stat-block cards use a parchment background and a thin accent border to distinguish them visually from narrative content.
- Initiative tables alternate row shading lightly to keep rows scannable.
- Single-encounter trackers should fit on one page when feasible. Boss-tier encounters with 5+ combatants and multiple triggers may flow to a second page; do not compress to fit.
- **Every image renders at full-page size** (sizing rule in **Invariants**). Portrait images (3:4) fill the page; landscape images (16:9, 4:3) preserve aspect ratio and let surrounding content flow into the remaining vertical space. Heading + image pairs are bound together so headings aren't orphaned. Adjacent page breaks are coalesced, and body paragraphs use `allowWidows=0` / `allowOrphans=0` so a paragraph can't leave one stray line alone at the top of an otherwise-empty page.

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
- **Debrief payments** — table of `Item | Condition | Payer | Amount`. If the adventure crosses a milestone or XP advance, list it here as *earned — apply between sessions* (never staged as a mid-session level-up; see Invariants).
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