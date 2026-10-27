# BHEE completion pass, 2026-10-22

Asset: modular/buildings/electrical_engineering.blend; export Asset_electrical_engineering. Backup before.blend. Local frame and placement unchanged at campus origin [143.8499984741211,135]. Main structural outer wall polygon derives official FID292, source EPSG4326 converted with project x84810.60416539927,y111040 per degree. Main perimeter vertices retained; wall faces replaced with segmented spandrels/jambs and real openings. FID109 former18m stair projection removed and replaced low estimated entrance volume; its exact outline/height remains unresolved.

Changes: 4169 export objects (formerly5), perimeter windows/mullions/sills, limestone courses, triple portal, photo-supported dark cornice/red tile eave, first-floor laboratory benches/screens/scopes/seats, lounge tables/green chairs/carpet, partitions with door gaps, exposed beams/light bars, floor/roof slabs clipped to official polygon with inferred courtyard. Save and reopen passed. No external texture files; procedural materials portable. shader_overview.png rendered in Cycles; overview.png and interior_cutaway.png Workbench. Shader preview supports material visibility, not geometric fidelity.

Sources downloaded and viewed:
- Purdue2025 exterior: https://engineering.purdue.edu/ECE/News/2025/a-century-of-circuits-and-community-purdues-electrical-engineering-building-turns-100/bhee.jpg (facade.jpg), redbrick, limestone, tall dark window mullions, triple stone portal, tile eave.
- Purdue2024 completed-renovation article: https://engineering.purdue.edu/ECE/Wavelinks/2024/articles/max-w-and-maileen-brown-family-hall-of-electrical-engineering (article.html). Three photos downloaded; banner is interior despite generic alt text. Photos show actual labs/lounge, white exposed services, bench equipment, gray floor and green fabric/carpet.
- https://engineering.purdue.edu/ECE/Giving/BHEE/BHEE_First_Floor_Renovation.pdf (renovation.pdf, plan_0/1.png). Proposal explicitly subject to change; used as inferred functional layout, not as-built certification.
- GoogleMaps queried by parent: BHEE pin40.4288777,-86.9117698; place identity corroboration only, gallery ambiguous with MSEE. No false StreetView claim.
- Official footprint cache audit/official_building_references.json source Purdue ArcGIS BuildingShapesZip4 FeatureServer0; retrieved2026-10-22. Source date/precision unknown.

Remaining: exact bay count/positions, courtyard dimensions and glazing, roof geometry, heights18m (estimate), room locations, stairs/upperfloor interiors, full facade inscription and accessibility need stronger plans/photos. Uniform bays are estimated and not a faithful surveyed reconstruction. Interior illustrates documented first-floor functions, not complete as-built interior. Child independent review score5.2/10 before final technical fixes, no9/10 claim. Final source and fidelity limitations prevent honest 9/10. No master or shared manifest edits.

## 2026-10-27 source reconciliation and rebuild

The previous independent score of 6.0/10 remains the historical score for the earlier asset. This revision addresses the largest source-backed gaps and needs a fresh independent grade before any new score is claimed.

### Reconciled geometry and facade work

- Added both Purdue campus GIS BHEE components, FID 292 and FID 109, as separate parts of the named local-coordinate asset. Both feature rings now generate perimeter walls and clipped floor/roof plates; the former small generic entrance placeholder is removed. Neither component was rescaled. The source polygons have no published survey accuracy/date, and FID 109's height remains estimated.
- Rebuilt courtyard elevations from opening modules, brick piers, glazing, sills and limestone courses instead of opaque 13.6 m blank wall blocks. Courtyard bay spacing remains estimated because no as-built courtyard elevation was found.
- Moved the three portal composition and engraved “ELECTRICAL ENGINEERING” band to the south facade segment identified by the source polygon and the Purdue 2025 facade photograph. The 2025 photo also supports red brick, limestone, dark window frames, cornice and the red-tile eave. Portal spacing and most other facade rhythms remain estimates from a single elevation photo.
- Increased facade window width and spacing to better match the visible scale in Purdue's exterior reference.
- First-floor lab and lounge equipment is retained. Purdue's 2013 building emergency plan supports five floor designations (basement, ground, first, second, third) plus attic, and the Duncan Annex's office/research-lab use. It does not provide measured facade height. The 18 m geometry and all upper levels remain estimates.

### Saved evidence and validation

- `source_evidence.json` records feature IDs, project transform, official links, retrieved/local evidence, and uncertainty.
- `electrical_engineering_bep.pdf` is the locally saved Purdue 2013 life-safety source. The 2024 renovation article/photos and proposed first-floor plan remain in this building-specific folder; the proposal is not treated as as-built evidence.
- `overview_20261027.png`, `front_facade_20261027.png`, and `interior_cutaway_20261027.png` are regenerated Workbench review views. `shader_overview_20261027.png` is a lit Cycles facade/material view. `render.py` can reproduce all four. `build.py` regenerates the modular asset from the current detailed file and the official footprint cache.
- Fresh-open and portability checks are in `check.json`. No external image files are referenced by the asset.

The full roof silhouette, exact height, feature 109's vertical form, facade treatment on unphotographed sides, floor-by-floor as-built interiors, and complete stair/accessibility network remain unresolved. That earlier assessment is superseded by the accepted independent R2 grade documented below.


## 2026-10-27 independent grade and master integration

Independent R2 review scored the frozen asset 8.3/10 at SHA-256 `535ff224bd0105389a2fea01c5542e219d48716ad6089b173a42efbe0a7b4612`; see `audit/electrical_engineering_independent_grade_r2/result.json`. Both official GIS footprint components (FID 292 and FID 109) match source extents. Four above-grade floors follow the plan designations; total height, full roof silhouette, upper-floor interiors, and unphotographed facade details remain partly estimated or unverified. The coordinator refreshed the master library link and bounds; a fresh-open integration audit is recorded in `audit/master_integration_2026-10-27_r2.json`.
