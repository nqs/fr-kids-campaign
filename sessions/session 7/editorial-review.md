# Editorial Review — Session 007

## Scope and sources

Reviewed the five Session 007 Markdown deliverables against Session 006's played log, approved outline and attendance (five Level 6 PCs), and `references/campaign-guide/_raw/pages/page-0145.md`. Continuity review is distinct from subsequent PDF asset/layout verification. No session-log or campaign history was updated.

## Findings resolved

- **Scene chain:** portal arrival with Juniper already present → camp signal/missing-person warning → named captives and keeper relationship → maintenance instructions before the finale. Alternate routes remain real; bypassing camp has duplicate clues, leaving the boundary succeeds.
- **Geography:** one-mile-radius sphere centered on lighthouse; landing west edge, camp midway 400 ft off road, New Sarshel nine miles east of tower. Off-road travel avoids the road loop but does not instantly end illusions inside the radius. This corrects the prior contradiction of an off-road camp remaining trapped after supposedly universal off-road immunity.
- **Time:** sky is illusory, not stopped. Dawn three hours after landing; normal travel/rest clocks. Veyra starts at dawn or rushes her charge when confronted. Alarm readies rather than prematurely starts the rite; an unopposed dawn rite completes in three rounds. Early arrival is measured by time remaining, not whether the party accepted a rest.
- **History/evidence:** Tamsin was deceived by a false repairer; Orin is her old courier friend. She supplied warning and copied instructions, retaining original log. Andry briefly escaped with the cult schedule before recapture. Camp tally is fifteen travelers excluding Orin: nine camp, four captive, two earlier deaths. The complete ledger, not the torn schedule, supplies city addresses.
- **Attendance:** four returning PCs land; Juniper witnesses it. No prescribed build or resource state. Absent PCs' locations remain DM/player decisions; no invented death/capture. Sela remains unresolved.
- **NPC personality:** Orin's warmth and guilt; Tamsin's keeper habits and divided duty; Ilde's grief plus practical competence; Veyra's ambition, fear, genuine negotiation options and interruptible rope escape. Captives are named and characterized before rescue.
- **Keeper outcomes:** key and written code remain lootable when unconscious or dead. Passing her uses ordinary movement, not arbitrary vanishing. Her charm does not confer unrelated charm/fear immunity.
- **Finale:** clear separation of lesser emissary and sealed prisoner; one capped clock rule; thresholds trigger once; freed people immune to ritual drain. No instant child death. Segment six has three rounds to reseal before a persistent regional consequence; exit stair remains open. Pedestal destruction stops the rite but does not itself repair lens or seal.
- **Actions:** restore one arm with one successful DC13 action or two no-roll actions; repeated checks/interference may take longer. Captive release is a visible no-roll catch, not a redundant skill tax. Shutter never pauses ritual. No false guaranteed damage/action counts. All reaction choices share one reaction.
- **Rules/budgets:** fly is potentially available at Level6; no invented universal flight/teleport escape distances. Spell effects and homebrew exceptions distinguished. Daily budget 20,000 versus nominal adjusted encounter sum7,950; CRs still explicitly provisional, not verified DMG calculations.
- **Consequences:** actual survivors, inventory, Veyra's observations and acquired evidence determine outcomes; no automatic ledger transfer, hostile magistrates, forced sunrise, or guaranteed villain escape.
- **Presentation:** handout appearance cues aligned with inspected portraits, private mechanical notes kept out; quickref rewritten for table use. Existing maps remain schematic and written geometry authoritative.

## Remaining preparation choices / limitations

- Juniper's character and absent-PC placement belong to players/DM.
- Homebrew encounter CRs remain provisional; this pass is not playtesting or a full CR audit.
- Some existing portrait backgrounds show open water. Treat them as atmospheric/vision imagery, not a literal current coastline; the published adventure is explicitly on dry seabed. No art was regenerated in this edit.
- Existing `/opt/data/lighthouse-preplay-proposals.md` predates these changes and must be revised before any campaign-guide adoption. It is not incorporated into this adventure or campaign canon.
- Timing is an estimate for a two-hour table session; skip optional keeper combat if needed.

## Verification gate

Run cross-file assertions for clock/boundary/key rules, planned status, valid image paths, five initiative rows per fight, and encounter-map ordering. Rebuild the PDF from revised Markdown; independently verify expected sections, every manifest image embedded, no empty pages, and standalone tactical-map pages. Record actual build results in the overview only after verification.

## Named-portrait and grid revision

Regenerated four portraits through the default Hermes image function: Tamsin Reed, Orin Vale, Veyra Sorn, Brine Fiend. Visual inspection confirmed exact large centered name-only lettering, with no additional readable words. Regenerated both maps and visually confirmed square grids: 16×16 approach at 80×80 feet; 12×12 lantern field at 60×60 feet. Every square represents 5×5 feet. Some map lines pass beneath decorative terrain; written encounter dimensions remain authoritative. Scene and title art retained. Successful exact prompts and measured image sizes updated in the manifest. This is an art revision, not a change to story outcomes or encounter rules.


## Revision 2 — art and portrait-page review

- **Portrait pages were wrong:** the handouts printed a heading, the artwork's own baked-in nameplate, and four description bullets, so the name appeared twice and the page was noisy. Fixed at both layers: the raw portraits are now generated wordless, the description bullets moved into the DM sections of File 1 (nothing lost), and the renderer now typesets the name once at the foot of the page.
- **Renderer change:** `scripts/md_to_pdf.py` composes an illustrated handout page as image + name only when the manifest entry carries `portrait_name`; the name is Times-Bold 28 pt, horizontally centered, and the image is scaled to the largest size the page allows. Covered by `scripts/test_portrait_layout.py` (fail-first test: the old composer printed the heading and bullets).
- **Title/camp pages keep their captions** — the name-only rule applies to NPC and creature portraits, not scene illustrations.
- **Tamsin's portrait was a bearded man** while the text makes her an elderly woman; regenerated and re-verified as an elderly woman, full head visible, no lettering.
- **Artwork provenance is mixed.** Both Codex OAuth credentials are rate-limited until roughly 25 September 2026 (`usage_limit_reached`), so the four portraits and the two maps were made with `gpt-image-2-medium` before the quota ran out, and Tamsin was re-made on `openrouter/google/gemini-2.5-flash-image`, which also returns a faint corner artist mark — cropped off (bottom 12%) before use. Future sessions should check `hermes auth list` before image generation and expect to fall back to OpenRouter.
