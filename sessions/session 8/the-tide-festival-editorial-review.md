# Editorial Review — Session 008, The Tide Festival

Continuity-first review, run after the Markdown was generated and before the PDF was built (Step 5a).

## Sources checked

- `sessions/session 7/session 7 - log.md` (corrected against the recording), `Session7.m4a.md`, `campaign/session-log.md`, `campaign/party.md` and the character pages for Naan, Nalith, Kto and Yinu.
- Canon: *FR Campaign Guide* p. 145 (New Sarshel kept pace with the retreating sea; trade; Grand Council) and *Player's Guide* p. 107 (Impiltur's ports dried up; people moved to New Sarshel).
- The approved outline: four PCs at Level 6, a happy and fun tone.
- All five deliverables and all nine images.

## Causal chain

- **1.1 → 1.2.** S7 ended with the party setting out east with the survivors. The Bracks exist because Gullwhistle saw the light go out from Gull Row that night. Whatever happens at the booth, the Bracks give up the *golden bird pin* clue, and Wren runs ahead, which explains the cheering crowd at the gate.
- **1.2 → 2.1.** Warden Plumm houses everyone and hands over the schedule; the Noon Bells are the first item on Tide Day. The long rest happens in between.
- **2.1 → 2.2.** Brother Amsel reads the ledger and names the Gilded Gull Club, Gull Row and *"for the Summoning"*, then sends the party to the games where the Gulls will be. **Bypass:** if the party skips the Hall, Amsel finds them on Festival Green and reads the ledger there.
- **2.2 → 3.1.** Gullwhistle reads the scroll at the parade **whether or not the party exposes the club** — the exposure only changes why he does it and what the ending gives. If the party steals the scroll, a second copy keeps the scene intact without punishing the clever play: the float still wakes, but nobody is riding it.
- **3.1 → 3.2.** However the float stops, it ends in the fountain, so the soaked public confession always happens. The number of crowd groups saved sets the size of the reward.
- **3.2 → Session 009.** Captain Lorrow's free passage hands the next destination to the players.

## World-state ledger

- **Distance and time.** Tower to city is 9 miles (the DM said so at the table in S7). The toll booth is 6 miles along, in the early morning; the city is reached late morning at a walking-with-a-cart pace (~3 mph).
- **Days.** Lantern Eve is arrival day (dusk lanterns, long rest). Tide Day holds the Noon Bells, the games, the parade at sunset and the fireworks at nightfall. The schedule handout matches the adventure's day table.
- **Rest.** The party has not rested since S6 (confirmed on the S7 tape). There is a short rest on the road and a long rest Lantern Eve night, so Encounter 2 is fought fully rested.
- **The ledger.** At the S7 table: "the names of several in … New Sarshel that were funding her to summon this demon … but you don't see why." The handout shows three names, *"for the Summoning"*, and unreadable fire-script — so it shows *who* paid, not *why*, exactly as played. Both readings of "summoning" are true (Veyra meant the demon; the club thought she meant the tide).
- **Who knows what.** The Gulls never went to the lighthouse and knew nothing of the prisoners. Gullwhistle knows the light went out (spyglass), not who has the ledger, so he hires the Bracks to collect "any books or papers."
- **Headcount.** About fifteen walkers: the *Embergull* camp, Tamsin, and the four freed prisoners (named here for the first time ⚗️).

## Findings and fixes

1. **The church thread was attributed to Kto, but the tape points at Naan.** The S7 log and campaign log credited Kto. On the recording: *"Lily looks so angry. She's missing mass."* — Lilli plays Naan. Kto's vision, though, was her god's recognition. **Fix:** the S7 log and `campaign/session-log.md` now say "most likely Naan — confirm"; Scene 2.1 gives mass to "the PC who has been missing mass" and gives Kto her own recognition beat, so it works either way.
2. **The recap reflected the earlier wrong S7 summary.** **Fix:** File 3 uses the corrected record — Yinu taken by the light and chained, Nalith's *dispel magic* on Tamsin, Naan's *cloud of daggers*, Yinu's *lightning bolt*.
3. **The handout ledger gave the game away.** A line reading "Promise them the tide" told the players the twist before Scene 2.2. **Removed.**
4. **Showing the ledger to Plumm in 1.2 had no effect until the very end.** **Fix:** she now points out the three Gulls by name in 2.2, which shortcuts the search. Restitution in 3.2 no longer depends on it.
5. **The "beaten Bracks" path skipped a step.** They ended up in the stocks with no explanation. **Fix:** the walkers hand them to the watch at the gate in 1.2.
6. **The Bracks' booth appeared overnight.** **Fix:** it is an old salt-collector's hut they moved into.
7. **The float's movement rule was unclear.** "Stops when it reaches that creature" could mean several things, and it had no target once every crowd group was resolved. **Fix:** it rolls toward whoever hit it most recently; with no crowd left, it chases its last attacker.
8. **The rider-thrown-off effect conflicted.** Tail Swipe's DC 15 Strength save clashed with a second DC 13 Dex save for riders. **Fix:** a Tail Swipe hit also throws a rider 10 ft. off the float, with no extra save.
9. **The potions of healing** were listed in the rewards but given nowhere in the story. **Fix:** Brother Amsel gives them in 2.1.
10. **Scene 3.1 didn't follow the template.** Its NPC note was a loose line. **Fix:** Gullwhistle now has a proper NPC block.
11. **The art shows a "TOAL" sign as blank** (the image is wordless by rule). The text says the sign is hand-painted and misspelled. **Keep the text**; say it at the table.

12. **PDF: the ⚗️ homebrew marker printed as two black boxes.** The PDF's built-in Times font has no glyph for it; Session 7's PDF had the same defect. **Fix:** `scripts/md_to_pdf.py` now prints it as a superscript dagger (†). Test: `scripts/test_homebrew_marker.py` failed before the fix and passes after.
13. **PDF: HP checkboxes ran off the page.** Every HP box was drawn in a single row (90 HP ≈ 720 pt, wider than the 612-pt page) — the float's row and Session 7's Veyra and Brine Fiend rows. **Fix:** the boxes wrap at 10 per row. Test: `scripts/test_hp_boxes_wrap.py` failed before and passes after. The float's row was also changed to 10-HP milestone boxes. Both PDFs were rebuilt; Session 7 is still 48 pages.

## Rules and numbers

- **Thresholds:** 2014 DMG per PC at Level 6 (300 / 600 / 900 / 1,400) × 4 = **1,200 / 2,400 / 3,600 / 5,600**.
- **Encounter 1:** 3 × 450 + 25 = 1,375 × 2 (four creatures) = **2,750 → Medium**.
- **Encounter 2:** 1,800 + 2 × 100 = 2,000 × 2 (three creatures) = **4,000 → Hard**.
- ***Dispel magic*** against a 5th-level effect: automatic with a 5th-level slot, otherwise DC 10 + 5 = **15**. The party's casters have 3rd-level slots at most, so this is a check — it is meant to be one of three ways to stop the float, not a sure thing.
- ***Charm Person*** works on Marisol because she is not hostile (S7's ruling was that it fails on a hostile enemy) — a deliberate, happy callback.
- ***Pyrotechnics*** is a 2nd-level wizard spell from *Xanathar's Guide*, so Yinu can copy it.
- **Heroic Inspiration** uses the 2024 term, matching the campaign's 2024 PHB.
- **All stat blocks are homebrew ⚗️** except the giant crab.

## Tone check (happy and fun)

- Every villain gives up, blabs, or apologises. Both fights carry non-lethal rules, and anyone dropped is stable.
- Hazards end with people soggy, sticky, or sitting in a fountain. The S7 demon plot is acknowledged once (Amsel, on request) and kept out of the day.
- **Spotlights:** Kto (archery, name read out), Nalith (lantern for her mother, crab races), Yinu (Tibbet's real lesson, her staff back if needed), Naan (mass and quiet, the white room for real). Each one answers that PC's S7 vision with something true.
- **Not written in:** Fiorn, Dirk, Tyvlex.

## Machine-checked pass — PASS

A scripted assertion pass over all five files and the manifest:
- **Retired strings:** none of the 13 fixed or forbidden strings remain.
- **Fiorn:** appears only in "not written in" lines.
- **Cross-file numbers:** float HP, AC and DCs, the dispel level, the thresholds and the XP math match between the tracker and the quick reference.
- **Rewards:** all 7 rewards appear in both File 1 and File 4.
- **Scenes:** all six IDs exist and every cross-reference resolves; every scene has a Purpose line and an Encounter line.
- **Initiative:** exactly one row per combatant and four blank PC rows in each encounter.
- **Maps:** they appear only in File 2, every caption starts with `Tactical Map`, and each sits before the next encounter.
- **Images:** all 9 Markdown targets exist on disk and equal the manifest; every manifest entry has a prompt; portrait headings match `portrait_name`.
- **Player handouts:** no DM secret appears in File 3.
- **Status:** the overview still reads as unplayed, and `campaign/session-log.md` has no Session 8 content.

**PDF gate:** 37 pages, no blank pages, 10 image placements, 9 unique images (equal to the manifest). The 4 portrait pages each carry one image plus one 28-pt bold name at 0.90–0.94 fill. Nothing (text or drawing) passes the right margin on any page of the Session 7 or Session 8 PDF.

**Image gate:** every image was checked by eye. None has text or a watermark. The two maps have 12×12 and 16×16 grids, each covering the whole image, and every requested feature is present. All three new portraits match their written description, with heads fully in frame and full-bleed art.

## Open DM decisions

- **Whose mass is it?** Most likely Naan; confirm with Lilli and Kaitlyn.
- **Did Yinu get her staff back in the lantern room?** Tamsin returns it in 1.1 if not — confirm with Sev.
- **Coin denomination from S7** ("15 book pieces").
- **Where the *Laughing Otter* sails** — ask the players at the end of the session.
- **Campaign guide:** add New Sarshel, Gull Row and the festival to `campaign/geography.md`, and the new NPCs to `campaign/roster.md`, after this session is played.
