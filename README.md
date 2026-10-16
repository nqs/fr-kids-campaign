# Forgotten Realms — Kids Campaign

The DM's knowledge base for an ongoing D&D 5e campaign set in **Shadowdale**, the Dalelands. This repo holds the campaign guide, per-session deliverables, and the operating docs that drive content generation.

## Campaign Guide

- [world](campaign/world.md) — setting overview, cosmology, timeline, tone
- [geography](campaign/geography.md) — regions, cities, travel distances, climate
- [factions](campaign/factions.md) — organizations, their goals, their conflicts
- [roster](campaign/roster.md) — NPCs and relationships
- [party](campaign/party.md) — current PCs, levels, classes, backstories, goals
- [session-log](campaign/session-log.md) — what's happened so far, loose ends, foreshadowing

## Sessions

Each session has a **landing page** — a short summary plus links to the adventure, its images, and its other assets.

- [Session 001 — The Missing Scout](sessions/session%201/the-missing-scout-0-overview.md)
- [Session 002 — The Second Cleft](sessions/session%202/the-second-cleft-0-overview.md)
- [Session 003 — The Half-Mask Shrine](sessions/session%203/the-half-mask-shrine-0-overview.md)
- [Session 004 — The Greengrass Greengage Affair](sessions/session%204/the-greengrass-greengage-0-overview.md)
- [Session 005 — The Hawthorn Gate](sessions/session%205/the-hawthorn-gate-0-overview.md)
- [Session 006 — The Green Lord's Court](sessions/session%206/the-green-lords-court-0-overview.md)
- [Session 007 — The Lighthouse on Dry Land](sessions/session%207/the-lighthouse-on-dry-land-0-overview.md)
- [Session 008 — The Tide Festival](sessions/session%208/the-tide-festival-0-overview.md)

## Reference Material

Markdown extracts of the Forgotten Realms sourcebooks live under `references/`:

- `references/campaign-guide/_raw/` — DM-facing setting reference (region overviews, dungeons, NPC stat blocks)
- `references/players-guide/_raw/` — player-facing setting reference (cosmology, cities, factions, deities)

Each guide has a single `full.md`, per-page files under `pages/page-NNNN.md`, and extracted figures under `images/`. Grep these for a city/faction/NPC name to pull canon. (The original PDFs are no longer carried in the repo.)

## DM Operating Doc

- [Campaign Keeper instructions](AGENTS.md) — source hierarchy, canon-first rules, generator handoff
- [Adventure Generator workflow](dnd-adventure-generator.md) — scope → outline → images → markdown → guide → PDF

---

# Wiki (BookStack)

The campaign wiki is the self-hosted **BookStack** at [wiki.nqs.io](https://wiki.nqs.io), shelf **Forgotten Realms Kids Campaign**. Content is authored here as **GitHub-flavoured Markdown**, so it also renders cleanly when browsing the repo.

**You only ever edit this repo.** The `Sync BookStack` GitHub Action (`.github/workflows/sync-bookstack.yml`) runs `scripts/sync_bookstack.py` on every push to `main` that touches campaign content. It mirrors `campaign/`, `sessions/`, `AGENTS.md`, and `dnd-adventure-generator.md` onto the shelf (books → chapters → pages), updates only what changed, and recycles pages whose source file was deleted. Links to PDFs, images, recordings, and `references/` point back to this repo. Trigger it manually (optionally as a dry run) from **Actions → Sync BookStack → Run workflow**.

> [!IMPORTANT]
> **One-time setup:** a BookStack API token with permission to manage shelves, books, and pages, stored as the repo secret `BOOKSTACK_API_TOKEN` (`<token_id>:<token_secret>`). See the header of `scripts/sync_bookstack.py`.

## Layout

```
fr-kids-campaign/
├── README.md                     # this file — repo landing page + index
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

Pages link to one another with **standard relative Markdown links** — e.g. `[roster](campaign/roster.md)` — rather than Obsidian `[[wikilinks]]`. Relative links resolve correctly in the repo file browser and in pull-request diffs, and `scripts/sync_bookstack.py` rewrites them to BookStack page URLs. Spaces in session-folder paths are URL-encoded as `%20`.

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
