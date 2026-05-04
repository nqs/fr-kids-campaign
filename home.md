# Forgotten Realms — Kids Campaign

The DM's vault for an ongoing D&D 5e campaign set in **Shadowdale**, the Dalelands.

## Campaign Bible

- [[world]] — setting overview, cosmology, timeline, tone
- [[geography]] — regions, cities, travel distances, climate
- [[factions]] — organizations, their goals, their conflicts
- [[roster]] — NPCs and relationships
- [[party]] — current PCs, levels, classes, backstories, goals
- [[session-log]] — what's happened so far, loose ends, foreshadowing

## Sessions

- [[sessions/session 1/the-missing-scout|Session 001 — The Missing Scout]]
- [[sessions/session 2/the-second-cleft-1-adventure|Session 002 — The Second Cleft]]
- [[sessions/session 3/the-half-mask-shrine-1-adventure|Session 003 — The Half-Mask Shrine]]

## Reference Material

PDFs live in `references/`:
- `forgotten-realms-campaign-guide.pdf` — DM-facing setting reference
- `forgotten-realms-players-guide.pdf` — player-facing setting reference

## DM Operating Doc

- [[agents|Campaign Keeper instructions]] — source hierarchy, canon-first rules, generator handoff
- [[dnd-adventure-generator|Adventure Generator workflow]] — scope → outline → images → markdown → bible → PDF

---

# Obsidian Setup

Open this folder as a vault (**Obsidian → Open folder as vault → select `fr-kids-campaign/`**), then install the plugins below from **Settings → Community plugins → Browse**. Their IDs are already listed in `.obsidian/community-plugins.json`, so once you click *Install* and *Enable* for each, the vault picks them up automatically.

You'll need to **turn off Restricted Mode** the first time (Settings → Community plugins → Turn on community plugins).

## Vault layout

```
fr-kids-campaign/
├── home.md                       # this file — vault index + Obsidian setup
├── agents.md                     # Campaign Keeper agent instructions
├── dnd-adventure-generator.md    # Generation workflow (scope → outline → images → markdown → bible → PDF)
├── campaign/                     # campaign-bible canon
│   ├── world.md                  # setting overview
│   ├── geography.md              # regions, cities, travel
│   ├── factions.md               # organizations and their conflicts
│   ├── roster.md                 # NPCs and relationships
│   ├── party.md                  # current PCs
│   └── session-log.md            # campaign-wide session index + loose ends
├── sessions/                     # per-session deliverables (root-level)
│   └── session <N>/              # adventure / combat-tracker / handouts / images.json / pdf
└── references/                   # canonical FR sourcebook PDFs (DM and player guides)
```

Wikilinks like `[[roster]]` resolve regardless of folder, so bullets here work whether the target is at root or under `campaign/`. Path-prefixed wikilinks (e.g. `[[sessions/session 3/...]]`) point at the root-level `sessions/` tree.

## Formatting

Stat blocks in this vault are authored as plain markdown tables and bolded prose inside each session's combat-tracker file. Fantasy Statblocks / Initiative Tracker are intentionally **not** used — the ReportLab PDF pipeline reads markdown directly.

| Plugin | ID | What it does |
|---|---|---|
| **Admonition** | `obsidian-admonition` | Callout boxes for *DM Notes*, *Read-Aloud*, *Secrets*, *Rules*. Provides a sidebar to define custom callout types and icons. |
| **Dice Roller** | `obsidian-dice-roller` | Inline clickable dice — `` `dice: 2d6+3` `` or `` `dice: 1d20` `` becomes a roll button you can use at the table. |
| **Leaflet** | `obsidian-leaflet-plugin` | Interactive maps. Drop a map image into a `\`\`\`leaflet` block and pin locations that link back to notes. |
| **Style Settings** | `obsidian-style-settings` | Exposes UI controls for any theme/snippet that opts in. Useful for tweaking the print snippet without editing CSS. |

## Printing & Export

| Plugin | ID | What it does |
|---|---|---|
| **Better Export PDF** | `better-export-pdf` | Drop-in replacement for Obsidian's built-in PDF export with header/footer templates, page numbers, table of contents, and proper page breaks before H1. Use this for player handouts. |
| **Pandoc Plugin** | `obsidian-pandoc` | Export notes to PDF / DOCX / EPUB / LaTeX via Pandoc. Better for long-form (a full adventure write-up) than Better Export PDF. Requires Pandoc installed locally; on macOS: `brew install pandoc basictex`. |

## Print stylesheet

`.obsidian/snippets/dnd-print.css` is enabled in `appearance.json`. It activates under `@media print` (and inside Better Export PDF), giving printed/exported notes:

- Parchment background (`#f5ecd7`) and dark-brown body text
- Bookman / Palatino serif body, Trajan-style headings in `#58180d` red
- Page break before each `# H1` so each top-level section starts on a new page
- Avoid-break rules on stat blocks, callouts, tables, code blocks
- Themed callouts for `[!dm]` and `[!read-aloud]`
- Hides Obsidian UI chrome that shouldn't print

If you don't like it, disable it in **Settings → Appearance → CSS snippets**.

## Quick reference: useful syntax

### Stat block (markdown table — vault convention)

```markdown
**Drow Scout** · Medium humanoid (elf) · CR 1/2
**AC** 14 · **HP** 13 (3d8) · **Speed** 30 ft.

| STR | DEX | CON | INT | WIS | CHA |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 10 (+0) | 14 (+2) | 10 (+0) | 11 (+0) | 13 (+1) | 11 (+0) |

**Saves** Dex +4 · **Senses** darkvision 120 ft.
**Traits** *Fey Ancestry* — advantage on saves vs. charm; immune to magical sleep.
**Actions** *Shortsword* — Melee, +4 to hit, reach 5 ft., 1d6+2 piercing.
```

See any session's combat tracker (`sessions/session <N>/<slug>-2-combat-tracker.md`) for live examples.

### DM callout (Admonition)

```markdown
> [!dm] DM Note
> Lady Ulphor will not say this aloud, but she suspects the Underdark is open.
```

### Read-aloud callout

```markdown
> [!read-aloud]
> The cleft narrows. Cold air flows up from below, smelling of wet stone and something older.
```

### Inline dice

```markdown
The drow scout strikes for `dice: 1d6+2` piercing damage.
```

## Recommended workflow for adventure printing

1. Draft the session note in Markdown (stat-block tables, read-aloud callouts, dice).
2. Preview in Obsidian's Reading View — confirm formatting and that no stat-block table or callout straddles a page boundary.
3. Export with **Better Export PDF** (single note) or **Pandoc** (chained notes, e.g. session + relevant NPCs).
4. The print snippet handles the parchment/serif treatment automatically.
