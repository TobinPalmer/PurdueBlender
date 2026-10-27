# Independent grade: Gemini Cooperative House (FID 825)

**Verdict: 7.0/10 — below the 8/10 acceptance threshold.**  
**Reviewed asset:** `modular/buildings/massing_gemini_cooperative_fid825.blend`  
**SHA-256:** `c9cf72b41dc43d919d0dea0c3740bf164c7411897d4857f7bd1f43b6978cc547` (matches the requested revision)

## Category scores

| Category | Score | Assessment |
|---|---:|---|
| Identity, site, and footprint | 1.9/2.0 | FID 825 is Gemini Cooperative at 172 Littleton St. Model slab ring and GIS ring have 14 vertices and approximately 0.99999996 intersection-over-union. This is a strong site-outline match; it does not independently certify master-file placement or exact wall-to-footprint alignment. |
| Massing and story form | 1.4/2.0 | Broad three-level house mass is plausible, with stepped outline. The model reads as a long, regular bar in the supplied view, while the reference photo shows distinct wings and offsets. Overall height is an estimate, not a surveyed value. |
| Facade and entrance | 1.2/2.0 | Brick lower level, light horizontal siding, dark window frames, and warm roof color broadly match the photo. The model has a repetitive window grid and largely uninterrupted lower brick wall; the photo has varied opening sizes and locations, and a substantial central covered entry with brick piers, landing, and railings. The model entry is too small and simplified. |
| Roof and silhouette | 0.8/2.0 | This is the largest visual mismatch. The photo shows multiple intersecting roof sections, prominent front-facing gables, varied dormers, and several changes in eave/ridge height. The model has a mostly continuous broad roof plane, four evenly spaced small dormers, and weak wing/gable articulation. Three chimney elements help, but do not recover the silhouette. |
| Schematic interior, portability, and evidence | 1.7/2.0 | An independent Blender 5.2.3 reopen found the expected scene and collection, 809 mesh objects, ten named materials, no material-less meshes, no linked libraries, and no unpacked external images. Named corridor partitions, floor plates, kitchen island, dining table, and computer-room desk support a usable schematic interior. The interior is explicitly representative rather than a verified floor plan, and furnishing/layout fidelity remains unproven. |
| **Total** | **7.0/10** | **Below threshold** |

## Source-backed observations and estimates

- **Identity/address (source-backed):** the raw Purdue GIS feature is FID 825, name `Gemini`, owner `COOP`, address `172 Littleton St`. The current official exterior image visibly identifies “Gemini” and “172 Littleton”; the official house site and Purdue BoilerLink listing provide independent identity/address cross-checks.
- **Footprint (source-backed with conversion caveat):** the raw GIS footprint is 14 vertices with area approximately 492.643 m² in the project’s approximate local conversion. The asset’s lower slab ring reproduces that outline within numerical precision. GIS imagery overlap and under-roof wall offsets are not independently resolved.
- **Visible levels (photo interpretation):** the official exterior photo appears to show a brick ground floor, a full siding-clad floor, and an upper attic/third level expressed by gables and dormers. This is a visual estimate from one oblique image, not a measured floor count.
- **GIS floor field conflict:** the raw GIS record reports `NUM_LEVELS=1` and `CountOfFLO=1`, in conflict with the three apparent visible levels in the official photo. The field’s semantics are unclear here; it could represent an incomplete/categorical GIS attribute. It should be retained as a source conflict and must not be treated as evidence that the photo-visible upper levels do not exist. Conversely, the photo alone does not prove three full-height interior storeys.
- **Dimensions and interior:** the asset’s 11.15 m ridge height, story count, window positions, roof geometry, and room partitions are estimates. The source evidence does not include a measured elevation or floor plan.

## Changes needed to reach 8/10

1. Break the long roof into photo-supported wings with distinct gables, valleys/intersections, eave levels, and dormer sizes/positions. Keep these changes constrained by the existing GIS footprint and mark uncertain roof details as estimated.
2. Replace the uniformly spaced dormer/window rhythm with the asymmetry and size variation visible in the official photo; add the recognizable front-facing gables.
3. Rework the main front entry as a broad, covered porch/portico with the central brick piers, landing, and visible railings; align its position and width to the photo.
4. Add appropriately placed windows to the lower brick story and vary the facade openings by wing instead of leaving a blank continuous brick band and regular grid.
5. Keep the interior clearly labeled schematic; a cutaway or floor-by-floor inspection view would make the included partitions/common spaces verifiable without implying an as-built plan.

## Evidence files and sources

- Official photo reviewed: [`../official_home_exterior.jpg`](../official_home_exterior.jpg), sourced from [Gemini Cooperative official site](https://www.geminicooperative.com/about) (Wix CDN image URL recorded in `audit/gemini/asset_evidence.json`).
- GIS feature: `audit/gemini/fid825.geojson`; project crosswalk and transformation notes: `audit/gemini/asset_evidence.json`.
- Fresh-open audit: [`fresh_open_probe.json`](fresh_open_probe.json), Blender log: [`fresh_open.log`](fresh_open.log).
- Slab polygon extracted from the independently reopened asset: [`slab_ring.json`](slab_ring.json); extraction log: [`slab_ring.log`](slab_ring.log).
- This is an independent visual/structural review of the identified asset revision. It does not grade the full campus scene or prove how a downstream master file links or positions the asset.
