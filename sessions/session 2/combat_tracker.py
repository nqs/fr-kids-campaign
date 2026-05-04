"""Combat tracker pages for The Second Cleft.

Appended to the adventure PDF between the main body and the player-handout
appendix. Each combat gets a tracker sheet (initiative + HP tick boxes +
triggers + aftermath) followed by stat-block cards for its non-PC combatants.
"""
import math
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether,
)

CONDITIONS_REF = ("Bln · Chr · Deaf · Frt · Grp · Inc · Inv · Prl · Pet · "
                  "Pzn · Prn · Rst · Stn · Uns · Conc")

ENCOUNTERS = [
    {
        "id": "site_b_chimney",
        "name": "The Hawthorn Chimney — What Came Up After",
        "scene_ref": "Session 002, Scene 2",
        "location": "Site B, Living Wood, Old Skull's southwestern flank",
        "difficulty": "Hard for 5×L5 (~2,700 XP)",
        "light": "Dim under hawthorn canopy; full dark inside chimney shaft",
        "terrain": "Difficult terrain on hawthorn roots; chimney shaft = vertical 20 ft. climb",
        "triggers": [
            "Encounter starts when party investigates chimney shaft (or after ~3 in-fiction min if hesitating)",
            "Both giant spiders climb out on initiative count 10 of round 1",
            "Drider attempts retreat down shaft if reduced below ¼ HP",
        ],
        "combatants": [
            {"name": "Wounded Drider (Lolthite)", "init": 12, "ac": 19, "hp": 75,
             "note": "Starts <½ HP — strike top half of HP boxes",
             "tactics": "R1 Web on heaviest melee (likely Kto). Then close with obsidian dagger + bite. Retreats below ¼ HP."},
            {"name": "Giant Spider A (in shaft)", "init": 10, "ac": 14, "hp": 26,
             "note": "Stays in shaft", "tactics": "Advantage on attacks vs. anyone leaning into the shaft."},
            {"name": "Giant Spider B", "init": 10, "ac": 14, "hp": 26,
             "note": "Drops on caster", "tactics": "Drops onto closest light-armored caster (Yinu or Loric)."},
        ],
        "loot": ("Bone scroll case (intel — Lady Ulphor 50 gp) · Broken ceremonial half-mask "
                 "(Orvyn 80 gp / Ulphor 40 gp) · Drow poison ×2 vials · ~30 gp coin"),
        "stat_cards": ["drider", "giant_spider"],
    },
    {
        "id": "site_c_watcher",
        "name": "The Watcher Above",
        "scene_ref": "Session 002, Scene 3",
        "location": "Cleft mouth, Site C, Old Skull's northern flank",
        "difficulty": "Trivial (skill encounter — stealth check, not protracted combat)",
        "light": "Late afternoon to dusk; deep shadow at the cleft mouth",
        "terrain": "Watcher 60 ft. up a wind-stunted pine; cleft mouth below",
        "triggers": [
            "DC 17 Perception to spot her before she spots the party",
            "If she sees them first, she blows the brass signal horn on her turn",
            "If horn sounds → Khelziir's cell goes to alert; party loses surprise on Combat 3 antechamber",
        ],
        "combatants": [
            {"name": "Drow Scout (Watcher)", "init": 14, "ac": 15, "hp": 13,
             "note": "Elevated cover", "tactics": "Blow horn first. Then hand crossbow from elevation."},
        ],
        "loot": "Brass signal horn (key item) · Hand crossbow + 10 bolts · Drow poison ×1 · ~5 gp",
        "stat_cards": ["drow_scout"],
    },
    {
        "id": "site_c_shrine",
        "name": "The Shrine — Khelziir's Last Ritual",
        "scene_ref": "Session 002, Scene 4",
        "location": "Chamber 3, Site C shrine-camp",
        "difficulty": "Hard for 5×L5 (~4,400 XP). Becomes Deadly if the portal opens.",
        "light": "Black candles, greenish flames — dim throughout. Cookfire in antechamber.",
        "terrain": "Three chambers. Shrine has 8-ft obsidian portal circle at center; basalt altar at back.",
        "triggers": [
            "RITUAL COUNTDOWN: 3 rounds. Stop = kill/KO Khelziir, full-round silence "
            "(he can step out — only delays), or destroy anchor (AC 12, 40 HP, vuln. bludgeoning).",
            "If countdown reaches 0: 4× Vhaeraunian drow step through on the next initiative.",
            "Chamber 2 spider shrieks alarm if silk curtain disturbed (audible throughout dungeon).",
            "If watcher's horn sounded: scouts ready, one sprints to the Shrine to warn Khelziir.",
        ],
        "combatants": [
            {"name": "Khelziir Aun'velve", "init": 13, "ac": 16, "hp": 78,
             "note": "Will not break formation from altar",
             "tactics": "R1 spirit guardians + BA shield of faith. R2 silence on loudest caster. "
                        "R3 spiritual weapon, continue ritual. R4+ portal opens."},
            {"name": "Zeldrazz T'orrl", "init": 14, "ac": 18, "hp": 71,
             "note": "Drow Elite Warrior reskin",
             "tactics": "Opens with poisoned attacks vs. PC who tried to kill him last session. Protective of Khelziir."},
            {"name": "Drow Scout (Antechamber A)", "init": 11, "ac": 15, "hp": 13,
             "note": "Fletching at start", "tactics": "Grabs crossbow, fights from cover. Dies R1 if surprised."},
            {"name": "Drow Scout (Antechamber B)", "init": 11, "ac": 15, "hp": 13,
             "note": "Dozing at start", "tactics": "Sprints to Shrine to warn Khelziir if not dropped R1."},
            {"name": "Giant Spider (pen, optional)", "init": 10, "ac": 14, "hp": 26,
             "note": "Released only if chain cut", "tactics": "Will not distinguish friend from foe."},
            {"name": "Vhaeraunian Drow ×4 (reinforcements)", "init": 10, "ac": 15, "hp": 13,
             "note": "Only if countdown hits 0",
             "tactics": "Step through portal on next initiative. Standard Drow stat block (MM p.128)."},
        ],
        "loot": ("Khelziir's silver half-mask (Orvyn 200 gp) · Spell scroll of Silence · "
                 "Greater Healing potion ×2 · Drow poison ×4 vials · The portal anchor (ending-dependent)"),
        "stat_cards": ["khelziir", "zeldrazz", "drow_scout", "giant_spider", "drow_reinforcement"],
    },
]
