---
title: Obsidian Setup
type: setup
tags:
  - setup
  - obsidian
---

# Obsidian Setup

Open this folder as a vault (**Obsidian → Open folder as vault → select `fr-kids-campaign/`**), then install the plugins below from **Settings → Community plugins → Browse**. Their IDs are already listed in `.obsidian/community-plugins.json`, so once you click *Install* and *Enable* for each, the vault picks them up automatically.

You'll need to **turn off Restricted Mode** the first time (Settings → Community plugins → Turn on community plugins).

## Formatting

| Plugin | ID | What it does |
|---|---|---|
| **Fantasy Statblocks** | `fantasy-statblocks` | Renders proper 5e-style monster/NPC stat blocks from a YAML code block. Drop `\`\`\`statblock` into a note and you get a Wizards-style boxed stat block. |
| **Admonition** | `obsidian-admonition` | Callout boxes for *DM Notes*, *Read-Aloud*, *Secrets*, *Rules*. Provides a sidebar to define custom callout types and icons. |
| **Dice Roller** | `obsidian-dice-roller` | Inline clickable dice — `` `dice: 2d6+3` `` or `` `dice: 1d20` `` becomes a roll button you can use at the table. |
| **Initiative Tracker** | `initiative-tracker` | Pulls creatures from Fantasy Statblocks and runs combat, HP, conditions. Pairs with Dice Roller. |
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

### Stat block (Fantasy Statblocks)

````markdown
```statblock
name: Drow Scout
size: medium
type: humanoid (elf)
ac: 14
hp: 13 (3d8)
speed: 30 ft.
stats: [10, 14, 10, 11, 13, 11]
saves:
  - dexterity: 4
traits:
  - name: Fey Ancestry
    desc: Advantage on saves vs. charm; magic can't put it to sleep.
actions:
  - name: Shortsword
    desc: "*Melee Weapon Attack:* +4 to hit, reach 5 ft. +1d6+2 piercing."
```
````

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

1. Draft the session note in Markdown (statblocks, read-aloud callouts, dice).
2. Preview in Obsidian's Reading View — confirm formatting and that no statblock/callout straddles a page boundary.
3. Export with **Better Export PDF** (single note) or **Pandoc** (chained notes, e.g. session + relevant NPCs).
4. The print snippet handles the parchment/serif treatment automatically.
