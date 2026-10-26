# Tarkington Hall independent regrade R3

**Score: 7.2/10 — below the 8/10 threshold**

Canonical SHA-256: `825d57329797fd45b6eb7784c8a6011f99a575bed6a97c11ed06e098eb618ee1`

## Criteria

### Correct identity and source-backed footprint — 1.5/2.0

The official Purdue GIS snapshot is FID 662/code TARK; the 2023 Indiana ortho overlay agrees on the characteristic four-arm residence-hall form. Fresh export-only shell extraction yields IoU 0.688, mean symmetric boundary residual 2.10 m, P95 9.37 m, and Hausdorff 11.34 m. The footprint now includes the two connector shell groups. The central/core perimeter and selected shell proxy still diverge materially. The GIS perimeter is not documented as surveyed wall faces; the orthophoto comparison may represent roof edges.

### Position, orientation, and scale/dimensions — 1.2/2.0

On the same local GIS transform, the export-shell centroid is offset -0.25 m east-west and 0.66 m north-south (0.71 m resultant); plan bounds are broadly similar. The independent asset reopen verifies the root transform is identity, but the campus Placement_tarkington_hall marker is outside this building library and was not checked in this pass, so campus position/orientation remain unverified here. GIS-to-local conversion is approximate; no surveyed wall dimensions were found.

### Evidence-backed height, floors, and roof form — 1.3/2.0

The model has four occupied floors and a flat-roof, four-wing massing with roof penthouses/equipment. Purdue’s current emergency plan identifies East and West wings with four floors each and central lounge, reception, dining/kitchen, study/recreation, mail, laundry, linen, mechanical, and staff uses. The reopened asset bounds reach 19.1 m, but the public material reviewed provides no measured building elevation; roof/penthouse heights and parts of the core remain modeled estimates. Orthophoto/GIS residuals include outliers above 9 m.

### Facade, entrances, and distinctive architecture — 1.6/2.0

The exterior render reads as a brick residence hall with four wings, repetitive window bays, light horizontal bands, roof masses, and a central entrance. R3 connector forms are now included in the actual export, correcting a major omission in R2. The facade treatment remains highly repetitive and simplified, with limited entrance articulation and no detailed representation of the verified central uses. The one available room cutaway has beds/desks but sparse finishes and little room-specific detailing; no representative central lounge/dining or typical full-floor interior is evidenced.

### Modular export, portability, and complete evidence — 1.6/2.0

Fresh Blender 5.2.3 LTS reopened the exact canonical SHA. Asset_tarkington_hall contains all 910 expected objects/891 meshes, including all 96 connector meshes (48 each side), all connector objects are linked only to the asset collection and parented to the identity root, and no duplicate names, nonfinite vertices, materialless meshes, invalid material indices, missing external images, or foreign linked libraries were found. Sixteen used materials are present. Source snapshots, exterior/room renders, and footprint overlays exist; evidence remains limited for campus marker transform, measured elevations, and the interior program.

## Independently recomputed export-only metrics

- Shell objects: 35
- Polygon IoU: 0.687638
- Mean symmetric boundary residual: 2.102 m
- P95 residual: 9.372 m
- Hausdorff: 11.341 m
- Shell centroid offset: -0.252 m east-west, 0.659 m north-south

## Findings

- **High:** Footprint agreement is improved but still not acceptance-grade for a faithful footprint: IoU 0.688; mean residual 2.10 m; P95 9.37 m; Hausdorff 11.34 m. Inspect the central core and wing endings against the ortho while retaining uncertainty about whether the GIS boundary is a roof or wall edge.
- **High:** Verify the canonical master Placement_tarkington_hall marker, linked asset orientation, and site position in a read-only master check; that transform is not stored in this building asset and is not proven by the local shell-to-GIS centroid comparison.
- **Medium:** Improve façade and interior evidence beyond one simplified dorm-room cutaway. Model recognizable central lounge/dining/reception/common functions and provide a typical room/floor view using the official program as evidence.
- **Medium:** Document reliable height/floor-elevation sources or clearly keep the 19.1 m roof height and roof-top masses labeled as estimates.

## Evidence inspected

- `independent_reopen_r3.json` and `independent_reopen_r3.log` (fresh Blender 5.2.3 process).
- `independent_shell_vertices_r3.json` (fresh export-collection-only geometry extraction).
- `independent_footprint_r3.json` (new computation from the saved GIS feature and extracted vertices).
- `ortho_footprint_overlay_r2.png`, `exterior_r2.png`, and `room_r6.png`.
- `refinement_r2.md`, `AGENT.md`, official Purdue housing page, and official emergency plan.
