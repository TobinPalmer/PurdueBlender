# Niswonger Aviation Technology — independent grade R3

**Score: 7.8/10** (five categories, 0–2 points each)  
**Asset SHA-256:** `4bf95e846ffe3c66b6479f7975d8f218a1cba8bf6f2949b688f6618777d1853b`  
**Master:** `purdue_campus_master.blend`

## Reopen and integration checks

- Opened the asset in a fresh Blender 5.2.3 background process and matched its SHA-256 to the requested digest.
- The `Asset_niswonger_aviation_tech` collection contains 2,300 objects, including 2,214 meshes. Its object-name set matches all 2,300 names in `modular/manifest.json` exactly.
- Mesh bounds match the manifest local building bounds exactly: X `[-50, 50] m`, Y `[-65.5, 65.5] m`, Z `[-0.15, 10.200645 m]`. The wider all-object bounds include cameras and lights; the manifest bounds describe the building mesh envelope. Those camera/light outliers are documented separately in `bounds_outliers_r3.json`.
- No mesh is missing a material, and the asset has no external image-file dependencies.
- The master contains the linked asset collection and a `Placement_niswonger_aviation_tech` instance at `(-1325, -1229.5, 0) m`, with zero rotation and unit scale. This translates the local footprint to the manifest's expected world XY bounds.
- Both R2 wing roof plates and the separate `NISW_Photographic_Sloping_Roof` are present. The two R2 additions have the `NISW_Roof_Membrane` material. Hangar aircraft, roof trusses and the sloping roof object remain in the asset.

## Score rationale

| Category | Score | Evidence and limits |
|---|---:|---|
| Identity and footprint | 1.8/2 | Correct footprint bounds and recognizable aviation-building composition; precise roof extent is not confirmed by a plan. |
| Position and scale | 2.0/2 | Master collection link and placement transform agree exactly with the manifest. |
| Roof and levels | 1.2/2 | Two wings are closed and the glazed sloping roof is retained, but the new roof plates are minimal slabs sized from modeled wall tops. Photos support enclosed roofed spaces, not exact roof dimensions or detailing. |
| Distinctive exterior | 1.5/2 | Brick, glazing, sloped glazed volume and hangar features appear in the model; the new broad roof planes remain generic. |
| Interior, materials, export and evidence | 1.3/2 | Detailed room/hangar inventory, material on all meshes, no external image dependencies, and six project photos plus a render are available. Roof material/detailing and source validation are limited. |
| **Total** | **7.8/10** | |

## Concrete remaining gaps

1. Verify both added roof footprints and elevations against an as-built roof plan, aerial imagery, or current roof photographs. Current extents are explicitly approximate.
2. Add roof-specific form and detailing where supported by sources (parapets, drainage falls, curbs, skylights or mechanical units); do not infer these solely from interior photographs.
3. Review the new roof plates from exterior viewpoints for edge alignment and how they meet the existing glazed connector and Hangar 1 roof.
4. Capture a fresh close exterior render from the source-photo side and compare the brick, glass, mullions and roof silhouette directly with exterior references.

## Reopen evidence files

- `independent_reopen_r3.json` — exact asset inventory, manifest-name comparison, root, materials, roof objects, and master collection placement.
- `bounds_outliers_r3.json` — mesh bounds and non-building camera/light outliers.
- `exterior_after_roof_r2.png` — available project render inspected for this review.
- `msktd_project_1.jpg` through `msktd_project_6.jpg` — supplied MSKTD project reference photographs inspected for this review.
