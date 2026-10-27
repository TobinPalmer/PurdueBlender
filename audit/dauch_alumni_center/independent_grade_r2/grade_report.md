# Independent grade — Dauch Alumni Center r2

**Score: 7.65/10 — below the 8.0 passing threshold.** The frozen asset SHA matched exactly: `f110473f7d30b3e3e01072e3c4ed0287d5c36eaa720e25cd2eaaad7ffd649bda`. I opened the file in a separate Blender 5.2.3 LTS process, checked the expected collection and local coordinate placement, reviewed the overview/sign-detail renders, and compared them with the cited Purdue/GIS/Archives records.

## Rubric

| Criterion | Score | Finding |
|---|---:|---|
| Correct identity and source-backed footprint | 2.00/2.00 | Purdue GIS FID 71 and address 403 W Wood Street match; all 109 unique perimeter vertices reproduce within 0.0000015 m. |
| Position, orientation, and scale/dimensions | 1.80/2.00 | Manifest origin matches GIS polygon centroid within 1e-11 m. Decorative bounds are stale and the facade photo bearing is not survey-registered. |
| Evidence-backed height, floors, and roof form | 0.90/2.00 | Official Purdue database says three-story while GIS says four levels; the model uses four levels and a flat, strongly striped roof. Shell side normals point inward. |
| Facade, entrances, and distinctive architecture | 1.40/2.00 | Brick/glass frontage, glazed entrance, flagpoles, and new freestanding sign are recognizable; window rhythm, roof appearance, and low-poly planting remain stylized. |
| Modular export, portability, and complete evidence | 1.55/2.00 | Expected local collection opens with portable materials and no image dependencies. Evidence is clear about estimates and schematic interiors, but manifest extents need updating and shell winding needs correction. |

## Fresh-open and geometry checks

- Blender version: 5.2.3 LTS. Scene `Scene` and collection `Asset_dauch_alumni_center` loaded. The collection contains 663 objects (659 meshes).
- Exact asset SHA-256: `f110473f7d30b3e3e01072e3c4ed0287d5c36eaa720e25cd2eaaad7ffd649bda` (374,858 bytes).
- Purdue BuildingShapes feature FID 71 identifies the Dick & Sandy Dauch Alumni Center at 403 W Wood Street. The GIS outer ring has 109 unique vertices; the exported shell has 109 unique XY positions. Independent nearest-point comparison gives maximum error **0.00000146 m** and RMS error **0.00000072 m**.
- The manifest placement origin `[241.198987, -618.185206] m` matches the independently computed GIS polygon centroid within 0.00000000001 m. The shell local bounds are X `-30.669..29.726`, Y `-19.687..16.850`, Z `0.35..14.40 m`.
- The shell is topologically closed (218 vertices, 327 edges, 111 faces; zero boundary, nonmanifold, or zero-area faces), but the signed volume is **-8437.89 m³**. Face inspection finds all 109 vertical side faces point inward, while the upper cap points up and the lower cap points down. Recalculate the side-face winding and verify the signed volume afterward.
- There are 29 used node-based materials and no external image dependencies or zero-area faces across the collection.
- Manifest full-asset bounds are stale. The current asset reaches local Y `-25.125 m`, while the manifest says `-23.530 m`; adding the placement origin makes the actual south bound 1.595 m farther south than recorded. This aligns with the new sign/plant geometry and does not move the structural shell.

## Reference comparison and remaining uncertainty

Purdue’s Campus Facilities and Buildings Historic Database describes the center as a three-story brick building with glass accents, built 2004–present, with 69,154 gross square feet. Purdue for Life identifies the current alumni-center use/address and references the building-specific exterior photo. The Home of Purdue listing provides another building-specific exterior view. The new model sign and approach planting respond to those images and the sign-detail preview makes the two-line lettering readable.

The model’s roof appears as a large flat pink-striped plane, unlike the curved roofline recorded from the cited building photo. Story evidence conflicts: GIS `NUM_LEVELS=4`, while Purdue’s historic database says three stories; no measured section or height source resolves it. The Archives UA 137 finding aid says a floorplan is in the collection, but this revision did not retrieve it, so the interior remains appropriately labeled schematic rather than as-built.

The complete evaluator and machine-readable evidence are in `result.json` and `fresh_open_findings.json`; scripts and Blender log are `evaluate.py`, `inspect_asset.py`, and `blender_fresh_open.log`.

## Required revisions to reach a pass

1. Reverse the winding of the 109 GIS shell side faces so they are outward-facing and consistent with both caps; confirm with fresh-open normal checks and positive signed volume.
2. Resolve or clearly preserve the three-story/four-level conflict, and reshape the roof silhouette/material to match the cited curved roofline evidence. Continue to label unmeasured heights as estimates.
3. Update the manifest’s complete local/world asset bounds to include the new southward sign/plant extents; keep the centroid placement origin unchanged.
4. Keep the public-facing sign and context, but reduce the faceted shrub appearance if another visual pass is made.
