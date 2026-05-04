"""Content flowables for The Second Cleft."""
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import Spacer, PageBreak
from reportlab.lib.units import inch

def build(g):
    p, b, H1, H2, H3, BODY, READ, CAPTION = (
        g["p"], g["b"], g["H1"], g["H2"], g["H3"], g["BODY"], g["READ"], g["CAPTION"])
    captioned, boxed_table, appendix_img = g["captioned"], g["boxed_table"], g["appendix_img"]
    img, IMAGES, TITLE, SUBTITLE, APP_LABEL, APP_KICKER, Paragraph = (
        g["img"], g["IMAGES"], g["TITLE"], g["SUBTITLE"], g["APP_LABEL"], g["APP_KICKER"], g["p"].__self__ if False else None)
    from reportlab.platypus import Paragraph
    f = []
    # ---- COVER / SUMMARY ----
    f += [Spacer(1, 0.4*inch),
          Paragraph("The Second Cleft", TITLE),
          Paragraph("Session 002 — A Shadowdale Adventure", SUBTITLE)]
    f.append(boxed_table([
        ["Title", "The Second Cleft"],
        ["Tier / Level", "Tier 2 — 5 PCs at Level 5 (advance to 6 on completion)"],
        ["Duration", "~3.5–4 hours of play"],
        ["Setting", "Shadowdale → Old Skull's northern flank → the Living Wood fringe"],
        ["Hook From", "Session 001 — The Missing Scout (the Vhaeraunian map fragment)"],
    ], header=False, col_widths=[1.4*inch, 5.0*inch]))
    f += [Spacer(1, 0.2*inch), Paragraph("Adventure Summary", H1),
          p("The Vhaeraunian map fragment the party recovered last session is no longer just intelligence — "
            "it's a deadline. Lady Ulphor confirms her militia have corroborated the markings: the two unscouted "
            "sites are real, and the southern one (Site B, in the Living Wood) has gone dark in the last forty-eight "
            "hours. The party is dispatched to scout Site B for evidence of where the cell went, then proceed to "
            "Site C — the deeper cave on the northern flank — and either neutralize it or bring back enough "
            "information for Lady Ulphor to commit the militia to a coordinated strike."),
          p("Site B turns out to have been purged the night before by a rival drow faction. Site C is a half-finished "
            "Vhaeraunian shrine-camp, run by a priest of Vhaeraun named <b>Khelziir Aun'velve</b>, racing to consecrate "
            "a small surface-side portal anchor. <b>Zeldrazz T'orrl is here</b> — alive, healed, demoted, and furious. "
            "The session ends with the portal anchor either smashed, stolen for study, or — if the party is clever and "
            "lucky — turned into a Harper intelligence asset.")]
    f.append(PageBreak())

    # ---- SCENE 1 ----
    f += [Paragraph("Scene 1 — The Briefing at the Ashaba House", H1),
          Paragraph("Setup", H2),
          p("Morning. Lady Addee Ulphor's working room at the Ashaba House. <b>Brynn Ashford</b> is present and taking "
            "notes; <b>Corwick Helm</b> arrives partway through, leather apron still on. Lady Ulphor has the "
            "Vhaeraunian map fragment unrolled on her desk, weighted with a tin mug and an inkwell."),
          captioned("brynn", max_w=3.2),
          captioned("corwick", max_w=3.2),
          Paragraph("What Lady Ulphor Offers", H2)]
    f += b([
        "<b>250 gp</b> on completion of the scouting mission, with proof",
        "<b>+200 gp bonus</b> if the party can disable or destroy any drow staging site",
        "Sela Wyndmere's herbal kit — 3× healing poultices, 2× antitoxin (already paid for)",
        "The use of two militia at the trailhead as reserve: <b>Aelinor Wains</b> (Corwick's most reliable scout) and, "
        "if the party insists, <b>Rellan Tessar</b> — Corwick prefers Aelinor; Rellan is still Exhaustion 1",
    ])
    f += [Paragraph("New Information Lady Ulphor Shares", H2)]
    f += b([
        "<b>Site B</b> (southern marking, Living Wood) was watched by a militia scout for two days. As of yesterday "
        "morning, smoke from the chimney <i>stopped</i>. Either the cell broke camp or something killed them.",
        "<b>Site C</b> (northern marking, deeper in Old Skull's flank) is showing increased activity. Sela has reported "
        "fey withdrawing from a quarter-mile radius around it.",
        "The map fragment had a sigil in the corner the party didn't recognize. Lady Ulphor has identified it: "
        "a <b>Vhaeraunian priestly mark</b>. A <i>cleric</i> is on the surface. That changes the threat profile.",
    ])
    f += [Paragraph("Side Channel — Brynn Ashford", H2),
          p("Brynn will, at some point during the briefing or after, find a moment to speak privately with one PC "
            "(GM's choice — likely the one with the highest CHA or already known to be politically aware). His ask: "
            "<b>Orvyn Tal asked him this morning whether the militia were planning to follow up on the map.</b> "
            "Brynn lied and said no. He'd like to know what the party finds before the Harpers do."),
          Paragraph("DM Notes — Briefing Tone", H2)]
    f += b([
        "Lady Ulphor is composed but tighter than last session. She touches the Pendant of Ashaba twice while talking.",
        "Corwick volunteers Aelinor over Rellan with no explanation; the truth is he doesn't trust Rellan's nerves yet.",
        "If the party asks about Captain Helm's earlier cover-up, Lady Ulphor says simply: <i>\"Captain Helm and I "
        "are speaking later this week. The matter is closed publicly. Privately it remains open.\"</i>",
    ])
    f.append(PageBreak())

    # ---- SCENE 2 ----
    f += [Paragraph("Scene 2 — The Living Wood Approach (Site B)", H1),
          captioned("site_b_loc"),
          Paragraph("Travel", H2),
          p("Approximately 5 hours from the village to the southern site, on Old Skull's southwestern flank, "
            "through the fey-dense edge of the Living Wood. Aelinor (and Rellan, if he came) holds the trailhead "
            "at a half-collapsed shepherd's bothy ~30 minutes from Site B. Beyond that, the party is on its own.")]
    f += [Paragraph("Skill Challenge — \"The Wood is Watching\"", H2),
          p("<b>4 successes before 3 failures.</b> DCs 13–15. Suggested checks (one per PC per round, no repeats):")]
    f += b([
        "<b>Survival</b> or <b>Nature</b> to find Sela's old foraging trail",
        "<b>Perception</b> or <b>Investigation</b> to spot fey wards on bark — acorn-and-iron warnings to trespassers",
        "<b>Persuasion</b> or <b>Performance</b> to greet a watching dryad respectfully (Nalith and Fiorn shine here)",
        "<b>Arcana</b> to recognize a flickering Feywild seam and route around it",
    ])
    f += b([
        "<b>Per failure:</b> a glamour-trick costs the party an hour, splits the marching order, or imposes one level "
        "of Exhaustion on the failing PC until next short rest.",
        "<b>On full success:</b> they arrive at Site B in late afternoon, with daylight still to work in.",
        "<b>On full failure:</b> they arrive at dusk, having lost their reserve at the bothy (Aelinor will hold but "
        "won't be able to find them again), and the encounter inside Site B happens in dim light.",
    ])
    f += [Paragraph("Arrival at Site B", H2),
          Paragraph("Approaching the Hawthorn Chimney", H3),
          Paragraph("The hawthorn closes overhead in a low arch — pale berries, black thorns. Beneath the boughs, "
            "a fire pit lies cold under a film of ash, three bedrolls splayed around it like petals torn from a "
            "flower. One has a long dark stain along its length. The chimney mouth is a dark wound in the rock, "
            "and from inside, very faintly, comes the sound of something dragging itself upward.", READ),
          captioned("site_b_map"),
          Paragraph("What the Party Finds (DC 13 Investigation)", H2)]
    f += b([
        "A natural rock chimney rising 20 ft. into a granite outcrop, surrounded by hawthorn",
        "Fire pit cold for ~30 hours. Three bedrolls; one slashed open and bloodstained",
        "<b>Drag marks</b> — humanoid, leading <i>into</i> the chimney shaft and <i>down</i>",
        "A <b>bone scroll case</b> with a half-burnt Undercommon order: <i>\"…abandon Site B, reinforce the priest, "
        "the surface anchor must be set by the dark of the moon.\"</i>",
        "A <b>Vhaeraun half-mask</b>, smaller than Zeldrazz's, ceremonial, broken",
        "A <b>spider-silk thread</b> leading down the chimney's interior — too thick to be natural",
    ])
    f += [Paragraph("Encounter — What Came Up After", H1),
          p("As soon as the party investigates the chimney shaft (or after ~3 in-fiction minutes if they hesitate), "
            "the wounded survivor of last night's purge climbs out to silence the witnesses."),
          captioned("drider", max_w=4.0),
          Paragraph("Combatants", H2)]
    f.append(boxed_table([
        ["Combatant", "CR", "XP", "Notes"],
        ["Wounded Drider (Lolthite)", "6", "2,300", "Below half HP at start; will fight to silence party"],
        ["Giant Spider × 2", "1", "200 each", "Climb out of the shaft on initiative count 10 of round 1"],
    ], col_widths=[2.4*inch, 0.5*inch, 0.7*inch, 2.8*inch]))
    f += [Paragraph("Tactics", H2)]
    f += b([
        "The drider opens with <b>Web</b> on the party's heaviest melee (most likely Kto), then closes with the "
        "obsidian dagger and bite. It uses the chimney shaft as a fallback — if reduced below 1/4 HP, it will "
        "attempt to retreat downward.",
        "The two giant spiders flank — one stays in the chimney shaft (advantage on attacks vs. anyone leaning in), "
        "the other drops onto the closest light-armored caster (Yinu or Loric).",
        "<b>Encounter difficulty:</b> Hard for 5×L5 (~2,700 XP). Adjust by adding a third spider for Deadly.",
    ])
    f += [Paragraph("What This Means (DM-facing)", H2),
          p("This is the first hard evidence that the <b>Vhaeraunian and Lolthite drow factions are at war beneath "
            "Shadowdale</b>. The drider is a Lolthite enforcer; the camp she purged was Vhaeraunian. The party can "
            "exploit this rivalry going forward — or get caught between it. The drider, if interrogated rather than "
            "killed (good luck), knows only that her matron was ordered to <i>\"close the surface mouths Vhaeraun "
            "is opening.\"</i> She will not cooperate willingly."),
          Paragraph("Loot from Site B", H2)]
    f += b([
        "<b>Bone scroll case</b> with the half-burnt Vhaeraunian order (intelligence — Lady Ulphor will pay 50 gp)",
        "<b>Broken ceremonial half-mask</b> (Orvyn Tal will pay 80 gp; Lady Ulphor 40 gp)",
        "<b>Drow poison ×2 vials</b> looted from the bedrolls (the spiders disturbed them but didn't take them)",
        "<b>~30 gp</b> in mixed coin and trade goods",
    ])
    f.append(PageBreak())

    # ---- SCENE 3 ----
    f += [Paragraph("Scene 3 — Travel to Site C & The Watcher Above", H1),
          captioned("site_c_loc"),
          Paragraph("The Trek", H2),
          p("Approximately 4 hours overland from Site B to Site C, skirting the granite shoulder of Old Skull. "
            "If Aelinor and Rellan are with the party, they hold position at the shepherd's bothy — they will "
            "not enter the cleft regardless of how the conversation goes. Corwick was clear about that."),
          Paragraph("Encounter — The Watcher", H2),
          p("A single <b>Drow Scout (CR 1/2)</b> is perched in a wind-stunted pine 60 ft. above the cleft mouth, "
            "with a brass signal horn slung at her belt. <b>DC 17 Perception</b> to spot her before she spots the "
            "party. If she sees them first, she <b>blows the horn before being killed</b> — Khelziir's cell goes "
            "to alert status, and the party loses surprise on the antechamber fight in Scene 4."),
          Paragraph("The Cleft Mouth", H2),
          p("A vertical fissure 6 ft. wide, 10 ft. tall, breathing cold spider-musk air. Spider silk threads cross "
            "the opening at ankle and chest height — a tripwire warning system Khelziir installed last week. "
            "<b>DC 14 Perception</b> to spot the silk in the dim light at the cleft's lip. Anyone who walks into "
            "it without spotting it triggers a soft chime that echoes down the cleft — Chamber 1 goes to alert."),
          Paragraph("Approach Options", H2)]
    f += b([
        "<b>Frontal stealth</b> — Stealth check (group, DC 13) to enter the cleft without triggering the silk",
        "<b>Cut the wires</b> — Sleight of Hand (DC 12) to cut without ringing the chime",
        "<b>Climb above</b> — the cleft is climbable along a side chimney; DC 15 Athletics, drops party into "
        "Chamber 1 from the ceiling (no silk, surprise round if quiet)",
    ])
    f.append(PageBreak())

    # ---- SCENE 4 — SITE C ----
    f += [Paragraph("Scene 4 — The Shrine-Camp (Site C)", H1),
          p("A three-chamber dungeon carved into a natural cleft beneath Old Skull's northern face. The Vhaeraunians "
            "have been working here for roughly two weeks. Khelziir is in a hurry; the place is functional, not finished."),
          captioned("site_c_map"),
          Paragraph("Chamber 1 — The Antechamber", H2),
          p("A 30 × 30 ft. natural cavern with two bedroll piles, a cold cookfire in the center, and a weapon rack "
            "against the east wall holding three hand crossbows and a sheaf of bolts. <b>2× Drow Scouts (CR 1/4)</b> "
            "are on watch; one is fletching, one is dozing. If the party kept surprise, both can be dropped in the "
            "first round; if not, one will sprint for the Shrine to warn Khelziir."),
          Paragraph("Chamber 2 — The Spider Pen", H2),
          p("A 20 × 40 ft. side chamber separated from Chamber 1 by a curtain of spider-silk. <b>1× Giant Spider "
            "(CR 1)</b> is chained to the wall — Khelziir's pet sentinel. If the silk curtain is disturbed, the "
            "spider <b>shrieks</b> (a Vhaeraunian-trained alarm response), audible throughout the dungeon. "
            "Cutting the chain releases the spider; it will not distinguish friend from foe."),
          Paragraph("Chamber 3 — The Shrine", H2),
          captioned("shrine"),
          p("A 40 × 50 ft. chamber. A black basalt slab altar at the back, draped with a Vhaeraunian half-mask banner. "
            "A <b>partially-consecrated portal anchor</b> sits at the chamber's center: a circle of obsidian shards "
            "8 ft. across, half-inscribed with Undercommon glyphs in luminescent silver ink. Khelziir stands at the "
            "altar mid-ritual; Zeldrazz flanks him. Black candles burn on the altar with greenish flames."),
          Paragraph("The Boss Encounter", H1),
          captioned("khelziir", max_w=4.0),
          Paragraph("Khelziir Aun'velve — Drow Priest of Vhaeraun", H2),
          p("<b>Medium humanoid (drow), neutral evil. CR 6.</b> AC 16 (chain shirt + shield of faith). HP 78 (12d8+24). "
            "Speed 30 ft. STR 11, DEX 14, CON 14, INT 13, WIS 17, CHA 14. Saves WIS +6, CHA +5. Skills Perception +6, "
            "Religion +4, Stealth +5. Senses darkvision 120 ft., passive Perception 16. Languages Common, Elvish, "
            "Undercommon. <b>Innate Spellcasting:</b> faerie fire 1/day, darkness 1/day, levitate 1/day. "
            "<b>Spellcasting (cleric, save DC 14, +6 to hit):</b> cantrips — guidance, sacred flame, thaumaturgy; "
            "1st (4) — bane, command, shield of faith; 2nd (3) — silence, spiritual weapon; 3rd (3) — dispel magic, "
            "spirit guardians; 4th (1) — banishment. <b>Sunlight Sensitivity.</b>"),
          Paragraph("Actions", H3)]
    f += b([
        "<b>Multiattack:</b> Two shortsword attacks.",
        "<b>Shortsword:</b> +5 to hit, reach 5 ft., 1d6+2 piercing plus 1d6 poison.",
        "<b>Hand Crossbow:</b> +5 to hit, range 30/120 ft., 1d6+2 piercing plus drow poison (Save DC 13 CON or "
        "unconscious 1 hour, ends if damaged).",
    ])
    f += [Paragraph("Tactics", H3),
          p("<b>Round 1:</b> casts <i>spirit guardians</i> (shadow-form skull spirits orbit him), then bonus-action "
            "<i>shield of faith</i> on himself. <b>Round 2:</b> <i>silence</i> centered on the loudest caster (likely "
            "Yinu or Loric — shut down the Wizard or the Sorcerer). <b>Round 3:</b> <i>spiritual weapon</i> (a black "
            "blade) and continues the consecration ritual. <b>Round 4+:</b> if the anchor is still intact, it activates "
            "and summons reinforcements (see below). Khelziir will not break formation from the altar — finishing the "
            "ritual matters more than his own survival.")]
    f += [captioned("zeldrazz", max_w=4.0),
          Paragraph("Zeldrazz T'orrl — Returning Antagonist", H2),
          p("<b>Medium humanoid (drow), neutral evil. CR 5.</b> Use the <i>Drow Elite Warrior</i> stat block "
            "(MM p.128). Reskinned with: a plain steel scimitar in place of the drow-made one; a fresh scar across "
            "his left cheek; a chip on his shoulder the size of Old Skull. He has personally targeted whichever "
            "PC dealt the killing-attempt blow last session and will <b>open with poisoned attacks against them</b>."),
          Paragraph("Encounter Math", H2)]
    f.append(boxed_table([
        ["Combatant", "CR", "XP"],
        ["Khelziir Aun'velve (Vhaeraun priest)", "6", "2,300"],
        ["Zeldrazz T'orrl (drow elite warrior)", "5", "1,800"],
        ["Drow Scout × 2 (Antechamber)", "1/4", "100"],
        ["Giant Spider (if released from pen)", "1", "200"],
        ["Total (if all engaged)", "—", "~4,400 (Hard for 5×L5)"],
    ], col_widths=[3.5*inch, 0.7*inch, 1.8*inch]))
    f += [Paragraph("The Ritual Countdown", H2),
          p("<b>3 rounds remaining</b> when the party enters the Shrine. Each round Khelziir is alive, conscious, "
            "and not silenced or stunned, the countdown ticks down by one. If it reaches zero, the portal anchor "
            "<b>activates</b>: a tear opens above the obsidian circle and <b>4× Vhaeraunian drow reinforcements</b> "
            "(use Drow stat block, MM p.128) step through on the next initiative. The encounter escalates to Deadly. "
            "The party can stop the countdown by: killing Khelziir, knocking him unconscious, silencing him for a "
            "full round (he can step out of <i>silence</i>, so this only delays), or destroying the half-finished "
            "anchor itself (<b>AC 12, 40 HP, vulnerable to bludgeoning</b> — but striking it provokes opportunity "
            "attacks from anyone in melee with the striker, and Khelziir treats it as an attack on himself)."),
          Paragraph("The Three Endings", H1),
          p("<b>1) Smash the anchor</b> (loud win) — The portal collapses inward in a thunderclap of cold air. "
            "Khelziir's cell is permanently shut down; Lady Ulphor is delighted; the militia get credit publicly; "
            "the Vhaeraunians know the surface knows. <i>Reputation: +Lady Ulphor, +Corwick. Loose end: a furious "
            "response from below within 2–3 weeks.</i>"),
          p("<b>2) Steal the anchor for study</b> (quiet win) — Requires a successful <b>DC 16 Arcana</b> check by "
            "Yinu or Loric to disrupt the consecration without triggering the portal. The anchor goes back to "
            "Lady Ulphor, who hands it to Orvyn Tal for Harper analysis. <i>Reputation: +Harpers significantly, "
            "+Lady Ulphor privately, neutral publicly.</i>"),
          p("<b>3) Turn it into a feed</b> (clever win) — If a PC succeeds on a <b>DC 18 Religion or Arcana</b> check "
            "after Khelziir falls, they realize the half-finished anchor can be left running as a one-way listening "
            "glyph into the Vhaeraunian command structure. Orvyn Tal will pay handsomely (<b>+500 gp</b>) and offer "
            "Harper recruitment for this. <i>Reputation: +Harpers heavily; the Vhaeraunians don't know they're "
            "being listened to — yet.</i>")]
    f.append(PageBreak())

    # ---- NPCs ----
    f += [Paragraph("NPCs in Play", H1)]
    f.append(boxed_table([
        ["NPC", "Source", "Role This Session"],
        ["Lady Addee Ulphor", "Roster", "Briefing, payment, post-session debrief"],
        ["Brynn Ashford", "Roster", "Side-channel ask about Harper disclosure"],
        ["Corwick Helm", "Roster", "Militia liaison; assigns Aelinor"],
        ["Sela Wyndmere", "Roster", "Provides poultices; fey-edge warning about Site C"],
        ["Orvyn Tal", "Roster", "Surfaces post-session if anchor route 2 or 3 chosen"],
        ["Rellan Tessar", "Session 001", "Wants to come; Corwick says no"],
        ["Aelinor Wains", "NEW (DM addition)", "Militia scout; holds the trailhead — flag for canonization"],
        ["Khelziir Aun'velve", "NEW (DM addition)", "Vhaeraunian priest antagonist — flag for canonization"],
        ["Zeldrazz T'orrl", "Session 001", "Returning antagonist (alive, demoted, furious)"],
    ], col_widths=[1.9*inch, 1.6*inch, 3.0*inch]))

    # ---- TREASURE & REWARDS ----
    f += [Paragraph("Treasure & Rewards", H1)]
    f += b([
        "<b>250 gp</b> scouting payment + <b>200 gp bonus</b> for neutralizing Site C = 450 gp baseline",
        "<b>Khelziir's silver half-mask</b> — Vhaeraunian priestly regalia (Orvyn Tal: 200 gp; Lady Ulphor: 100 gp)",
        "<b>Spell scroll of Silence</b> (from Khelziir's pouch)",
        "<b>Potion of Greater Healing × 2</b> (Vhaeraunian field stock)",
        "<b>Drow poison × 4 vials</b> (looted from Zeldrazz and the scouts)",
        "<b>The portal anchor</b> — 800 gp value to the Harpers if delivered intact (Ending 2); 400 gp to Lady "
        "Ulphor as evidence; 0 gp if smashed (+ public reputation); +500 gp Harper bounty if turned into a feed (Ending 3)",
        "<b>From Site B:</b> bone scroll case (50 gp), broken half-mask (40–80 gp), drow poison ×2, ~30 gp coin",
        "<b>Milestone:</b> Advance party to <b>Level 6</b> at session end",
    ])

    # ---- LOOSE ENDS ----
    f += [Paragraph("Loose Ends This Session Sets Up", H1)]
    f += b([
        "<b>Lolthite vs. Vhaeraunian war beneath Old Skull</b> is now confirmed and exploitable",
        "<b>Khelziir's superiors below</b> will retaliate — Session 3 candidate",
        "<b>Orvyn Tal / Harper recruitment</b> is now actionable depending on ending",
        "<b>Corwick Helm's cover-up</b> still unresolved — Lady Ulphor mentions: <i>\"Captain Helm and I are "
        "speaking later this week.\"</i>",
        "<b>Zeldrazz T'orrl</b> — if he escapes a second time, he becomes a personal nemesis arc",
    ])
    f.append(PageBreak())

    # ---- DM COMBAT TRACKER ----
    from combat_render import build_combat_tracker
    f += build_combat_tracker(g)

    # ---- PLAYER HANDOUT APPENDIX ----
    f += [Paragraph("Player Handout Appendix", H1),
          Paragraph("One image per page. Show these at the table when the party encounters the "
                    "person, monster, or location depicted. Maps may be revealed in sections at GM discretion.",
                    BODY),
          PageBreak()]
    page_w, page_h = LETTER
    handout_order = ["brynn", "corwick", "khelziir", "zeldrazz", "drider",
                     "site_b_loc", "site_c_loc", "shrine", "site_b_map", "site_c_map"]
    for key in handout_order:
        label = IMAGES[key][2]
        f += [Paragraph("Player Handout", APP_KICKER),
              Paragraph(label, APP_LABEL),
              Spacer(1, 0.15*inch),
              appendix_img(key, page_w, page_h),
              PageBreak()]

    return f
