# Independent R8 grade — Morgan J. Burke Boilermaker Aquatic Center

**Score: 7.9/10 — below the 8/10 completion threshold.**

## Asset and validation reviewed

- Source: `modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend`
- SHA-256: `eec37c28a65fc0c3d48feea6791bb4bbe92b0f218a4f8099689abca078b6aa9a`
- The calculated source-file SHA-256 matches `validation_r8.json`, `evidence_r8.json`, and `asset_sha256_r8.txt`.
- Blender 5.2.3 reopen validation reports 1,080 total asset objects, 96 R8 additions, 70 GIS ring vertices and 70 shell segments, material assignments, and zero external image dependencies. The reported bidirectional 2 μm comparison is a local outline correspondence only; it does not establish survey accuracy or master registration.
- Reviewed all four R8 renders: interior lighting/banners, bleacher aisle, north entry, and facade reveals.

## Rubric

| Criterion | Score | Assessment |
|---|---:|---|
| Correct identity and source-backed footprint | 1.9/2 | Purdue GIS feature 896 and building-specific project references support the identity. The model shell follows the local GIS ring closely. The GIS perimeter is not a surveyed wall line. |
| Position, orientation, and scale | 1.6/2 | The manifest has a local-coordinate placement origin and the local outline matches the feature. This revision’s evidence does not independently report the MJB master marker’s transform against that origin, so exact campus placement remains unverified here. |
| Evidence-backed height, floors, and roof form | 0.9/2 | The building reads as a tall natatorium and has a roof/truss system, but no measured roof section, eave/ridge elevations, or as-built truss geometry supports the modeled profile or dimensions. The review views do not resolve this gap. |
| Facade, entrance, and distinctive features | 1.7/2 | The model communicates the brick shell, ribbon glazing, north entrance/canopy, signage, and pool-hall character. R8’s glazing reveals add depth. Long wall areas and repeated bays still appear schematic, and the exact facade opening schedule is not measured. |
| Modular export, portability, and evidence | 1.8/2 | The stable asset path and collection remain intact; the file reopens, materials are assigned, and images are packed or procedural. Evidence clearly records sources and uncertainty. The independent placement check remains outstanding. |
| **Total** | **7.9/10** | **Does not pass.** |

## R8 changes recognized

The continuous aluminum tier banks and central aisle replace the previous block-like seating; the wall-mounted panels replace floating banners; and elongated diffusers plus area lights make the lighting more legible. These are meaningful improvements supported qualitatively by the Arsee Engineers project photo and Huston Electric’s documentation of the Aquatic Center LED installation. The exact seating layout, aisle rails, banner dimensions/positions, and fixture schedule remain estimates.

The interior images still hide the roof structure and read as a broad flat ceiling. The source photo shows exposed trusses; a review view that reveals the model’s existing trusses over the pool and seating would provide a stronger feature comparison. The current seats also read mostly as repeated flat plates, and the rails are thin and visually disconnected in places. These issues keep the image-level interior match short of a confident pass.

## Highest-value next work

1. Produce an interior review view with the ceiling/roof cutaway arranged to show the modeled trusses, long fixtures, wall panels, pool, and seating together; confirm the saved model—not only the render setup—contains that structure.
2. Refine the aluminum tiers and aisle handrails so the seating reads as connected bleachers with a continuous accessible stair/aisle route.
3. Have the coordinator verify `Placement_morgan_j_burke_boilermaker_aquatic_center` against the manifest origin and record that specific transform. This cannot be inferred from the local FID 896 outline test.
4. Keep the roof profile and height labeled unverified unless a measured section or elevation is found; do not invent dimensions to raise the score.

## Evidence references

- Arsee Engineers project page identifies the Aquatic Center project and links its facility photo: https://www.arsee-engineers.com/project-athletic.html
- Huston Electric describes the Aquatic Center LED installation: https://hustonelectric.com/huston-dives-in-to-help-on-purdue-aquatic-center/
- Purdue Athletics facility page/search result describes the facility’s program, name, and photo gallery: https://purduesports.com/facilities/morgan-j.-burke-aquatic-center/12
- Full R8 evidence and uncertainty record: `evidence_r8.json`; source render review in the four R8 PNGs named there.

The grade applies to this saved R8 hash. It does not certify the master placement or exact roof/height accuracy.
