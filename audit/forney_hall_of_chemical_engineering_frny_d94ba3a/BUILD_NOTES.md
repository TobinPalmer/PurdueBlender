# Forney Hall of Chemical Engineering (FRNY)

Candidate build for stable asset `massing_forney_hall_of_chemical_engineering_frny_d94ba3a`.

## Files

- Asset: `modular/buildings/massing_forney_hall_of_chemical_engineering_frny_d94ba3a.blend`
- Builder: `modular/buildings/build_massing_forney_hall_of_chemical_engineering_frny_d94ba3a.py`
- Source register and raw snapshots: this folder (`source_register.json`, `purdue_gis_current.json`, `openstreetmap_way_117146497_full.json`)
- Review renders: `forney_exterior_preview.png`, `forney_roof_and_footprint_preview.png`, `forney_schematic_interior_preview.png`
- Footprint comparison: `footprint_comparison.png` and `footprint_comparison.json`

## Geometry and source review

The exported collection and scene keep the manifest names. The replacement massing follows Purdue campus GIS layer 0, FRNY OBJECTID 12, using the repository's approximate latitude/longitude to campus XY formula. The official source ring has 85 non-closure vertices; a closed-loop 0.4 m RDP simplification yields 22 structural vertices. Model footprint bounds are approximately X `[-69.355, 17.182]` m, Y `[193.220, 279.034]` m. The model remains in campus coordinates, preserving `kind=massing` behavior.

OpenStreetMap way 117146497 (version 9, last edited 2022-06-25) agrees with the Purdue GIS outline by 3,578.27 m² intersection, 98.80% of the GIS polygon and 96.24% of the OSM polygon, after the same approximate local conversion. Symmetric difference is 183.38 m². These are footprint-outline comparisons, not a survey. The former rectangular massing's 88.03 x 86.17 m bounds were close to the source bounds but its 7,585.58 m² rectangle filled in the footprint's notches; the returned GIS ring itself computes to about 3,621.90 m² in the local approximation.

The GIS attribute `Shape.STArea()` reports 6,261.056 m², which conflicts with the returned ring's 3,621.90 m² locally computed area. This mismatch is recorded and unresolved; no global rescaling was made. GIS also provides a separate 1938–1939 FRNY record whose outline is almost wholly inside the newer whole-building polygon. The second record is treated as historical source context, not as another physical building.

## Architecture represented

The exterior is built from procedural red brick, limestone courses/sills, dark glazing and metal window frames, a recessed entrance with stone arch/identification panel, green coping, and restrained schematic roof exhaust/HVAC. Purdue's exterior photo supports the brick/stone character, repeated dark windows and roof-edge color; facade details, window placements, HVAC count and exact entrance position are not survey-measured. Wall top is modeled at 13.9 m, using the legacy GIS `R=46 ft` (~14.02 m) only as a height estimate. Counted levels (6) and photographic story impressions do not fully agree.

The separate `FRNY_Schematic_Interior` collection is intentionally marked as schematic. It includes a Henson Atrium/distillation-column feature, 200 auditorium seats, lab benches and generic partitions from Purdue-published building uses. Room locations and floor layouts are not a georeferenced reproduction of Purdue floor plans.

## Evidence / uncertainty

- Purdue GIS snapshot retrieved 2026-10-26; service fields reference the 2002–2004 addition and report `ChangeYear` 2018. Source CRS output: EPSG:4326; conversion: project local approximate XY, not a surveyed CRS.
- OSM raw geometry retrieved 2026-10-26; edit date 2022-06-25.
- A Purdue Events Calendar image is preserved as `official_exterior.jpg`. Its accessible metadata does not provide a photograph capture date or camera azimuth.
- Google Maps place record was checked at 40.4294512, -86.9139597. A Street View panorama request at 40.42952, -86.91401 returned “No Street View imagery available here.” This only records the sampled point; it does not assert no imagery exists along every nearby road.
- Roof deck form and overall height remain estimated because the accessible sources include no survey or authoritative roof imagery. Purdue's building area sources also report conflicting addition figures; they were not used for footprint scaling.

## Validation state

The candidate was generated and rendered in Blender 5.2.3. Fresh-open validation found 21 objects (16 mesh, 5 text), 24,634 mesh polygons, 33,150 mesh vertices, 11 used materials, no external image or linked-library dependencies, no modifiers, and no hidden asset objects. The shell bounds are 86.54 x 85.81 x 13.90 m; whole-asset bounds include roof equipment and entry steps. SHA-256: `24D28F5617A7B9A9604812A49F7C9E855D75257AC4832EA44D7E8EED6D51B216`.

Fresh-open structural and portability results are in `fresh_open_validation.json`; the asset has not been independently graded yet. Keep the candidate pending until the coordinator's independent reviewer assesses it against its evidence.
