# Independent review: Zundo Family Dentistry R1

**Overall score: 7.6/10 — below the project's 8.0 completion threshold.**

**Reviewed file:** `modular/buildings/zundo_family_dentistry.blend`  
**Review date:** 2026-10-26  
**Review method:** Opened the candidate directly in Blender 5.2.3 in a clean background session, inspected the export collection and material assignments, and reviewed the supplied exterior and interior renders, build metrics, validation report, raw OSM snapshot, and source record. The candidate reopened with 148 objects in the export collection, 147 meshes, and 13 materials used by exported objects. The preview site context is separated from the export collection.

## Category scores

| Category | Score | Findings |
| --- | ---: | --- |
| Identity, source-backed footprint, and coordinate readiness | 9.0/10 | The address is supported by the practice's official location page; OSM way 887558318 identifies the same address and provides an eight-vertex footprint. The candidate's shell is constructed from the transformed ring, and the documented local origin is reproducible with the project approximation. GIS/OSM geometry is not a surveyed wall line; exact entrance and facade layout remain uncertain. Master placement has not yet been independently checked. |
| Exterior form and architectural detail | 6.8/10 | The low, light-colored, single-story profile is consistent with the limited street-level description. The L-shaped/notched plan and parapet establish a plausible massing. The render reads as a generic box: facade articulation is very sparse, windows are dark rectangular panels with repeated frames, and the entry is difficult to distinguish. The context trees obscure some views, and the sign is not legible at the shown scale. Height, roof, and facade arrangement are estimates rather than measured facts. |
| Materials and surface treatment | 7.2/10 | The candidate uses local procedural materials for stucco, roof membrane, concrete, glazing, metal, and interior finishes, with no external texture dependency. These are appropriately restrained but render almost uniformly smooth; the wall and roof surfaces lack visible scale-specific texture and the glazing reads nearly black. |
| Interior completeness and readability | 6.0/10 | The roof-off image shows a reception zone, corridor, four treatment bays, chairs, carts, and basic partitions. This is a useful schematic fit-out, but it lacks evidence-backed room organization, doors, detailed cabinetry, sinks, instruments, lighting, and convincing chair/equipment forms. The top-down presentation also has heavy shadows and the interior reads as a sparse blockout. No source floor plan or interior photographs were found, so the layout must remain explicitly schematic. |
| File health, organization, and portability | 8.8/10 | Stable export collection retained, clean reopen passes, material assignments are present, and preview-only ground and trees are outside the export collection. The collection is organized by named elements. |

Weighted overall score: 7.6/10 (source/footprint 25%, exterior form 30%, materials 15%, interior 15%, file health 15%).

## Changes needed for 8/10

1. Make the street-facing entry unmistakable with a recessed or projecting doorway, door glazing/frame, accessible approach, and a composition that matches the available street-level view. Reposition the preview camera and trees so they do not hide the facade or the practice sign.
2. Add facade-specific articulation supported by a closer source image if one can be found: varied window widths/heights and spacing, visible wall returns/reveals, and trim that makes the low office read as an actual dental practice rather than a plain shell. Keep uncertain details labeled as inferred.
3. Improve visible material response with subtle, appropriately scaled stucco/paint, roof, sidewalk, and concrete variation. Lift the glazing from near-black to readable blue-gray reflections; confirm procedural textures are visible in the final lighting.
4. Refine the schematic interior for legibility: add door openings/doors, reception casework and waiting seats with more shape, treatment-chair headrests/arms, operatory cabinets and sinks, and practical ceiling/task lights. Keep the schematic disclaimer because no plan evidence supports exact room locations.
5. Provide a clear street-level front view and one side/rear view in the evidence set, plus a bright roof-off interior view. Current renders show only one exterior angle and a dim top-down plan.

## Evidence limits

The official page supports the address and practice identity, not architecture. The OSM snapshot supports a mapped footprint and approximate site location, not surveyed wall faces. The source record states the Google Maps preview appears low, light-colored, elongated, and one-storey-looking; no capture date was visible. The candidate's 3.9 m roof height, exact facade openings, sign placement, and interior layout are estimated or schematic. Do not report them as measured.
