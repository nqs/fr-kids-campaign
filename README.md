# Forgotten Realms — Kids Campaign

The DM's knowledge base for an ongoing D&D 5e campaign set in **Shadowdale**, the Dalelands. This wiki holds the campaign guide, per-session deliverables, and the operating docs that drive content generation.

## Campaign Guide

- [world](campaign/world.md) — setting overview, cosmology, timeline, tone
- [geography](campaign/geography.md) — regions, cities, travel distances, climate
- [factions](campaign/factions.md) — organizations, their goals, their conflicts
- [roster](campaign/roster.md) — NPCs and relationships
- [party](campaign/party.md) — current PCs, levels, classes, backstories, goals
- [session-log](campaign/session-log.md) — what's happened so far, loose ends, foreshadowing

## Sessions

- [Session 001 — The Missing Scout](sessions/session%201/the-missing-scout.pdf)
- [Session 002 — The Second Cleft](sessions/session%202/the-second-cleft-1-adventure.md)
- [Session 003 — The Half-Mask Shrine](sessions/session%203/the-half-mask-shrine-1-adventure.md)
- [Session 004 — The Greengrass Greengage Affair](sessions/session%204/the-greengrass-greengage-1-adventure.md)
- [Session 005 — The Hawthorn Gate](sessions/session%205/the-hawthorn-gate-1-adventure.md)

## Reference Material

Markdown extracts of the Forgotten Realms sourcebooks live under `references/`:

- `references/campaign-guide/_raw/` — DM-facing setting reference (region overviews, dungeons, NPC stat blocks)
- `references/players-guide/_raw/` — player-facing setting reference (cosmology, cities, factions, deities)

Each guide has a single `full.md`, per-page files under `pages/page-NNNN.md`, and extracted figures under `images/`. Grep these for a city/faction/NPC name to pull canon. (The original PDFs are no longer carried in the repo.)

## DM Operating Doc

- [Campaign Keeper instructions](AGENTS.md) — source hierarchy, canon-first rules, generator handoff
- [Adventure Generator workflow](dnd-adventure-generator.md) — scope → outline → images → markdown → guide → PDF

---

# GitHub Wiki Setup

This content is authored as **GitHub-flavoured Markdown** so it renders cleanly both when browsing the repo and when published as a GitHub Wiki. There are no plugins to install and no app to configure.

**You only ever edit this repo.** The repo's GitHub Wiki is generated automatically from these files by the `Sync Wiki` GitHub Action (`.github/workflows/sync-wiki.yml`): on every push to `main` it runs `scripts/build_wiki.py` to stage a wiki-ready tree (extensionless page links, `session N` → `session-N`, references/PDFs linked back to the repo) and pushes it into the repo's `*.wiki.git`. No second repo to maintain by hand.

> [!IMPORTANT]
> **One-time setup:** the wiki repo must exist before the Action can push to it. Enable **Settings → Features → Wikis**, then open the **Wiki** tab and click **Create the first page** once (any content). After that the sync runs on its own. You can also trigger it manually from the **Actions → Sync Wiki → Run workflow** button.

## Layout

```
fr-kids-campaign/
├── README.md                     # this file — GitHub repo landing page
├── Home.md                       # wiki landing page + index (same content)
├── _Sidebar.md                   # wiki navigation sidebar
├── AGENTS.md                     # Campaign Keeper agent instructions
├── dnd-adventure-generator.md    # Generation workflow (scope → outline → images → markdown → guide → PDF)
├── campaign/                     # campaign-guide canon
│   ├── world.md                  # setting overview
│   ├── geography.md              # regions, cities, travel
│   ├── factions.md               # organizations and their conflicts
│   ├── roster.md                 # NPCs and relationships
│   ├── party.md                  # current PCs
│   └── session-log.md            # campaign-wide session index + loose ends
├── sessions/                     # per-session deliverables
│   └── session <N>/              # adventure / combat-tracker / handouts / quick-ref / images / pdf
└── references/                   # markdown extracts of the FR sourcebooks (DM and player guides)
```

## Linking between pages

Pages link to one another with **standard relative Markdown links** — e.g. `[roster](campaign/roster.md)` — rather than Obsidian `[[wikilinks]]`. Relative links resolve correctly in the repo file browser, in pull-request diffs, and in the rendered GitHub Wiki. Spaces in session-folder paths are URL-encoded as `%20`.

> [!NOTE]
> If you publish these pages to the repo's actual GitHub Wiki (the separate `*.wiki.git`), GitHub also supports `[[Page Title]]` wikilink syntax there. The relative-link form used here was chosen because it works everywhere, including normal repo browsing.

## Callouts

Obsidian/Admonition callouts have been converted to **GitHub alerts** with a bold label that preserves the original callout type:

| Original Obsidian type | GitHub alert | Bold label |
|---|---|---|
| `[!dm]` | `[!IMPORTANT]` | **DM:** |
| `[!hook]` | `[!TIP]` | **Hook:** |
| `[!flag]` | `[!WARNING]` | **Flag:** |
| `[!cite]` | `[!NOTE]` | **Source:** |
| `[!quote]` / `[!read-aloud]` | `[!NOTE]` | **Read-aloud:** |
| `[!lore]` | `[!NOTE]` | **Lore:** |
| `[!note]` | `[!NOTE]` | **Note:** |

Example:

```markdown
> [!IMPORTANT]
> **DM:** Lady Ulphor will not say this aloud, but she suspects the Underdark is open.
```

GitHub renders the five alert keywords (`NOTE`, `TIP`, `IMPORTANT`, `WARNING`, `CAUTION`) with a coloured icon and rule.

## Stat blocks

Stat blocks are authored as plain Markdown tables and bolded prose inside each session's combat-tracker file — no Fantasy Statblocks / Initiative Tracker dependency. The ReportLab PDF pipeline (`scripts/build_pdf.py`) reads this Markdown directly.

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

## Printing & Export

PDFs are built from the Markdown with the repo's ReportLab script:

```
.venv/bin/python scripts/build_pdf.py [<session-number-or-folder>]
```

With no argument it builds the latest session; pass `3` or `"sessions/session 3"` to target a specific one. Final output lands at `sessions/session <N>/<adventure-slug>.pdf`. See `dnd-adventure-generator.md` for the full PDF specification.
