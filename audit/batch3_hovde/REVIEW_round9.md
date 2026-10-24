# Hovde Hall — round 9 building-side review

## Round 9 implementation

The largest source-backed correction is restoring the full six-column colonnade. Julian Herzog's near-frontal 2016 photo shows six supports; round 8 had removed the two inner supports and therefore did not match the reference. The six columns are now placed at regular 3.24 m intervals across a wider portico. The near-frontal image suggests a portico-to-long-façade width ratio of roughly 0.25; combining that visual estimate with the Purdue Archives record's 70 by 230 ft dimensions gives an approximate modeled portico width of 17.9 m. Image perspective and the source framing leave about ±0.04 ratio uncertainty, so this is an estimate rather than a measured elevation.

Round 9 also increases the shaft/base/capital scale slightly, adds depth to the pediment face, and gives the cornice/crown a subtle limestone trim material. Brick variation was softened while preserving the approximately 0.21 m brick width and 0.065 m course height. Glazing was lifted from dark blue toward blue-gray reflections. These are appearance refinements, not material samples from the building.

The saved source was reopened in Blender 5.2.3 for exterior and interior evidence renders. `final_asset_check_round9.json` records 727 collection objects, 715 meshes, no unmaterialed meshes, six restored columns, portico member dimensions, and the retained `HOVD_Root` transform `[-62.85, 93, 0]`, Z rotation `0.689754 rad`, scale `[1,1,1]`.

## Evidence files

- `exterior_round9.png` — overall source asset view.
- `portico_detail_round9.png` — frontal portico detail with all six columns visible.
- `presidential_office_cutaway_round9.png` and `trustees_boardroom_cutaway_round9.png` — interpretive room cutaways. Their plans remain explicitly unverified.
- `evidence_round9.json` — providers, source URLs, dates, CRS, photo coordinates, evidence use, measurement method, uncertainty, and outstanding checks.
- `reference_herzog_hovde_2016.jpg` — raw full-resolution CC BY 4.0 source image snapshot; author and attribution details are recorded in `evidence_round9.json`.
- `round9_edit.py` — reproducible source-library change.
- `render_round9.py` — render-only evidence setup.
- `final_check_round9.py` and `final_asset_check_round9.json` — saved/reopened source integrity record.

## Remaining limits

- Coordinator still needs to compare the local structural shell and placement against official Purdue GIS feature 618 and nearby context in the master. No master or marker was changed here.
- Portico width/spacing remain image-derived estimates; no dimensioned elevation was located.
- The official Archives record supports the four-story identity, building dimensions, and boardroom context, but no exact room plan. Interior cutaways remain schematic.
- Roof profile and material are visually supported by the photo and campus architectural history, but no Hovde-specific roof plan was found.

**Independent score not yet assigned.** Round 8 scored 7.8/10; send round 9 evidence to an independent reviewer before deciding whether further edits are needed.
