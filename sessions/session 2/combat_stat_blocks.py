"""Stat-block data for the combat tracker cards.

Each entry renders as a half-page card: header strip, defenses line,
abilities, traits, spells (with slot tick boxes), actions, tactics.
"""

STAT_BLOCKS = {
    "drider": {
        "portrait": "drider",
        "title": "Wounded Drider (Lolthite enforcer)",
        "type_line": "Large monstrosity, chaotic evil",
        "cr": "6", "xp": "2,300",
        "ac": "19 (natural armor)", "hp": "75 (10d10+20)",
        "speed": "30 ft., climb 30 ft.",
        "abilities": "STR 16  DEX 16  CON 18  INT 13  WIS 14  CHA 12",
        "saves_skills": ("Skills Perception +5, Stealth +9 · Senses darkvision 120 ft., "
                         "passive Perception 15 · Languages Elvish, Undercommon"),
        "traits": [
            "Fey Ancestry — adv. on saves vs. charmed; can't be put to sleep magically.",
            "Spider Climb — climb difficult surfaces incl. ceilings without check.",
            "Sunlight Sensitivity — disadv. on attack rolls and Perception (sight) in sunlight.",
            "Web Walker — ignore movement restrictions from webbing.",
            "Innate Spellcasting (1/day each): dancing lights, darkness, faerie fire.",
        ],
        "actions": [
            "Multiattack — Longsword + Bite, OR Longbow ×2.",
            "Bite — +6 to hit, 1d4+3 piercing + 4d8 poison (DC 14 CON half).",
            "Longsword — +6 to hit, 1d8+3 (1d10+3 two-handed) slashing.",
            "Longbow — +6 to hit, 150/600 ft., 1d8+3 piercing + 2d8 poison (DC 14 CON half).",
            "Web (Recharge 5-6) — 30/60 ft., DC 13 DEX or restrained; AC 10, 5 HP, vuln. fire/slashing.",
        ],
        "tactics": ("R1 Web on heaviest melee. Close, multiattack. Below ¼ HP: retreat down chimney shaft. "
                    "Will not surrender; will not negotiate."),
        "loot": "Obsidian dagger (50 gp curio) · 2× Lolthite signal stones",
    },
    "giant_spider": {
        "portrait": None,
        "title": "Giant Spider",
        "type_line": "Large beast, unaligned",
        "cr": "1", "xp": "200",
        "ac": "14 (natural armor)", "hp": "26 (4d10+4)",
        "speed": "30 ft., climb 30 ft.",
        "abilities": "STR 14  DEX 16  CON 12  INT 2  WIS 11  CHA 4",
        "saves_skills": ("Skills Stealth +7 · Senses blindsight 10 ft., darkvision 60 ft., "
                         "passive Perception 10 · MM p.328"),
        "traits": [
            "Spider Climb — including ceilings.",
            "Web Sense — knows location of anything in contact with the same web.",
            "Web Walker — ignores movement restrictions from webbing.",
        ],
        "actions": [
            "Bite — +5 to hit, reach 5 ft., 1d8+3 piercing + 2d8 poison (DC 11 CON half; "
            "if reduced to 0 HP, stable but poisoned and paralyzed for 1 hr).",
            "Web (Recharge 5-6) — 30/60 ft. ranged, DC 11 DEX or restrained; AC 10, 5 HP, vuln. fire/slash.",
        ],
        "tactics": "Drops on or webs the closest soft target. Pursues until killed.",
        "loot": "—",
    },
    "drow_scout": {
        "portrait": None,
        "title": "Drow Scout",
        "type_line": "Medium humanoid (elf), neutral evil",
        "cr": "1/2", "xp": "100",
        "ac": "15 (studded leather)", "hp": "13 (3d8)",
        "speed": "30 ft.",
        "abilities": "STR 10  DEX 14  CON 10  INT 11  WIS 13  CHA 12",
        "saves_skills": ("Skills Perception +5, Stealth +6, Survival +5 · "
                         "Senses darkvision 120 ft., passive Perception 15 · "
                         "Languages Elvish, Undercommon"),
        "traits": [
            "Fey Ancestry — adv. on saves vs. charmed; immune to magical sleep.",
            "Sunlight Sensitivity — disadv. on attack & Perception (sight) in sunlight.",
            "Innate Spellcasting (1/day each): dancing lights, darkness, faerie fire.",
        ],
        "actions": [
            "Multiattack — 2× shortsword OR 2× hand crossbow.",
            "Shortsword — +4 to hit, 1d6+2 piercing.",
            "Hand Crossbow — +4 to hit, 30/120 ft., 1d6+2 piercing + drow poison "
            "(DC 13 CON or unconscious 1 hr; ends if damaged).",
        ],
        "tactics": "Crossbow from cover. Drops shortsword for stealth retreat if outmatched.",
        "loot": "Hand crossbow · 10 bolts · Drow poison ×1 · 5 gp",
    },
    "drow_reinforcement": {
        "portrait": None,
        "title": "Vhaeraunian Drow (reinforcement)",
        "type_line": "Medium humanoid (elf), neutral evil",
        "cr": "1/4", "xp": "50",
        "ac": "15 (chain shirt)", "hp": "13 (3d8)",
        "speed": "30 ft.",
        "abilities": "STR 10  DEX 14  CON 10  INT 11  WIS 11  CHA 12",
        "saves_skills": ("Skills Perception +2, Stealth +4 · Senses darkvision 120 ft., "
                         "passive Perception 12 · Standard Drow, MM p.128"),
        "traits": [
            "Fey Ancestry, Sunlight Sensitivity, Innate Spellcasting (1/day each: "
            "dancing lights, darkness, faerie fire).",
        ],
        "actions": [
            "Shortsword — +4 to hit, 1d6+2 piercing.",
            "Hand Crossbow — +4 to hit, 30/120 ft., 1d6+2 + drow poison "
            "(DC 13 CON or unconscious 1 hr).",
        ],
        "tactics": "Step through the portal. Form a line in front of Khelziir. Fight to the death.",
        "loot": "Standard Drow loadout (deconstruct ×4)",
    },
    "khelziir": {
        "portrait": "khelziir",
        "title": "Khelziir Aun'velve — Drow Priest of Vhaeraun",
        "type_line": "Medium humanoid (drow), neutral evil",
        "cr": "6", "xp": "2,300",
        "ac": "16 (chain shirt + shield of faith)", "hp": "78 (12d8+24)",
        "speed": "30 ft.",
        "abilities": "STR 11  DEX 14  CON 14  INT 13  WIS 17  CHA 14",
        "saves_skills": ("Saves WIS +6, CHA +5 · Skills Perception +6, Religion +4, Stealth +5 · "
                         "Senses darkvision 120 ft., passive Perception 16 · "
                         "Languages Common, Elvish, Undercommon"),
        "traits": [
            "Fey Ancestry, Sunlight Sensitivity.",
            "Innate Spellcasting (1/day each — strike when used): 1× faerie fire · 1× darkness · 1× levitate.",
        ],
        "spells": {
            "header": "Spellcasting (cleric, save DC 14, +6 to hit)",
            "lines": [
                ("Cantrips", "guidance, sacred flame, thaumaturgy", 0),
                ("1st", "bane, command, shield of faith", 4),
                ("2nd", "silence, spiritual weapon", 3),
                ("3rd", "dispel magic, spirit guardians", 3),
                ("4th", "banishment", 1),
            ],
        },
        "actions": [
            "Multiattack — 2× shortsword.",
            "Shortsword — +5 to hit, 1d6+2 piercing + 1d6 poison.",
            "Hand Crossbow — +5 to hit, 30/120 ft., 1d6+2 + drow poison (DC 13 CON or unconscious 1 hr).",
        ],
        "tactics": ("R1 spirit guardians + BA shield of faith. R2 silence on loudest caster. "
                    "R3 spiritual weapon, continue ritual. R4+ portal opens. Will not leave altar."),
        "loot": "Silver half-mask (200 gp) · Spell scroll of Silence · 2× Greater Healing potions",
    },
    "zeldrazz": {
        "portrait": "zeldrazz",
        "title": "Zeldrazz T'orrl — Drow Elite Warrior (reskinned)",
        "type_line": "Medium humanoid (drow), neutral evil",
        "cr": "5", "xp": "1,800",
        "ac": "18 (chain shirt + shield)", "hp": "71 (13d8+13)",
        "speed": "30 ft.",
        "abilities": "STR 14  DEX 18  CON 13  INT 11  WIS 13  CHA 12",
        "saves_skills": ("Saves DEX +7, CON +4, WIS +4 · Skills Perception +4, Stealth +7 · "
                         "Senses darkvision 120 ft., passive Perception 14 · MM p.128"),
        "traits": [
            "Fey Ancestry, Sunlight Sensitivity.",
            "Innate Spellcasting (1/day each — strike when used): 1× dancing lights · 1× darkness · 1× faerie fire · 1× levitate.",
        ],
        "actions": [
            "Multiattack — 2× shortsword (one as bonus action — see below).",
            "Shortsword — +7 to hit, 1d6+4 piercing + 3d6 poison (DC 13 CON half) + 2d6 poison "
            "(DC 13 CON or poisoned 1 min, retry each end of turn).",
            "Hand Crossbow — +7 to hit, 30/120 ft., 1d6+4 + drow poison (DC 13 CON or unconscious 1 hr).",
        ],
        "reactions": ["Parry — +3 AC vs. one melee attack he can see, must be wielding a melee weapon."],
        "tactics": ("Opens with poisoned attacks vs. PC who tried to kill him last session "
                    "(carries the grudge openly). Protective of Khelziir — will interpose."),
        "loot": "Plain steel scimitar · 2× drow poison vials · cracked half-mask trophy",
    },
}
