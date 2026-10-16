# Editorial Review — Session 008, The Tide Festival

Continuity-first review (Step 5a), run after the Markdown was written and before the PDF was built. **Revision 2** (2026-10-16) reworks the tone at the DM's direction: *villains can be villains and don't need to be silly; the day should be upbeat and the NPCs should have a lightness to them.* Revision 1's findings are kept below; anything revision 2 replaced is marked.

## Sources checked

- `sessions/session 7/session 7 - log.md` (corrected against the recording), `Session7.m4a.md`, `campaign/session-log.md`, `campaign/party.md` and the character pages for Naan, Nalith, Kto and Yinu.
- Canon: *FR Campaign Guide* p. 145 (New Sarshel kept pace with the retreating sea; trade; Grand Council) and *Player's Guide* p. 107 (Impiltur's ports dried up; people moved to New Sarshel).
- The approved outline (four PCs at Level 6) and the DM's revision-2 tone direction.
- All five deliverables and all nine images.

## Revision 2 — what changed

- **Tone rules (Files 0, 1, 2, 4).** "Silly villains who give up, slapstick hazards, nobody dies" is now *upbeat day, real villains*. The villains lie, threaten, and fight to win. The lightness sits with the walkers, Plumm, Amsel, Tibbet, Lorrow, and the games. Normal death saves apply; bystanders can be hurt, nobody dies on screen, and there is no gore.
- **The Gilded Gull Club.** Gullwhistle **knew** the light was fed with lured travellers and paid anyway. Marisol was fooled. Dunstan suspected and chose not to ask. This matches how the table read the ledger in Session 7 (*"funding her to summon this demon"*) instead of turning it into a joke.
- **The Brack Brothers** are salt-road wreckers hired to take the ledger and stop the walkers. There are four ways to avoid the fight (hand over the ledger, buy them off, bluff, scare) and a real fight if those fail. New stat blocks: net, caltrops, grab-and-throw, Parry. The crab is now **Clacker**, a harnessed salvage beast (same *Monster Manual* giant crab).
- **Scene 2.2.** Gullwhistle is gracious, then threatening. Tibbet overheard him say *"the book goes into the harbor with them."* Dunstan's admission and Veyra's letter (new, in Common) prove he knew.
- **Encounter 2.** The float has brass teeth and Steam Breath (4d6 fire). The gulls go for the ledger. Gullwhistle joins as a CR 2 combatant who can escape by rowboat off the south edge, or surrender. Crowd groups the float reaches are hurt, not soaked.
- **Scene 3.2.** Justice: the Council, Gullwhistle's estate seized to rehouse the survivors, Marisol's feast, and his gold gull pin as a trophy. If he escapes, he becomes an open villain. The reward stays at 600 gp.
- **Art.** Regenerated the Brack Brothers and Gullwhistle portraits and the float scene. The title image, the salt-road scene, Tibbet, Tamsin and both maps are unchanged; the map geometry did not change.

## Revision 2 — decisions taken by default

The DM didn't answer these four proposal questions, so each takes the recommended option. Any can be reversed cheaply.

- **Did Gullwhistle know about the prisoners? Yes.** It is what makes him a real villain.
- **Can he escape? Yes, if the party lets him reach the boat.** The boat is telegraphed, and he surrenders at 15 HP or fewer with no way out.
- **A letter pointing at Veyra's master? No.** Veyra's letter only proves Gullwhistle agreed to the price; who she served stays open.
- **The giant crab? Kept** as the Bracks' working salvage crab: no hat, same stats, same XP.

## Revision 2 — findings and fixes

1. **Wren only ran ahead "when trouble starts."** In the peaceful branches nobody explained the cheering crowd at the gate. **Fix:** she runs ahead in every branch.
2. **In two branches the party never learned the pin clue.** If they handed over the ledger or bluffed the Bracks, Mort never talked, yet 2.1 had Amsel react to his description. **Fix:** Mort's teal-and-gold gull purse is visible in every outcome. Plumm and Amsel read it as the club's colors, and the "G." note and spoken description come on top when the Bracks talk.
3. **Bluffed Bracks had no follow-through.** **Fix:** they join the "went free" branch. Gullwhistle won't pay for fish-wrapping, so they turn up at the parade for their money.
4. **The surrender trigger "Mort drops" clashed with "Mort talks."** **Fix:** the brothers talk if he is down.
5. **Tibbet was deaf in one ear but overheard a quiet conversation.** **Fix:** the deafness is gone.
6. **Ollie had d10 hit dice as a Medium creature.** **Fix:** 9d8 + 27 = 67 HP. The initiative row now has 67 boxes, and the quick reference matches.
7. **3.2 had no branch for Gullwhistle being killed** under normal rules. **Fix:** "taken or killed" share an outcome, and Plumm is grim about it.
8. **PDF: initiative tables split from their heading.** The rebuilt revision-2 PDF left "Round Strip & Initiative" alone at the bottom of a page (Encounter 1) and split Encounter 2's table across two pages. Session 7's PDF had both of its tables split the same way. **Fix:** `scripts/md_to_pdf.py` keeps an initiative table, its heading and its intro lines together. Test: `scripts/test_init_table_keep_together.py` failed before the fix and passes after. Both PDFs were rebuilt; each initiative table is now on one page with its Conditions line.
9. **Handout leak check.** Nothing in File 3 reveals that Gullwhistle knew, his escape route, his charm or whistle, or the scroll's nature. The float handout now describes teeth and steam, with no villain line.

## Causal chain

- **1.1 → 1.2.** S7 ended with the party setting out east with the survivors. The Bracks exist because Gullwhistle saw the light go out from Gull Row. In every branch the party sees the gull purse, and Wren runs ahead, which explains the crowd at the gate.
- **1.2 → 2.1.** Plumm houses everyone and hands over the schedule. The Noon Bells are the first item on Tide Day, with the long rest in between.
- **2.1 → 2.2.** Amsel names the club, Gull Row and *"for the Summoning"* from the ledger (or from the purse if the ledger is gone) and sends the party to the games. **Bypass:** if the party skips the Hall, he finds them on the Green.
- **2.2 → 3.1.** Gullwhistle reads the scroll at the parade **whether or not the party exposes the club** — exposure changes only where he starts (on the float, or in the grandstand) and how much proof exists. If they lift the scroll, a second copy keeps the scene intact, and the stolen letter becomes proof.
- **3.1 → 3.2.** However the float stops, it ends in the fountain. Gullwhistle is taken, killed, or escapes; each has a 3.2 outcome. The number of crowd groups saved sets the cheers and Heroic Inspiration.
- **3.2 → Session 009.** Captain Lorrow's free passage hands the next destination to the players.

## World-state ledger

- **Distance and time.** Tower to city is 9 miles (the DM said so at the table in S7). The roadblock is 6 miles along, in the early morning; the city is reached late morning at a walking-with-a-cart pace (~3 mph).
- **Days.** Lantern Eve is arrival day (dusk lanterns, long rest). Tide Day holds the Noon Bells, the games, the parade at sunset and the fireworks at nightfall. The schedule handout matches the adventure's day table.
- **Rest.** None since S6 (confirmed on the S7 tape). A short rest on the road and a long rest Lantern Eve night, so Encounter 2 is fought fully rested.
- **The ledger.** At the S7 table: *"the names of several in … New Sarshel that were funding her to summon this demon … but you don't see why."* The handout shows three names, *"for the Summoning"*, and unreadable fire-script — *who* paid, not *why*, exactly as played. Revision 2 makes the table's reading the true one.
- **Who knows what.** Gullwhistle knows the light went out and that Veyra kept papers, but not who has them, so he hires the Bracks for "every book and paper." Marisol knows only "a summoning of the tide." Dunstan heard "the light needs feeding." Nobody in the club knows who Veyra served.
- **Evidence custody.** The ledger stays with the party unless handed to the Bracks or snatched by a gull. The "G." note is in Mort's coat. Veyra's letter is in Gullwhistle's coat, and can be lifted in 2.2 or found on him in 3.2.
- **Headcount.** About fifteen walkers: the *Embergull* camp, Tamsin, and the four freed prisoners (named here for the first time ⚗️).

## Revision 1 findings (kept for the record)

1. **The church thread was attributed to Kto, but the tape points at Naan** (*"Lily looks so angry. She's missing mass."*). The S7 log and campaign log now say "most likely Naan — confirm"; Scene 2.1 works either way.
2. **The recap reflected the earlier wrong S7 summary.** File 3 now uses the corrected record.
3. **The handout ledger gave the twist away** ("Promise them the tide"). Removed.
4. **Showing Plumm the ledger in 1.2 did nothing until the end.** She now points out the Gulls in 2.2.
5. **The "beaten Bracks" path skipped a step.** The walkers hand them to the watch in 1.2.
6. **The booth appeared overnight.** It's an old salt-collector's hut.
7. **The float's movement rule was unclear.** It now rolls toward its most recent attacker, then its last attacker once the crowds are resolved.
8. **The rider effect was contradictory.** A Tail Swipe hit throws a rider 10 ft., with no extra save.
9. **The potions of healing weren't given anywhere.** Amsel gives them in 2.1.
10. **Scene 3.1's NPC note didn't follow the template.** It's now a full NPC block.
11. **The "TOAL" sign art.** *Superseded by revision 2:* the sign is gone, and the Bracks are wreckers at a salt-collector's hut.
12. **PDF: the ⚗️ marker printed as black boxes.** The renderer now prints it as a superscript †, with a regression test.
13. **PDF: HP checkboxes ran off the page.** They now wrap at 10 per row, with a regression test.

## Rules and numbers

- **Thresholds:** 2014 DMG per PC at Level 6 (300 / 600 / 900 / 1,400) × 4 = **1,200 / 2,400 / 3,600 / 5,600**.
- **Encounter 1:** 3 × 450 + 25 = 1,375 × 2 (four creatures) = **2,750 → Medium** (unchanged).
- **Encounter 2:** 1,800 + 450 + 2 × 100 = 2,450 × 2 (four creatures) = **4,900 → Hard** (was 4,000 with three creatures; still below Deadly 5,600).
- **Damage check:** the float's Multiattack averages 32.5 a round and Steam Breath 14 per target. Gullwhistle's rapier averages 15, and he spends early rounds moving and whistling. A fully rested Level 6 party can take a Hard fight, and the float spends turns on crowds unless hit.
- **Hit dice and initiative:** each stat block's HP equals the average of its dice, and NPC initiative is `round(avg(1d20 + DEX))` (checked by script).
- ***Dispel magic*** against a 5th-level effect: automatic with a 5th-level slot, otherwise a check at DC 15. The party's casters have 3rd-level slots at most.
- ***Charm Person*** on Marisol works because she isn't hostile (S7's ruling was that it fails on a hostile enemy).
- ***Pyrotechnics*** is a 2nd-level wizard spell from *Xanathar's Guide*, so Yinu can copy it. **Heroic Inspiration** uses the 2024 term, matching the campaign's 2024 PHB.
- **All stat blocks are homebrew ⚗️** except Clacker (giant crab).

## Tone check (revision 2)

- **Villains are played straight.** Gullwhistle is charming and cold; he offers, threatens, and either fights or flees. The Bracks banter but mean it, and surrender only when beaten. No villain gives up for comic effect.
- **The lightness is with the friends.** Bram's shanties, Wren's autographs, Dagna's pickles, Plumm's clipboard, Amsel's nosiness, Tibbet's singed eyebrows, Lorrow's bad jokes, the crab races, and the pickle contest.
- **Danger is telegraphed:** the walkers at the roadblock, the gulls' target, the escape boat, area spells near crowds. Bystanders can be hurt but nobody dies on screen.
- **Spotlights unchanged:** Kto (archery, name read out), Nalith (lantern for her mother, crab races), Yinu (Tibbet's real lesson, her staff back if needed), Naan (mass and quiet, the white room for real).
- **Not written in:** Fiorn, Dirk, Tyvlex.

## Machine-checked pass — PASS

A scripted assertion pass over all five files, the manifest, and the request list:
- **Retired strings:** none of the 41 revision-1 tone strings remain in any file (non-lethal rules, comic abilities, the hat, the confetti breath, "fools, not monsters," and so on). Survivors were reviewed: Dunstan sweating in 3.2 and "the golden-pin clue" are intended.
- **Fiorn:** appears only in "not written in" lines.
- **Cross-file numbers:** every stat block's AC and HP matches the quick reference; HP equals the dice average; initiative matches DEX; the thresholds and both XP lines are present; the budget bands are asserted numerically.
- **Initiative tables:** exactly one row per combatant, each HP box count equals the creature's HP, and four blank PC rows per encounter.
- **Scenes:** all six scene IDs exist, every reference resolves, and File 4's scene titles match File 1's. Every scene has Purpose, Setting, and Encounter lines.
- **Branches:** every Brack outcome (bought off, scared off, bluffed, taken in, fled, ledger handed over) has a follow-through. All 10 rewards appear in File 1 and File 4.
- **Maps:** they appear only in File 2, captions start with `Tactical Map`, and each map comes before the next encounter.
- **Images:** all 9 Markdown targets exist and equal the manifest; every entry has a prompt; the three r2 entries carry the exact submitted prompt from `image-prompts.json`; portrait headings match `portrait_name`.
- **Player handouts:** none of 15 DM-only facts appear in File 3.
- **Status:** the overview reads as unplayed, and `campaign/session-log.md` has no Session 8 content. The S7 recap facts are intact.

**PDF gate (revision 2):** 41 pages, no blank pages, 10 image placements, 9 unique images (equal to the manifest). The 4 portrait pages pass the one-image-one-name check. Nothing passes the right margin, both initiative tables are each on one page, there are 27 † markers and no ⚗ glyphs left in the text layer, and the word "silly" appears nowhere in the PDF. All 4 renderer tests pass. Session 7 was rebuilt with the same renderer: still 48 pages, both initiative tables on one page.

**Image gate (revision 2):** I checked each regenerated image by eye.
- **Brack Brothers:** three adult men, all heads in frame, net and cudgel, sling and bandolier, bald brawler, and a red crab in a rope harness with no hat.
- **Gullwhistle:** slim, silver-streaked ginger beard, teal-and-gold coat, gull pin, feathered tricorn, rapier, and the sealed scroll. He reads as polished and quietly threatening.
- **Float scene:** brass teeth, glowing green eye, steam, a fleeing crowd, two gulls, and the nobleman with a glowing scroll. No blood or visible injuries.
- **All three:** no text or watermark, and full-bleed to all four edges. The six unchanged images keep their revision-1 checks: wordless, maps on 12×12 and 16×16 grids.

## Open DM decisions

- **Whose mass is it?** Most likely Naan; confirm with Lilli and Kaitlyn.
- **Did Yinu get her staff back in the lantern room?** Tamsin returns it in 1.1 if not — confirm with Sev.
- **Coin denomination from S7** ("15 book pieces").
- **The four revision-2 defaults above** — Gullwhistle knew, he can escape, no master letter, Clacker kept.
- **Where the *Laughing Otter* sails** — ask the players at the end of the session.
- **Campaign guide:** add New Sarshel, Gull Row and the festival to `campaign/geography.md`, and the new NPCs to `campaign/roster.md`, after this session is played.
