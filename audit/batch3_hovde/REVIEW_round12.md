# Hovde Hall — round 12 source-model revision

Round 11 received an independent 7.7/10. The review found that the improved portico/capitals and overall dimensions were working, but asked for roof uncertainty to be handled conservatively, more depth/material quality in the stone, and clearer window sightlines.

## Round 12 changes

- **Roof:** the six-vertex roof mesh previously implied a broad hipped surface with a 0.90 m rise. The 2016 geotagged exterior shows red clay tile and a low eave, while the SAH Archipedia account supports the campus red-clay-tile palette; neither supplies Hovde's roof plan or hidden pitch. I reduced the inferred surface rise to 0.16 m and kept the modeled tile cap shallow. The actual ridge/hip layout and roof construction remain unverified.
- **Stone and capitals:** warmed the limestone color response, reduced coarse bump relief, and adjusted roughness for a more dressed-stone finish. Added fine raised limestone midribs to the six pointed leaf blades on each capital. Carving dimensions and details remain photo-informed interpretations.
- **Window sightlines:** shifted only the three central window assemblies on each upper story into the open bays between the six portico columns. First-floor entrance glazing and doors, plus side and rear windows, remain in place. The 2016 photo supports the visible columns and windows behind them; exact individual window centers remain estimates.

## Reopen and render check

Blender 5.2.3 reopened the saved source asset and rendered the following views. `final_asset_check_round12.json` reports 760 export objects (740 meshes and eight curves), no unmaterialed meshes, valid mesh face indices, six columns at 0.79 m diameter, roof rise 0.16 m, and root location `[-62.85, 93, 0]`, Z rotation `0.689754 rad`, unit scale. GIS/master alignment remains for coordinator verification.

- `same_angle_reference_round12.png` — entrance-centered comparison with the 2016 photo.
- `portico_detail_round12.png` and `portico_oblique_round12.png` — entry recess and window/column relationship.

## Independent review — 2026-10-24

**Score: 8.0/10 — meets the visual acceptance threshold.** The reviewer compared the saved model with the 2016 source photo, round-12 entrance/portico/capital/roof views, and reopen evidence. The reduced roof rise, improved upper window alignment, and valid saved export were confirmed.

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.8/2 |
| Position, orientation, scale | 1.2/2 |
| Floors, height, roof | 1.5/2 |
| Facade and entrance | 1.8/2 |
| Modular export and evidence | 1.7/2 |

Open items: master/GIS position and orientation still need coordinator verification against feature 618; roof plan and pitch remain unverified; limestone and capital relief remain simpler than the photograph; some windows are partly masked. The independent grade accepts the visual revision, but does not certify those unresolved placement or roof details.
- `portico_capital_close_round12.png` — capital leaves and fine midrib detail.
- `roof_detail_round12.png` — shallow cap with terracotta tile material; pitch beyond the visible low edge remains unknown.
- `round12_refine.py`, `round12_realign_front_windows.py`, `render_round12.py`, `render_capital_close_round12.py`, and `final_check_round12.py` preserve the revision and checks.

## Remaining limits

There is no Hovde-specific dimensioned roof drawing in the available source set. Only the visible tile color and low eave are supported; the exact roof plan, pitch, and hidden structure remain unverified. Portico size, capital carving, and the repositioned upper central windows remain visual estimates. GIS registration and the master placement marker were not edited or checked in this pass.

**Ready for a fresh independent grade.**

## Second independent assessment — 2026-10-24

A second fresh reviewer scored the same saved round **7.7/10**, below the acceptance threshold: identity/source footprint 1.7/2, position/orientation/scale 1.0/2, floors/height/roof 1.4/2, facade/entrance 1.8/2, modular export/evidence 1.8/2. It independently confirmed the source reopen and visual improvements, but treated master/GIS placement and orientation as unverified and emphasized that roof pitch/ridge and capital carving remain uncertain. Because the two graders disagreed across the acceptance gate, keep Hovde **in progress** until the coordinator resolves placement/orientation against GIS and obtains a fresh grade. The official GIS feature snapshot is `gis_feature_618_snapshot_20261024.json`.

### Coordinator placement verification — 2026-10-24

The coordinator reopened `purdue_campus_master.blend` in Blender 5.2.3. `Placement_hovde_hall` is at `(-49.8026924, 78.2442474, 0)`, with zero rotation and unit scale, exactly matching the manifest origin. Applying that marker to the current source structural bounds gives an AABB center offset of 0.382 m from GIS feature 618, a 1.255 m width difference and 1.019 m depth difference; the source wall heading (39.52°) is within 0.19° of the GIS long-edge direction. These checks support placement and orientation at screening level. Exact wall-centerline/polygon coincidence remains unverified, and the roof shape/pitch remains unverified. See `coordinator_placement_review_20261024.json`.
