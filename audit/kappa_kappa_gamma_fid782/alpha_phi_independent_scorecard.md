# Alpha Phi (FID 764) independent scorecard

**Review date:** 2026-10-28  
**Reviewed asset:** `../../modular/buildings/massing_house_301841331_735e92f.blend`  
**Asset SHA-256:** `92B5AF509B3DC4E651CEA635DE449CF43A1210E7CBD23F5EF595551EE4A81EDC`  
**Review scope:** Read-only review of the current asset, `audit/alpha_phi_fid764/` source packet, build configuration/script, and saved previews. Alpha Phi files were not modified.  
**Independent score:** **5.8/10 — below the 8/10 completion threshold.**

## Category scores

| Category | Weight | Score | Basis |
| --- | ---: | ---: | --- |
| Identity and source provenance | 20% | 5.5/10 | FID 764 attributes support Alpha Phi, SOAF, and 801 David Ross Rd. The raw feature snapshot contains coordinates but no `spatialReference` member; the build config assumes EPSG:3857 from the coordinate values. The packet has no saved exterior reference, floor plan, or source-observation record. |
| Plan geometry and placement | 25% | 8.0/10 | The build script converts and uses the complete 16-vertex feature ring for exterior walls, which is a strong source-derived plan basis. The packet does not include a post-build coordinate overlay or dimensional comparison, and the CRS assumption is not preserved in the raw snapshot. |
| Exterior silhouette and openings | 25% | 5.5/10 | The visible asset has a coherent two-level red-brick residence and a broad gable roof. The 7.4 m wall height, 10 m ridge, roof dimensions/axis, two-story reading, entrance edge 13, and window rhythm are interpretive. No saved source image or measured elevation supports those choices. The one-level GIS attributes conflict with the modeled story count and do not resolve it. |
| Materials and facade detail | 10% | 6.5/10 | Brick, contrasting trim, windows, and an entry porch are clearly differentiated and procedurally textured. Their color, rhythm, porch form, and details are not traceable to a cited visual source in this packet. |
| Interior evidence and legibility | 10% | 3.0/10 | Interior room modules and furnishings are explicitly generic and unverified. The saved `schematic_upper_rooms.png` is very dark and mostly blank, so it does not let a reviewer assess the arrangement clearly. |
| Presentation and technical evidence | 10% | 4.0/10 | The exterior three-quarter preview communicates the model. A read-only open in Blender 5.2.3 succeeded and showed the expected scene, one mesh object, and one-object asset collection (3,747 vertices). The packet has no fresh-open report, rendered plan/footprint overlay, or source-to-model validation record. |

**Weighted calculation:** 0.20×5.5 + 0.25×8.0 + 0.25×5.5 + 0.10×6.5 + 0.10×3.0 + 0.10×4.0 = **5.825**, reported as **5.8/10**.

## Evidence reviewed

- `audit/alpha_phi_fid764/source_feature_764_raw.json`: FID 764, `BUILDING_N=Alpha Phi`, `BLDG_ABBR=SOAF`, `ADDRESS=801 David Ross Rd`, `NUM_LEVELS=1`, `Extrution=12`, and 16 distinct ring vertices. The ring coordinates are Web Mercator-like values, but the saved response omits an explicit spatial reference.
- `audit/alpha_phi_fid764/build_config.json`: two modeled stories; wall and roof heights; entry edge 13; principal axis; all marked estimated or interpretive where applicable.
- `audit/alpha_phi_fid764/build_detail.py`: exterior walls derived from the converted source ring; generic windows, porch, gable roof, and room modules authored as illustrative geometry. The source comments refer to a “labeled Purdue house illustration” without recording its URI or a local copy.
- `audit/alpha_phi_fid764/exterior_three_quarter.png`: visually coherent red-brick/stone-trim house with a broad gable roof and entry porch. This image alone cannot establish resemblance to the real Alpha Phi house.
- `audit/alpha_phi_fid764/schematic_upper_rooms.png`: mostly dark/empty from the saved top-down view, with only a narrow diagonal band of geometry legible.
- Read-only asset open: Blender 5.2.3 LTS; expected scene and collection names; one mesh object named `House_301841331`, with 3,747 vertices.

## Remediation before reconsidering 8/10

1. Add the source service URL, retrieval date, explicit source CRS, and an unmodified response that preserves its spatial reference. Reconcile the feature identity/address with a second reliable source.
2. Save and cite at least one identifiable exterior view of the actual chapter house and any available site or elevation plan. Record which model choices each source supports; preserve date and access details.
3. Compare the source ring with the built wall footprint in a top-down overlay and report plan dimensions, translation, and rotation error separately.
4. Recheck the broad gable roof, roof orientation/overhang, wall height/story count, window spacing, and entry edge against those references. Keep dimensions marked estimated until a source supports them.
5. Reframe and relight the upper-room preview so the furniture, partitions, and floor are readable, or replace it with a clear review-only cutaway. Continue to label the room plan as schematic unless current plans/photos establish it.
6. Add a fresh-open validation record for the final asset and confirm stable object, collection, transform, and dependency behavior.

The exterior model is a plausible illustrative residence and its footprint construction is substantially grounded in the supplied GIS ring. The current packet does not establish that the above-grade design or interior represents the actual Alpha Phi building closely enough for a passing detailed-model grade.
