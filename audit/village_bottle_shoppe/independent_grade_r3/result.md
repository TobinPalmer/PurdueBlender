# Independent grade — Village Bottle Shoppe

**Score: 8.7/10 — pass**  
**Exact asset SHA-256:** `E5210EC34D7159932586D92059FDD010E4D235C5102898E13DF4EA797D155E83`  
**Blender:** 5.2.3 LTS; reopened directly from the saved asset.

## Score breakdown

| Category | Score | Findings |
| --- | ---: | --- |
| Site identity and source confidence | 8.5 | Official store information and Indiana FSSA support the 1832 Northwestern Ave location. The 2018 Indiana footprint `objectid=409442` is matched to that address. The 302 Vine St Hi ViNE appraisal photos are a different branch and were correctly excluded. The user-contributed exact-address photos are undated, and the raw photo-listing snapshot referenced in the audit is missing. |
| Footprint, orientation, and placement | 9.5 | All four projected GIS ring corners are within 0.000059 m of a mesh vertex. Computed polygon area is 472.920 m² and agrees with the asset's footprint property. Undocumented raw service area/perimeter values are correctly not used. Building height is estimated. |
| Massing and architectural details | 7.5 | The model is now a low commercial volume instead of the unsupported gabled house. The direct storefront photo supports the brick wall, tan masonry display bay, dark glazing, oversized red sign, and broad white fascia, all reflected in the model. A smaller exact-address photo appears to show a glazed entry on another elevation; the model omits it, and that photo's bearing is not documented, so placement should be verified before adding the door. Other elevations and roof construction remain inferred. |
| Materials and texturing | 8.3 | Eight portable node-based materials include procedural brick and block plus concrete, white fascia, aluminum, glass, roof membrane, and red sign lettering. The render reads as the documented materials; some procedural variation is subtle at overview scale. |
| Interior and evidence handling | 9.0 | No dependable floor plan was found. Leaving the interior unmodeled avoids inventing a layout. The separate Hi ViNE tenant interior is not used as evidence. |
| Blender integrity and portability | 9.8 | Exact saved file reopens in Blender 5.2.3 LTS with the stable scene/collection/object names intact. It contains 2,488 vertices and 1,866 faces, with zero non-manifold, boundary, or wire edges. No linked libraries or external image paths. |

**Weighted total: 8.7/10.**

## Independent fresh-open results

`fresh_open_probe.json` records the exact tested SHA. The asset reopened cleanly, retained only the expected mesh in its asset collection and scene, and has no external dependencies. I independently projected the four-corner GIS footprint with the conversion documented in `modular/AGENTS.md`; nearest mesh vertex errors were 0.000018–0.000059 m.

## Evidence and remaining limits

The exact-address photo confirms the shop sign and visible storefront treatment. The 2023 aerial helps verify the shallow roof outline; the 2018 footprint supports plan shape and placement. The raw source attributes `SHAPE__Area=817.718` and `SHAPE__Length=116.950` conflict with the projected ring measurements and have unknown units, so they remain unused. The smaller second photo suggests a glass entry on an adjacent wall, but does not establish its orientation; exact height, unseen elevations, and interior plan remain unverified.

The audit's README lists `google_business_photo_listing.html` as a preserved source snapshot, but it is absent from the supplied `sources/` folder. Keep that provenance limitation visible or add the snapshot before the next revision.

## Recommendation

The model passes the 8.0 threshold and can proceed to master integration. If a clearer, correctly oriented exact-address view becomes available, consider adding the side entry and capture the photo listing page in the audit.
