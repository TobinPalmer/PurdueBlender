# Rawls Hall R11 handoff

## Saved asset and reopen verification

Updated `modular/buildings/rawls_hall.blend` from the independently reviewed R10 baseline. R10 input SHA-256: `d361f211a8177e234d475493d6242ad396981b7f3fed29dc57f37f54e1026d9e`. R11 saved-asset SHA-256: `19d2ec5828daee8b2529d8b0790422b9a43a9f795b41c6fb2e6bc8c21e1ec9eb`.

`round11_reopen_validation.json` was produced by opening the saved R11 asset in Blender 5.2.3. It confirms 761 scene objects (753 meshes), identity `AssetRoot_rawls_hall`, no materialless meshes, missing external images or linked libraries, and no structural changes to the 16 plan/shell/glass objects compared with the exact R10 baseline. The glass still has 44 panes. The asset is not committed; master/shared files were not edited.

## R11 changes

- Added 20 chair objects to the existing 42 chairs, bringing the model count to 62, as listed by Purdue's 2023 RAWL 1086 classroom guide. The arrangement is an illustrative allocation across the existing six rows, not a surveyed seat plan. The fixed table/desk arrangement remains schematic and its dimensions are not claimed to be exact.
- Repositioned the two source-informed projection panels and added six abstract high-contrast screen cues so both surfaces can be read from a clear southeast pane sightline. The guide supports dual projectors, but does not give screen positions, dimensions, orientation, or actual projected content.
- Retuned the curtain-wall shader to roughness 0.26, transmission 0.90 and specular IOR level 0.04. This is a render-legibility estimate, not a measured glass specification.
- Kept all 44 pane positions and all plan-derived wall geometry unchanged. No upper-floor partition or atrium/core circulation claim was added.

## Evidence renders

- `se_curtainwall_full_round11.png` — full southeast facade from the saved R11 asset.
- `se_curtainwall_through_glass_round11.png` — view aimed through pane 2 toward the paired projection surfaces and room seating; the screens and some rows are legible. The view still has a visible glass reflection and does not show all 62 chair objects at once.
- `render_round11.py` reopens the saved assigned asset before rendering. It adds a render-only soft interior fill light to lift the schematic seating through glass; that light is not saved in the building asset or represented as an installed fixture.

## Evidence sources and limits

The Purdue 2023 RAWL 1086 Classroom Guide lists fixed tiered tables, 62 seats, a lectern and dual projectors: https://kcc.krannert.purdue.edu/Faq/Item/Download/2194 (retrieved 2026-10-25). The Purdue 2024 Rawls Hall first-floor plan remains the plan source and supports only the shown first-floor layout: https://roadschool.purdue.edu/maps/2024%20Rawls%20Hall.pdf (retrieved 2026-10-25).

The approximately 1 m plan-to-shell registration uncertainty remains. The pane layout is inherited and not independently surveyed. Tier rises, classroom furniture positions and projector placement are schematic. Upper-floor partitions and circulation are unverified. Master placement and surrounding-campus alignment are outside this asset review.

R11 independent grade: pending coordinator review. Asset modified: yes. Master/shared/README files modified: no. Commit created: no.
