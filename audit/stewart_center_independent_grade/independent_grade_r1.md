# Stewart Center independent grade — R1

**Score: 6.9/10 — below the 8/10 pass threshold.**  
**Asset verified:** `modular/buildings/stewart_center.blend`  
**SHA-256:** `a3d7e9aba5cf2d32aa0aef5d458dfb6225841126c6a43c272bb60011fe310249`  
**Fresh Blender reopen:** 1,940 collection objects, including 1,927 meshes.

This is a new independent grade of the remediated file. The prior 6.0/10 pre-remediation scorecard is preserved as historical context only; it did not determine this result.

| Criterion | Score | Evidence and assessment |
|---|---:|---|
| Identity and GIS footprint fidelity | 1.8/2 | Purdue GIS OBJECTID 615 identifies Stewart Center. The 52 structural wall segments closely trace the cleaned 53-vertex GIS outline; the overlay and bounds agree to under 0.01 m. GIS is a campus-map footprint, not a wall survey. |
| Placement, orientation, scale, and interior layout | 1.4/2 | Root is at identity/origin; the manifest has the established placement origin. Module bounds are within the footprint, and the Road School maps broadly support the south entrance and Loeb east/northeast of HSSE. The plan has no north arrow or scale. Ringel reads west/left of HSSE in the schematic, but its modeled bounds are east of HSSE. The master placement marker was not freshly checked. |
| Floors, height, and roof form | 1.0/2 | Archival material supports three floors in the central portion. Modeled wall height (16.5 m), overall height (22.5 m), roof elevation, and rooftop forms are not supported by dimensioned elevation/roof sources and remain estimates. |
| Facade, entrances, and distinctive identity | 0.9/2 | The model has perimeter brick walls, a window rhythm, horizontal base courses, south entrance glazing/frame, and broad stairs. In the inspected oblique views, the facade still reads as generic; the more specific stone/column entry and historic library/Fowler Hall composition are not clearly represented. The documented mural is absent. |
| Modular integrity, portability, and evidence quality | 1.8/2 | Fresh Blender reopen confirms the exact hash and object count, identity root, no materialless meshes, and no missing image dependencies. Build record, validation, GIS snapshot, overlay, floor-map snapshots, and multiple views are available. Facade dimensions, roof, heights, exact module offsets, and master placement still lack strong verification. |
| **Total** | **6.9/10** | **Does not meet 8/10 pass threshold.** |

## GIS shell and plan review

The strongest improvement is the shell: the current perimeter follows the Purdue GIS outline as 52 segments rather than a broad rectangular approximation. The `footprint_overlay.png`, `structural_wall_probe.json`, GIS feature snapshot, and `building_validation.json` support the plan trace and bounds. The GIS service establishes footprint and campus location only. It cannot verify facade recesses, roof form, floor elevations, or exact wall positions.

The 2024 Road School map is a schematic floor plan with room labels but no north arrow or scale. It supports broad adjacencies: main entrance toward the bottom/south, Loeb east/northeast of the central library, and Gallery to the left/west on the plan. The modeled Ringel Gallery is placed east of the HSSE center. Because the map is not georeferenced, that apparent discrepancy is a meaningful concern but not a survey-grade proof of an incorrect world direction. Current exact interior offsets cannot be called verified.

## Actionable findings

1. Recheck Ringel Gallery relative to HSSE against any georeferenced or dimensioned plan, and document the transform used. Do not claim the current relative location is exact from the 2024 schematic alone.
2. Replace estimated wall/overall heights and rooftop blocks with dimensions from a reliable elevation/roof source, or label them as deliberate visual approximations in project evidence.
3. Refine the south entrance and facade from Purdue photographic references: column/stone framing, window proportions, and the historic library/Fowler Hall volumes need clearer treatment.
4. Add source-backed roof articulation and rooftop equipment instead of relying on the broad plain roof and abstract blocks.
5. Open the master scene and verify its instance marker against the asset manifest before certifying campus placement.

## Evidence and limitations

The grade is based on the fresh Blender reopen probe, validation and wall records, GIS OBJECTID 615 snapshot and overlay, 2024 Road School floor-map PDF/pages, and south/north/top renders saved beside this report. The archival source supports historical identity and a three-floor central portion but gives no measured elevations. Available exterior imagery supports entry character, not dimensions. Tree/landscape variation is not scored for this building asset.

See `independent_grade_r1.json` for the machine-readable five-criterion scorecard and `evaluate_stewart_r1.py` for the deterministic score calculation. The earlier `INDEPENDENT_GRADE.md` and `independent_grade.json` remain untouched.
