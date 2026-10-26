# Hockmeyer Hall of Structural Biology (HOCK)

Focused repair passes after independent r1 (6.25/10) and r2 (7.75/10), 2026-10-26.

## Footprint decision

Purdue BuildingShapes feature FID 669 identifies Hockmeyer by code, full name, and address. Its layer metadata records native WKID 102100/3857 and `Shape__Area` in Esri meters; the geometry query was requested in EPSG:4326. The native area value 3358.578 m² divided by the project-local ground area 1943.099 m² is 1.7285, close to the expected Web Mercator area scale factor 1/cos(latitude)^2 = 1.7257 at 40.4274° (about 0.2% difference). The prior 73% mismatch is projection distortion in the area attribute, not an area target the shell should be resized to. The model uses the exact Purdue ring, with the repository geographic approximation.

OSM way 283274991 independently matches the name/address and broadly overlaps the Purdue ring in `geometry/hock_gis_osm_outline_comparison.png`. A recheck with polygon boundary-to-segment metrics gives 96.28% intersection-over-union, 3.72% symmetric difference, and 3.603 m boundary Hausdorff. The earlier 16.27 m figure came from vertex-to-vertex matching, which overstates error when 58 and 28-vertex polygons sample curved edges at different points. The remaining discrepancy is localized; no survey drawing was found to establish which edge is the wall line. Purdue's official campus GIS ring remains the single chosen footprint; OSM vertices are not spliced or averaged into it. This is retained as a source limitation.

## Facade and height repair

The official Purdue 2009 dedication photo visibly shows red brick, a large pale opaque upper-cladding volume, and extensive blue-green curtainwall around the courtyard. Storrow|Kinsella project images label two views as looking north and south across the Hockmeyer courtyard and describe the entrance sequence and arrival space. Together these support using the GIS re-entrant/courtyard edge candidates for the broad glazing zones, but do not determine the exact door or facade bay placement. The model now includes the pale panels and larger multi-story glazed runs. The photo is not compass-registered to the GIS outline; the assignment of those facade elements to candidate re-entrant edges is illustrative. No exact doorway position is supported, so the custom doorway and canopy were removed.

Purdue Biological Sciences' 2010 article describes Hockmeyer as three stories and 65,690 square feet; that reported gross area is about 3.14 times the local GIS footprint and independently fits a three-story program, but it is not a height measurement.  Purdue's current emergency plan also describes three occupied floors, a penthouse and a basement. The main 11.4 m envelope remains an estimate (3 x 3.8 m illustrative floor-to-floor spacing), not a measured height. The emergency plan supports penthouse presence, but official exterior photos do not clearly isolate a separate penthouse mass and no roof plan or dimensions were found, so the speculative rooftop block was removed. The undocumented GIS `Extrution=60` remains unused.

## R3 evidence refinement

The GIS/OSM comparison now uses polygon boundary-to-segment and overlap metrics instead of point-to-point vertex pairing. The two local polygons have 96.28% intersection-over-union, 3.72% symmetric difference, and 3.603 m boundary Hausdorff. The earlier 16.27 m figure was vertex-to-vertex; unequal vertex sampling of the same curves inflated that number. Raw source geometry and the unblended official Purdue shell remain unchanged. Full calculations are in `geometry/gis_osm_footprint_metrics.json`.

Facade registration is still unverified: the official exterior photo lacks geolocation; Storrow|Kinsella's north/south courtyard captions support the inward-facing glazing zone but not a specific edge or doorway. The revised model therefore has no claimed door position. The current emergency plan confirms a penthouse exists, but the exterior images do not isolate a rooftop block. The roof is a neutral flat cap and the penthouse is documented but not represented as a separate mass. Main-envelope height remains an estimate.

## Export limitation

The original Blender 5.2.45 asset remains untouched at `original_asset_blender_5_2.blend`. The bundled Blender 5.2.0 binary exits before running Python (`WM_OT_drop_blend_file`), so the fresh asset was rebuilt and reopened with Blender 4.5.15. The expected collection name survives and the geometry checks run, but Blender 4.5 truncates the required long scene ID; the full expected name is also retained in a scene custom property, but `reopen_validation.json` records actual scene-name contract failure explicitly.
