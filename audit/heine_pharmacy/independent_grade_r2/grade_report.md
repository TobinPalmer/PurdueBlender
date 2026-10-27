# Heine Pharmacy R2 independent grade

**Score: 8.5/10 — PASS**

Exact SHA-256: `962fe3572903061e9d590759118ea945b28d32c338a0a5f6b8ce40da18e7d9d7`

## Criteria

### Identity and source-backed footprint — 1.9/2.0

- Evidence: Official Purdue GIS layer 0, FID 606 names Robert E. Heine Pharmacy Building / RHPH.
- Evidence: Independent comparison of its 92-point WGS84 ring (using the documented approximate campus transform and bbox-center origin) with the saved shell’s 22-point base ring found maximum point-to-segment deviation 0.267 m GIS→shell and 0.000002 m shell→GIS. The GIS source supplies no survey date/tolerance, so the project CRS approximation remains a limitation.
- Finding: Identity and shell footprint are strongly supported. The small remaining deduction reflects the approximate transform and unsurveyed GIS tolerance.

### Position, orientation, and dimensions — 1.8/2.0

- Evidence: The current saved asset retains the documented campus placement origin [-193.84218632570293, 259.60496004008974] m and local GIS shell bounds [[-36.168739318847656, 36.168739318847656], [-33.99116516113281, 33.99116516113281], [-1.0, 22.0]] m. R2 fresh-open validation confirms `shell_geometry_preserved=true` and no origin/manifest edit.
- Evidence: The prior master-sync record verified this origin on the placement marker. R2 did not alter that origin, but an updated master fresh-open check is still due after coordinator sync.
- Finding: Local plan and campus anchor remain consistent with the GIS crosswalk. A fresh master-link check after the shared manifest count is corrected remains a coordinator integration step.

### Height, floors, and roof form — 1.25/2.0

- Evidence: Purdue OEP plan supports five above-grade floors plus a G-floor and basement; the model retains the five-level horizontal facade organization. The cited oblique photo supports a flat parapet and limited rooftop mechanical form.
- Evidence: Structural shell bounds retain Z [-1.0, 22.0] m; the asset’s penthouse/roof details raise total collection bounds to [-1.1799999475479126, 23.52248764038086] m. Absolute levels remain estimated. GIS attributes list 8 levels and roof value 61 with unresolved datum/units, conflicting with the OEP floor description.
- Finding: Five above-grade floors are source-supported, but exact absolute height, lower-level exposure, roof datum and mechanical penthouse dimensions remain unverified. Interior floor/room boundaries are deliberately schematic.

### Facade, entrances, and distinctive architecture — 1.8/2.0

- Evidence: Compared the R2 fresh-open render with the cited 2023-10-18 exterior photo: the selected elevation now has seven tall narrow glazing bays, two long glazed sections per bay, broad pale stone mid-panels, restrained rails, brick fields and horizontal pale courses. The render’s four large stone arches and five substantial piers span a substantial portion of that facade, matching the photo’s defining entrance composition.
- Evidence: The fresh-open validation reports 14 long glazing faces, 21 broad stone faces, 4 arches, 17.25 m portal width and 7.35 m portal top. No source elevation establishes exact opening sizes or arch dimensions.
- Finding: R2 resolves the R1 composition mismatch: window rhythm and arch scale read substantially closer to the one source elevation. Deduct slightly because the photo is oblique/partly occluded, exact dimensions and hidden elevations are unsupported, and the remaining facades are not validated against comparable images.

### Modular export, portability, and complete evidence — 1.75/2.0

- Evidence: Independent Blender 5.2.3 reopen found stable collection `Asset_heine_pharmacy`, 108 objects / 105 meshes and 18 used materials. The saved SHA matches the R2 verification record; no missing external texture path was found.
- Evidence: Evidence documents official GIS FID and transform, dated licensed source photo, official OEP floor/use evidence, uncertainties, R2 edits, and exact saved-file hash. Interior cues are explicitly labeled schematic in their object names and evidence.
- Finding: The shared manifest still has object_count=133 while the current export contains 108 objects. The asset retains the stable collection and is fresh-open portable; update manifest and run master-link verification during integration.
- Finding: No evidence of room-by-room interior accuracy is claimed; schematic labeling is appropriate.

## Overall findings

- Passes the independent 8/10 threshold for a detailed exterior asset.
- The main remaining limits are uncertainty in absolute height and unseen facades/interior. Shared manifest object count and fresh master-link verification remain coordinator-owned integration work.
