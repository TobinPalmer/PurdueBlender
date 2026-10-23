# Potter Engineering Center — Independent Round 3 Review

**Reviewed asset:** `modular/buildings/potter_engineering.blend`  
**Review date:** 2026-10-23  
**Independent score:** **6.7/10** (up from 6.3/10; improved stairwell depiction, still well short of 9/10)

## Review scope and method

I inspected `stairwell_cutaway.png`, `exterior_current.png`, and `facade_detail_current.png`, then opened the saved asset in a fresh headless Blender 5.2.3 process. I checked its object collection/root, stair object extents, slab objects and the provided ray-check evidence. I made no edits to the blend file.

## What improved

- Round 3 adds visible handrails and Boolean openings in the three upper floor slabs and the penthouse-level slab. The stairwell cutaway now reads as paired flights with landings passing through these apertures, a useful improvement over flights ending at solid slabs.
- The saved file reopens in Blender 5.2.3. `Asset_potter_engineering` contains 500 objects; `AssetRoot_potter_engineering` remains at `(0, 0, 0)`. The structural envelope remains approximately 58.4515 × 67.4320 m in XY and 13.4112 m high. No missing file-backed image dependencies were reported.
- Three stair cores and four modeled transitions per core are present (24 flight objects total). The source basis remains the 2016 existing-plan stair labels S01–S03. A roof-level T-shaped Room 401 mass remains based on the historic plan and its labeled 3,547 sf area.
- The facade close view still shows distinct brick, pale precast, window frames and projecting shades. The broad envelope and root are stable, preserving the intended asset placement frame.

## Remaining issues

### Stair continuity is only partially demonstrated

The cutaway is a strong improvement, but its bottom flight begins below the first occupied-floor slab without a corresponding opening in the basement slab (`POTR_Interior_Slab_Level_0_EstimatedElevation`). The build script explicitly omitted that opening pending reconciliation with the basement plan. So the basement-to-first-floor transition is not shown as a continuous passage into the basement. No doorways or connected surrounding corridors are modeled, and there is no elevator shaft. The three core centers, 4.6 × 3.6 m aperture sizes, tread sizes, landing sizes and repeated stair positions are estimates; the 2016 plans establish core labels/approximate locations, not those dimensions or the exact same configuration at every level.

The supplied ray checks test only whether one vertical ray at each core center hits each slab. They show a clear center point, not the full opening perimeter, stair-to-opening clearance, landing-to-corridor access, or a walkable route. The cutaway image supports visual continuity through upper levels, but it is an isolated explanatory crop rather than a building circulation check. Do not treat the stairs as verified or code-compliant.

### Roof profile and overall exterior still need work

The full exterior render remains dominated by an untextured light-gray roof slab spanning the whole footprint. The historic penthouse reads as a low raised T-shaped patch on that roof, but its exact alignment and height remain approximate. No dated, orientation-known roof imagery or measured roof plan is cited. The newly cut roof apertures and some white rail-like forms are visible from the exterior, which makes those unverified stair elements read as rooftop projections. The roof membrane still needs a more convincing material and a clearer reconciliation with the penthouse mass.

Facade texture and frames help, but the close view is still a highly regular repeated bay: small dark windows, uniform pale panels and brick piers repeat with little elevation-specific variation. The available references do not establish the exact facing direction or panel-by-panel distribution. The full exterior remains an isolated studio view without neighboring context or a verifiable entry composition.

### Interior and evidence record

The model still contains raster-derived historic partition meshes with reported dense, overlapping/fragmentary geometry. Room 205 is a small historical vignette only; current Purdue material cited by the asset report does not verify it as current. The project still lacks a connected, currently verified interior plan, doors, corridors, elevator, or program details. The 2016 plans must remain labeled historic and separate from the 2026–28 renovation concepts.

The round-3 evidence is ahead of the written report: `stairwell_checks.json` and the new cutaway show openings/rails, but `REPORT.md` still describes round 2 and says openings and rails are absent, calls `stair_core_current.png` the relevant image, and says the round-2 review is pending. The report should be brought into sync before the asset is presented as round 3. Also, the roof plate is a zero-thickness T-shaped mesh (which may be suitable as a surface, but is not a modeled roof assembly).

## Scorecard

| Category | Score / 10 | Reason |
|---|---:|---|
| Footprint, placement and massing | 7.0 | XY dimensions/root are stable; penthouse is a historic-plan estimate, not an independently re-registered surveyed outline. |
| Exterior form and facade fidelity | 5.8 | Recognizable material vocabulary and rounded tower; repetitive elevations and no verified entrance composition. |
| Materials and surface detail | 6.6 | Brick/precast/glazing are more legible; roof remains broad and featureless, glazing very dark. |
| Interior completeness and circulation | 5.4 | Upper slab openings, rails and paired flights improve the cutaway; basement transition and surrounding circulation remain disconnected/unverified. |
| Architectural details and rooftop | 6.3 | Historic penthouse cue is useful, but roof treatment and relation to openings/projections remain unresolved. |
| Technical health and modular export | 9.0 | Fresh Blender reopen, stable root and collection, no missing image dependencies. |
| Evidence and source discipline | 8.0 | Historic/current/future distinction is mostly clear; report is stale against round-3 checks and key placements/dimensions are estimates. |

**Overall: 6.7/10**

## Highest-impact next steps

1. Reconcile the basement stair location against the basement plan, then model a supported basement aperture and landing, or explicitly show the basement stair termination as unknown. Inspect aperture perimeters and stair/landing overlaps rather than relying on center-point rays alone.
2. Update `REPORT.md` to accurately describe the new stair openings/rails and cite the round-3 evidence. Keep the approximate dimensions and historic-plan basis explicit.
3. Improve the roof surface and clarify whether the T-shaped mass is a penthouse, while retaining its historic-plan and registration caveats. Remove or resolve stair/rail forms that protrude above roof surfaces unless evidence supports them.
4. Obtain current, connected interior/egress information and orientation-known, dated exterior imagery before claiming complete circulation or elevation-specific facade accuracy. Keep Room 205 historical and any future renovation work separate.

## Fresh-reopen evidence

- Blender 5.2.3 LTS reopened the saved blend successfully.
- Collection `Asset_potter_engineering`: 500 objects; root `(0, 0, 0)`.
- Structural envelope XY dimensions: approximately `58.4515 × 67.4320 m`.
- Round-3 check file reports 24 stair flights, 12 handrail objects, clear center-ray checks for 12 upper slab/roof apertures, and no missing external images. These checks do not establish full clearance or a connected building route.
- Basement slab was not included in those 12 aperture checks. The build script says its opening is omitted, so the lowest stair transition remains incomplete.
